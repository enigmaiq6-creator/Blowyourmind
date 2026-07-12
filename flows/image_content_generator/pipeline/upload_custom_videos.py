import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# Añadir la raíz al PYTHONPATH para poder importar las herramientas
sys.path.append(str(Path(__file__).resolve().parents[3]))

from tools.social_media.facebook import FacebookTool
from tools.social_media.instagram import InstagramTool
from tools.common.messenger import Messenger

def main():
    load_dotenv()
    
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    instagram_publish = os.getenv("INSTAGRAM_PUBLISH", "true").lower() == "true"
    
    if not page_id or page_id == "TU_PAGE_ID_AQUI" or not access_token or access_token == "TU_ACCESS_TOKEN_AQUI":
        Messenger.error("❌ Error: FACEBOOK_PAGE_ID y FACEBOOK_PAGE_ACCESS_TOKEN no están configurados correctamente.")
        return
        
    videos_dir = Path("videos_to_upload")
    if not videos_dir.exists():
        videos_dir.mkdir(parents=True, exist_ok=True)
        Messenger.info("📁 Creada la carpeta 'videos_to_upload'. Añade videos aquí.")
        return
        
    video_files = list(videos_dir.glob("*.mp4"))
    if not video_files:
        Messenger.info("ℹ️ No se encontraron videos (.mp4) en la carpeta 'videos_to_upload'.")
        return
        
    fb_tool = FacebookTool(page_id=page_id, access_token=access_token)
    ig_tool = InstagramTool(page_id=page_id, access_token=access_token)
    
    Messenger.success(f"🎥 Encontrados {len(video_files)} video(s) para procesar.")
    
    # Procesar solo el primer video disponible
    video_path = video_files[0]
    filename_wo_ext = video_path.stem
    
    # Reemplazar guiones bajos por espacios para hacer el nombre legible
    clean_name = filename_wo_ext.replace("_", " ").strip()
    
    # Si se usa "--" se separa título y descripción, si no, se usa el nombre formateado para ambos
    if "--" in clean_name:
        parts = clean_name.split("--", 1)
        title = parts[0].strip()
        description = parts[1].strip()
    else:
        title = clean_name
        description = f"🤯 {title}\n\nWhat do you think about this? 👇\n\n#BlowYourMind #ViralReels #Mysteries #DidYouKnow #History"
        
    Messenger.info(f"\n==========================================")
    Messenger.info(f"Processing: {video_path.name}")
    Messenger.info(f"Title: {title}")
    Messenger.info(f"Description: {description}")
    Messenger.info(f"==========================================")
    
    # 1. Subida a Facebook Page (Reels/Videos)
    try:
        Messenger.info("📤 Subiendo a Facebook...")
        fb_video_id = fb_tool.upload_video(
            file_path=video_path,
            description=description,
            title=title,
            published=True
        )
        if fb_video_id:
            Messenger.success(f"✅ Subido exitosamente a Facebook! ID: {fb_video_id}")
    except Exception as fb_err:
        Messenger.error(f"❌ Error al subir a Facebook: {fb_err}")
        
    # 2. Subida a Instagram (si está habilitado)
    if instagram_publish:
        try:
            Messenger.info("📤 Subiendo a Instagram Reels...")
            ig_media_id = ig_tool.publish_reel(
                file_path=video_path,
                caption=f"{title}\n\n{description}"
            )
            if ig_media_id:
                Messenger.success(f"✅ Subido exitosamente a Instagram! ID: {ig_media_id}")
        except Exception as ig_err:
            Messenger.error(f"❌ Error al subir a Instagram: {ig_err}")
            
    # 3. Eliminar archivo local ya procesado
    try:
        video_path.unlink()
        Messenger.info(f"🗑️ Eliminado de la cola de subidas: {video_path.name}")
    except Exception as del_err:
        Messenger.warning(f"⚠️ No se pudo eliminar el archivo local: {del_err}")

if __name__ == "__main__":
    main()
