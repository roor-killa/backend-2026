
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