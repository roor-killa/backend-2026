# 🌴 KaribDocs — RAG & Fine-Tuning avec FastAPI
**Université des Antilles — Web Backend L2 — Semestre 2 2025/2026**

---

## 📋 Table des Matières

1. [Concepts Fondamentaux](#1-concepts-fondamentaux)
2. [Architecture & Stack Technique](#2-architecture--stack-technique)
3. [Configuration du Projet](#3-configuration-du-projet)
4. [Upload & Indexation de Documents](#4-upload--indexation-de-documents)
5. [Pipeline RAG Complet & Chatbot](#5-pipeline-rag-complet--chatbot)
6. [Intégration Google Drive](#6-intégration-google-drive)
7. [Introduction au Fine-Tuning](#7-introduction-au-fine-tuning)
8. [TPs & Livrables](#8-tps--livrables)
9. [Évaluation & Barème](#9-évaluation--barème)

---

## 1. Concepts Fondamentaux

### 1.1 Qu'est-ce que le RAG ?

**RAG** (Retrieval-Augmented Generation) est une architecture qui combine la **recherche d'information** avec la **génération de texte** par un LLM. Plutôt que de se fier uniquement aux connaissances "gelées" d'un modèle pré-entraîné, le RAG permet d'injecter dynamiquement des données contextuelles dans la requête envoyée au LLM.

> 💡 **Problème résolu par le RAG**
> - Un LLM classique (GPT-4, Mistral...) est entraîné sur des données jusqu'à une date précise
> - Il ne connaît pas VOS documents internes, vos règlements, vos rapports spécifiques
> - Le RAG "branche" le LLM sur votre base de données documentaire en temps réel
> - Résultat : des réponses précises, factuelles, basées sur VOS données

#### Comparaison : LLM classique vs RAG

| LLM Classique | LLM avec RAG |
|---|---|
| Connaissances figées à la date d'entraînement | Accès aux documents en temps réel |
| Hallucinations possibles sur faits précis | Réponses ancrées dans les sources |
| Ne peut pas citer les sources | Peut citer la source exacte |
| Fine-tuning coûteux pour mise à jour | Mise à jour = nouveau document uploadé |

---

### 1.2 Le Pipeline RAG — Vue Globale

#### Phase 1 : Indexation (offline)

1. Chargement du document (PDF, DOCX, TXT, etc.)
2. Découpage en **chunks** (morceaux de texte)
3. Conversion de chaque chunk en **vecteur** (embedding)
4. Stockage des vecteurs dans une **base vectorielle** (ChromaDB, Pinecone, etc.)

#### Phase 2 : Requête (online)

1. L'utilisateur pose une question
2. La question est convertie en vecteur (même modèle d'embedding)
3. Recherche des chunks les plus similaires (cosine similarity)
4. Assemblage d'un prompt : `[contexte récupéré]` + `[question utilisateur]`
5. Envoi au LLM → réponse générée

```python
# Illustration simplifiée du pipeline RAG
question = "Quels sont les horaires du port de Fort-de-France ?"

# Étape 1 : Embedding de la question
question_vector = embed(question)

# Étape 2 : Recherche sémantique
chunks = vector_db.similarity_search(question_vector, k=3)

# Étape 3 : Construction du prompt
prompt = f"""
Contexte (extrait de vos documents) :
{chr(10).join(chunks)}

Question : {question}
Répondez en vous basant uniquement sur le contexte fourni.
"""

# Étape 4 : Appel LLM
response = llm.generate(prompt)
```

---

### 1.3 Les Embeddings

Un **embedding** est une représentation numérique d'un texte sous forme de vecteur de haute dimension (ex: 1536 dimensions pour `text-embedding-ada-002`). La propriété fondamentale : deux textes sémantiquement proches ont des vecteurs proches dans l'espace vectoriel.

> 🏝️ **Exemple caribéen**
> - `"mangue mûre"` et `"fruit tropical sucré"` → vecteurs **proches**
> - `"biguine"` et `"musique antillaise traditionnelle"` → vecteurs **proches**
> - `"SARA carburant"` et `"station essence"` → vecteurs **proches**
> - `"mangue"` et `"algorithme de tri"` → vecteurs **très éloignés**

---

### 1.4 Bases Vectorielles

| Solution | Type | Usage | Coût |
|---|---|---|---|
| **ChromaDB** | Local / Embarqué | Dev, projets étudiants | Gratuit |
| **Pinecone** | Cloud managé | Production scalable | Freemium |
| **Qdrant** | Self-hosted / Cloud | Production open-source | Gratuit |
| **pgvector** | Extension PostgreSQL | Existant PostgreSQL | Gratuit |
| **FAISS (Meta)** | Local / In-memory | Recherche rapide | Gratuit |

> ✅ **Choix pour KaribDocs**
> - **ChromaDB** en développement (simple, embarqué, aucun service externe)
> - **pgvector** en production (réutilise votre PostgreSQL existant)

---

### 1.5 RAG vs Fine-Tuning

| Critère | RAG | Fine-Tuning |
|---|---|---|
| Coût | Faible | Élevé (GPU, temps) |
| Mise à jour des données | Immédiate | Nécessite ré-entraînement |
| Cas d'usage | Docs changeants, Q&A | Style, ton, tâches spécifiques |
| Traçabilité des sources | Oui (citation) | Non |
| Complexité d'implémentation | Moyenne | Élevée |

> 💡 **Règle pratique**
> - **RAG** → pour répondre à des questions sur des documents spécifiques (votre cas !)
> - **Fine-Tuning** → pour adapter le style/comportement du modèle sur une tâche précise
> - Les deux peuvent être combinés : Fine-Tuning + RAG = modèle spécialisé + données fraîches

---

## 2. Architecture & Stack Technique

### 2.1 Vue d'ensemble de KaribDocs

**KaribDocs** est un backoffice intelligent qui permet à des utilisateurs connectés de gérer leurs documents et d'interroger un chatbot IA entraîné sur leurs propres données.

| Couche | Technologie |
|---|---|
| **Frontend** | Interface backoffice (HTML/JS ou React) |
| **Backend API** | FastAPI (Python) |
| **Authentification** | JWT (OAuth2 Bearer token) |
| **Base de données** | PostgreSQL |
| **Base vectorielle** | ChromaDB (dev) / pgvector (prod) |
| **LLM** | Mistral AI API |
| **Embeddings** | sentence-transformers (local) |
| **Stockage fichiers** | Système local (dev) / S3-compatible (prod) |
| **Google Drive** | OAuth2 Google + API Drive |

---

### 2.2 Dépendances

```txt
# requirements.txt

# --- Framework ---
fastapi==0.111.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.7.4
pydantic-settings==2.3.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# --- RAG & LLM ---
langchain==0.2.5
langchain-community==0.2.5
langchain-mistralai==0.1.9
chromadb==0.5.0
sentence-transformers==3.0.1
pypdf==4.2.0
python-docx==1.1.2
unstructured==0.14.6

# --- Google Drive ---
google-api-python-client==2.133.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
```

---

### 2.3 Structure du Projet

```
karibdocs/
├── app/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── config.py               # Settings (Pydantic BaseSettings)
│   ├── database.py             # Connexion SQLAlchemy
│   │
│   ├── models/                 # Modèles SQLAlchemy (ORM)
│   │   ├── user.py
│   │   ├── document.py
│   │   └── chat_session.py
│   │
│   ├── schemas/                # Schémas Pydantic (validation API)
│   │   ├── user.py
│   │   ├── document.py
│   │   └── chat.py
│   │
│   ├── routers/                # Routes FastAPI
│   │   ├── auth.py             # /auth/login, /auth/register
│   │   ├── documents.py        # /documents/upload, /documents/
│   │   ├── drive.py            # /drive/connect, /drive/sync
│   │   └── chat.py             # /chat/ask, /chat/sessions
│   │
│   ├── services/               # Logique métier
│   │   ├── auth_service.py
│   │   ├── document_service.py # Indexation RAG
│   │   ├── rag_service.py      # Pipeline RAG
│   │   ├── drive_service.py    # Google Drive
│   │   └── chat_service.py
│   │
│   └── core/
│       ├── security.py         # JWT utils
│       └── dependencies.py     # get_current_user
│
├── alembic/                    # Migrations BDD
├── uploads/                    # Fichiers uploadés (dev)
├── chroma_db/                  # Base vectorielle (dev)
├── .env
├── docker-compose.yml
└── Makefile
```

---

### 2.4 Docker Compose

```yaml
# docker-compose.yml
version: '3.9'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
      - ./uploads:/app/uploads
      - ./chroma_db:/app/chroma_db
    env_file: .env
    depends_on:
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: karibdocs
      POSTGRES_USER: kd_user
      POSTGRES_PASSWORD: kd_secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

```bash
# .env
DATABASE_URL=postgresql://kd_user:kd_secret@db:5432/karibdocs
SECRET_KEY=votre-clef-secrete-jwt-tres-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

MISTRAL_API_KEY=votre-clef-mistral

GOOGLE_CLIENT_ID=votre-client-id
GOOGLE_CLIENT_SECRET=votre-secret

UPLOAD_DIR=./uploads
CHROMA_DIR=./chroma_db

# Paramètres RAG
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RAG_K_RESULTS=4
```

---

## 3. Configuration du Projet

### 3.1 Point d'entrée FastAPI

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, documents, drive, chat
from app.database import create_tables

app = FastAPI(
    title="KaribDocs API",
    description="🌴 Backoffice intelligent de gestion documentaire — Université des Antilles",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    create_tables()

app.include_router(auth.router,      prefix="/auth",      tags=["Authentification"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(drive.router,     prefix="/drive",     tags=["Google Drive"])
app.include_router(chat.router,      prefix="/chat",      tags=["Chatbot IA"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "KaribDocs", "version": "1.0.0"}
```

---

### 3.2 Configuration (Pydantic Settings)

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    MISTRAL_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/drive/oauth/callback"

    UPLOAD_DIR: str = "./uploads"
    CHROMA_DIR: str = "./chroma_db"
    MAX_FILE_SIZE_MB: int = 50

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RAG_K_RESULTS: int = 4

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### 3.3 Modèles de Base de Données

```python
# app/models/document.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename        = Column(String(255), nullable=False)
    original_name   = Column(String(255), nullable=False)
    file_type       = Column(String(50))
    file_size       = Column(Integer)
    source          = Column(String(50), default="upload")   # "upload" ou "drive"
    drive_file_id   = Column(String(255), nullable=True)
    is_indexed      = Column(Boolean, default=False)
    chunk_count     = Column(Integer, default=0)
    collection_name = Column(String(255))
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="documents")
```

```python
# app/models/chat_session.py
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    title      = Column(String(255), default="Nouvelle conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role       = Column(String(20))    # "user" ou "assistant"
    content    = Column(Text)
    sources    = Column(Text)          # JSON : sources citées
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
```

---

## 4. Upload & Indexation de Documents

### 4.1 Router Documents

```python
# app/routers/documents.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.models.user import User
from app.schemas.document import DocumentOut

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload un document et l'indexe en arrière-plan."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Type non supporté: {file.content_type}")

    service = DocumentService(db)
    document = await service.save_document(file, current_user)

    # Indexation asynchrone (ne bloque pas la réponse HTTP)
    background_tasks.add_task(service.index_document, document.id)

    return document

@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    return service.get_user_documents(current_user.id)

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    service.delete_document(document_id, current_user.id)
    return {"message": "Document supprimé avec succès"}

@router.post("/{document_id}/reindex")
def reindex_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    background_tasks.add_task(service.index_document, document_id, force=True)
    return {"message": "Ré-indexation lancée en arrière-plan"}
```

---

### 4.2 Service de Gestion Documentaire

```python
# app/services/document_service.py
import os, uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.models.document import Document
from app.models.user import User
from app.config import settings
from app.services.rag_service import RAGService

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService()

    async def save_document(self, file: UploadFile, user: User) -> Document:
        """Sauvegarde le fichier sur disque et crée l'entrée BDD."""
        user_dir = os.path.join(settings.UPLOAD_DIR, str(user.id))
        os.makedirs(user_dir, exist_ok=True)

        ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(user_dir, unique_name)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        doc = Document(
            user_id=user.id,
            filename=unique_name,
            original_name=file.filename,
            file_type=ext,
            file_size=len(content),
            source="upload",
            collection_name=f"user_{user.id}",  # 1 collection ChromaDB par utilisateur
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def load_document(self, document: Document) -> list:
        """Charge et parse un document selon son type."""
        file_path = os.path.join(settings.UPLOAD_DIR, str(document.user_id), document.filename)

        loaders = {
            "pdf":  lambda p: PyPDFLoader(p).load(),
            "docx": lambda p: Docx2txtLoader(p).load(),
            "txt":  lambda p: TextLoader(p, encoding="utf-8").load(),
            "md":   lambda p: TextLoader(p, encoding="utf-8").load(),
        }
        loader_fn = loaders.get(document.file_type)
        if not loader_fn:
            raise ValueError(f"Type non supporté: {document.file_type}")

        return loader_fn(file_path)

    def index_document(self, document_id: int, force: bool = False):
        """Pipeline d'indexation : charge → découpe → embed → stocke."""
        doc = self.db.get(Document, document_id)
        if not doc or (doc.is_indexed and not force):
            return

        try:
            # 1. Chargement
            pages = self.load_document(doc)

            # 2. Découpage en chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            )
            chunks = splitter.split_documents(pages)

            # 3. Ajout de métadonnées
            for chunk in chunks:
                chunk.metadata.update({
                    "document_id": doc.id,
                    "filename":    doc.original_name,
                    "user_id":     doc.user_id,
                })

            # 4. Stockage dans ChromaDB
            ids = self.rag_service.add_documents(
                collection_name=doc.collection_name,
                documents=chunks,
                doc_id=str(doc.id),
                force=force,
            )

            # 5. Mise à jour BDD
            doc.is_indexed  = True
            doc.chunk_count = len(ids)
            self.db.commit()

        except Exception as e:
            print(f"Erreur indexation doc {document_id}: {e}")
            raise
```

---

### 4.3 Service RAG — Gestion ChromaDB

```python
# app/services/rag_service.py
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document as LCDocument
from app.config import settings

class RAGService:
    """Service centralisé pour les opérations RAG."""

    def __init__(self):
        # Modèle d'embedding local (gratuit, supporte le français)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

    def get_or_create_collection(self, collection_name: str) -> Chroma:
        return Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def add_documents(
        self,
        collection_name: str,
        documents: list[LCDocument],
        doc_id: str,
        force: bool = False
    ) -> list[str]:
        vectorstore = self.get_or_create_collection(collection_name)

        if force:
            vectorstore._collection.delete(where={"document_id": doc_id})

        ids = [f"{doc_id}_chunk_{i}" for i in range(len(documents))]
        vectorstore.add_documents(documents=documents, ids=ids)
        return ids

    def similarity_search(
        self,
        collection_name: str,
        query: str,
        k: int = None,
        filter_metadata: dict = None
    ) -> list[LCDocument]:
        k = k or settings.RAG_K_RESULTS
        vectorstore = self.get_or_create_collection(collection_name)
        return vectorstore.similarity_search(query=query, k=k, filter=filter_metadata)

    def delete_document_chunks(self, collection_name: str, doc_id: str):
        vectorstore = self.get_or_create_collection(collection_name)
        vectorstore._collection.delete(where={"document_id": doc_id})
```

---

## 5. Pipeline RAG Complet & Chatbot

### 5.1 Service Chat

```python
# app/services/chat_service.py
from langchain_mistralai import ChatMistralAI
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
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            api_key=settings.MISTRAL_API_KEY,
            temperature=0.1,
            max_tokens=2048,
        )

    def ask(self, user_id: int, question: str, session_id: int = None) -> dict:
        """Traitement complet d'une question RAG."""

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
        response = self.llm.invoke(messages)

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
            return self.db.get(ChatSession, session_id)
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
```

---

### 5.2 Router Chat

```python
# app/routers/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.user import User
from typing import List

router = APIRouter()

@router.post("/ask", response_model=ChatResponse)
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pose une question au chatbot RAG."""
    service = ChatService(db)
    return service.ask(
        user_id=current_user.id,
        question=request.question,
        session_id=request.session_id,
    )

@router.get("/sessions")
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.chat_session import ChatSession
    return db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()

@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.chat_session import ChatMessage
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
```

---

### 5.3 Schémas Pydantic

```python
# app/schemas/chat.py
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Quels sont les délais de livraison mentionnés dans le contrat ?",
                "session_id": None
            }
        }
    }

class ChatResponse(BaseModel):
    session_id: int
    answer: str
    sources: List[str]
    chunks_used: int
```

---

## 6. Intégration Google Drive

### 6.1 Flux OAuth2

> 🔐 **Étapes du flux**
> 1. L'utilisateur clique "Connecter Google Drive"
> 2. Redirection vers la page d'autorisation Google
> 3. L'utilisateur accepte → Google renvoie un `code`
> 4. Notre API échange le `code` contre des tokens (`access_token` + `refresh_token`)
> 5. On stocke les tokens en BDD → accès persistent

---

### 6.2 Service Google Drive

```python
# app/services/drive_service.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from app.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
]

SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "application/vnd.google-apps.document": "docx",  # Google Docs → export DOCX
}

class DriveService:
    def get_auth_url(self) -> str:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id":     settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
                    "token_uri":     "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def list_files(self, credentials: dict, folder_id: str = None) -> list:
        creds = Credentials(**credentials)
        service = build("drive", "v3", credentials=creds)

        query = "trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        mime_filter = " or ".join([f"mimeType='{m}'" for m in SUPPORTED_MIME_TYPES])
        query += f" and ({mime_filter})"

        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, size, modifiedTime)",
            pageSize=50,
        ).execute()
        return results.get("files", [])

    def download_file(self, file_id: str, mime_type: str, credentials: dict) -> bytes:
        creds = Credentials(**credentials)
        service = build("drive", "v3", credentials=creds)

        # Google Docs → export DOCX automatique
        if mime_type == "application/vnd.google-apps.document":
            request = service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            request = service.files().get_media(fileId=file_id)

        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue()
```

---

### 6.3 Router Drive

```python
# app/routers/drive.py
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.drive_service import DriveService
from app.services.document_service import DocumentService
from app.models.user import User

router = APIRouter()

@router.get("/connect")
def connect_drive(current_user: User = Depends(get_current_user)):
    """Redirige l'utilisateur vers l'autorisation Google."""
    service = DriveService()
    return {"auth_url": service.get_auth_url()}

@router.get("/oauth/callback")
def oauth_callback(code: str = Query(...), db: Session = Depends(get_db)):
    """Reçoit le code OAuth2 et stocke les tokens."""
    service = DriveService()
    tokens = service.exchange_code(code)
    # TODO : lier les tokens à l'utilisateur via le paramètre `state`
    return {"message": "Google Drive connecté avec succès"}

@router.get("/files")
def list_drive_files(
    folder_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    credentials = _get_user_credentials(current_user.id, db)
    service = DriveService()
    files = service.list_files(credentials, folder_id)
    return {"files": files, "count": len(files)}

@router.post("/sync/{file_id}")
def sync_drive_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importe et indexe un fichier depuis Drive."""
    credentials = _get_user_credentials(current_user.id, db)
    drive_svc = DriveService()
    doc_svc   = DocumentService(db)

    file_info = drive_svc.get_file_info(file_id, credentials)
    content   = drive_svc.download_file(file_id, file_info["mimeType"], credentials)

    doc = doc_svc.save_from_bytes(
        content=content,
        filename=file_info["name"],
        user=current_user,
        source="drive",
        drive_file_id=file_id,
    )
    background_tasks.add_task(doc_svc.index_document, doc.id)

    return {"message": f"'{file_info['name']}' importé", "document_id": doc.id}
```

---

## 7. Introduction au Fine-Tuning

### 7.1 Cas d'usage pour KaribDocs

> 🎯 **Quand utiliser le Fine-Tuning ?**
> - Adapter le ton du chatbot au contexte caribéen (expressions locales)
> - Entraîner le modèle sur un domaine très spécialisé (droit antillais, agriculture tropicale)
> - Améliorer la qualité des réponses sur un type de document précis
> - Créer un modèle qui respecte les préférences de formatage de votre organisation

---

### 7.2 Préparation du Dataset (format JSONL)

```jsonl
{"messages": [
  {"role": "system",   "content": "Tu es KaribDocs Assistant, spécialiste en analyse de documents antillais."},
  {"role": "user",     "content": "Qu'est-ce que le TCSP à Fort-de-France ?"},
  {"role": "assistant","content": "Le TCSP (Transport Collectif en Site Propre) est le réseau de bus en voie dédiée de l'agglomération foyalaise..."}
]}
{"messages": [
  {"role": "system",   "content": "Tu es KaribDocs Assistant..."},
  {"role": "user",     "content": "Explique le crédit agricole en Martinique"},
  {"role": "assistant","content": "La BRED (anciennement Crédit Agricole Martinique) propose..."}
]}
```

> **Minimum recommandé :** 50 à 100 exemples pour un fine-tuning efficace

---

### 7.3 Fine-Tuning via Mistral AI API

```python
# scripts/finetune_mistral.py
import os, time
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def upload_dataset(file_path: str) -> str:
    """Upload le fichier JSONL sur les serveurs Mistral."""
    with open(file_path, "rb") as f:
        response = client.files.upload(
            file={"file_name": "karib_dataset.jsonl", "content": f},
            purpose="fine-tune",
        )
    print(f"Dataset uploadé : {response.id}")
    return response.id

def create_finetune_job(training_file_id: str) -> str:
    """Lance le job de fine-tuning."""
    job = client.fine_tuning.jobs.create(
        model="open-mistral-7b",
        training_files=[training_file_id],
        hyperparameters={
            "training_steps": 100,
            "learning_rate":  0.0001,
        },
        suffix="karibdocs-v1",
    )
    print(f"Job créé : {job.id} — Statut: {job.status}")
    return job.id

def monitor_job(job_id: str):
    """Surveille l'avancement du fine-tuning."""
    while True:
        job = client.fine_tuning.jobs.get(job_id=job_id)
        print(f"Statut: {job.status} | Tokens: {job.trained_tokens}")
        if job.status in ["SUCCESS", "FAILED", "CANCELLED"]:
            if job.status == "SUCCESS":
                print(f"✅ Modèle disponible : {job.fine_tuned_model}")
            break
        time.sleep(30)

if __name__ == "__main__":
    file_id = upload_dataset("./data/dataset_karib.jsonl")
    job_id  = create_finetune_job(file_id)
    monitor_job(job_id)
```

---

### 7.4 Utiliser le Modèle Fine-Tuné

```python
# app/config.py
MISTRAL_MODEL: str = "mistral-large-latest"
MISTRAL_FINETUNED_MODEL: str = ""  # Ex: "ft:open-mistral-7b:org:karibdocs-v1"

# app/services/chat_service.py
def get_llm(use_finetuned: bool = False):
    model = settings.MISTRAL_FINETUNED_MODEL if (
        use_finetuned and settings.MISTRAL_FINETUNED_MODEL
    ) else settings.MISTRAL_MODEL

    return ChatMistralAI(
        model=model,
        api_key=settings.MISTRAL_API_KEY,
        temperature=0.1,
    )
```

> ⚠️ **Coûts Fine-Tuning Mistral**
> - ~$2 / million de tokens d'entraînement
> - 1000 exemples ≈ 100k–500k tokens → budget estimé : **$5 à $20**
> - Alternative gratuite : **Ollama** + modèle local (Llama 3, Mistral 7B)
> - Pour le cours : le RAG seul suffit, le fine-tuning est un **bonus**

---

## 8. TPs & Livrables

### TP 1 — Mise en place de l'environnement *(Semaine 1-2)*

**Objectif :** Configurer Docker et démarrer KaribDocs

1. Cloner le repo : `git clone` + `git checkout -b group-NomGroupe`
2. Configurer le `.env` (BDD, clef Mistral sandbox)
3. Démarrer : `docker-compose up --build`
4. Vérifier `/docs` et appliquer les migrations : `alembic upgrade head`
5. Implémenter `/auth/register` et `/auth/login` avec JWT
6. Tester avec Postman : inscription → connexion → récupération du token

---

### TP 2 — Upload et Indexation *(Semaine 3-4)*

**Objectif :** Implémenter le système d'upload et l'indexation RAG

1. Implémenter `POST /documents/upload` (validation, sauvegarde, indexation en BG)
2. Tester l'upload d'un PDF du Journal Officiel de la Martinique
3. Vérifier l'indexation en inspectant ChromaDB
4. Implémenter `GET /documents/` et `DELETE /documents/{id}`
5. Ajouter la pagination à la liste
6. **Bonus :** Implémenter `POST /documents/{id}/reindex`

---

### TP 3 — Pipeline RAG & Chatbot *(Semaine 5-6)*

**Objectif :** Implémenter le chatbot complet avec RAG

1. Implémenter `POST /chat/ask` avec le service RAG complet
2. Uploader 3 documents sur un thème commun (ex : règlements UA)
3. Poser 5 questions et évaluer la pertinence des réponses
4. Implémenter `GET /chat/sessions` et l'historique des messages
5. Ajouter la liste des sources citées dans chaque réponse
6. Comparer les réponses avec et sans RAG (appel LLM direct vs augmenté)

---

### TP 4 — Google Drive & Fine-Tuning *(Semaine 7-8)*

**Objectif :** Connecter Google Drive et initier un fine-tuning

1. Créer un projet Google Cloud et activer l'API Drive
2. Implémenter `GET /drive/connect` et `GET /drive/oauth/callback`
3. Lister les fichiers d'un dossier Drive
4. Implémenter `POST /drive/sync/{file_id}`
5. Créer un dataset JSONL de 30+ exemples Q&A caribéens
6. **Bonus :** Lancer un job de fine-tuning Mistral et utiliser le modèle résultant

---

## 9. Évaluation & Barème

### 9.1 Critères

| Critère | Points | Détail |
|---|---|---|
| Authentification JWT fonctionnelle | 10 | Register, Login, token valide |
| Upload & indexation (≥3 types) | 15 | PDF, DOCX, TXT indexés |
| Pipeline RAG complet | 20 | Recherche sémantique + LLM |
| Sources citées dans chaque réponse | 10 | Traçabilité des chunks |
| Historique des conversations | 10 | Sessions + messages |
| Intégration Google Drive (OAuth + sync) | 15 | Flux OAuth2 + import fichier |
| Qualité du code (clean, commenté, typé) | 10 | PEP8, docstrings, types Pydantic |
| Tests unitaires (pytest) | 5 | ≥5 tests services |
| **Bonus : Fine-Tuning fonctionnel** | +5 | Dataset + job Mistral |
| **TOTAL** | **100** | |

---

### 9.2 Politique IA

> ⚠️ **Règle importante**
> - L'utilisation de ChatGPT, Claude, Copilot est **AUTORISÉE**
> - **CONDITION :** Vous devez expliquer chaque ligne de code à l'oral si demandé
> - Tout code inexpliqué = **0 sur la partie concernée**
> - Citer les sources IA utilisées dans votre `README.md`

---

### 9.3 Livrables

- [ ] Repo GitHub (branche `group-NomGroupe`) avec `README.md` complet
- [ ] Fichier `.env.example` (sans les vraies clefs !)
- [ ] Collection Postman exportée (tests des endpoints)
- [ ] Rapport PDF (5-10 pages) : architecture, difficultés, décisions techniques
- [ ] Démo vidéo (3-5 min) : Upload → Question chatbot → Réponse avec sources

---

## 🔗 Ressources

| Ressource | Lien |
|---|---|
| FastAPI | https://fastapi.tiangolo.com |
| LangChain Python | https://python.langchain.com |
| ChromaDB | https://docs.trychroma.com |
| Mistral AI API | https://docs.mistral.ai |
| sentence-transformers | https://sbert.net |
| Google Drive API | https://developers.google.com/drive |
| Hugging Face | https://huggingface.co |
| pgvector | https://github.com/pgvector/pgvector |
| Ollama (LLM local) | https://ollama.com |
