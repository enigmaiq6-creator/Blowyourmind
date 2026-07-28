import os
import subprocess
import requests
import random
from pathlib import Path
from pydantic import Field
from tools.common.messenger import Messenger
from tools.common.base_model import BaseModelTool
from typing import Optional

class PexelsTool(BaseModelTool):
    """
    Herramienta para interactuar con la API de Pexels y descargar videos e imágenes de stock.
    """
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("PEXELS_API_KEY"))

    def fetch_image(self, query: str, out_path: Path, min_width: int = 1080) -> bool:
        """
        Busca una imagen basada en el query y la descarga.
        Prueba sin orientación primero; si no hay resultados, prueba square.
        Recorta la imagen a formato cuadrado (center crop) para el layout Fact Split.
        Retorna True si fue exitoso, False en caso contrario.
        """
        if not self.api_key:
            Messenger.warning("⚠️ No se encontró PEXELS_API_KEY en el entorno. Saltando Pexels.")
            return False

        if not query or not query.strip():
            Messenger.warning("⚠️ Query de Pexels vacío. Saltando búsqueda.")
            return False

        Messenger.info(f"🔎 Buscando imagen en Pexels para: '{query}'...")
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.api_key}

        def search_pexels(orientation: str = "") -> list:
            nonlocal url, headers
            for attempt in range(2):
                page = 1 if attempt == 0 else random.randint(1, 3)
                params = {"query": query, "per_page": 15, "page": page}
                if orientation:
                    params["orientation"] = orientation
                resp = requests.get(url, headers=headers, params=params)
                resp.raise_for_status()
                photos = resp.json().get("photos", [])
                if photos:
                    return photos
            return []

        try:
            photos = search_pexels()
            if not photos:
                photos = search_pexels("square")

            if not photos:
                Messenger.warning(f"⚠️ No se encontraron imágenes para '{query}' en Pexels.")
                return False

            selected = random.choice(photos)
            src = selected.get("src", {})
            download_link = src.get("large") or src.get("original")
            if not download_link:
                return False

            Messenger.info(f"⬇️ Descargando imagen de Pexels...")
            img_res = requests.get(download_link, stream=True)
            img_res.raise_for_status()

            out_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path = out_path.with_suffix(".raw" + out_path.suffix)
            with open(raw_path, "wb") as f:
                for chunk in img_res.iter_content(chunk_size=8192):
                    f.write(chunk)

            from PIL import Image
            img = Image.open(raw_path)
            w, h = img.size
            if w != h:
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                img = img.crop((left, top, left + side, top + side))
                img.save(out_path, quality=92)
                raw_path.unlink()
                Messenger.info(f"   ✂️ Recortada a cuadrado: {side}x{side}")
            else:
                raw_path.rename(out_path)

            Messenger.success(f"✅ Imagen descargada: {out_path.name}")
            return True

        except Exception as e:
            Messenger.error(f"❌ Error al consultar Pexels API (imagen): {e}")
            return False

    def fetch_video(self, query: str, out_path: Path) -> bool:
        """
        Busca un video vertical basado en el query y lo descarga.
        Retorna True si fue exitoso, False en caso contrario.
        """
        if not self.api_key:
            Messenger.warning("⚠️ No se encontró PEXELS_API_KEY en el entorno. Saltando Pexels.")
            return False

        if not query or not query.strip():
            Messenger.warning("⚠️ Query de Pexels vacío. Saltando búsqueda.")
            return False

        Messenger.info(f"🔎 Buscando video en Pexels para: '{query}'...")
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.api_key}
        
        # Aleatoriedad fuerte: página al azar entre 1 y 3 para evitar repetir siempre los mismos clips top.
        random_page = random.randint(1, 3)
        params = {
            "query": query,
            "per_page": 15,
            "page": random_page,
            "size": "large"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            videos = data.get("videos", [])
            if not videos:
                if random_page > 1:
                    params["page"] = 1
                    response = requests.get(url, headers=headers, params=params)
                    data = response.json()
                    videos = data.get("videos", [])
                    
                if not videos:
                    Messenger.warning(f"⚠️ No se encontraron videos para '{query}' en Pexels.")
                    return False

            selected_video = random.choice(videos)
            
            video_files = selected_video.get("video_files", [])
            if not video_files:
                return False
                
            # Preferir HD vertical (height > width) pero aceptar cualquiera
            best_file = None
            portrait_hd = None
            landscape_hd = None
            for f in video_files:
                if f.get("quality") == "hd":
                    w = f.get("width") or 0
                    h = f.get("height") or 0
                    if h > w and not portrait_hd:
                        portrait_hd = f
                    elif w >= h and not landscape_hd:
                        landscape_hd = f
            
            best_file = portrait_hd or landscape_hd or video_files[0]
                
            download_link = best_file.get("link")
            if not download_link:
                return False

            Messenger.info(f"⬇️ Descargando video de Pexels ({selected_video.get('duration')}s)...")
            vid_res = requests.get(download_link, stream=True)
            vid_res.raise_for_status()
            
            out_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path = out_path.with_suffix(".raw.mp4")
            with open(raw_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Recortar a 9:16 vertical si es necesario
            w = best_file.get("width") or 0
            h = best_file.get("height") or 0
            if w > h:
                Messenger.info("   📐 Recortando video a 9:16 vertical...")
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(raw_path),
                    "-vf", "crop=ih*9/16:ih,scale=1080:1920",
                    "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                    "-an", str(out_path)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                raw_path.unlink()
            else:
                raw_path.rename(out_path)
            
            Messenger.success(f"✅ Video descargado con éxito: {out_path.name}")
            return True

        except Exception as e:
            Messenger.error(f"❌ Error al consultar Pexels API: {e}")
            return False
