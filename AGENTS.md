# BlowYourMind Content Engine — Geography Reels

## Proyecto
```
C:\Users\Vanes\.gemini\antigravity\scratch\BlowYourMind-Content-Engine
```

Este proyecto genera exclusivamente **Geography / Mind-Blowing Science Reels** (9:16 vertical, 1080x1920).

## Para correr (full pipeline)
```powershell
cd C:\Users\Vanes\.gemini\antigravity\scratch\BlowYourMind-Content-Engine
poetry run python -m flows.image_content_generator.pipeline.daily_automated_content
```

## Pipeline steps
1. `prompt_shorts/geography/` — Gemini genera script con datos geográficos, map pins, camera paths
2. `step2_generate_images` — Genera imágenes de escena vía Gemini/Vertex AI
3. `step3_generate_audios` — TTS (Vertex AI o Gemini) + Whisper alignment
4. `step2b_generate_video_clips` — Remotion render (MapRender 3D, SplitMap, DataVisualization, AI images, stock video)
5. `step4-7` — Ensamblaje, subtítulos PRO, música, renombrado
6. `step8` — Subida a Facebook

## Remotion debug
```powershell
cd flows/image_content_generator/remotion && npm start
```

## Output
```
flows/image_content_generator/out_short/ideas/idea_{id}/
```

---

# ═══════════════════════════════════════════
# SESIÓN: 3 JUN 2026 — RESUMEN COMPLETO
# ═══════════════════════════════════════════

## Bug fijo: Subtitles colorkey
- `Subtitles.tsx` tenía `backgroundColor: '#000000'` (negro) en lugar de `'#00FF00'` (verde) → colorkey en step5_pro no removía nada, overlay negro cubría el video entero → output 1.3 MB.
- **Fix**: Cambiar `backgroundColor` a `'#00FF00'` en `remotion/src/Subtitles.tsx:27`.

## Logro principal
Video **"Earth's Invisible Walls"** (Idea 2) regenerado exitosamente con **mapas satelitales 3D**, países iluminados, pins, rutas, word-pill subtitles, y música de fondo. Archivo: `out_short/ideas/idea_000002/earths_invisible_walls_how_one_mountain_range_separates_worlds_and_creates_unseen_life.mp4` (72.8 MB, 1:04, 1080×1920).

## Problema detectado y fix
- **Bug MAP_STYLES**: `MapRender.tsx` referenciaba `MAP_STYLES` antes de la declaración → todas las escenas fallaban a `ai_image` (solo imágenes, sin mapas).
- **Fix**: Movido `const MAP_STYLES = {...}` a nivel de módulo, antes de cualquier función que lo use.

## Optimización de velocidad (~5× más rápido)

### Antes (por escena):
- 8 llamadas separadas a `npx.cmd remotion render` (una por escena)
- Cada una arrancaba Node.js, cargaba imports, renderizaba, salía
- Tiempo: ~5-8 minutos

### Ahora (batch):
- **1 sola llamada** a `MultiSceneVideo` que renderiza TODAS las escenas juntas
- ffmpeg corta el video único en clips individuales por escena
- Tiempo: ~1-2 minutos

### Archivos modificados:
1. **`remotion/src/MultiSceneVideo.tsx`** — Mejorado para pasar TODAS las props a MapRender:
   - `subtitleWords`, `hexIcons`, `routes`, `regions`, `mapStyle`, `scanEffect`, `lowerThirdData`
   - Ya no solo `latitude/longitude/zoom/pitch/bearing`
2. **`pipeline/pipeline.py`** — Nuevo método `_build_scene_props()` (DRY). Step2b detecta si todas las escenas usan MapRender y las renderiza en lote con `MultiSceneVideo`. Si alguna escena necesita otro compositor (DataViz, SplitMap, HexDataGrid, stock), cae al sistema anterior por escena.

## Estado de las ideas
| ID | Título | Estado |
|----|--------|--------|
| 1 | Earth's Invisible Walls [Hook B] | `COMPLETED` |
| 2 | Earth's Invisible Walls | `COMPLETED` ✅ (recién regenerado) |
| 3 | The Silent Thaw [Hook B] | `SCRIPT_GENERATED` |
| 4 | The Silent Thaw | `SCRIPT_GENERATED` |

## Tareas pendientes / mejoras futuras
- [ ] **Ideas 3-4**: Correr pipeline completo para "The Silent Thaw" (glaciares, cambio climático)
- [ ] **SFX**: Descargar efectos de sonido a `resource/sfx/` (whoosh, impactos, transiciones) — los intentos desde Mixkit dieron 403
- [ ] **Más pistas bg-music**: Solo hay 4 tracks (echoes, feedback_dreams, selpan, tapis)
- [ ] **Verificar calidad de mapas**: Confirmar que los tiles satelitales de ArcGIS se renderizan bien y no hay rate limiting
- [ ] **Step8 Facebook upload**: Probar subida automática
- [ ] **Optimización adicional**: El split con ffmpeg re-codifica cada clip (lento). Se podría usar `-c copy -avoid_negative_ts make_zero` si los keyframes alinean
- [ ] **Estados mezclados**: Idea 1 (Hook B) comparte script con Idea 2. Al resetear Idea 2 a AUDIO_GENERATED, Hook B también estaba COMPLETED

## Nuevo video generado
- **Idea 7**: "The Disappearing Edges: When Coasts Vanish 20 Meters Annually [Hook B]" — `out_short/ideas/idea_000007/the_disappearing_edges_when_coasts_vanish_20_meters_annually_hook_b.mp4` (47.8 MB, 46s, 1080×1920). Contenido sobre erosión costera.

## Outputs disponibles
```
idea_000002/
├── clips/          ← clips individuales (step2b)
├── videos/         ← clips con audio (step4 assembly)
├── editions/
│   ├── raw_video.mp4          ← video ensamblado sin subtítulos
│   ├── remotion_overlay.mp4   ← overlay de subtítulos (green screen)
│   ├── pro_subtitled_video.mp4← video con word-pill subtitles
│   └── final_video.mp4        ← con música de fondo
├── images/         ← imágenes base (step2)
├── audios/         ← TTS por escena (step3)
├── earths_invisible_walls_....mp4  ← PRODUCTO FINAL (72.8 MB)
├── script.json
└── idea.json
```

## ═══════════════════════════════════════════
# SESIÓN: 4 JUN 2026 — TEXT OVERLAY FIX
# ═══════════════════════════════════════════

## Problema raíz: Text overlap
Los componentes de overlay (SceneOverlay, floating label, vignettes, LowerThird, subtítulos)
usaban posiciones fijas (coordenadas estáticas como `top: '25%'`, `bottom: 240`).
Cuando un texto era largo o habían múltiples elementos, se solapaban entre sí.

## Solución: Dynamic Layout Stack

### Nuevo archivo: `remotion/src/LayoutStack.tsx`
- **`LayoutStack`**: Componente de stacking vertical que reemplaza coordenadas fijas
  - Props: `items` (array de {key, render, height}), `zone` ('top' | 'middle' | 'bottom'), `align`
  - `zone='top'` → posiciona desde `top: 60` hacia abajo con gap de 16px
  - `zone='middle'` → centra verticalmente
  - `zone='bottom'` → posiciona desde `bottom: 180` hacia arriba
  - Sin coordenadas fijas — flexbox column con gap automático
- **`MeasuredText`**: Texto con auto-scale dinámico según longitud
  - `autoScaleFontSize()` recibe texto, maxWidth, maxFontSize → calcula fontSize exacto
  - Previene overflow horizontal
- **`PADDING = 20`, `MIN_MARGIN = 16`**: Márgenes de seguridad obligatorios

### Refactor: `remotion/src/SceneOverlay.tsx`
- **Eliminadas todas las coordenadas fijas** (`top: '25%'`, `top: '30%'`, `bottom: 120`)
- Cada `type` (title, nightmare, takeover, trade, etc.) define su contenido como array de `StackItem`
- Todo se renderiza dentro de `<LayoutStack zone="top">` → los elementos fluyen verticalmente
- `BigNumber` ahora usa `MeasuredText` con auto-scale de fontSize (80→28 según longitud)
- Añadido `wordBreak: 'break-word'` y `maxWidth: '100%'` en todos los textos

### Ajustes: `remotion/src/MapRender.tsx`
- **Floating label**: movido de `top: '30%'` a `top: '40%'` — debajo de SceneOverlay
- **Vignettes**: movidos de `top: 400` a `top: '42%'` — debajo de SceneOverlay

### Ajustes: `remotion/src/LowerThird.tsx`
- **Posición**: cambiada de `bottom: 240` a `bottom: 320` — más espacio de subtítulos (bottom: 160)

## Stress testing
- Texto corto: "6mm" → fontSize 80 (máximo) — ok
- Texto largo: "THE CANAL THAT CHANGED THE WORLD" (30 chars) → fontSize ~42 (auto-scalado)
- Múltiples elementos (year + label + BigNumber + detail) → todos fluyen verticalmente con gap 16px

## Relevant Files
- `remotion/src/LayoutStack.tsx` — **NUEVO**: sistema de stacking dinámico + auto-scale
- `remotion/src/SceneOverlay.tsx` — **REFACTOR**: sin coordenadas fijas, usa LayoutStack
- `remotion/src/MapRender.tsx` — floating label top:30%→40%, vignettes top:400→42%
- `remotion/src/LowerThird.tsx` — bottom:240→320

## ═══════════════════════════════════════════
# SESIÓN: 5 JUN 2026 — 7 LEVELS MODE (ENGLISH)
# ═══════════════════════════════════════════

## Nuevo modo: `seven_levels`
Se creó el modo **"7 Levels"** (inglés) — videos de 8 escenas (intro + 7 niveles escalantes).

### Archivos nuevos:
- **`prompt_shorts/seven_levels/__init__.py`** — exports
- **`prompt_shorts/seven_levels/models.py`** — `SevenLevelsIdea`, `SevenLevelsScene`, `SevenLevelsHandler`
- **`prompt_shorts/seven_levels/constants.py`** — prompts en inglés: `IDEA_PROMPT_SEVEN_LEVELS`, `SCRIPT_PROMPT_SEVEN_LEVELS`, `AUDIO_PROMPT_SEVEN_LEVELS`, `FOCUS_AREAS_SEVEN_LEVELS`

### Archivos modificados:
- **`prompt_shorts/manager.py`** — nuevo método `_generate_seven_levels_story()`, routing por mode
- **`pipeline/pipeline.py`** — `_category` map + `load_script()` + `step5_pro_subtitles()` level_markers
- **`pipeline/main.py`** — `--mode` choices incluye `seven_levels`
- **`remotion/src/Subtitles.tsx`** — level badges (LEVEL X/7), impact gradients, progress bar, level titles
- **`tools/video_editing/remotion.py`** — `render_subtitles()` acepta `level_markers` param
- **`pipeline/daily_automated_content.py`** — soporta `MODE=seven_levels`
- **`Makefile`** — targets `icg-7-*` para steps del modo seven_levels
- **`ENGLISH_BOT_SETUP_GUIDE.md`** — guía completa del proyecto en inglés

### Cómo correr:
```powershell
# Full pipeline
make icg-7-all

# O con Poetry
poetry run python -m flows.image_content_generator.pipeline.main short all --mode seven_levels
```

### Subtitles.tsx features nuevas:
- Level badge con gradient según impacto (Low→verde, Medium→naranja, High→rojo, Extreme→púrpura)
- Level title debajo del badge
- Progress bar con dots animados por nivel
- Underline de palabra actual se colorea según el nivel activo
```

## ═══════════════════════════════════════════
# SESIÓN: 6 JUN 2026 — STANDARD MODE + OPTIMIZACIONES
# ═══════════════════════════════════════════

## Nuevo modo: `standard` (Curiosity Reels)
Se creó el modo Standard — videos de curiosidades rápidas (6-8 escenas, 50-60s).

### Archivos nuevos:
- **`prompt_shorts/stories/__init__.py`** — exports
- **`prompt_shorts/stories/models.py`** — `StoryIdea`, `StoryHandler`
- **`prompt_shorts/stories/constants.py`** — prompts en inglés + 30 focus areas (cognitive biases, animal superpowers, space curiosities, etc.)

### Archivos modificados:
- **`prompt_shorts/manager.py`** — nuevo método `_generate_stories_story()`, routing para mode "stories"/"standard"
- **`pipeline/pipeline.py`** — `load_script()` ahora carga `StoryHandler` para categoría "stories"
- **`Makefile`** — targets `icg-s-*` con `--mode standard`

## Optimizaciones de velocidad

### Cambio a API Key (no Vertex) para texto
- **`gemini_base.py`**: ahora usa `GEMINI_API_KEY` por defecto en vez de Vertex AI
- Controlado por `USE_VERTEX_AI_GEMINI=false` (default)
- Vertex AI para Gemini tiene cuotas más restrictivas; API key tiene mejor throughput

### Reducción de reintentos
- **`gemini_base.py`**: de 8 intentos × 90s a **4 intentos × 30s**
- Tiempo máximo de espera: 2 min (antes 12 min)

### Modelo más rápido
- **`text_generation/gemini.py`**: cambiado de `gemini-2.5-flash` → `gemini-2.0-flash`
- Free tier: 60 RPM vs 10 RPM del 2.5-flash

### Vertex AI reactivado (con $300 crédito)
- **`gemini_base.py`**: `USE_VERTEX_AI_GEMINI` default ahora es `true`
- **`daily_post.yml`**: añadido `USE_VERTEX_AI_GEMINI: "true"` al workflow
- Usa Vertex AI con cuotas más altas + los $300 de crédito GCP

## Workflow mejorado
- **`daily_post.yml`**: ahora acepta `mode` como input (`workflow_dispatch`) con opciones: geography, seven_levels, standard, stories
- **`daily_automated_content.py`**: selección ponderada aleatoria de modo
  - Default weights: `geography=0.1, seven_levels=0.5, standard=0.4`
  - Configurable via `MODE_WEIGHTS` env var
  - Forzar modo via `MODE` env var

## Costo por video
| Componente | Costo |
|-----------|:-:|
| Texto (Gemini 2.0 Flash via Vertex) | ~$0.0003 |
| Imágenes (Imagen 3) × 8 | ~$0.24 |
| Audio (Vertex TTS) | ~$0.002 |
| Stock video, Whisper, FFmpeg | GRATIS |
| **Total** | **~$0.25 USD** |
| **Con $300 crédito Vertex** | **~1,200 videos** |

## Outputs
- Todos los cambios fueron commiteados y pusheados a `origin/main`
- Commits: `1aa8d85`, `9de3863`, `7288d73`, `a016dfa`, `03900e9`, `c91af2b`, `1eb48f8`, `570c32b`

## Cómo correr cada modo
```powershell
make icg-s-all     # Standard (Curiosity Reels)
make icg-7-all     # 7 Levels (English)
make icg-g-all     # Geography (3D Maps)
make icg-f-all     # Finance (English)
make icg-w-all     # What If (Alternate Geography)
```

## ═══════════════════════════════════════════
# SESIÓN: 21 JUN 2026 — WHAT IF MODE + GIT FIX
# ═══════════════════════════════════════════

## Nuevo modo: `what_if`
Se creó el modo **"What If"** (alternate geography / counterfactual scenarios) — videos de 5-6 escenas explorando "qué pasaría si" la geografía mundial fuera diferente.

Se portaron los 14 topics del proyecto `automatizacion-videos-ia` como `FOCUS_AREAS_WHAT_IF` (21 topics total con 7 adicionales), con selección secuencial sin repetición (como Finance mode). Cuando se agoten, Gemini genera nuevos dinámicamente.

### Archivos nuevos:
- **`prompt_shorts/what_if/__init__.py`** — exports
- **`prompt_shorts/what_if/models.py`** — `WhatIfIdea`, `WhatIfScene`, `WhatIfHandler`
- **`prompt_shorts/what_if/constants.py`** — prompts en inglés: `IDEA_PROMPT_WHAT_IF`, `SCRIPT_PROMPT_WHAT_IF`, `AUDIO_PROMPT_WHAT_IF`, `FOCUS_AREAS_WHAT_IF` (21 topics)

### Archivos modificados:
- **`prompt_shorts/manager.py`** — nuevo método `_generate_what_if_story()`, routing para mode "what_if", añadido `WhatIfHandler` a `CATEGORIES`
- **`pipeline/pipeline.py`** — `_category` map + `load_script()` para `WhatIfHandler`
- **`pipeline/main.py`** — `--mode` choices incluye `what_if`
- **`daily_automated_content.py`** — label "What If" para el modo
- **`Makefile`** — targets `icg-w-*` (step1-8 + all)
- **`.github/workflows/daily_post.yml`** — opción `what_if` en inputs

### Visual style
Map-based infographic documentary style (dark navy, teal/coral accents, same aesthetic as the original `automatizacion-videos-ia` project). All scenes use `visual_type: "ai_image"` (Vertex AI Imagen).

### Cómo correr:
```powershell
make icg-w-all     # Full pipeline
# O step por step:
make icg-w-step1   # Solo Step 1 (generar story)
make icg-w-step2   # Solo Step 2 (generar imágenes)
```

### Output esperado
Video ~60s con mapas generados por AI, narración TTS, subtítulos animados, música de fondo. Mismo pipeline que los otros modos.

### Fix: automatizacion-videos-ia git 403
- **Problema**: Workflow `generate-videos.yml` fallaba con `403 Write access to repository not granted`
- **Causa**: El job no tenía `permissions: contents: write`, por lo que el GITHUB_TOKEN solo tenía acceso de lectura
- **Fix**: Añadido `permissions: contents: write` al job + `concurrency` group para evitar que runs simultáneos del cron (9, 15, 21 UTC) se pisen entre sí

## ═══════════════════════════════════════════
# SESIÓN: 22 JUN 2026 — FIX TRACKING CSV PERSISTENCIA EN GITHUB ACTIONS
# ═══════════════════════════════════════════

## Problema: `what_if` siempre subía el mismo video
El modo `what_if` (y potencialmente otros modos con selección secuencial) siempre generaba el mismo topic porque el CSV de tracking no persistía entre runs de GitHub Actions.

## Causa raíz
`ideas_tracking.csv` y `automated_posts_history.csv` vivían en `out_short/` que está en `.gitignore`:
```gitignore
**/out_short   ← ignora toda la carpeta de output
```
El workflow usaba `git add -f` para forzar el CSV, pero si un run fallaba a mitad, el CSV nunca se actualizaba. En el siguiente run se clonaba el repo sin historial → siempre seleccionaba el primer topic de `FOCUS_AREAS_WHAT_IF`.

## Solución: carpeta `tracking/` dedicada (git-tracked)

### Archivos modificados:
- **`flows/image_content_generator/tracking/.gitkeep`** — [NUEVO] carpeta dedicada fuera de `out_short/`, incluida en git sin `-f`
- **`pipeline/main.py`** — Nueva constante `TRACKING_BASE = Path("flows/image_content_generator/tracking")` pasada al `Pipeline`
- **`pipeline/pipeline.py`** — Nuevo campo `tracking_base: Optional[Path] = None`. La propiedad `store` usa `tracking_base` si está disponible, sino `out_base` (compatibilidad local)
- **`pipeline/daily_automated_content.py`** — `history_file` y `video_csv` apuntan a `tracking/` en lugar de `out_short/`; `sync_to_github()` actualizado con los nuevos paths
- **`.github/workflows/daily_post.yml`** — Step de commit ahora hace `git add flows/image_content_generator/tracking/` (sin `-f`) en lugar de los paths de `out_short/`

### Commit: `dde78d4`

## ═══════════════════════════════════════════
# SESIÓN: 22 JUN 2026 — LIMPIEZA DE MODOS Y PLANIFICACIÓN FUTURA
# ═══════════════════════════════════════════

## 1. Simplificación a Mono-Modo (Geography)
- **Problema**: El repositorio contenía múltiples modos en desuso o rotos (`stories`, `seven_levels`, `finance`, `what_if`).
- **Cambios**:
  - Se eliminaron las carpetas de estos modos en `prompt_shorts/`.
  - Se limpió `PromptManagerShorts` (`manager.py`) eliminando todas las funciones privadas generadoras que no fuesen de `geography`.
  - Se simplificó `daily_automated_content.py` para correr exclusivamente el pipeline en modo `geography`.
  - Se actualizó `daily_post.yml` para limitar las opciones de ejecución únicamente a `geography`.

## 2. Planificación de Segundo Modo de Contenido
- **Objetivo**: Añadir un nuevo modo de contenido personalizado para que conviva junto a `geography`.
- **Estado**: La estructura está limpia y lista para la extensión. El usuario ha solicitado delegar esta tarea al siguiente modelo de IA.
- **Instrucciones para el siguiente Agente**:
  - Lee el prompt de abajo para conocer la intención y pregúntale al usuario para definir la temática y el estilo visual del nuevo modo.
  - Deberás recrear una carpeta en `prompt_shorts/<nombre_modo>` con su `constants.py` ( prompts de Script e Idea) y `models.py` (Esquemas Pydantic).
  - Deberás registrar el nuevo modo en `manager.py`, `pipeline.py` y actualizar las opciones en `main.py` y `daily_post.yml`.
