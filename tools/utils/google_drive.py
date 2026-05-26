import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tools.common.messenger import Messenger

def get_drive_credentials():
    """
    Attempts to retrieve and load credentials from:
    1. GOOGLE_APPLICATION_CREDENTIALS environment variable (points to file)
    2. GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable (direct JSON string)
    """
    # 1. Check path to file
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and os.path.exists(creds_path):
        try:
            return service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
        except Exception as e:
            Messenger.warning(f"Failed to load credentials from file {creds_path}: {e}")

    # 2. Check direct JSON string
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if creds_json:
        try:
            info = json.loads(creds_json, strict=False)
            return service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
        except Exception as e:
            Messenger.warning(f"Failed to load credentials from GOOGLE_APPLICATION_CREDENTIALS_JSON string: {e}")

    return None

def upload_video_to_drive(file_path: Path, folder_id: str) -> str | None:
    """
    Uploads a video file (.mp4) to the specified Google Drive folder.
    Returns the webViewLink of the uploaded file if successful, otherwise None.
    """
    if not file_path.exists():
        Messenger.error(f"Upload failed: File does not exist at {file_path}")
        return None

    Messenger.info(f"Preparing to upload {file_path.name} to Google Drive...")

    creds = get_drive_credentials()
    if not creds:
        Messenger.warning("Google Drive credentials not found or invalid. Skipping upload.")
        # Print the service account email tip so user knows what to do
        Messenger.info("Tip: Set GOOGLE_APPLICATION_CREDENTIALS pointing to your GCP Service Account JSON key.")
        return None

    try:
        # Build the drive service
        service = build("drive", "v3", credentials=creds)

        file_metadata = {
            "name": file_path.name,
            "parents": [folder_id]
        }

        media = MediaFileUpload(
            str(file_path),
            mimetype="video/mp4",
            resumable=True
        )

        Messenger.info(f"Uploading file '{file_path.name}' to folder ID '{folder_id}'...")
        
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                Messenger.info(f"   Upload progress: {int(status.progress() * 100)}%")

        file_id = response.get("id")
        web_link = response.get("webViewLink")

        Messenger.success(f"Successfully uploaded to Google Drive! File ID: {file_id}")
        Messenger.info(f"Link: {web_link}")
        
        # Log service account email as a helper so they know who to share folder with
        if hasattr(creds, "service_account_email"):
            Messenger.info(f"Note: Ensure your Drive folder is shared with: {creds.service_account_email}")

        return web_link

    except Exception as e:
        error_str = str(e)
        if "accessNotConfigured" in error_str or "has not been used" in error_str or "is disabled" in error_str:
            Messenger.error("❌ Google Drive API is NOT ENABLED in your Google Cloud project!")
            Messenger.error("👉 To fix this, follow these steps:")
            Messenger.error("   1. Open this URL in your browser:")
            Messenger.error("      https://console.developers.google.com/apis/api/drive.googleapis.com/overview")
            Messenger.error("   2. Click 'ENABLE' to activate the Google Drive API.")
            Messenger.error("   3. Wait 1-2 minutes and re-run the workflow.")
        else:
            Messenger.error(f"Google Drive upload encountered an error: {e}")
        return None
