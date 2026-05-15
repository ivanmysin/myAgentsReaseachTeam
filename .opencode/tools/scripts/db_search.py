#!/usr/bin/env python3
"""
Поиск статей в SQLite базе данных.
Режимы: keyword, sql, author, doi, id
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path


def load_env():
    """Загрузить переменные из .env файла."""
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def get_db_path():
    load_env()
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    if not db_path:
        print("ERROR: LITBASE_SQLITE_PATH not set in .env", file=sys.stderr)
        sys.exit(1)
    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}", file=sys.stderr)
        sys.exit(1)
    return db_path


def format_results(rows, columns):
    """Форматировать результаты в читаемый вид."""
    if not rows:
        print("No results found.")
        return
    print(f"Found {len(rows)} result(s):\n")
    for i, row in enumerate(rows, 1):
        print(f"--- Result {i} ---")
        for col, val in zip(columns, row):
            if val is None:
                continue
            val_str = str(val)
            if col == "full_text" and len(val_str) > 500:
                val_str = val_str[:500] + "... [truncated]"
            elif col == "abstract" and len(val_str) > 1000:
                val_str = val_str[:1000] + "... [truncated]"
            print(f"  {col}: {val_str}")
        print()


def search_keyword(conn, query, fields, limit):
    """Полнотекстовый поиск по title, abstract, full_text."""
    field_list = ", ".join(fields)
    terms = query.split()
    conditions = []
    params = []
    for term in terms:
        term_cond = "(title LIKE ? OR abstract LIKE ? OR full_text LIKE ?)"
        conditions.append(term_cond)
        params.extend([f"%{term}%"] * 3)

    where = " AND ".join(conditions)
    sql = f"SELECT {field_list} FROM Articles WHERE {where} LIMIT ?"
    params.append(limit)

    cursor = conn.execute(sql, params)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def search_sql(conn, query, fields, limit):
    """Выполнить произвольный SQL-запрос."""
    if not query.strip().upper().startswith("SELECT"):
        print("ERROR: Only SELECT queries are allowed.", file=sys.stderr)
        sys.exit(1)
    try:
        cursor = conn.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        format_results(rows, columns)
    except sqlite3.Error as e:
        print(f"SQL Error: {e}", file=sys.stderr)
        sys.exit(1)


def search_author(conn, name, fields, limit):
    """Поиск по автору."""
    field_list = ", ".join(fields)
    sql = f"SELECT {field_list} FROM Articles WHERE authors LIKE ? LIMIT ?"
    cursor = conn.execute(sql, [f"%{name}%", limit])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def search_doi(conn, doi, fields):
    """Поиск по DOI."""
    field_list = ", ".join(fields)
    sql = f"SELECT {field_list} FROM Articles WHERE doi = ?"
    cursor = conn.execute(sql, [doi])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def search_id(conn, article_id, fields):
    """Поиск по ID."""
    field_list = ", ".join(fields)
    sql = f"SELECT {field_list} FROM Articles WHERE id = ?"
    cursor = conn.execute(sql, [article_id])
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    format_results(rows, columns)


def main():
    parser = argparse.ArgumentParser(description="Search articles database")
    parser.add_argument(
        "mode", choices=["keyword", "sql", "author", "doi", "id"]
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--fields",
        default="id,title,authors,date,doi,abstract",
        help="Comma-separated fields to return",
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--full", action="store_true", help="Include full_text"
    )
    args = parser.parse_args()

    fields = [f.strip() for f in args.fields.split(",")]
    if args.full and "full_text" not in fields:
        fields.append("full_text")

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    try:
        if args.mode == "keyword":
            search_keyword(conn, args.query, fields, args.limit)
        elif args.mode == "sql":
            search_sql(conn, args.query, fields, args.limit)
        elif args.mode == "author":
            search_author(conn, args.query, fields, args.limit)
        elif args.mode == "doi":
            search_doi(conn, args.query, fields)
        elif args.mode == "id":
            search_id(conn, args.query, fields)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
