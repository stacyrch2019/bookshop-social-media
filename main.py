#!/usr/bin/env python3
"""
main.py — Bookshop.org social media automator

Usage examples:
  python main.py                                # random book, all platforms
  python main.py --mode curated                 # from your curated picks
  python main.py --mode seasonal                # season/holiday appropriate
  python main.py --mode new                     # recently added books
  python main.py --mode random --genre sci-fi   # random sci-fi pick
  python main.py --platforms bluesky            # Bluesky only
  python main.py --dry-run                      # preview without posting
  python main.py --book 9781984880963           # post a specific ISBN
"""
import argparse
import sys
from pathlib import Path

# Make sure src/ is importable
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from src.book_picker import BookPicker
from src.image_gen import create_slide
from src.caption_gen import generate_captions
from src.bluesky_post import post_to_bluesky
from src.instagram_post import post_to_instagram
from src.tiktok_post import post_to_tiktok


def main():
    parser = argparse.ArgumentParser(
        description="Post book recommendations to Instagram, Bluesky, and TikTok",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mode",
        choices=["random", "curated", "seasonal", "new"],
        default="random",
        help="How to select the book (default: random)",
    )
    parser.add_argument(
        "--genre",
        help="Filter by genre (mystery, thriller, sci-fi, horror, etc.)",
    )
    parser.add_argument(
        "--book",
        metavar="ISBN",
        help="Post a specific book by ISBN (bypasses mode/genre selection)",
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["bluesky", "instagram", "tiktok", "all"],
        default=["all"],
        help="Platforms to post to (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate image + captions but don't post anywhere",
    )
    parser.add_argument(
        "--no-mark",
        action="store_true",
        help="Don't update last_posted in books.csv after posting",
    )
    args = parser.parse_args()

    config = Config()
    picker = BookPicker("books.csv")

    # ── Select book ────────────────────────────────────────────────────────
    if args.book:
        matches = [b for b in picker.books if b.get("isbn") == args.book]
        book = matches[0] if matches else None
        if not book:
            print(f"✗ ISBN {args.book} not found in books.csv")
            sys.exit(1)
    else:
        book = picker.pick(mode=args.mode, genre=args.genre)
        if not book:
            print("✗ No book matched your criteria. Try a different mode or genre.")
            sys.exit(1)

    print(f"\n📚  {book['title']}")
    print(f"    by {book['author']}  [{book.get('genre', '?')}]")
    print(f"    ISBN: {book.get('isbn', 'n/a')}")

    # ── Generate image ─────────────────────────────────────────────────────
    print("\n⏳  Generating slide image...")
    try:
        image_path = create_slide(book)
        print(f"✓   Image saved: {image_path}")
    except Exception as e:
        print(f"✗   Image generation failed: {e}")
        sys.exit(1)

    # ── Generate captions ──────────────────────────────────────────────────
    captions = generate_captions(book, config.affiliate_id)

    # ── Resolve platforms ──────────────────────────────────────────────────
    platforms = args.platforms
    if "all" in platforms:
        platforms = ["bluesky", "instagram", "tiktok"]

    # ── Dry run ────────────────────────────────────────────────────────────
    if args.dry_run:
        print("\n─── DRY RUN (nothing posted) ───────────────────────────────\n")
        for p in platforms:
            print(f"[{p.upper()}]")
            print(captions[p])
            print()
        print(f"Image: {image_path}")
        return

    # ── Post ───────────────────────────────────────────────────────────────
    print(f"\n🚀  Posting to: {', '.join(platforms)}\n")
    results = {}

    if "bluesky" in platforms:
        results["bluesky"] = post_to_bluesky(book, image_path, captions["bluesky"], config)

    if "instagram" in platforms:
        results["instagram"] = post_to_instagram(book, image_path, captions["instagram"], config)

    if "tiktok" in platforms:
        results["tiktok"] = post_to_tiktok(book, image_path, captions["tiktok"], config)

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n📊  Results:")
    any_success = False
    for platform, success in results.items():
        icon = "✓" if success else "✗"
        print(f"    {icon}  {platform}")
        if success:
            any_success = True

    # ── Mark posted ────────────────────────────────────────────────────────
    if any_success and not args.no_mark:
        picker.mark_posted(book)
        print(f"\n✓   books.csv updated (last_posted = today)")

    if not any_success:
        sys.exit(1)


if __name__ == "__main__":
    main()
