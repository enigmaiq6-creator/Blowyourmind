from typing import List, Type, ClassVar, Optional
from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.geography import constants as geo_constants


class GeographyIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = geo_constants.IDEA_PROMPT_GEOGRAPHY
    intrigue_header: str = Field(description="A short, punchy 3-5 word phrase to persist at the top of the video in ALL CAPS to create extreme intrigue (e.g., 'EL MURO DE COLOMBIA', 'EL SECRETO DE LOS ANDES').")
    caption: str = Field(description="Una descripción para redes sociales (Facebook/Instagram) altamente viral, educativa e intrigante sobre el misterio geográfico presentado. DEBE incluir entre 5 y 8 hashtags extremadamente virales (Ej: #Geografia #SabiasQue #Curiosidades #DatosGeograficos + específicos del tema).")
    category: str = "geography"


class MapCamera(BaseModel):
    latitude: float = Field(description="Latitude coordinate of the camera target location.")
    longitude: float = Field(description="Longitude coordinate of the camera target location.")
    zoom: float = Field(description="Map zoom level (value between 3.0 for continents and 12.0 for local spots).")
    pitch: float = Field(description="Camera inclination in degrees (between 30 and 60 for 3D perspective).")
    bearing: float = Field(description="Camera orientation/rotation angle in degrees (between -180 and 180).")


class GeographyScene(Scene):
    camera: MapCamera = Field(description="Configuración de la cámara del mapa satelital 3D para esta escena.")
    highlight_region: str = Field(default="none", description="Nombre de la región, país o accidente geográfico a resaltar de forma brillante en el mapa (ej. 'Colombia', 'Andes Mountains', o 'none' si no se resalta nada).")
    arrow_direction: str = Field(default="none", description="Descripción del flujo de una flecha animada en el mapa (ej. 'from: Pacific Ocean, to: Andes Mountains' o 'none').")
    floating_label: str = Field(default="none", description="Etiqueta flotante con datos clave o números de impacto en mayúsculas (ej: '52.32 MILLONES', '3 CORDILLERAS' o 'none').")
    sfx: str = Field(default="none", description="Efecto de sonido ambiental o de impacto para esta escena ('jungle_ambient', 'rain_and_thunder', 'heavy_wind', 'digital_swoosh', 'ocean_waves', o 'none').")


class GeographyHandler(CategoryHandler):
    category: str = "geography"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [GeographyIdea]
    scenes: List[GeographyScene] = Field(description="List of scenes detailing the geography script")
