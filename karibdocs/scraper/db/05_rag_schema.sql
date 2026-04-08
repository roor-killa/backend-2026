-- =============================================================================
-- Lang Matinitjé — RAG schema (documents + chunks)
-- First step: dedicated pgvector-ready storage for retrieval
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- Store document-level metadata and source tracking.
CREATE TABLE IF NOT EXISTS rag_documents (
    id              BIGSERIAL PRIMARY KEY,
    source_id       TEXT NOT NULL,
    title           TEXT,
    source_url      TEXT,
    language        VARCHAR(10) NOT NULL DEFAULT 'fr',
    checksum        TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_rag_documents_source_id UNIQUE (source_id)
);

-- Store chunk text and its vector embedding used by semantic retrieval.
CREATE TABLE IF NOT EXISTS rag_chunks (
    id                  BIGSERIAL PRIMARY KEY,
    document_id         BIGINT NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index         INTEGER NOT NULL,
    chunk_text          TEXT NOT NULL,
    token_count         INTEGER,
    embedding_model     TEXT NOT NULL,
    embedding           vector(384),
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_rag_chunks_document_chunk UNIQUE (document_id, chunk_index)
);

COMMENT ON TABLE rag_documents IS 'Canonical documents for RAG ingestion.';
COMMENT ON TABLE rag_chunks IS 'Text chunks with embeddings for semantic retrieval.';
COMMENT ON COLUMN rag_chunks.embedding IS 'Embedding vector dimension 384 (e.g. all-MiniLM-L6-v2).';

CREATE INDEX IF NOT EXISTS idx_rag_documents_language
    ON rag_documents (language);

CREATE INDEX IF NOT EXISTS idx_rag_documents_source_url
    ON rag_documents (source_url);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_document_id
    ON rag_chunks (document_id);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding_model
    ON rag_chunks (embedding_model);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_metadata
    ON rag_chunks USING gin (metadata);

-- HNSW is suitable for cosine nearest-neighbor retrieval in pgvector.
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding_hnsw
    ON rag_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Reuse trigger helper from schema.sql.
DROP TRIGGER IF EXISTS trg_rag_documents_updated_at ON rag_documents;
CREATE TRIGGER trg_rag_documents_updated_at
    BEFORE UPDATE ON rag_documents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_rag_chunks_updated_at ON rag_chunks;
CREATE TRIGGER trg_rag_chunks_updated_at
    BEFORE UPDATE ON rag_chunks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- END
-- =============================================================================