import time
from pathlib import Path
from typing import Any, Optional
import json

from google.genai import types
import google.auth
import google.auth.transport.requests
import requests
from google.cloud import storage

from tools.common.gemini_base import GeminiBase
from tools.common.messenger import Messenger


class GeminiVideoGenerator(GeminiBase):
    """
    Tool for generating videos using Gemini Veo 3.1 models.
    Supports text-to-video and image-to-video interpolation.
    """
    video_model: str = "veo-3.1-fast-generate-001"

    def generate_video(
        self,
        prompt: str,
        out_path: str,
        img_start_path: Optional[str] = None,
        img_end_path: Optional[str] = None
    ) -> None:
        """
        Generates a high-fidelity video using Veo 3.1 and saves it to disk.
        """
        out_path_obj = Path(out_path)
        out_path_obj.parent.mkdir(parents=True, exist_ok=True)

        Messenger.info(f"🚀 Starting AI Video generation: {out_path_obj.name}...")

        # 1. Setup Configuration
        config_args: dict[str, Any] = {
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "duration_seconds": 6.0, # Optimized for Veo 3.1 Fast
            "fps": 24
        }

        if img_end_path:
            config_args["last_frame"] = types.Image(
                image_bytes=Path(img_end_path).read_bytes(),
                mime_type="image/png"
            )

        # 2. Prepare Inputs
        image_input = None
        if img_start_path:
            image_input = types.Image(
                image_bytes=Path(img_start_path).read_bytes(),
                mime_type="image/png"
            )

        # 3. Trigger Generation
        time.sleep(10)
        Messenger.info(f"    Generating Video: {out_path_obj.name}...")
        Messenger.info(f"    Prompt: {prompt}")
        
        config = types.GenerateVideosConfig(**config_args)
        
        operation = self._execute_with_retry(
            self.client.models.generate_videos,
            model=self.video_model,
            prompt=prompt,
            image=image_input,
            config=config
        )

        Messenger.info(f" DEBUG: Operation Name: {operation.name}")

        # 4. Hybrid Polling (SDK + Manual Fallback)
        Messenger.info(" Waiting for video generation (polling)...")
        
        op_name = operation.name
        resource_name = op_name.rpartition('/operations/')[0]
        
        # Prepare auth for manual fallback
        creds, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        
        final_resp_dict = None
        
        while True:
            time.sleep(20)
            
            try:
                # Attempt SDK polling first
                if self.client.vertexai:
                    resp_dict = self.client.operations._fetch_predict_videos_operation(
                        operation_name=op_name,
                        resource_name=resource_name
                    )
                else:
                    op = self.client.operations.get(operation)
                    # For non-vertex, we can just use the op object
                    if op.done:
                        operation = op
                        break
                    continue

                if resp_dict.get("done"):
                    Messenger.info("   ✅ Generation complete (done: True)")
                    final_resp_dict = resp_dict
                    break
                else:
                    Messenger.info(f"   ⏳ Still processing...")
            except Exception as e:
                Messenger.warning(f"   ⚠️ Polling error: {e}. Trying manual REST fallback...")
                try:
                    creds.refresh(auth_req)
                    url = f"https://{self._location}-aiplatform.googleapis.com/v1beta1/{resource_name}:fetchPredictOperation"
                    resp = requests.post(
                        url, 
                        headers={"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"},
                        json={"operationName": op_name}
                    )
                    if resp.status_code == 200:
                        resp_dict = resp.json()
                        if resp_dict.get("done"):
                            Messenger.info("   ✅ Manual poll: Generation complete.")
                            final_resp_dict = resp_dict
                            break
                        else:
                            Messenger.info(f"   ⏳ Manual poll: Still processing...")
                    else:
                        Messenger.error(f"   ❌ Manual poll failed ({resp.status_code}): {resp.text}")
                except Exception as inner_e:
                    Messenger.error(f"   ❌ Manual poll exception: {inner_e}")

        # 5. Handle Result
        video_uri = None
        if final_resp_dict:
            # Check for errors in response
            if "error" in final_resp_dict:
                raise RuntimeError(f"❌ Video generation failed: {final_resp_dict['error']}")
                
            with open("latest_response.json", "w") as f:
                json.dump(final_resp_dict, f, indent=2)
            Messenger.info("   💾 Full response dumped to latest_response.json")
                
            Messenger.info(f"   📊 Full Response metadata keys: {list(final_resp_dict.keys())}")
            # Extract URI manually to bypass SDK parsing bugs
            resp = final_resp_dict.get("response", {})
            Messenger.info(f"   🔍 Resp Type: {type(resp)}, Keys: {list(resp.keys()) if isinstance(resp, dict) else 'N/A'}")

            # Try all possible keys and formats
            raw_videos = []
            if isinstance(resp, dict):
                if not resp:
                     Messenger.warning("   ⚠️ Response field is empty! Checking metadata for safety flags...")
                     meta = final_resp_dict.get("metadata", {})
                     Messenger.info(f"   🔍 Metadata: {json.dumps(meta, indent=2)}")
                raw_videos = resp.get("videos") or resp.get("generatedVideos") or []
            
            Messenger.info(f"   🔍 Raw Videos count: {len(raw_videos)}")
            if raw_videos and len(raw_videos) > 0:
                first_video_entry = raw_videos[0]
                Messenger.info(f"   🔍 First entry keys: {list(first_video_entry.keys()) if isinstance(first_video_entry, dict) else 'N/A'}")
                
                # Check for URI
                video_data = first_video_entry.get("video", {})
                video_uri = video_data.get("uri")
                
                # Check for base64 bytes (some models return bytes directly)
                video_bytes_b64 = first_video_entry.get("bytesBase64Encoded")
                
                if video_uri:
                    Messenger.info(f"   🔍 Extracted URI: {video_uri}")
                elif video_bytes_b64:
                    Messenger.info(f"   🔍 Extracted Base64 Bytes (length: {len(video_bytes_b64)})")
                    import base64
                    video_bytes = base64.b64decode(video_bytes_b64)
                    with open(out_path, "wb") as f:
                        f.write(video_bytes)
                    Messenger.success(f"Video saved from base64: {out_path}")
                    return # SUCCESS, we are done
            
            # Check safety filters
            filtered_count = resp.get("raiMediaFilteredCount", 0)
            if filtered_count > 0:
                reasons = resp.get("raiMediaFilteredReasons", ["Unknown"])
                Messenger.warning(f"   ⚠️ {filtered_count} videos were filtered by safety filters. Reasons: {reasons}")
                if not video_uri:
                    raise RuntimeError(f"❌ Video generation blocked by safety filters: {reasons}")

        if not video_uri:
            Messenger.error(f"❌ Video generation failed. Response dump: {json.dumps(final_resp_dict, indent=2)}")
            raise RuntimeError("❌ Video generation succeeded but no URI was found in response (Filtered?).")

        # 6. Download from GCS
        Messenger.info(f"   🎬 Downloading video from: {video_uri}")
        if video_uri.startswith("gs://"):
            try:
                # Parse gs://bucket/path
                parts = video_uri[5:].split("/", 1)
                bucket_name = parts[0]
                blob_name = parts[1]
                
                storage_client = storage.Client()
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.download_to_filename(str(out_path))
                Messenger.success(f"Video saved: {out_path}")
            except Exception as e:
                raise RuntimeError(f"❌ Failed to download from GCS: {e}")
        else:
            # Fallback to standard client download if possible (unlikely for gs://)
            raise RuntimeError(f"❌ Unsupported video URI format: {video_uri}")
