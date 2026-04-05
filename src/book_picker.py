"""
book_picker.py — Select a book from books.csv based on posting mode.

Modes:
  random    — Any book not posted in the last 30 days
  curated   — Books marked curated=true, not recently posted
  seasonal  — Books whose seasonal_tags match the current season/month
  new       — Books added in the last 60 days, not yet posted
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path


SEASON_MAP = {
    12: ["winter", "holiday"],
    1: ["winter"],
    2: ["winter"],
    3: ["spring"],
    4: ["spring"],
    5: ["spring"],
    6: ["summer"],
    7: ["summer"],
    8: ["summer"],
    9: ["fall"],
    10: ["fall", "halloween"],
    11: ["fall", "holiday"],
}


class BookPicker:
    def __init__(self, csv_path: str = "books.csv"):
        self.csv_path = Path(csv_path)
        self.books = self._load()

    def _load(self) -> list[dict]:
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _recently_posted(self, book: dict, days: int = 30) -> bool:
        lp = book.get("last_posted", "").strip()
        if not lp:
            return False
        try:
            posted = date.fromisoformat(lp)
            return (date.today() - posted).days < days
        except ValueError:
            return False

    def pick(self, mode: str = "random", genre: str | None = None) -> dict | None:
        pool = [b for b in self.books if not self._recently_posted(b)]

        if genre:
            pool = [b for b in pool if b.get("genre", "").lower() == genre.lower()]

        if not pool:
            pool = list(self.books)
            if genre:
                pool = [b for b in pool if b.get("genre", "").lower() == genre.lower()]

        if mode == "curated":
            curated = [b for b in pool if b.get("curated", "").lower() == "true"]
            pool = curated if curated else pool

        elif mode == "seasonal":
            month = date.today().month
            tags = SEASON_MAP.get(month, [])
            seasonal = [
                b for b in pool
                if any(t in (b.get("seasonal_tags") or "").lower() for t in tags)
            ]
            pool = seasonal if seasonal else pool

        elif mode == "new":
            cutoff = date.today() - timedelta(days=60)
            new_books = [
                b for b in pool
                if b.get("added_date", "") and
                date.fromisoformat(b["added_date"]) >= cutoff and
                not b.get("last_posted", "").strip()
            ]
            pool = new_books if new_books else pool

        return random.choice(pool) if pool else None

    def mark_posted(self, book: dict) -> None:
        """Update last_posted date for the given book in the CSV."""
        today = date.today().isoformat()
        rows = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row["isbn"] == book["isbn"]:
                    row["last_posted"] = today
                rows.append(row)

        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def affiliate_url(self, book: dict, affiliate_id: str) -> str:
        """Return affiliate URL, constructing from ISBN if not already set."""
        url = book.get("affiliate_url", "").strip()
        if url and "YOUR_ID" not in url:
            return url
        isbn = book.get("isbn", "").strip()
        if isbn and affiliate_id:
            return f"https://bookshop.org/a/{affiliate_id}/{isbn}"
        return "https://bookshop.org"