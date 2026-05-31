from typing import List, Type, ClassVar, Optional
from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.geography import constants as geo_constants


class GeographyIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = geo_constants.IDEA_PROMPT_GEOGRAPHY
    intrigue_header: str = Field(description="A short, punchy 3-5 word phrase to persist at the top of the video in ALL CAPS to create extreme intrigue. MUST include a key data number when possible (e.g., '40,000 KM WOUND', '8,000 MM RAIN', 'THE FLYING RIVERS').")
    personal_impact: str = Field(description="A single sentence explaining how this phenomenon affects the viewer personally (e.g., 'This river in the sky determines if YOUR city has rain or drought.'). Must use 'YOUR' or 'YOU' to make it personal.")
    key_data_stat: str = Field(description="ONE specific, mind-blowing data point in numeric format with units that will be displayed as a floating HUD label (e.g., '8,000 mm/year', '40,000 km', '200 mph', '52 million people').")
    caption: str = Field(description="A highly viral, educational, and intriguing social media caption (Facebook/Instagram) about the presented geographical mystery in English. MUST include 5 to 8 extremely viral hashtags (e.g., #GeographySecrets #MindBlowingFacts #HiddenWorld #HowNatureWorks + topic specific tags).")
    category: str = "geography"


class MapCamera(BaseModel):
    latitude: float = Field(description="Latitude coordinate of the camera target location.")
    longitude: float = Field(description="Longitude coordinate of the camera target location.")
    zoom: float = Field(description="Map zoom level (value between 3.0 for continents and 12.0 for local spots).")
    pitch: float = Field(description="Camera inclination in degrees (between 30 and 60 for 3D perspective).")
    bearing: float = Field(description="Camera orientation/rotation angle in degrees (between -180 and 180).")


class MapPin(BaseModel):
    latitude: float = Field(description="Latitude coordinate of the map pin location.")
    longitude: float = Field(description="Longitude coordinate of the map pin location.")
    label: str = Field(description="Short label or city/place name for this pin (e.g. 'Bogota', 'Andes', 'Pacific Ocean').")
    value: str = Field(default="", description="Optional data value displayed below the label (e.g. '8.7M people', '6,700m').")


class MapVignette(BaseModel):
    icon: str = Field(default="📊", description="Emoji icon for this vignette card.")
    title: str = Field(description="Short title or category for this data point (e.g. 'ANNUAL RAINFALL', 'POPULATION', 'LENGTH').")
    value: str = Field(description="The actual data value in BIG numbers (e.g. '8,000 mm', '52 Million', '6,700 KM').")


class CameraWaypoint(BaseModel):
    latitude: float = Field(description="GPS latitude for this waypoint.")
    longitude: float = Field(description="GPS longitude for this waypoint.")
    zoom: float = Field(ge=1.0, le=20.0, default=5.0, description="Zoom level. 1 = world, 5 = country, 10 = city, 13 = streets/buildings, 15+ = individual blocks.")
    pitch: float = Field(ge=0, le=90, default=40, description="Tilt angle in degrees. 0 = top-down, 60 = dramatic 3D.")
    bearing: float = Field(ge=-180, le=180, default=0, description="Rotation/heading in degrees.")


class GeographyScene(Scene):
    visual_type: str = Field(default="map_3d", description="Type of scene. Use 'map_3d' for 3D satellite map fly-overs (default), 'ai_image' for AI-generated conceptual illustrations, 'data_viz' for animated data charts/numbers, 'split_map' for side-by-side comparison maps, or 'stock_video' for stock footage.")
    image_prompt: Optional[str] = Field(default=None, description="Physical description and style in ENGLISH for AI image generation. Only required when visual_type is 'ai_image' or as Ken Burns fallback.")
    camera: Optional[MapCamera] = Field(default=None, description="Satellite 3D map camera configuration for this scene. Required for 'map_3d' scenes.")
    camera_latitude: float = Field(default=0.0, description="Flat latitude for direct Remotion props. Use camera.latitude instead.")
    camera_longitude: float = Field(default=0.0, description="Flat longitude for direct Remotion props. Use camera.longitude instead.")
    camera_zoom: float = Field(default=0.0, description="Flat zoom for direct Remotion props. Use camera.zoom instead.")
    camera_pitch: float = Field(default=0.0, description="Flat pitch for direct Remotion props. Use camera.pitch instead.")
    camera_bearing: float = Field(default=0.0, description="Flat bearing for direct Remotion props. Use camera.bearing instead.")
    camera_path: List[CameraWaypoint] = Field(default=[], description="Sequence of camera waypoints for a cinematic fly-through during this scene. The camera smoothly interpolates through these points over the scene duration. Example: [waypoint wide over country, waypoint zoomed into city, waypoint wide again]. Leave empty for simple static animation.")
    highlight_region: str = Field(default="none", description="Name of the region, country, or geographical feature to highlight brightly on the map with neon glow (e.g. 'Colombia', 'Brazil', 'USA', or 'none'). Supports real GeoJSON country borders.")
    arrow_direction: str = Field(default="none", description="Description of the flow of an animated arrow on the map (e.g. 'from: Pacific Ocean, to: Andes Mountains' or 'none').")
    floating_label: str = Field(default="none", description="Floating label with key impact data or numbers in ALL CAPS (e.g. '52.32 MILLION', '3 MOUNTAIN RANGES', '8,000 MM RAIN' or 'none').")
    map_pins: List[MapPin] = Field(default=[], description="List of 2-4 animated map pins highlighting specific locations on the map. Each pin has coordinates and a label. These appear as pulsing markers.")
    vignettes: List[MapVignette] = Field(default=[], description="List of 2-4 information vignettes/bullet points that appear sequentially on the right side of the screen. Each shows an icon, title, and big data value.")
    sfx: str = Field(default="none", description="Environmental or impact sound effect for this scene ('jungle_ambient', 'rain_and_thunder', 'heavy_wind', 'digital_swoosh', 'ocean_waves', 'volcanic_rumble' or 'none').")


class GeographyHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = geo_constants.SCRIPT_PROMPT_GEOGRAPHY
    category: str = "geography"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [GeographyIdea]
    scenes: List[GeographyScene] = Field(description="List of scenes detailing the geography script")
