from typing import List, Type, ClassVar, Optional
from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.geography import constants as geo_constants


class GeographyIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = geo_constants.IDEA_PROMPT_GEOGRAPHY
    intrigue_header: str = Field(description="A short, punchy 3-5 word phrase to persist at the top of the video in ALL CAPS to create extreme intrigue (e.g., 'THE WALL OF COLOMBIA', 'THE SECRET OF THE ANDES').")
    caption: str = Field(description="A highly viral, educational, and intriguing social media caption (Facebook/Instagram) about the presented geographical mystery in English. MUST include 5 to 8 extremely viral hashtags (e.g., #Geography #MindBlowingFacts #EarthSecrets + topic specific tags).")
    category: str = "geography"


class MapCamera(BaseModel):
    latitude: float = Field(description="Latitude coordinate of the camera target location.")
    longitude: float = Field(description="Longitude coordinate of the camera target location.")
    zoom: float = Field(description="Map zoom level (value between 3.0 for continents and 12.0 for local spots).")
    pitch: float = Field(description="Camera inclination in degrees (between 30 and 60 for 3D perspective).")
    bearing: float = Field(description="Camera orientation/rotation angle in degrees (between -180 and 180).")


class GeographyScene(Scene):
    camera: MapCamera = Field(description="Satellite 3D map camera configuration for this scene.")
    highlight_region: str = Field(default="none", description="Name of the region, country, or geographical feature to highlight brightly on the map (e.g. 'Colombia', 'Andes Mountains', or 'none' if nothing is highlighted).")
    arrow_direction: str = Field(default="none", description="Description of the flow of an animated arrow on the map (e.g. 'from: Pacific Ocean, to: Andes Mountains' or 'none').")
    floating_label: str = Field(default="none", description="Floating label with key impact data or numbers in ALL CAPS (e.g. '52.32 MILLION', '3 MOUNTAIN RANGES' or 'none').")
    sfx: str = Field(default="none", description="Environmental or impact sound effect for this scene ('jungle_ambient', 'rain_and_thunder', 'heavy_wind', 'digital_swoosh', 'ocean_waves', or 'none').")


class GeographyHandler(CategoryHandler):
    category: str = "geography"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [GeographyIdea]
    scenes: List[GeographyScene] = Field(description="List of scenes detailing the geography script")
