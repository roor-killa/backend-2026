
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
import json
from app.models.chat_session import ChatSession, ChatMessage
from app.services.rag_service import RAGService
from app.config import settings

SYSTEM_PROMPT = """Tu es KaribDocs Assistant, un assistant intelligent pour l'analyse documentaire.
Tu travailles pour des utilisateurs de la Martinique et des Antilles.

RÈGLES STRICTES :
1. Réponds UNIQUEMENT en te basant sur les documents fournis dans le contexte
2. Si la réponse n'est pas dans les documents, dis-le clairement
3. Cite toujours la source (nom du fichier) de tes informations
4. Réponds en français sauf demande contraire
5. Sois précis, structuré et professionnel
"""

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.rag = RAGService()
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.1,
            num_predict=2048,
        )

    def ask(self, user_id: int, question: str, session_id: int = None) -> dict:
        """Traitement complet d'une question RAG."""
        question = (question or "").strip()
        if not question:
            raise ValueError("La question ne peut pas être vide")

        # 1. Session de conversation
        session = self._get_or_create_session(user_id, session_id, question)

        # 2. Recherche sémantique
        relevant_docs = self.rag.similarity_search(
            collection_name=f"user_{user_id}",
            query=question,
            k=settings.RAG_K_RESULTS,
        )

        # 3. Construction du contexte
        if not relevant_docs:
            context = "Aucun document pertinent trouvé."
            sources = []
        else:
            context_parts = []
            sources = []
            for i, doc in enumerate(relevant_docs):
                fname = doc.metadata.get("filename", "Inconnu")
                context_parts.append(f"[Source {i+1} — {fname}]\n{doc.page_content}")
                if fname not in sources:
                    sources.append(fname)
            context = "\n\n".join(context_parts)

        # 4. Prompt augmenté
        augmented_prompt = f"""
CONTEXTE DOCUMENTAIRE :
{context}

---
QUESTION : {question}
"""

        # 5. Appel LLM
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=augmented_prompt),
        ]
        try:
            response = self.llm.invoke(messages)
        except Exception as exc:
            raise RuntimeError(
                f"Ollama indisponible ou modèle introuvable ({settings.OLLAMA_MODEL})"
            ) from exc

        # 6. Sauvegarde en BDD
        self._save_messages(session.id, question, response.content, sources)

        return {
            "session_id":  session.id,
            "answer":      response.content,
            "sources":     sources,
            "chunks_used": len(relevant_docs),
        }

    def _get_or_create_session(self, user_id, session_id, question):
        if session_id:
            session = self.db.get(ChatSession, session_id)
            if not session or session.user_id != user_id:
                raise ValueError("Session introuvable")
            return session
        title = question[:50] + "..." if len(question) > 50 else question
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def _save_messages(self, session_id, question, answer, sources):
        self.db.add(ChatMessage(session_id=session_id, role="user",    content=question, sources="[]"))
        self.db.add(ChatMessage(session_id=session_id, role="assistant", content=answer,   sources=json.dumps(sources)))
        self.db.commit()


    