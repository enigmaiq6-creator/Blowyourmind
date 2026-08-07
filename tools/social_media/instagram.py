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
        Uploads a local video/image file to a public hosting service to get a direct URL
        that Instagram's servers can access. Tries multiple free hosts with auto-expiry.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # --- Intento 1: catbox.moe (CDN directo, Meta puede descargarlo sin problemas) ---
        try:
            Messenger.info(f"📤 Uploading file to catbox.moe for public URL...")
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://catbox.moe/user/api.php",
                    data={"reqtype": "fileupload", "userhash": ""},
                    files={"fileToUpload": (file_path.name, f, "image/jpeg")},
                    timeout=120
                )
            response.raise_for_status()
            url = response.text.strip()
            if url.startswith("https://"):
                Messenger.info(f"   ✅ Public URL (catbox.moe): {url}")
                return url
            raise RuntimeError(f"catbox.moe returned unexpected response: {url}")
        except Exception as e:
            Messenger.warning(f"⚠️ catbox.moe failed: {e}. Trying file.io...")

        # --- Intento 2: file.io (Soporta archivos grandes) ---
        try:
            Messenger.info(f"📤 Uploading file to file.io for public URL...")
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://file.io",
                    files={"file": f},
                    data={"expires": "1d"},
                    timeout=180
                )
            response.raise_for_status()
            data = response.json()
            if data.get("success") and data.get("link"):
                url = data["link"]
                Messenger.info(f"   ✅ Public URL (file.io): {url}")
                return url
            raise RuntimeError(f"file.io returned unexpected response: {data}")
        except Exception as e:
            Messenger.warning(f"⚠️ file.io failed: {e}. Trying transfer.sh...")

        # --- Intento 3: transfer.sh (Excelente velocidad, PUT request) ---
        try:
            Messenger.info(f"📤 Uploading file to transfer.sh for public URL...")
            with open(file_path, "rb") as f:
                response = requests.put(
                    f"https://transfer.sh/{file_path.name}",
                    data=f,
                    timeout=180
                )
            response.raise_for_status()
            url = response.text.strip()
            Messenger.info(f"   ✅ Public URL (transfer.sh): {url}")
            return url
        except Exception as e:
            Messenger.warning(f"⚠️ transfer.sh failed: {e}. Trying 0x0.st fallback...")

        # --- Intento 4: 0x0.st (Última opción) ---
        try:
            Messenger.info(f"📤 Uploading file to 0x0.st for public URL...")
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://0x0.st",
                    files={"file": f},
                    timeout=180
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

    def publish_carousel(self, image_paths: list[Path], caption: str = "") -> str:
        """
        Uploads multiple images as carousel items, then publishes them as a carousel.
        """
        import json
        insta_id = self.get_instagram_business_account_id()
        
        child_ids = []
        for path in image_paths:
            try:
                public_url = self.upload_to_public_host(path)
                
                # Create a media container for this carousel item
                container_url = f"{self.base_url}/{insta_id}/media"
                container_params = {
                    "image_url": public_url,
                    "is_carousel_item": "true",
                    "access_token": self.access_token
                }
                
                response = requests.post(container_url, data=container_params)
                if response.status_code != 200:
                    Messenger.error(f"   ❌ Instagram API error response for {path.name}: {response.text}")
                response.raise_for_status()
                child_id = response.json()["id"]
                child_ids.append(child_id)
                Messenger.info(f"   Carousel item container created (ID: {child_id}) for {path.name}")
                
                # Brief sleep to avoid hitting limits
                time.sleep(2)
            except Exception as e:
                Messenger.error(f"❌ Failed to process carousel item {path.name}: {e}")
                
        if not child_ids:
            raise RuntimeError("No carousel items were uploaded successfully. Cannot create Instagram carousel.")
            
        # Create the main carousel container
        Messenger.info("🎬 Creating main Instagram Carousel container...")
        main_url = f"{self.base_url}/{insta_id}/media"
        main_params = {
            "media_type": "CAROUSEL",
            "children": json.dumps(child_ids),
            "caption": caption,
            "access_token": self.access_token
        }
        
        response = requests.post(main_url, data=main_params)
        if response.status_code != 200:
            Messenger.error(f"   ❌ Instagram API main container error: {response.text}")
        response.raise_for_status()
        container_id = response.json()["id"]
        Messenger.info(f"   Main Carousel container created (ID: {container_id}). Waiting for processing...")
        
        # Poll status
        status_url = f"{self.base_url}/{container_id}"
        status_params = {
            "fields": "status_code,status,error_message",
            "access_token": self.access_token
        }
        
        max_attempts = 15
        for attempt in range(1, max_attempts + 1):
            time.sleep(5)
            status_resp = requests.get(status_url, params=status_params)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            status_code = status_data.get("status_code")
            error_msg = status_data.get("error_message", "No error details")
            
            Messenger.info(f"   Carousel container status check {attempt}/{max_attempts}: {status_code}")
            if status_code == "FINISHED":
                break
            elif status_code == "ERROR":
                raise RuntimeError(f"Instagram failed to process the carousel: {error_msg}")
        else:
            raise TimeoutError("Instagram carousel processing timed out.")
            
        # Publish the Carousel
        Messenger.info("🚀 Publishing Instagram Carousel...")
        publish_url = f"{self.base_url}/{insta_id}/media_publish"
        publish_params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        publish_resp = requests.post(publish_url, data=publish_params)
        publish_resp.raise_for_status()
        media_id = publish_resp.json()["id"]
        
        Messenger.success(f"✅ Carousel successfully published on Instagram! ID: {media_id}")
        return media_id
