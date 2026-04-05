"""
caption_gen.py — Generate platform-tailored captions for a book post.

Each platform gets a different style:
  Bluesky    — Conversational + affiliate link embedded
  Instagram  — Emoji-forward, hashtag block, "link in bio"
  TikTok     — Short, punchy, BookTok hashtags
"""

GENRE_HASHTAGS = {
    "mystery":    ["#MysteryBooks", "#CrimeFiction", "#WhodunitReads", "#MysteryBookClub"],
    "thriller":   ["#ThrillerReads", "#ThrillerBooks", "#PageTurner", "#CantPutItDown"],
    "sci-fi":     ["#SciFiBooks", "#ScienceFiction", "#SciFiReads", "#SpaceOpera"],
    "horror":     ["#HorrorBooks", "#HorrorReads", "#DarkFiction", "#SpookyReads"],
    "literary":   ["#LiteraryFiction", "#BookishVibes", "#LiteraryReads"],
    "romance":    ["#RomanceBooks", "#RomanceReads", "#HEA", "#RomanceCommunity"],
    "nonfiction": ["#Nonfiction", "#NonfictionReads", "#TrueStory", "#NonfictionBookClub"],
    "memoir":     ["#Memoir", "#MemoirReads", "#TrueStory", "#NonfictionReads"],
    "history":    ["#HistoryBooks", "#HistoricalReads", "#NonfictionHistory", "#HistoryBuff"],
    "biography":  ["#Biography", "#Biographies", "#TrueStory", "#NonfictionReads"],
    "science":    ["#ScienceBooks", "#PopScience", "#NonfictionScience", "#LearnSomething"],
    "politics":   ["#PoliticsBooks", "#Democracy", "#Antifa", "#NonfictionReads", "#CivicReads"],
    "default":    ["#BookRecommendations", "#BookishLife", "#MustRead"],
}

COMMON_HASHTAGS = [
    "#BookTok", "#Bookstagram", "#ReadingCommunity",
    "#BookLovers", "#IndieBookshop", "#Bookshop",
]

DISCLOSURE = "As an affiliate of Bookshop.org, I make a small percentage on each book sale."


def _genre_tags(genre: str) -> list[str]:
    return GENRE_HASHTAGS.get(genre.lower().strip(), GENRE_HASHTAGS["default"])


def generate_captions(book: dict, affiliate_id: str) -> dict[str, str]:
    title = book.get("title", "")
    author = book.get("author", "")
    genre = book.get("genre", "default")
    blurb = book.get("blurb", "").strip()

    isbn = book.get("isbn", "").strip()
    url = book.get("affiliate_url", "").strip()
    if not url or "YOUR_ID" in url:
        url = f"https://bookshop.org/a/{affiliate_id}/{isbn}" if isbn else "https://bookshop.org"

    tags_list = _genre_tags(genre) + COMMON_HASHTAGS[:4]

    # ── Bluesky ──────────────────────────────────────────────────────────────
    # ── Bluesky ──────────────────────────────────────────────────────────────
    bsky = f"📚 {title} by {author}\n\n"
    if blurb:
        # Trim blurb to keep total under 300 chars
        max_blurb = 200 - len(title) - len(author)
        trimmed = blurb[:max_blurb] + "…" if len(blurb) > max_blurb else blurb
        bsky += f"{trimmed}\n\n"
    bsky += f"Shop: {url}\n"
    bsky += f"{DISCLOSURE}"

    # ── Instagram ────────────────────────────────────────────────────────────
    ig_openers = [
        "If your TBR isn't tall enough yet, let me help. 📚",
        "This one deserves a spot on your shelf.",
        "Current rec I keep pressing into people's hands:",
        "Not me recommending books again… oh wait, yes me.",
    ]
    opener = ig_openers[len(title) % len(ig_openers)]

    ig = f"{opener}\n\n"
    ig += f"✦ {title}\n"
    ig += f"✦ {author}\n\n"
    if blurb:
        ig += f"{blurb}\n\n"
    ig += f"{DISCLOSURE}\n\n"
    ig += "🔗 Shop link in bio — every purchase supports indie booksellers!\n\n"
    ig += " ".join(_genre_tags(genre) + COMMON_HASHTAGS)

    # ── TikTok ───────────────────────────────────────────────────────────────
    tt = f"{title} by {author} — {blurb[:80] + '…' if len(blurb) > 80 else blurb}\n"
    tt += f"{DISCLOSURE}\n"
    tt += "Link in bio 🔗\n"
    tt += " ".join(_genre_tags(genre)[:3] + ["#BookTok", "#BookRecommendation"])

    return {
        "bluesky": bsky,
        "instagram": ig,
        "tiktok": tt,
    }