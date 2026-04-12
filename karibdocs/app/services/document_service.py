

import os, uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.schema import Document as LCDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.models.document import Document
from app.models.user import User
from app.config import settings
from app.services.rag_service import RAGService

_MIME_TO_EXT = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.google-apps.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService()

    async def save_document(self, file: UploadFile, user: User) -> Document:
        """Sauvegarde le fichier sur disque et crée l'entrée BDD."""
        user_dir = os.path.join(settings.UPLOAD_DIR, str(user.id))
        os.makedirs(user_dir, exist_ok=True)

        original_name = file.filename or "uploaded_file"
        ext = original_name.split(".")[-1].lower() if "." in original_name else "txt"
        unique_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(user_dir, unique_name)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        doc = Document(
            user_id=user.id,
            filename=unique_name,
            original_name=original_name,
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
            "txt":  lambda p: self._load_text_file(p),
            "md":   lambda p: self._load_text_file(p),
        }
        loader_fn = loaders.get(document.file_type)
        if not loader_fn:
            raise ValueError(f"Type non supporté: {document.file_type}")

        return loader_fn(file_path)

    def _load_text_file(self, file_path: str) -> list[LCDocument]:
        """Charge un fichier texte en essayant plusieurs encodages courants."""
        with open(file_path, "rb") as handle:
            head = handle.read(8)

        # ZIP signature -> likely docx/xlsx/other binary archive, not plain text.
        if head.startswith(b"PK"):
            raise RuntimeError(
                f"Fichier binaire detecte pour {file_path}. Le type de fichier en base est probablement incorrect."
            )

        encodings = ("utf-8", "utf-8-sig", "cp1252", "latin-1")
        last_error: Exception | None = None

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as handle:
                    content = handle.read()
                return [LCDocument(page_content=content, metadata={"source": file_path})]
            except UnicodeDecodeError as exc:
                last_error = exc

        raise RuntimeError(f"Impossible de lire le fichier texte {file_path}") from last_error

    def save_from_bytes(
        self,
        content: bytes,
        filename: str,
        user: User,
        source: str = "drive",
        drive_file_id: str | None = None,
        mime_type: str | None = None,
    ) -> Document:
        """Sauvegarde un fichier binaire (ex: Drive) puis crée l'entrée BDD."""
        user_dir = os.path.join(settings.UPLOAD_DIR, str(user.id))
        os.makedirs(user_dir, exist_ok=True)

        original_name = filename or "drive_file"
        ext = _MIME_TO_EXT.get((mime_type or "").lower())
        if not ext:
            ext = original_name.split(".")[-1].lower() if "." in original_name else "txt"
        unique_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(user_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(content)

        doc = Document(
            user_id=user.id,
            filename=unique_name,
            original_name=original_name,
            file_type=ext,
            file_size=len(content),
            source=source,
            drive_file_id=drive_file_id,
            collection_name=f"user_{user.id}",
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_user_documents(self, user_id: int) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def delete_document(self, document_id: int, user_id: int):
        doc = self.db.get(Document, document_id)
        if not doc or doc.user_id != user_id:
            raise ValueError("Document introuvable")

        file_path = os.path.join(settings.UPLOAD_DIR, str(doc.user_id), doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        self.rag_service.delete_document_chunks(doc.collection_name, str(doc.id))

        self.db.delete(doc)
        self.db.commit()

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

            title_context = (doc.original_name or doc.filename or "").strip()
            if title_context:
                for chunk in chunks:
                    if not chunk.page_content.startswith("Titre document:"):
                        chunk.page_content = f"Titre document: {title_context}\n\n{chunk.page_content}"

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