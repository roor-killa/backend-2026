
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