"""
config.py — Load credentials and settings from .env
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.affiliate_id = os.getenv("BOOKSHOP_AFFILIATE_ID", "")

        self.bluesky_handle = os.getenv("BLUESKY_HANDLE", "")
        self.bluesky_password = os.getenv("BLUESKY_PASSWORD", "")

        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.instagram_user_id = os.getenv("INSTAGRAM_USER_ID", "")
        self.imgur_client_id = os.getenv("IMGUR_CLIENT_ID", "")

        self.tiktok_access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")

    def check(self, platform: str) -> tuple[bool, list[str]]:
        """Return (ready, missing_keys) for a given platform."""
        checks = {
            "bluesky": [
                ("BLUESKY_HANDLE", self.bluesky_handle),
                ("BLUESKY_PASSWORD", self.bluesky_password),
            ],
            "instagram": [
                ("INSTAGRAM_ACCESS_TOKEN", self.instagram_access_token),
                ("INSTAGRAM_USER_ID", self.instagram_user_id),
                ("IMGUR_CLIENT_ID", self.imgur_client_id),
            ],
            "tiktok": [
                ("TIKTOK_ACCESS_TOKEN", self.tiktok_access_token),
            ],
        }
        missing = [k for k, v in checks.get(platform, []) if not v]
        return (len(missing) == 0, missing)