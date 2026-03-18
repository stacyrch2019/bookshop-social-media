"""
tiktok_post.py — Post photo slides to TikTok via the Content Posting API.

⚠  TikTok API setup is the most involved of the three platforms.

Setup requirements:
  1. TikTok Developer account at developers.tiktok.com
  2. Create an app and request the "Content Posting API" product
  3. Enable scopes: video.upload, video.publish (for photo posts too)
  4. Complete TikTok's app review (can take a few days)
  5. Run the OAuth flow to get an access token (see README for instructions)

The access token expires — you'll need to refresh it periodically using
your refresh token. See: developers.tiktok.com/doc/content-posting-api-reference

Photo post notes:
  - TikTok calls these "photo" or "carousel" posts
  - Up to 35 photos per post
  - Supported formats: JPEG, WebP
  - Each image: max 20MB, min 360x360px
  - This script posts a single image slide
"""
import requests


TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"


def _get_creator_info(access_token: str) -> dict | None:
    """Fetch creator's posting settings (required before creating post)."""
    resp = requests.post(
        f"{TIKTOK_API_BASE}/post/publish/creator_info/query/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        timeout=15,
    )
    if resp.status_code == 200:
        return resp.json().get("data", {})
    return None


def post_to_tiktok(book: dict, image_path: str, caption: str, config) -> bool:
    """
    Post a photo slide to TikTok.
    Returns True on success, False on failure.
    """
    ready, missing = config.check("tiktok")
    if not ready:
        print(f"  ✗ TikTok: missing credentials: {', '.join(missing)}")
        return False

    token = config.tiktok_access_token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    # Step 1: Get creator info (privacy level options etc.)
    creator_info = _get_creator_info(token)
    if not creator_info:
        print("  ✗ TikTok: could not fetch creator info (check access token)")
        return False

    # Respect the account's allowed privacy levels
    allowed_privacy = creator_info.get("privacy_level_options", ["PUBLIC_TO_EVERYONE"])
    privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in allowed_privacy else allowed_privacy[0]

    # Step 2: Initialize photo post
    init_body = {
        "post_info": {
            "title": caption[:2200],   # TikTok caption limit
            "privacy_level": privacy,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "auto_add_music": True,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "photo_cover_index": 0,
            "photo_images": [],         # filled after upload
        },
        "media_type": "PHOTO",
    }

    # Read image
    with open(image_path, "rb") as f:
        image_data = f.read()

    image_size = len(image_data)

    # Step 3: Initialize upload
    init_resp = requests.post(
        f"{TIKTOK_API_BASE}/post/publish/content/init/",
        headers=headers,
        json={
            **init_body,
            "source_info": {
                **init_body["source_info"],
                "photo_images": [{"size": image_size, "media_type": "JPEG"}],
            },
        },
        timeout=30,
    )

    if init_resp.status_code != 200:
        print(f"  ✗ TikTok init failed: {init_resp.text[:300]}")
        return False

    init_data = init_resp.json().get("data", {})
    publish_id = init_data.get("publish_id")
    upload_url = init_data.get("photo_upload_urls", [None])[0]

    if not publish_id or not upload_url:
        print(f"  ✗ TikTok: missing publish_id or upload URL in response")
        return False

    # Step 4: Upload the image chunk
    upload_resp = requests.put(
        upload_url,
        data=image_data,
        headers={
            "Content-Type": "image/jpeg",
            "Content-Length": str(image_size),
            "Content-Range": f"bytes 0-{image_size - 1}/{image_size}",
        },
        timeout=60,
    )

    if upload_resp.status_code not in (200, 201, 206):
        print(f"  ✗ TikTok upload failed: {upload_resp.status_code} {upload_resp.text[:200]}")
        return False

    # Step 5: TikTok processes and publishes automatically after successful upload.
    # The post status can be checked via:
    #   POST /v2/post/publish/status/fetch/ with {"publish_id": publish_id}
    print(f"  ✓ TikTok: image uploaded (publish_id: {publish_id})")
    print("    TikTok will process and publish the post automatically.")
    return True
