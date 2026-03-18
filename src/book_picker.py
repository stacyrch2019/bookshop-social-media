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
        with open(self.csv_path, newline="", enc
