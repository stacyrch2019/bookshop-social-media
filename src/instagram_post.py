"""
instagram_post.py — Post to Instagram via the Meta Graph API.

Setup requirements (one-time):
  1. Instagram Business or Creator account
  2. Linked Facebook Page
  3. Facebook App with Instagram Graph API enabled
  4. Long-lived access token (valid ~60 days — refresh before expiry)
  5. Free Imgur account for image hosting (Graph API needs a public URL)

Getting your credentials:
  - Go to developers.facebook.com, create an app (Business type)
  - Add "Instagram Graph API" product
  - Under Instagram Basic Display or Graph API, generate a token
  - Your Instagram User ID is shown in the Graph API Explorer

Refreshing your token (run this before it expires):
  GET https://graph.facebook.com/v18.0/oauth/access_token
    ?grant_type=fb_exchange_token
    &client_id={app_id}
    &client_secret={app_secret}
    &fb_exchange_token={current_token}
"""
import base64
import requests


GRAPH_BASE = "https://graph.facebook.com/v18.0"


def _upload_to_imgur(image_path: str, client_id: str) -> str | None:
    """Upload image to Imgur, return public URL."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    resp = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {client_id}"},
        json={"image": b64, "type": "base64"},
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json()["data"]["link"]
    print(f"  Imgur upload failed: {resp.status_code} {resp.text[:200]}")
    return None


def post_to_instagram(book: dict, image_path: str, caption: str, config) -> bool:
    """
    Post a single image to Instagram feed.
    Returns True on success, False on failure.
    """
    ready, missing = config.check("instagram")
    if not ready:
        print(f"  ✗ Instagram: missing credentials: {', '.join(missing)}")
        return False

    # Step 1: Get a public URL for the image via Imgur
    print("  → Uploading image to Imgur for Instagram...")
    public_url = _upload_to_imgur(image_path, config.imgur_client_id)
    if not public_url:
        print("  ✗ Instagram: could not get public image URL")
        return False

    user_id = config.instagram_user_id
    token = config.instagram_access_token

    # Step 2: Create media container
    container_resp = requests.post(
        f"{GRAPH_BASE}/{user_id}/media",
        params={
            "image_url": public_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=30,
    )
    if container_resp.status_code != 200:
        print(f"  ✗ Instagram container creation failed: {container_resp.text[:200]}")
        return False

    container_id = container_resp.json().get("id")
    if not container_id:
        print("  ✗ Instagram: no container ID returned")
        return False

    # Step 3: Publish the container
    publish_resp = requests.post(
        f"{GRAPH_BASE}/{user_id}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": token,
        },
        timeout=30,
    )
    if publish_resp.status_code == 200:
        print("  ✓ Instagram: posted successfully")
        return True
    else:
        print(f"  ✗ Instagram publish failed: {publish_resp.text[:200]}")
        return False
