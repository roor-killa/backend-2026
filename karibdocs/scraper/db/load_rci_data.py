#!/usr/bin/env python3
"""
Load RCI articles from rci_raw.json into rc_schema.rci_articles.
Usage: python load_rci_data.py [--host localhost] [--port 5433] [--db poo_db] [--user postgres] [--password postgres]
"""

import json
import sys
import argparse
from pathlib import Path
import pg8000.dbapi as pg


def read_json_with_fallback(path: Path):
    """Read JSON with fallback encodings for Windows-exported files."""
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    last_error = None

    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return json.load(f), encoding
        except UnicodeDecodeError as e:
            last_error = e
        except json.JSONDecodeError:
            # Decoding succeeded but JSON content is invalid with this decoding.
            raise

    raise UnicodeDecodeError(
        "utf-8",
        b"",
        0,
        1,
        f"Unable to decode JSON with tried encodings: {', '.join(encodings)}. Last error: {last_error}"
    )


def load_rci_articles(
    json_file: str,
    host: str = "localhost",
    port: int = 5433,
    database: str = "poo_db",
    user: str = "postgres",
    password: str = "postgres"
):
    """Load RCI articles from JSON file into rc_schema.rci_articles."""
    
    json_path = Path(json_file)
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_file}")
        return False
    
    try:
        articles, used_encoding = read_json_with_fallback(json_path)
        print(f"✅ Loaded {len(articles)} articles from {json_file} (encoding: {used_encoding})")
    except UnicodeDecodeError as e:
        print(f"❌ Could not decode file with supported encodings: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    # Connect to PostgreSQL
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
        print(f"✅ Connected to PostgreSQL at {host}:{port}/{database}")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    try:
        # Check if target table exists
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'rc_schema'
                AND table_name = 'rci_articles'
            );
        """)
        if not cur.fetchone()[0]:
            print("❌ rc_schema.rci_articles doesn't exist. Run 04_rc_schema.sql first.")
            conn.close()
            return False
        
        # Prepare data for insertion
        rows = []
        
        for article in articles:
            title = article.get('title', '').strip()
            body = article.get('body', article.get('infos', '')).strip()
            url = article.get('url', '').strip()
            
            # Skip if missing required fields
            if not title or not body or not url:
                print(f"⚠️  Skipping article with missing fields: {title[:50]}...")
                continue
            
            rows.append((
                title,
                article.get('author', ''),
                article.get('photo', ''),
                article.get('infos', ''),
                body,
                url,
                article.get('depth', 1)
            ))
        
        if not rows:
            print("❌ No valid articles to insert")
            conn.close()
            return False
        
        # Insert data (ignore duplicates based on unique url constraint)
        insert_sql = """
            INSERT INTO rc_schema.rci_articles
            (title, author, photo, infos, body, url, depth)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO UPDATE SET
                title = EXCLUDED.title,
                author = EXCLUDED.author,
                photo = EXCLUDED.photo,
                infos = EXCLUDED.infos,
                body = EXCLUDED.body,
                depth = EXCLUDED.depth,
                updated_at = NOW()
        """
        
        try:
            cur.executemany(insert_sql, rows)
            conn.commit()
            print(f"✅ Successfully inserted/updated {len(rows)} articles")
        except Exception as e:
            conn.rollback()
            print(f"❌ Database error during insert: {e}")
            return False
        
    finally:
        cur.close()
        conn.close()
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Load RCI articles into PostgreSQL')
    parser.add_argument('--json', default='../data/raw/rci_raw.json', help='Path to rci_raw.json')
    parser.add_argument('--host', default='localhost', help='PostgreSQL host')
    parser.add_argument('--port', type=int, default=5433, help='PostgreSQL port')
    parser.add_argument('--db', default='poo_db', help='Database name')
    parser.add_argument('--user', default='postgres', help='Database user')
    parser.add_argument('--password', default='postgres', help='Database password')
    
    args = parser.parse_args()
    
    # Find rci_raw.json relative to this script
    script_dir = Path(__file__).parent
    json_path = script_dir / args.json if not Path(args.json).is_absolute() else Path(args.json)
    
    success = load_rci_articles(
        str(json_path),
        host=args.host,
        port=args.port,
        database=args.db,
        user=args.user,
        password=args.password
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
