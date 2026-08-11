import os
import random
import time
from pathlib import Path
from typing import Optional

import requests
from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger


class FacebookTool(BaseModelTool):
    """
    Tool for interacting with Facebook Graph API.
    Handles video uploads (including Reels) and photo posts to a Facebook Page.
    """
    page_id: str
    access_token: str
    api_version: str = "v19.0"

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"

    @property
    def video_url(self) -> str:
        return f"https://graph-video.facebook.com/{self.api_version}"

    def upload_video(
        self,
        file_path: Path,
        description: str = "",
        title: Optional[str] = None,
        published: bool = True
    ) -> str:
        """
        Uploads a video to a Facebook Page.
        When published=True, uses the /video_reels API (rupload.facebook.com) so it appears in the page feed as a Reel.
        When published=False, uploads as a hidden draft via the classic /videos resumable API.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        file_size = file_path.stat().st_size
        
        if not published:
            # --- CLASSIC DRAFT VIDEO UPLOAD (/videos) ---
            chunk_size = 10 * 1024 * 1024  # 10MB per chunk
            Messenger.info(f"🚀 Starting Facebook video draft upload: {file_path.name} ({file_size / (1024*1024):.2f} MB)")

            params = {
                "upload_phase": "start",
                "file_size": file_size,
                "access_token": self.access_token
            }
            response = requests.post(f"{self.video_url}/{self.page_id}/videos", params=params)
            response.raise_for_status()
            data = response.json()
            upload_session_id = data["upload_session_id"]
            video_id = data["video_id"]
            Messenger.info(f"   Upload session started: {upload_session_id}")

            with open(file_path, "rb") as f:
                start_offset = 0
                while start_offset < file_size:
                    chunk = f.read(chunk_size)
                    end_offset = start_offset + len(chunk)
                    percentage = (start_offset / file_size) * 100
                    Messenger.info(f"   Uploading chunk: {start_offset} - {end_offset} ({percentage:.0f}%)")
                    
                    resp = requests.post(
                        f"{self.video_url}/{self.page_id}/videos",
                        params={"access_token": self.access_token},
                        data={
                            "upload_phase": "transfer",
                            "upload_session_id": upload_session_id,
                            "start_offset": start_offset,
                        },
                        files={"video_file_chunk": ("chunk.mp4", chunk, "video/mp4")}
                    )
                    resp.raise_for_status()
                    start_offset = end_offset

            finish_params = {
                "upload_phase": "finish",
                "upload_session_id": upload_session_id,
                "description": description,
                "access_token": self.access_token,
                "published": "false"
            }
            if title:
                finish_params["title"] = title

            response = requests.post(f"{self.video_url}/{self.page_id}/videos", params=finish_params)
            response.raise_for_status()
            Messenger.success(f"✅ Video saved as draft! ID: {video_id}")
            return video_id

        else:
            # --- FACEBOOK REELS UPLOAD (/video_reels) ---
            Messenger.info(f"🚀 Starting Facebook Reel upload: {file_path.name} ({file_size / (1024*1024):.2f} MB)")
            
            # 1. START Phase
            start_params = {
                "upload_phase": "start",
                "access_token": self.access_token
            }
            # Note: reels start phase uses graph.facebook.com, not graph-video
            response = requests.post(f"{self.base_url}/{self.page_id}/video_reels", params=start_params)
            if response.status_code != 200:
                Messenger.error(f"Reels START Phase failed: {response.text}")
                response.raise_for_status()
            
            video_id = response.json()["video_id"]
            Messenger.info(f"   Reel upload session started, video_id: {video_id}")
            
            # 2. TRANSFER Phase (rupload.facebook.com)
            rupload_url = f"https://rupload.facebook.com/video-upload/{self.api_version}/{video_id}"
            headers = {
                "Authorization": f"OAuth {self.access_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
            Messenger.info("   Uploading Reel binary to rupload.facebook.com...")
            with open(file_path, "rb") as f:
                # Meta allows sending the entire file in one POST for this endpoint
                upload_resp = requests.post(rupload_url, headers=headers, data=f)
            
            if upload_resp.status_code != 200:
                Messenger.error(f"Reels TRANSFER Phase failed: {upload_resp.text}")
                upload_resp.raise_for_status()
            Messenger.info("   Transfer complete.")

            # 3. FINISH Phase
            finish_params = {
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description,
                "access_token": self.access_token
            }
            response = requests.post(f"{self.base_url}/{self.page_id}/video_reels", params=finish_params)
            
            if response.status_code != 200:
                Messenger.error(f"Reels FINISH Phase failed: {response.text}")
                response.raise_for_status()
                
            Messenger.success(f"✅ Reel published in feed! ID: {video_id}")
            return video_id

    def upload_photo(self, file_path: Path, caption: str = "") -> str:
        """
        Uploads a photo to the Facebook Page and PUBLISHES it immediately.
        Includes robust exponential backoff to handle transient Facebook 500 errors.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Photo file not found: {file_path}")

        Messenger.info(f"📸 Uploading photo: {file_path.name}")
        
        url = f"{self.base_url}/{self.page_id}/photos"
        
        max_attempts = 4
        base_delay = 5.0
        
        for attempt in range(1, max_attempts + 1):
            try:
                with open(file_path, "rb") as photo_file:
                    files = {"source": photo_file}
                    data = {
                        "caption": caption,
                        "access_token": self.access_token
                    }
                    
                    response = requests.post(url, data=data, files=files)
                    response.raise_for_status()
                    
                    photo_id = response.json().get("id")
                    Messenger.success(f"✅ Photo published! ID: {photo_id}")
                    return photo_id
            except Exception as e:
                Messenger.warning(f"⚠️ Attempt {attempt}/{max_attempts} failed to upload photo: {str(e)}")
                if attempt == max_attempts:
                    raise e
                
                sleep_time = (base_delay * (2 ** (attempt - 1))) + random.uniform(1.0, 3.0)
                Messenger.warning(f"🔄 Sleeping for {sleep_time:.2f}s before retrying photo upload...")
                time.sleep(sleep_time)

    def upload_photo_unpublished(self, file_path: Path) -> str:
        """
        Uploads a photo to Facebook but keeps it UNPUBLISHED.
        Returns the photo ID for use in multi-photo posts.
        Includes robust exponential backoff to handle transient Facebook 500 errors.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Photo file not found: {file_path}")

        url = f"{self.base_url}/{self.page_id}/photos"
        
        max_attempts = 4
        base_delay = 5.0
        
        for attempt in range(1, max_attempts + 1):
            try:
                with open(file_path, "rb") as photo_file:
                    files = {"source": photo_file}
                    data = {
                        "published": "false",
                        "access_token": self.access_token
                    }
                    
                    response = requests.post(url, data=data, files=files)
                    response.raise_for_status()
                    return response.json().get("id")
            except Exception as e:
                Messenger.warning(f"⚠️ Attempt {attempt}/{max_attempts} failed to upload unpublished photo: {str(e)}")
                if attempt == max_attempts:
                    raise e
                
                sleep_time = (base_delay * (2 ** (attempt - 1))) + random.uniform(1.0, 3.0)
                Messenger.warning(f"🔄 Sleeping for {sleep_time:.2f}s before retrying unpublished photo upload...")
                time.sleep(sleep_time)

    def create_carousel_post(self, description: str, photo_ids: list[str]) -> str:
        """
        Creates a single post with multiple photos (Carousel style).
        Includes robust exponential backoff to handle transient Facebook 500 errors.
        """
        Messenger.info(f"📸 Creating carousel post with {len(photo_ids)} photos...")
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        attached_media = []
        for pid in photo_ids:
            attached_media.append({"media_fbid": pid})

        import json
        data = {
            "message": description,
            "attached_media": json.dumps(attached_media),
            "access_token": self.access_token
        }
        
        max_attempts = 4
        base_delay = 5.0
        
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(url, data=data)
                response.raise_for_status()
                
                post_id = response.json().get("id")
                Messenger.success(f"✅ Carousel post published! ID: {post_id}")
                return post_id
            except Exception as e:
                Messenger.warning(f"⚠️ Attempt {attempt}/{max_attempts} failed to create carousel post: {str(e)}")
                if attempt == max_attempts:
                    raise e
                
                sleep_time = (base_delay * (2 ** (attempt - 1))) + random.uniform(1.0, 3.0)
                Messenger.warning(f"🔄 Sleeping for {sleep_time:.2f}s before retrying carousel post...")
                time.sleep(sleep_time)

    def create_text_post(self, message: str) -> str:
        """
        Creates a text-only post on the Facebook Page.
        Includes robust exponential backoff to handle transient Facebook 500 errors.
        """
        Messenger.info("📝 Creating text post...")
        
        url = f"{self.base_url}/{self.page_id}/feed"
        data = {
            "message": message,
            "access_token": self.access_token
        }
        
        max_attempts = 4
        base_delay = 5.0
        
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(url, data=data)
                response.raise_for_status()
                
                post_id = response.json().get("id")
                Messenger.success(f"✅ Text post published! ID: {post_id}")
                return post_id
            except Exception as e:
                Messenger.warning(f"⚠️ Attempt {attempt}/{max_attempts} failed to create text post: {str(e)}")
                if attempt == max_attempts:
                    raise e
                
                sleep_time = (base_delay * (2 ** (attempt - 1))) + random.uniform(1.0, 3.0)
                Messenger.warning(f"🔄 Sleeping for {sleep_time:.2f}s before retrying text post...")
                time.sleep(sleep_time)

    def add_comment(self, post_id: str, message: str) -> str:
        """
        Adds a comment to a specific post or video on the Facebook Page.
        Used for Phase 4: Auto-Engagement.
        """
        Messenger.info(f"💬 Adding auto-comment to post {post_id}...")
        url = f"{self.base_url}/{post_id}/comments"
        data = {
            "message": message,
            "access_token": self.access_token
        }
        response = requests.post(url, data=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            Messenger.warning(f"⚠️ Failed to add comment: {e.response.text}")
            return ""
        
        comment_id = response.json().get("id")
        Messenger.success(f"✅ Comment added successfully! ID: {comment_id}")
        return comment_id

    def upload_captions(self, video_id: str, srt_file_path: Path, locale: str = "en_US") -> bool:
        """
        Uploads an SRT caption file to an existing video.
        The file must be named strictly as filename.locale.srt (e.g., subtitles.en_US.srt).
        """
        if not srt_file_path.exists():
            Messenger.warning(f"⚠️ Caption file not found: {srt_file_path}")
            return False

        Messenger.info(f"📝 Uploading {locale} captions to video {video_id}...")
        url = f"{self.video_url}/{video_id}/captions"
        
        try:
            with open(srt_file_path, "rb") as f:
                # Facebook requires the file name to match the locale format exactly
                filename = f"{video_id}.{locale}.srt"
                files = {"captions_file": (filename, f, "text/plain")}
                
                # Para subir archivos a Graph API a veces se envía access_token como data
                data = {
                    "access_token": self.access_token,
                    "default_locale": "none"  # "none" para que no sobreescriba el por defecto si no queremos
                }
                
                response = requests.post(url, data=data, files=files)
                response.raise_for_status()
                
                if response.json().get("success"):
                    Messenger.success(f"✅ Captions ({locale}) attached successfully!")
                    return True
                else:
                    Messenger.error(f"❌ Failed to attach captions: {response.text}")
                    return False
        except Exception as e:
            Messenger.error(f"❌ Exception uploading captions: {str(e)}")
            return False

    def publish_carousel(self, image_paths: list[Path], description: str = "") -> str:
        """
        Uploads multiple images as unpublished photos, then publishes them as a carousel.
        """
        photo_ids = []
        for path in image_paths:
            try:
                pid = self.upload_photo_unpublished(path)
                photo_ids.append(pid)
            except Exception as e:
                Messenger.error(f"❌ Failed to upload image {path.name} for carousel: {e}")
                
        if not photo_ids:
            raise RuntimeError("No photos were uploaded successfully. Cannot create Facebook carousel.")
            
        return self.create_carousel_post(description, photo_ids)
