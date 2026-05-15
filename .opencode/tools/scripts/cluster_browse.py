#!/usr/bin/env python3
"""
Просмотр кластеров статей.
Поддерживает:
- CSV файл: LITBASE_CLUSTERS_CSV (статьи + информация о кластерах)
- HTML файл: LITBASE_CLUSTERS_MD (ключевые слова кластеров)
"""

import argparse
import csv
import os
import re
import sys
from collections import defaultdict
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


def load_cluster_keywords_from_html():
    """Load cluster keywords from HTML summary file."""
    load_env()
    html_path = os.environ.get("LITBASE_CLUSTERS_MD")
    
    if not html_path or not Path(html_path).exists():
        return {}  # Return empty dict if no HTML file
    
    cluster_keywords = {}
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the table rows - pattern: <tr><td>NUM</td><td>COUNT</td><td><span class="keyword">...
    # Example: <tr><td><a href="cluster_00.html" class="doi-link" target="_blank">0</a></td><td>361</td><td><span class='keyword'>('navigation', 879) </span>...
    pattern = r'<tr><td><a[^>]*>(\d+)</a></td><td>(\d+)</td><td>(.*?)</td></tr>'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        cluster_id = int(match.group(1))
        count = int(match.group(2))
        keywords_html = match.group(3)
        
        # Extract keyword strings from spans
        # Handle both single and double quotes for class, and optional space before </span>
        # Pattern examples: <span class='keyword'>('word', 123)</span> or <span class="keyword">('word', 123) </span>
        kw_pattern = r'''<span\s+class=["']keyword["']>\s*\('([^']+)',\s*(\d+)\)\s*</span>'''
        keywords = []
        for kw_match in re.finditer(kw_pattern, keywords_html):
            word = kw_match.group(1)
            freq = kw_match.group(2)
            keywords.append(f"{word} ({freq})")
        
        cluster_keywords[cluster_id] = {
            'count': count,
            'keywords': keywords
        }
    
    return cluster_keywords


def load_clusters():
    """Load cluster information from CSV file."""
    load_env()
    csv_path = os.environ.get("LITBASE_CLUSTERS_CSV")
    if not csv_path:
        print("ERROR: LITBASE_CLUSTERS_CSV not set", file=sys.stderr)
        sys.exit(1)
    if not Path(csv_path).exists():
        print(f"ERROR: File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    clusters = defaultdict(list)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cluster_id = int(row["cluster"])
            clusters[cluster_id].append(row)

    return clusters


def list_clusters(clusters, html_keywords=None):
    """Показать все кластеры."""
    if html_keywords is None:
        html_keywords = load_cluster_keywords_from_html()
    
    print(f"Total clusters: {len(clusters)}\n")
    print(f"{'Cluster':>8} | {'Size':>5} | Keywords")
    print("-" * 80)

    for cluster_id in sorted(clusters.keys()):
        articles = clusters[cluster_id]
        
        # Try HTML keywords first, then fall back to CSV
        if cluster_id in html_keywords:
            keywords = ", ".join(html_keywords[cluster_id]['keywords'][:5])
        else:
            keywords = articles[0].get("keywords", "N/A")
        
        print(f"{cluster_id:>8} | {len(articles):>5} | {keywords}")


def show_cluster(clusters, cluster_id, html_keywords=None):
    """Показать статьи кластера."""
    if html_keywords is None:
        html_keywords = load_cluster_keywords_from_html()
    
    if cluster_id not in clusters:
        print(f"Cluster {cluster_id} not found.")
        return

    articles = clusters[cluster_id]

    # Show keywords from HTML
    print(f"=== Cluster {cluster_id} ===")
    if cluster_id in html_keywords:
        keywords = html_keywords[cluster_id]['keywords']
        print(f"Keywords: {', '.join(keywords)}")
    else:
        print(f"Keywords: {articles[0].get('keywords', 'N/A')}")
    print(f"Size: {len(articles)} articles\n")

    articles_sorted = sorted(
        articles, key=lambda x: float(x.get("similarity", 0)), reverse=True
    )

    for i, art in enumerate(articles_sorted, 1):
        sim = float(art.get("similarity", 0))
        print(f"{i:>3}. [{art['id']}] ({sim:.4f}) {art.get('date', 'N/A')} "
              f"- {art['title']}")
        if art.get("doi"):
            print(f"     DOI: {art['doi']}")


def find_clusters(clusters, query, html_keywords=None):
    """Найти кластеры по ключевым словам."""
    if html_keywords is None:
        html_keywords = load_cluster_keywords_from_html()
    
    query_terms = query.lower().split()
    results = []

    for cluster_id, articles in clusters.items():
        score = 0
        
        # Check HTML keywords
        if cluster_id in html_keywords:
            kw_text = " ".join(html_keywords[cluster_id]['keywords']).lower()
            score = sum(1 for term in query_terms if term in kw_text)
        
        # Also check CSV keywords if no match yet
        if score == 0:
            keywords = articles[0].get("keywords", "").lower()
            score = sum(1 for term in query_terms if term in keywords)
        
        if score > 0:
            results.append((cluster_id, score, articles))

    results.sort(key=lambda x: x[1], reverse=True)

    if not results:
        print(f"No clusters found matching: {query}")
        return

    print(f"Clusters matching \"{query}\":\n")
    for cluster_id, score, articles in results:
        if cluster_id in html_keywords:
            keywords = ", ".join(html_keywords[cluster_id]['keywords'][:5])
        else:
            keywords = articles[0].get("keywords", "N/A")
        print(
            f"  Cluster {cluster_id} (match: {score}, "
            f"size: {len(articles)}): {keywords}"
        )


def main():
    parser = argparse.ArgumentParser(description="Browse article clusters")
    parser.add_argument("mode", choices=["list", "show", "find"])
    parser.add_argument(
        "argument", nargs="?", default=None,
        help="Cluster number (for show) or query (for find)"
    )
    args = parser.parse_args()

    clusters = load_clusters()
    html_keywords = load_cluster_keywords_from_html()
    
    if not html_keywords:
        print("Note: HTML keywords file not found or empty. Using CSV keywords.")
        print()

    if args.mode == "list":
        list_clusters(clusters, html_keywords)
    elif args.mode == "show":
        if args.argument is None:
            print("ERROR: Cluster number required", file=sys.stderr)
            sys.exit(1)
        show_cluster(clusters, int(args.argument), html_keywords)
    elif args.mode == "find":
        if args.argument is None:
            print("ERROR: Search query required", file=sys.stderr)
            sys.exit(1)
        find_clusters(clusters, args.argument, html_keywords)


if __name__ == "__main__":
    main()
