#!/usr/bin/env python3
"""
Chunk rc_schema.rci_articles into rag_documents and rag_chunks.

Usage:
    python chunk_rci_to_rag.py
    python chunk_rci_to_rag.py --host localhost --port 5433 --db poo_db
    python chunk_rci_to_rag.py --chunk-size 180 --overlap 30 --embedding-model pending
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Iterable, Sequence

import pg8000.dbapi as pg


def split_words(text: str) -> list[str]:
    """Normalize whitespace and split into words."""
    return re.findall(r"\S+", text or "")


def chunk_text_words(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping word chunks."""
    words = split_words(text)
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []
    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break

    return chunks


def validate_chunking(chunk_size: int, overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError("--chunk-size must be > 0")
    if overlap < 0:
        raise ValueError("--overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("--overlap must be strictly smaller than --chunk-size")


def ensure_tables_exist(cur) -> None:
    cur.execute(
        """
        SELECT
            EXISTS(
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'rc_schema'
                AND table_name = 'rci_articles'
            ) AS has_rci,
            EXISTS(
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'rag_documents'
            ) AS has_docs,
            EXISTS(
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'rag_chunks'
            ) AS has_chunks
        """
    )
    has_rci, has_docs, has_chunks = cur.fetchone()

    if not has_rci:
        raise RuntimeError("Missing table rc_schema.rci_articles. Run 04_rc_schema.sql first.")
    if not (has_docs and has_chunks):
        raise RuntimeError("Missing rag_documents/rag_chunks. Run 05_rag_schema.sql first.")


def fetch_articles(cur, limit: int | None = None) -> Sequence[tuple]:
    sql = """
        SELECT id, title, author, photo, infos, body, url, depth, scraped_at, updated_at
        FROM rc_schema.rci_articles
        ORDER BY id
    """
    if limit is not None:
        sql += " LIMIT %s"
        cur.execute(sql, (limit,))
    else:
        cur.execute(sql)
    return cur.fetchall()


def upsert_document(cur, article: tuple) -> int:
    (
        article_id,
        title,
        author,
        photo,
        infos,
        _body,
        url,
        depth,
        scraped_at,
        updated_at,
    ) = article

    source_id = f"rci_article:{article_id}"
    metadata = {
        "source_table": "rc_schema.rci_articles",
        "source_pk": article_id,
        "author": author,
        "photo": photo,
        "infos": infos,
        "depth": depth,
        "scraped_at": str(scraped_at) if scraped_at else None,
        "source_updated_at": str(updated_at) if updated_at else None,
    }

    cur.execute(
        """
        INSERT INTO rag_documents (source_id, title, source_url, language, metadata)
        VALUES (%s, %s, %s, 'fr', %s::jsonb)
        ON CONFLICT (source_id) DO UPDATE
        SET title = EXCLUDED.title,
            source_url = EXCLUDED.source_url,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        RETURNING id
        """,
        (source_id, title, url, _to_json(metadata)),
    )
    return cur.fetchone()[0]


def _to_json(data: dict) -> str:
    import json

    return json.dumps(data, ensure_ascii=False)


def replace_chunks(
    cur,
    document_id: int,
    chunks: Iterable[str],
    embedding_model: str,
    article_url: str,
) -> int:
    cur.execute("DELETE FROM rag_chunks WHERE document_id = %s", (document_id,))

    rows = []
    for idx, chunk in enumerate(chunks):
        token_count = len(split_words(chunk))
        metadata = {
            "source": "rc_schema.rci_articles",
            "url": article_url,
        }
        rows.append(
            (
                document_id,
                idx,
                chunk,
                token_count,
                embedding_model,
                _to_json(metadata),
            )
        )

    if not rows:
        return 0

    cur.executemany(
        """
        INSERT INTO rag_chunks
        (document_id, chunk_index, chunk_text, token_count, embedding_model, metadata)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """,
        rows,
    )
    return len(rows)


def chunk_rci_to_rag(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    chunk_size: int,
    overlap: int,
    embedding_model: str,
    limit: int | None,
) -> bool:
    validate_chunking(chunk_size, overlap)

    try:
        conn = pg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            timeout=10,
        )
        cur = conn.cursor()
    except Exception as exc:
        print(f"❌ Failed to connect to PostgreSQL: {exc}")
        return False

    try:
        ensure_tables_exist(cur)

        articles = fetch_articles(cur, limit=limit)
        if not articles:
            print("⚠️  No article found in rc_schema.rci_articles.")
            return True

        processed_docs = 0
        total_chunks = 0
        skipped = 0

        for article in articles:
            body = (article[5] or "").strip()
            title = (article[1] or "").strip()
            url = (article[6] or "").strip()

            if not body or not title or not url:
                skipped += 1
                continue

            chunks = chunk_text_words(body, chunk_size=chunk_size, overlap=overlap)
            if not chunks:
                skipped += 1
                continue

            document_id = upsert_document(cur, article)
            inserted = replace_chunks(
                cur,
                document_id=document_id,
                chunks=chunks,
                embedding_model=embedding_model,
                article_url=url,
            )

            processed_docs += 1
            total_chunks += inserted

        conn.commit()
        print(
            "✅ Chunking complete: "
            f"documents={processed_docs}, chunks={total_chunks}, skipped={skipped}"
        )
        return True
    except Exception as exc:
        conn.rollback()
        print(f"❌ Chunking failed: {exc}")
        return False
    finally:
        cur.close()
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chunk rc_schema.rci_articles and upsert data into RAG tables"
    )
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=5433, help="PostgreSQL port")
    parser.add_argument("--db", default="poo_db", help="Database name")
    parser.add_argument("--user", default="postgres", help="Database user")
    parser.add_argument("--password", default="postgres", help="Database password")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=200,
        help="Chunk size in words",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=40,
        help="Word overlap between consecutive chunks",
    )
    parser.add_argument(
        "--embedding-model",
        default="pending",
        help="Value stored in rag_chunks.embedding_model",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of articles to process",
    )

    args = parser.parse_args()

    ok = chunk_rci_to_rag(
        host=args.host,
        port=args.port,
        database=args.db,
        user=args.user,
        password=args.password,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        embedding_model=args.embedding_model,
        limit=args.limit,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
