"""
caption_gen.py — Generate platform-tailored captions for a book post.

Each platform gets a different style:
  Bluesky    — Conversational + affiliate link embedded
  Instagram  — Emoji-forward, hashtag block, "link in bio"
  TikTok     — Short, punchy, BookTok hashtags
"""

GENRE_HASHTAGS = {
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


def _genre_tags(genre: str) -> list[str]:
    return GENRE_HASHTAGS.get(genre.lower().strip(), GENRE_HASHTAGS["default"])


def generate_captions(book: dict, affiliate_id
