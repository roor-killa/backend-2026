
from langchain_community.chat_models import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
import json
import re
from app.models.chat_session import ChatSession, ChatMessage
from app.models.document import Document
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
        self._llm = None

    def _get_llm(self):
        if self._llm is not None:
            return self._llm

        provider = (settings.LLM_PROVIDER or "ollama").lower()

        if provider == "mistral":
            if not settings.MISTRAL_API_KEY:
                raise RuntimeError("MISTRAL_API_KEY manquant pour LLM_PROVIDER=mistral")

            self._llm = ChatMistralAI(
                api_key=settings.MISTRAL_API_KEY,
                model=settings.MISTRAL_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=2048,
            )
            return self._llm

        if provider != "ollama":
            raise RuntimeError(
                f"LLM_PROVIDER invalide: {settings.LLM_PROVIDER}. Valeurs supportees: ollama, mistral"
            )

        self._llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            num_predict=2048,
        )
        return self._llm

    def ask(self, user_id: int, question: str, session_id: int = None) -> dict:
        """Traitement complet d'une question RAG."""
        question = (question or "").strip()
        if not question:
            raise ValueError("La question ne peut pas être vide")

        # 1. Session de conversation
        session = self._get_or_create_session(user_id, session_id, question)

        # 2. Recherche sémantique
        relevant_docs = self._retrieve_relevant_docs(user_id, question)

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
            llm = self._get_llm()
            response = llm.invoke(messages)
            answer_text = self._repair_mojibake(str(response.content))
        except Exception as exc:
            provider = (settings.LLM_PROVIDER or "ollama").lower()
            if provider == "mistral":
                model = settings.MISTRAL_MODEL
                extra = "Verifier MISTRAL_API_KEY et la connectivite internet"
            else:
                model = settings.OLLAMA_MODEL
                extra = "Verifier OLLAMA_BASE_URL et lancer `ollama pull <modele>`"

            raise RuntimeError(
                f"LLM indisponible ou modele introuvable ({provider}/{model}). {extra}"
            ) from exc

        # 6. Sauvegarde en BDD
        self._save_messages(session.id, question, answer_text, sources)

        return {
            "session_id":  session.id,
            "answer":      answer_text,
            "sources":     sources,
            "chunks_used": len(relevant_docs),
        }

    def _retrieve_relevant_docs(self, user_id: int, question: str):
        docs = (
            self.db.query(Document)
            .filter(Document.user_id == user_id, Document.is_indexed == True, Document.chunk_count > 0)
            .all()
        )

        if not docs:
            return []

        collection_names = []
        title_by_document_id: dict[int, str] = {}
        for doc in docs:
            if doc.collection_name and doc.collection_name not in collection_names:
                collection_names.append(doc.collection_name)
            title_by_document_id[doc.id] = (doc.original_name or doc.filename or "").lower()

        # Fallback for older rows where collection_name may be missing.
        default_collection = f"user_{user_id}"
        if default_collection not in collection_names:
            collection_names.append(default_collection)

        scored_chunks = []
        candidate_k = max(settings.RAG_K_RESULTS * 5, 20)
        for collection_name in collection_names:
            scored_chunks.extend(
                self.rag.similarity_search_with_scores(
                    collection_name=collection_name,
                    query=question,
                    k=candidate_k,
                )
            )

        if not scored_chunks:
            return []

        question_terms = self._tokenize_for_overlap(question)
        normalized_question = self._normalize_text(question)

        # Rerank using vector score + chunk overlap + explicit title/filename overlap.
        reranked = []
        for doc, score in scored_chunks:
            text = (doc.page_content or "").lower()
            overlap = sum(1 for term in question_terms if term in text)

            meta = doc.metadata or {}
            filename = str(meta.get("filename") or "").lower()

            raw_doc_id = meta.get("document_id")
            doc_id = self._safe_int(raw_doc_id)
            db_title = title_by_document_id.get(doc_id, "") if doc_id is not None else ""

            title_text = f"{filename} {db_title}".strip()
            title_overlap = sum(1 for term in question_terms if term in title_text)

            chunk_bonus = overlap / max(len(question_terms), 1)
            title_bonus = (title_overlap / max(len(question_terms), 1)) * 1.8

            if normalized_question and normalized_question in self._normalize_text(title_text):
                title_bonus += 2.0

            reranked.append((doc, float(score) + chunk_bonus + title_bonus))

        reranked.sort(key=lambda item: item[1], reverse=True)

        selected_docs = []
        seen_fingerprints = set()
        for doc, _ in reranked:
            fingerprint = (
                doc.metadata.get("document_id"),
                doc.metadata.get("filename"),
                (doc.page_content or "")[:160],
            )
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)
            selected_docs.append(doc)
            if len(selected_docs) >= settings.RAG_K_RESULTS:
                break

        return selected_docs

    def _tokenize_for_overlap(self, text: str) -> list[str]:
        terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9']+", text or "")]
        return [t for t in terms if len(t) >= 3]

    def _normalize_text(self, text: str) -> str:
        return " ".join(self._tokenize_for_overlap(text))

    def _safe_int(self, value) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _repair_mojibake(self, text: str) -> str:
        if not text:
            return text

        suspicious_markers = ("Ã", "Â", "├", "�")
        if not any(marker in text for marker in suspicious_markers):
            return text

        for source_encoding in ("cp437", "latin1", "cp1252"):
            try:
                repaired = text.encode(source_encoding).decode("utf-8")
                if repaired and repaired != text:
                    return repaired
            except Exception:
                continue

        return text

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
        self.db.add(ChatMessage(session_id=session_id, role="assistant", content=answer,   sources=json.dumps(sources, ensure_ascii=False)))
        self.db.commit()


    