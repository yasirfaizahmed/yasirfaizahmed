#!/usr/bin/env python3
"""
Utility to add a new article entry without editing JS/HTML.

Usage example:
python3 scripts/add_article.py \
  --title "My New Article" \
  --summary "Short summary" \
  --tags "LLM,Transformers" \
  --category "Technical" \
  --image "assets/images/articles/my-new-article.jpg" \
  --image-alt "Illustration for my new article"
"""

import argparse
import json
import re
from pathlib import Path


def parse_args():
  parser = argparse.ArgumentParser(description="Add an article to assets/data/articles.json")
  parser.add_argument("--title", required=True)
  parser.add_argument("--summary", required=True)
  parser.add_argument("--tags", required=True, help="Comma-separated tags")
  parser.add_argument("--category", default="Technical")
  parser.add_argument("--link", default="#")
  parser.add_argument("--image", default="", help="Path like assets/images/articles/file.jpg")
  parser.add_argument("--image-alt", default="")
  parser.add_argument("--content", default="", help="Optional full article content")
  return parser.parse_args()


def slugify(text: str) -> str:
  text = text.strip().lower()
  text = re.sub(r"[^a-z0-9\s-]", "", text)
  text = re.sub(r"\s+", "-", text)
  text = re.sub(r"-+", "-", text)
  return text


def main():
  args = parse_args()

  root = Path(__file__).resolve().parent.parent
  data_file = root / "assets" / "data" / "articles.json"
  data_file.parent.mkdir(parents=True, exist_ok=True)

  if data_file.exists():
    articles = json.loads(data_file.read_text(encoding="utf-8"))
    if not isinstance(articles, list):
      raise ValueError("assets/data/articles.json must contain a JSON array")
  else:
    articles = []

  item = {
    "id": slugify(args.title),
    "title": args.title.strip(),
    "summary": args.summary.strip(),
    "content": args.content.strip() or args.summary.strip(),
    "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
    "category": args.category.strip() or "Technical",
    "link": args.link.strip() or "#",
    "image": args.image.strip(),
    "imageAlt": args.image_alt.strip(),
  }

  articles.insert(0, item)
  data_file.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  print(f"Added article: {item['title']}")
  print(f"Updated file: {data_file}")


if __name__ == "__main__":
  main()
