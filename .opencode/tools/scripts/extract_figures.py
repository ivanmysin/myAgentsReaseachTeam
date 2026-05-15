#!/usr/bin/env python3
"""
Извлечение рисунков из PDF файла статьи.
"""

import argparse
import os
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


def main():
    parser = argparse.ArgumentParser(
        description="Extract figures from article PDF"
    )
    parser.add_argument("id", type=int, help="Article ID")
    parser.add_argument(
        "--output", default=None,
        help="Output directory (default: output/figures/<id>/)"
    )
    parser.add_argument(
        "--min-size", type=int, default=100,
        help="Minimum image dimension in pixels (default: 100)"
    )
    args = parser.parse_args()

    load_env()
    db_path = os.environ.get("LITBASE_SQLITE_PATH")
    pdf_dir = os.environ.get("LITBASE_PDF_DIR", "")

    if not db_path:
        print("ERROR: LITBASE_SQLITE_PATH not set", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT filepath, title FROM Articles WHERE id = ?", [args.id]
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"ERROR: Article {args.id} not found", file=sys.stderr)
        sys.exit(1)

    filepath, title = row

    if not filepath:
        print(f"ERROR: No filepath for article {args.id}", file=sys.stderr)
        sys.exit(1)

    # Extract just the filename from the stored path (removes any ../segments)
    # The filepath in DB may contain '../results/pdfs/' prefix from where DB was created
    filename = Path(filepath).name

    if not pdf_dir:
        # If no pdf_dir configured, try to use filepath as-is
        pdf_path = Path(filepath).resolve()
    else:
        # Use pdf_dir (full path) + filename
        pdf_path = Path(pdf_dir) / filename

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(
        args.output or f"output/figures/{args.id}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import fitz
    except ImportError:
        print(
            "ERROR: PyMuPDF not installed. Run: pip install PyMuPDF",
            file=sys.stderr,
        )
        sys.exit(1)

    doc = fitz.open(str(pdf_path))
    image_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue

                width = base_image.get("width", 0)
                height = base_image.get("height", 0)

                if width < args.min_size or height < args.min_size:
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image.get("ext", "png")
                image_filename = (
                    f"page{page_num + 1}_img{img_idx + 1}.{image_ext}"
                )
                image_path = output_dir / image_filename

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                image_count += 1
                print(
                    f"Extracted: {image_filename} "
                    f"({width}x{height}, {len(image_bytes)} bytes)"
                )

            except Exception as e:
                print(
                    f"Warning: Could not extract image {img_idx} "
                    f"from page {page_num + 1}: {e}",
                    file=sys.stderr,
                )

    doc.close()

    print(f"\nTotal images extracted: {image_count}")
    print(f"Output directory: {output_dir}")

    if image_count == 0:
        print("Note: No images found. The PDF might use vector graphics "
              "or the images are too small.")


if __name__ == "__main__":
    main()
