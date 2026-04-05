"""
bluesky_post.py — Post to Bluesky via the AT Protocol Python SDK (atproto).
"""


def post_to_bluesky(book: dict, image_path: str, caption: str, config) -> bool:
    try:
        from atproto import Client, models
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

        upload = client.upload_blob(image_data)

        client.send_post(
            text=caption,
            embed=models.AppBskyEmbedImages.Main(
                images=[
                    models.AppBskyEmbedImages.Image(
                        alt=alt_text,
                        image=upload.blob,
                    )
                ]
            )
        )
        print(f"  ✓ Bluesky: posted successfully")
        return True

    except Exception as e:
        print(f"  ✗ Bluesky: {e}")
        return False