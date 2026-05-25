import os
import requests
import random
from pathlib import Path
from pydantic import Field
from tools.common.messenger import Messenger
from tools.common.base_model import BaseModelTool
from typing import Optional

class PexelsTool(BaseModelTool):
    """
    Herramienta para interactuar con la API de Pexels y descargar videos de stock gratuitos.
    """
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("PEXELS_API_KEY"))

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
            "orientation": "portrait",
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
                # Fallback a la pagina 1 si la pagina random no tiene resultados
                if random_page > 1:
                    params["page"] = 1
                    response = requests.get(url, headers=headers, params=params)
                    data = response.json()
                    videos = data.get("videos", [])
                    
                if not videos:
                    Messenger.warning(f"⚠️ No se encontraron videos verticales para '{query}' en Pexels.")
                    return False

            # Elegir uno al azar de la lista completa
            selected_video = random.choice(videos)
            
            # Buscar el archivo de video de mejor calidad
            video_files = selected_video.get("video_files", [])
            if not video_files:
                return False
                
            # Ordenar por calidad (vertical 1080x1920 o similar)
            # Priorizamos calidad 'hd'
            best_file = None
            for f in video_files:
                if f.get("quality") == "hd" and f.get("width") and f.get("height") and f.get("height") > f.get("width"):
                    best_file = f
                    break
            
            # Fallback a cualquiera si no hay hd vertical
            if not best_file:
                best_file = video_files[0]
                
            download_link = best_file.get("link")
            if not download_link:
                return False

            Messenger.info(f"⬇️ Descargando video de Pexels ({selected_video.get('duration')}s)...")
            vid_res = requests.get(download_link, stream=True)
            vid_res.raise_for_status()
            
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            Messenger.success(f"✅ Video descargado con éxito: {out_path.name}")
            return True

        except Exception as e:
            Messenger.error(f"❌ Error al consultar Pexels API: {e}")
            return False
