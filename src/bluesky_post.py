"""
bluesky_post.py — Post to Bluesky via the AT Protocol Python SDK (atproto).

Bluesky is the easiest of the three: open API, no approval required.
Just create an App Password at: Settings > Privacy and Security > App Passwords
"""
import sys


def post_to_bluesky(book: dict, image_path: str, caption: str, config) -> bool:
    """
    Upload image and post to Bluesky.
    Returns True on success, False on failure.
    """
    try:
        from atproto import Client
    except ImportError:
        print("  ✗ Bluesky: atproto not installed. Run: pip install atproto")
        return False

    ready, missing = config.check("bluesky")
    if not ready:
        print(f"  ✗ Bluesky: missing credentials: {', '.join(missing)}")
        return False

    try:
        client = Client()
        client.login(config.bluesky_handle, config.bluesky_password)

        with open(image_path, "rb") as f:
            image_data = f.read()

        alt_text = (
            f"Book cover for '{book.get('title', '')}' "
            f"by {book.get('author', '')}"
        )

        client.send_image(
            text=caption,
            image=image_data,
            image_alt=alt_text,
        )
        print(f"  ✓ Bluesky: posted successfully")
        return True

    except Exception as e:
        print(f"  ✗ Bluesky: {e}")
        return False
