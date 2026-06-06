import os
import subprocess
import requests
import random
from pathlib import Path
from pydantic import Field
from tools.common.messenger import Messenger
from tools.common.base_model import BaseModelTool
from typing import Optional

class PixabayTool(BaseModelTool):
    """
    Herramienta para interactuar con la API de Pixabay y descargar videos de stock gratuitos.
    """
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("PIXABAY_API_KEY"))

    def fetch_video(self, query: str, out_path: Path) -> bool:
        """
        Busca un video basado en el query y lo descarga.
        Retorna True si fue exitoso, False en caso contrario.
        """
        if not self.api_key:
            Messenger.warning("⚠️ No se encontró PIXABAY_API_KEY en el entorno. Saltando Pixabay.")
            return False

        if not query or not query.strip():
            Messenger.warning("⚠️ Query de Pixabay vacío. Saltando búsqueda.")
            return False

        # Pixabay requiere formatear los espacios con '+'
        formatted_query = query.replace(" ", "+")
        Messenger.info(f"🔎 Buscando video en Pixabay para: '{query}'...")
        
        url = "https://pixabay.com/api/videos/"
        random_page = random.randint(1, 3)
        params = {
            "key": self.api_key,
            "q": formatted_query,
            "per_page": 15,
            "page": random_page,
            "safesearch": "true"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            hits = data.get("hits", [])
            if not hits:
                if random_page > 1:
                    params["page"] = 1
                    response = requests.get(url, params=params)
                    data = response.json()
                    hits = data.get("hits", [])
                    
                if not hits:
                    Messenger.warning(f"⚠️ No se encontraron videos para '{query}' en Pixabay.")
                    return False

            selected_video = random.choice(hits)
            
            videos_data = selected_video.get("videos", {})
            if not videos_data:
                return False
                
            # Preferir large (HD) > medium > cualquier otra
            best_video_obj = videos_data.get("large")
            if not best_video_obj or not best_video_obj.get("url"):
                best_video_obj = videos_data.get("medium")                
            if not best_video_obj or not best_video_obj.get("url"):
                best_video_obj = list(videos_data.values())[0]

            download_link = best_video_obj.get("url")
            if not download_link:
                return False

            Messenger.info(f"⬇️ Descargando video de Pixabay ({selected_video.get('duration')}s)...")
            vid_res = requests.get(download_link, stream=True)
            vid_res.raise_for_status()
            
            out_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path = out_path.with_suffix(".raw.mp4")
            with open(raw_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Pixabay no da dimensiones en la respuesta de hits, así que
            # detectamos con ffprobe si necesita recorte a 9:16
            try:
                probe = subprocess.run([
                    "ffprobe", "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "csv=p=0",
                    str(raw_path)
                ], check=True, capture_output=True, text=True)
                dims = probe.stdout.strip().split(",")
                if len(dims) == 2:
                    w, h = int(dims[0]), int(dims[1])
                    if w > h:
                        Messenger.info("   📐 Recortando video a 9:16 vertical...")
                        subprocess.run([
                            "ffmpeg", "-y", "-i", str(raw_path),
                            "-vf", "crop=ih*9/16:ih,scale=1080:1920",
                            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                            "-an", str(out_path)
                        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        raw_path.unlink()
                        Messenger.success(f"✅ Video descargado y recortado: {out_path.name}")
                        return True
            except Exception:
                pass
            
            raw_path.rename(out_path)
            Messenger.success(f"✅ Video descargado con éxito de Pixabay: {out_path.name}")
            return True

        except Exception as e:
            Messenger.error(f"❌ Error al consultar Pixabay API: {e}")
            return False
