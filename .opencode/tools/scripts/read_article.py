#!/usr/bin/env python3
"""
Чтение полного текста статьи из базы данных.
Поддерживает: полный текст, секции (эвристически), чанки, summary.
"""

import argparse
import math
import os
import re
import sqlite3
import sys
from pathlib import Path


def load_env():
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


def get_article(article_id):
    load_env()
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    if not db_path:
        print("ERROR: LITBASE_SQLITE_PATH not set", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT id, doi, title, full_text, abstract, date, journal, "
        "authors, volume, issue, pages, pmid, filepath "
        "FROM Articles WHERE id = ?",
        [article_id],
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"ERROR: Article with id={article_id} not found", file=sys.stderr)
        sys.exit(1)

    columns = [
        "id", "doi", "title", "full_text", "abstract", "date",
        "journal", "authors", "volume", "issue", "pages", "pmid", "filepath",
    ]
    return dict(zip(columns, row))


def extract_section(text, section_name):
    """Эвристическое извлечение секции из полного текста."""
    if not text:
        return None

    section_patterns = {
        "intro": [
            r"(?i)\b(introduction|background)\b",
        ],
        "methods": [
            r"(?i)\b(methods|materials?\s+and\s+methods|experimental\s+procedures"
            r"|methodology)\b",
        ],
        "results": [
            r"(?i)\b(results|findings)\b",
        ],
        "discussion": [
            r"(?i)\b(discussion|conclusions?\s+and\s+discussion)\b",
        ],
    }

    section_order = ["intro", "methods", "results", "discussion"]
    section_positions = {}

    for sec_name in section_order:
        patterns = section_patterns.get(sec_name, [])
        for pattern in patterns:
            matches = list(re.finditer(pattern, text))
            for m in matches:
                pos = m.start()
                line_start = text.rfind("\n", 0, pos)
                prefix = text[line_start + 1:pos].strip()
                if len(prefix) < 20:
                    if sec_name not in section_positions:
                        section_positions[sec_name] = pos
                    break

    if section_name not in section_positions:
        return None

    start = section_positions[section_name]

    current_idx = section_order.index(section_name)
    end = len(text)
    for next_sec in section_order[current_idx + 1:]:
        if next_sec in section_positions:
            end = section_positions[next_sec]
            break

    ref_match = re.search(r"(?i)\b(references|bibliography)\b", text[start:])
    if ref_match:
        ref_pos = start + ref_match.start()
        if ref_pos < end:
            end = ref_pos

    return text[start:end].strip()


def chunk_text(text, chunk_size=3000):
    """Разбить текст на чанки по словам."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i : i + chunk_size]))
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Read article from database")
    parser.add_argument("id", type=int, help="Article ID")
    parser.add_argument(
        "--section",
        choices=["intro", "methods", "results", "discussion", "all"],
        help="Extract specific section",
    )
    parser.add_argument(
        "--chunk", type=int, default=None,
        help="Return specific chunk number (0-indexed)"
    )
    parser.add_argument(
        "--chunks", action="store_true",
        help="Show number of chunks"
    )
    parser.add_argument(
        "--chunk-size", type=int, default=3000,
        help="Words per chunk (default: 3000)"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Show metadata + first 500 words"
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Show full text"
    )
    args = parser.parse_args()

    article = get_article(args.id)

    print(f"=== Article ID: {article['id']} ===")
    print(f"Title: {article['title']}")
    print(f"Authors: {article['authors']}")
    print(f"Date: {article['date']}")
    print(f"Journal: {article['journal']}")
    print(f"DOI: {article['doi']}")
    print(f"PMID: {article['pmid']}")
    print()

    full_text = article.get("full_text")
    has_text = bool(full_text and full_text.strip())

    if not has_text:
        print("WARNING: No full text available for this article.")
        print(f"\nAbstract:\n{article.get('abstract', 'N/A')}")
        return

    word_count = len(full_text.split())
    print(f"Full text: {word_count} words")
    print()

    if args.summary:
        print(f"Abstract:\n{article.get('abstract', 'N/A')}\n")
        words = full_text.split()[:500]
        print(f"First 500 words:\n{' '.join(words)}...")
        return

    if args.chunks:
        chunks = chunk_text(full_text, args.chunk_size)
        print(f"Total chunks ({args.chunk_size} words each): {len(chunks)}")
        for i, c in enumerate(chunks):
            print(f"  Chunk {i}: {len(c.split())} words")
        return

    if args.chunk is not None:
        chunks = chunk_text(full_text, args.chunk_size)
        if args.chunk < 0 or args.chunk >= len(chunks):
            print(
                f"ERROR: Chunk {args.chunk} out of range (0-{len(chunks)-1})",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"--- Chunk {args.chunk}/{len(chunks) - 1} ---\n")
        print(chunks[args.chunk])
        return

    if args.section:
        if args.section == "all":
            for sec in ["intro", "methods", "results", "discussion"]:
                content = extract_section(full_text, sec)
                if content:
                    print(f"=== {sec.upper()} ===\n{content}\n")
                else:
                    print(f"=== {sec.upper()} === [not found]\n")
        else:
            content = extract_section(full_text, args.section)
            if content:
                print(f"=== {args.section.upper()} ===\n{content}")
            else:
                print(f"Section '{args.section}' not found in this article.")
                print("Falling back to full text first 1000 words...")
                print(" ".join(full_text.split()[:1000]))
        return

    if args.full:
        print(f"=== FULL TEXT ===\n{full_text}")
        return

    print(f"Abstract:\n{article.get('abstract', 'N/A')}\n")
    words = full_text.split()[:500]
    print(f"First 500 words:\n{' '.join(words)}...")


if __name__ == "__main__":
    main()
