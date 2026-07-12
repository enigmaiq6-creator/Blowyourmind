import os
import time
import requests
from pathlib import Path
from typing import Optional
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class InstagramTool(BaseModelTool):
    """
    Tool for interacting with Instagram Graph API via Facebook Page credentials.
    Handles uploading Reels to a linked Instagram Business/Creator Account.
    """
    page_id: str
    access_token: str
    api_version: str = "v19.0"

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"

    def get_instagram_business_account_id(self) -> str:
        """
        Auto-discovers the Instagram Business Account ID linked to the Facebook Page.
        """
        Messenger.info("🔍 Discovering linked Instagram Business Account ID...")
        url = f"{self.base_url}/{self.page_id}"
        params = {
            "fields": "instagram_business_account",
            "access_token": self.access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        insta_account = data.get("instagram_business_account")
        if not insta_account:
            raise ValueError(
                "No Instagram Business Account linked to this Facebook Page. "
                "Ensure your Instagram Creator/Business account is linked in the Page settings."
            )
            
        insta_id = insta_account["id"]
        Messenger.success(f"✅ Found Instagram Business Account ID: {insta_id}")
        return insta_id

    def upload_to_public_host(self, file_path: Path) -> str:
        """
        Uploads a local video file to a public hosting service to get a direct URL
        that Instagram's servers can access. Tries file.io first, then 0x0.st as fallback.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        # --- Intento 1: file.io (más confiable, soporta archivos grandes) ---
        try:
            Messenger.info(f"📤 Uploading video to file.io for public URL...")
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://file.io",
                    files={"file": f},
                    data={"expires": "1d"},
                    timeout=300
                )
            response.raise_for_status()
            data = response.json()
            if data.get("success") and data.get("link"):
                url = data["link"]
                Messenger.info(f"   ✅ Public URL (file.io): {url}")
                return url
            raise RuntimeError(f"file.io returned unexpected response: {data}")
        except Exception as e:
            Messenger.warning(f"⚠️ file.io failed: {e}. Trying 0x0.st fallback...")

        # --- Intento 2: 0x0.st (fallback) ---
        try:
            Messenger.info(f"📤 Uploading video to 0x0.st for public URL...")
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://0x0.st",
                    files={"file": f},
                    timeout=300
                )
            response.raise_for_status()
            url = response.text.strip()
            Messenger.info(f"   ✅ Public URL (0x0.st): {url}")
            return url
        except Exception as e:
            raise RuntimeError(f"All public hosting services failed. Last error: {e}")

    def publish_reel(self, file_path: Path, caption: str = "") -> str:
        """
        Uploads and publishes a local video as a Reel on Instagram.
        """
        insta_id = self.get_instagram_business_account_id()
        public_video_url = self.upload_to_public_host(file_path)
        
        Messenger.info("🎬 Initializing Instagram Reel container...")
        container_url = f"{self.base_url}/{insta_id}/media"
        container_params = {
            "media_type": "REELS",
            "video_url": public_video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self.access_token
        }
        
        response = requests.post(container_url, data=container_params)
        response.raise_for_status()
        container_id = response.json()["id"]
        Messenger.info(f"   Reel container created (ID: {container_id}). Waiting for processing...")

        # Poll status — also fetch error_message for better diagnostics
        status_url = f"{self.base_url}/{container_id}"
        status_params = {
            "fields": "status_code,status,error_message",
            "access_token": self.access_token
        }
        
        max_attempts = 30
        for attempt in range(1, max_attempts + 1):
            time.sleep(10)
            status_resp = requests.get(status_url, params=status_params)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            status_code = status_data.get("status_code")
            error_msg = status_data.get("error_message", "No error details provided by Instagram")
            
            Messenger.info(f"   Container status check {attempt}/{max_attempts}: {status_code}")
            
            if status_code == "FINISHED":
                break
            elif status_code == "ERROR":
                raise RuntimeError(
                    f"Instagram failed to process the video container.\n"
                    f"   📋 Instagram error: {error_msg}\n"
                    f"   💡 Common causes: video codec not H.264, audio not AAC, "
                    f"aspect ratio not 9:16, duration over 90s, or resolution too low."
                )
        else:
            raise TimeoutError("Instagram video processing timed out after 5 minutes.")

        # Publish the Reel
        Messenger.info("🚀 Publishing Instagram Reel...")
        publish_url = f"{self.base_url}/{insta_id}/media_publish"
        publish_params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        publish_resp = requests.post(publish_url, data=publish_params)
        publish_resp.raise_for_status()
        media_id = publish_resp.json()["id"]
        
        Messenger.success(f"✅ Reel successfully published on Instagram! ID: {media_id}")
        return media_id
