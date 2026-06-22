from typing import List, Type, ClassVar, Optional
from pydantic import BaseModel, Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler, Scene
from flows.image_content_generator.pipeline.prompt_shorts.what_if import constants as what_if_constants


class WhatIfIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = what_if_constants.IDEA_PROMPT_WHAT_IF
    primary_country: str = Field(description="The main country or region involved in the scenario (e.g., 'Brazil', 'India', 'Africa').")
    primary_continent: str = Field(description="The continent where the scenario takes place (e.g., 'South America', 'Asia', 'Africa').")
    scenario_type: str = Field(description="Category of the scenario: 'location_swap', 'country_union', 'territorial_expansion', 'population_change', 'natural_change', 'alternate_history', or 'resource_shift'.")
    consequences: List[str] = Field(description="List of 3-5 specific, measurable consequences of the hypothetical change (e.g., population, territory, resources, military power, economy, culture, trade, conflicts, global influence).")
    unexpected_twist: str = Field(description="A single sentence describing a negative consequence, conflict, or difficulty that would arise from the scenario.")
    closing_question: str = Field(description="A short, engaging question that invites viewers to comment and debate (e.g., 'Would this new Brazil become a superpower?').")
    caption: str = Field(description="A deep, engaging social media caption explaining the scenario in English. MUST include 5 to 8 viral hashtags (e.g., #WhatIf #AlternateGeography #MapFacts #Geography).")
    category: str = "what_if"


class MapCamera(BaseModel):
    latitude: float = Field(description="Latitude coordinate of the camera target location.")
    longitude: float = Field(description="Longitude coordinate of the camera target location.")
    zoom: float = Field(description="Map zoom level (3.0 for continents, 5.0-8.0 for countries/regions).")
    pitch: float = Field(description="Camera inclination in degrees (between 30 and 50 for 3D perspective).")
    bearing: float = Field(description="Camera orientation/rotation angle in degrees (-180 to 180).")


class MapPin(BaseModel):
    latitude: float
    longitude: float
    label: str = Field(description="Short label or city/place name for this pin.")
    value: str = Field(default="", description="Optional data value displayed below the label.")


class MapVignette(BaseModel):
    icon: str = Field(default="📊")
    title: str = Field(description="Short title or category for this data point (e.g. 'POPULATION', 'AREA', 'GDP').")
    value: str = Field(description="The actual data value in BIG numbers (e.g. '214 Million', '17M km²').")


class CameraWaypoint(BaseModel):
    latitude: float
    longitude: float
    zoom: float = Field(ge=1.0, le=20.0, default=5.0)
    pitch: float = Field(ge=0, le=90, default=40)
    bearing: float = Field(ge=-180, le=180, default=0)


class HexIconData(BaseModel):
    latitude: float
    longitude: float
    icon: str = Field(default="📍", description="Emoji icon for resource/military/cultural markers.")
    label: str = Field(default="")
    value: str = Field(default="")
    color: str = Field(default="#FF0078")


class RouteData(BaseModel):
    waypoints: List[CameraWaypoint]
    color: str = Field(default="#FF0078")
    label: str = Field(default="")
    dot_labels: List[str] = Field(default=[])


class RegionData(BaseModel):
    name: str
    center_latitude: float
    center_longitude: float
    color: str
    label: str = Field(default="")
    radius_km: float = Field(default=200)


class HexGridItem(BaseModel):
    icon: str
    label: str = Field(default="")
    value: str = Field(default="")
    color: str = Field(default="#FF0078")


class HexGridData(BaseModel):
    title: str = Field(default="")
    items: List[HexGridItem]


class WhatIfScene(Scene):
    visual_type: str = Field(default="map_3d", description="Use 'map_3d' for political maps with country highlights. Use 'ai_image' ONLY for historical or impossible-to-map concepts.")
    image_prompt: Optional[str] = Field(default=None)
    camera: Optional[MapCamera] = Field(default=None)
    camera_latitude: float = Field(default=0.0)
    camera_longitude: float = Field(default=0.0)
    camera_zoom: float = Field(default=0.0)
    camera_pitch: float = Field(default=0.0)
    camera_bearing: float = Field(default=0.0)
    camera_path: List[CameraWaypoint] = Field(default=[], description="2-3 waypoints for cinematic fly-through over the map.")
    highlight_region: str = Field(default="none", description="Country or region to highlight with neon glow (e.g., 'Brazil', 'India', 'Africa').")
    arrow_direction: str = Field(default="none", description="Description of expansion/swap/movement arrow (e.g., 'Brazil expanding over all South America'). MANDATORY for Scene 3.")
    floating_label: str = Field(default="none", description="Key data label in ALL CAPS (e.g., '17 MILLION SQ KM', '450M PEOPLE', '$2.1 TRIL').")
    map_pins: List[MapPin] = Field(default=[], description="2-4 pins on key cities, resources, or strategic locations.")
    vignettes: List[MapVignette] = Field(default=[], description="2-3 data cards showing population, area, GDP, resources.")
    sfx: str = Field(default="none", description="Sound effect: 'whoosh', 'digital_swoosh', 'heavy_wind', 'ocean_waves', or 'none'.")
    map_style: str = Field(default="dark", description="Map style: 'dark' for premium contrast political maps, 'satellite' for realistic terrain. Default is 'dark'.")
    hex_icons: List[HexIconData] = Field(default=[], description="Hex markers for resource locations, military bases, cultural centers. 2-4 per consequence scene.")
    routes: List[RouteData] = Field(default=[], description="Animated route lines for trade routes, migration paths, or expansion arrows. 1-2 per scene.")
    regions: List[RegionData] = Field(default=[], description="Colored region overlays for breaking down continents into zones. 3-6 per scene.")
    hex_grid: Optional[HexGridData] = Field(default=None, description="Full-screen hex data grid for multi-metric comparisons. Use for consequence scenes showing population, area, GDP, resources side by side.")
    scene_overlay_type: Optional[str] = Field(default=None, description="Overlay type for this scene: 'title', 'big_number', 'year', 'location', 'nightmare', 'trade', or null.")


class WhatIfHandler(CategoryHandler):
    SCRIPT_PROMPT: ClassVar[str] = what_if_constants.SCRIPT_PROMPT_WHAT_IF
    category: str = "what_if"
    idea_variants: ClassVar[List[Type[BaseIdea]]] = [WhatIfIdea]
    scenes: List[WhatIfScene] = Field(description="List of 6 scenes for the What If scenario script")
