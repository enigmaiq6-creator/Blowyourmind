# AI Content Automation Engine (English Version)

> Copy of "AI Content Automation Engine" (EnigmaIQ Spanish) adapted for English.
> Same visual style, same pipeline, same APIs — everything in English.

---

## TABLE OF CONTENTS

1. [Architecture Overview](#1-architecture-overview)
2. [Required APIs & Credentials](#2-required-apis--credentials)
3. [Local Setup (Development)](#3-local-setup-development)
4. [Complete Project Structure](#4-complete-project-structure)
5. [Pipeline Step-by-Step](#5-pipeline-step-by-step)
6. [Mode 1: Standard (Curiosity Reels)](#6-mode-1-standard-curiosity-reels)
7. [Mode 2: Siete Niveles → "7 Levels" (English Version)](#7-mode-2-siete-niveles--7-levels-english-version)
8. [Remotion Subtitles System (Karaoke)](#8-remotion-subtitles-system-karaoke)
9. [Background Music System](#9-background-music-system)
10. [GitHub Actions CI/CD](#10-github-actions-cicd)
11. [Spanish → English Translation Map](#11-spanish--english-translation-map)
12. [Run Commands](#12-run-commands)
13. [Troubleshooting Tips](#13-troubleshooting-tips)

---

## 1. Architecture Overview

```
User prompt → Gemini Text Gen → Script JSON → Gemini/Vertex Images
  → Pexels/Pixabay Videos → Gemini TTS / Vertex TTS → Whisper Transcription
  → FFmpeg Video Assembly → Remotion Karaoke Subtitles → Background Music
  → Final Video → Facebook Upload
```

**Tech Stack:**
| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Text Gen | Gemini 2.0 Flash (`gemini-2.0-flash`) |
| Image Gen | Gemini Imagen 3 (`gemini-3.1-flash-image-preview`) or Vertex AI Imagen |
| Audio Gen | Gemini TTS (Fenrir voice) or Vertex AI TTS (Studio voices) |
| Stock Videos | Pexels API + Pixabay API |
| Transcription | OpenAI Whisper (`small` model) |
| Karaoke Subtitles | Remotion (React, renders PNG sequences) |
| Video Editing | FFmpeg (concatenation, mixing, scaling, transitions) |
| State Tracking | CSV-based (pandas) |
| Social Upload | Facebook Graph API v19.0 |
| CI/CD | GitHub Actions |
| Dependencies | Poetry |

---

## 2. Required APIs & Credentials

| Variable | Where to Get | Purpose |
|----------|-------------|---------|
| `GEMINI_API_KEY` | https://aistudio.google.com/ | Text, image, audio generation |
| `GCP_PROJECT_ID` | Google Cloud Console | Vertex AI (Imagen + TTS) |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | GCP Service Account | Auth for Vertex AI |
| `PEXELS_API_KEY` | https://www.pexels.com/api/ | Stock video search |
| `PIXABAY_API_KEY` | https://pixabay.com/api/docs/ | Stock video fallback |
| `FACEBOOK_PAGE_ID` | Facebook Page Settings | Upload destination |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook Graph API | Upload auth |

**Set these in `.env` for local dev and as GitHub Secrets for CI/CD.**

---

## 3. Local Setup (Development)

### Prerequisites
```bash
# 1. Python 3.11+
python --version  # must be ≥ 3.11

# 2. Install Poetry
pip install poetry

# 3. Install FFmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 4. Install Whisper
pip install openai-whisper

# 5. Install Node.js 20+ (for Remotion)
node --version  # must be ≥ 20
```

### Project Installation
```bash
# 1. Clone repo
git clone <your-repo-url>
cd <your-repo>

# 2. Install Python deps
poetry install

# 3. Install Remotion deps
cd flows/image_content_generator/remotion
npm ci
cd ../../..

# 4. Create .env file
cp .env.sample .env
# Fill in all API keys

# 5. Set up Whisper model
# The small model downloads automatically on first use (~500MB)
```

---

## 4. Complete Project Structure

```
project-root/
├── .env                          # API keys (gitignored)
├── .env.sample                   # Template
├── .github/workflows/daily_post.yml   # CI/CD pipeline
├── pyproject.toml                # Poetry config
├── Makefile                      # Convenience commands
├── Dockerfile                    # Containerized deployment
├── docker-compose.yml
│
├── flows/
│   └── image_content_generator/
│       ├── pipeline/
│       │   ├── main.py                    # CLI entry point
│       │   ├── pipeline.py                # Core orchestrator (all steps 1-8)
│       │   ├── schemas.py                 # State enum, VideoOrientation, IdeaRaw
│       │   ├── storage_csv.py             # CSV state machine
│       │   ├── daily_automated_content.py # GitHub Actions runner
│       │   ├── prompt_base/
│       │   │   ├── models.py              # BaseIdea, Scene, VideoScript, CategoryHandler
│       │   │   ├── manager.py             # BasePromptManager (alignment, audio prompts)
│       │   │   └── constants.py           # Base prompt constants
│       │   ├── prompt_shorts/
│       │   │   ├── manager.py             # PromptManagerShorts — routes modes
│       │   │   ├── stories/
│       │   │   │   ├── models.py          # StoryIdea, StoryHandler
│       │   │   │   ├── constants.py       # Standard curiosity prompts
│       │   │   │   └── stickman_manager.py
│       │   │   ├── siete_niveles/
│       │   │   │   ├── models.py          # SieteNivelesIdea, SieteNivelesScene, SieteNivelesHandler
│       │   │   │   ├── constants.py       # "7 Levels" prompts in Spanish
│       │   │   │   └── __init__.py
│       │   │   ├── geography/
│       │   │   │   ├── models.py
│       │   │   │   ├── constants.py
│       │   │   │   └── __init__.py
│       │   │   └── finances/              # Legacy niche (not needed for English)
│       │   └── repair_idea_2.py           # Repair/resume script
│       │
│       ├── remotion/
│       │   ├── package.json
│       │   ├── src/
│       │   │   ├── index.ts               # Remotion entry point
│       │   │   ├── Root.tsx               # Registers "Subtitles" composition
│       │   │   ├── Root.geography.tsx     # Geography composition
│       │   │   ├── Subtitles.tsx          # ** THE CORE — word karaoke engine (622 lines) **
│       │   │   ├── MapRender.tsx           # 3D map rendering (geography mode)
│       │   │   └── data/                  # input.json written dynamically
│       │   └── build/                     # Built Remotion output (gitignored)
│       │
│       ├── resource/
│       │   ├── bg-music/                  # Background music (organized by mode)
│       │   │   ├── standard/              # Mystery/cinematic tracks
│       │   │   ├── geography/             # Adventure/epic tracks
│       │   │   └── siete_niveles/         # Adventure/epic tracks
│       │   ├── fonts/                     # Auto-downloaded Montserrat fonts
│       │   └── reference/                 # Style reference images for Gemini
│       │
│       ├── out_short/                     # Output for short videos (9:16)
│       │   ├── ideas_tracking.csv         # State machine CSV
│       │   └── ideas/                     # Per-idea folders
│       └── out_long/                      # Output for long videos (16:9)
│
├── tools/
│   ├── text_generation/
│   │   └── gemini.py           # GeminiTextGenerator (JSON + raw + SRT translate)
│   ├── image_generation/
│   │   ├── gemini.py           # GeminiImageGenerator (batch, style refs)
│   │   ├── vertex_ai.py        # VertexAIImageGenerator (Imagen 3)
│   │   └── midjourney.py       # ImageTask model
│   ├── audio_generation/
│   │   ├── gemini.py           # GeminiAudioGenerator
│   │   ├── vertex_ai_tts.py    # VertexAIAudioGenerator (Studio TTS)
│   │   └── audio_tool.py       # Background music selector (per-mode)
│   ├── video_editing/
│   │   ├── ffmpeg.py           # FFmpegTool (concat, zoompan, subtitles, SFX, etc.)
│   │   ├── whisper.py          # WhisperTool (transcription, word tokens, SRT)
│   │   ├── whisper_schemas.py  # WhisperTranscription, WhisperToken models
│   │   └── remotion.py         # RemotionTool (renders via npx remotion render)
│   ├── video_generation/
│   │   ├── gemini.py           # GeminiVideoGenerator (Veo AI)
│   │   ├── pexels.py           # PexelsTool
│   │   └── pixabay.py          # PixabayTool
│   ├── social_media/
│   │   └── facebook.py         # FacebookTool (upload video, photo, captions, comments)
│   ├── common/
│   │   ├── gemini_base.py      # GeminiBase — shared API client with retry + usage tracking
│   │   ├── base_model.py       # BaseModelTool
│   │   ├── messenger.py        # Messenger — console log formatting
│   │   ├── cost_tracker.py     # CostTracker — tracks API spend per video
│   │   └── csv_processor.py    # CsvProcessor — generic CSV read/write
│   └── utils/
│       ├── text.py             # slugify, etc.
│       └── time.py             # retry decorator
│
└── models/                      # Whisper model files
    └── whisper/
```

---

## 5. Pipeline Step-by-Step

The pipeline has 8 steps (plus variant steps). Each step reads/writes the CSV state machine.

### State Machine
```
NEW → SCRIPT_GENERATED → IMAGES_GENERATED → CLIPS_GENERATED → AUDIO_GENERATED
  → VIDEO_GENERATED → VIDEO_PRO_SUBTITLED → VIDEO_MUSIC_GENERATED → COMPLETED → UPLOADED
```

**Files per step:**
```
idea_000001/
├── idea.json          # Idea metadata (title, hook, caption, etc.)
├── script.json        # Full script (scenes with narration, image_prompt, pexels_query, etc.)
├── images/
│   ├── scene_01.png   # Image for scene 1
│   ├── scene_02.png   # Image for scene 2
│   └── ...
├── clips/
│   ├── scene_01.mp4   # Video clip for scene 1
│   ├── scene_02.mp4   # Video clip for scene 2
│   └── ...
├── audios/
│   ├── scene_01.wav   # Audio narration for scene 1
│   ├── scene_02.wav   # Audio narration for scene 2
│   └── ...
├── videos/
│   ├── scene_01.mp4   # Composite (visual + audio) for scene 1
│   ├── scene_02.mp4   # Composite for scene 2
│   └── ...
└── editions/
    ├── raw_video.mp4           # All scenes concatenated
    ├── final_audio.wav         # Master audio
    ├── remotion_frames/        # Karaoke overlay frames (PNG sequence from Remotion)
    ├── pro_subtitled_video.mp4 # Final video with Remotion karaoke
    ├── final_video.mp4         # With background music
    └── thumbnail.jpg           # For Facebook upload
```

### Step 1: Generate Story & Script

**What it does:**
1. Picks a random focus area (e.g., "Cognitive Biases", "Hidden Animal Superpowers")
2. Generates an `idea` (title, hook, intrigue_header, caption) via Gemini with JSON output
3. Generates a full `script` (6-8 scenes for standard, 8 scenes for 7-levels)
4. **A/B Testing**: Creates a "Hook B" variant (alternative first scene) for double output
5. Saves both versions to CSV and disk

**Key files:**
- `pipeline.py:step1_generate_story()`
- `prompt_shorts/manager.py:generate_full_story()`
- `prompt_shorts/stories/constants.py` (standard prompts)
- `prompt_shorts/siete_niveles/constants.py` (7-levels prompts)

**Critical: Avoidance system**
Before generating, reads ALL past titles from `ideas_tracking.csv` and `automated_posts_history.csv` to avoid reposting similar content. This is handled by `DailyAutomator.get_recent_topics()`.

### Step 2: Generate Images

**What it does:**
1. Loads the script for the idea in `SCRIPT_GENERATED` state
2. Generates 1 image per scene using the scene's `image_prompt`
3. Uses either Gemini Imagen 3 (`gemini-3.1-flash-image-preview`) or Vertex AI Imagen (if `USE_VERTEX_AI_IMAGE=true`)
4. Saves as `scene_{NN}.png` in the `images/` subdir
5. Aspect ratio: 9:16 for shorts, 16:9 for longs

**Key files:**
- `pipeline.py:step2_generate_images()`
- `tools/image_generation/gemini.py`
- `tools/image_generation/vertex_ai.py`

**Important:** The Gemini image generator injects style reference images from `resource/reference/` as visual anchors for every scene.

### Step 2b: Generate Video Clips

**What it does:**
1. For each scene, tries to find a stock video matching `pexels_query`
2. Priority order: **Pexels API** → **Pixabay API** → **AI Image (Ken Burns)** → **Gradient placeholder**
3. For `map_3d` visual type, renders a Mapbox GL animation via Remotion (`MapRender.tsx`)
4. Saves as `scene_{NN}.mp4` in `clips/` subdir
5. Duration: 6 seconds per clip (later shortened to match narration)

**Key files:**
- `pipeline.py:step2b_generate_video_clips()`
- `tools/video_generation/pexels.py`
- `tools/video_generation/pixabay.py`

### Step 3: Generate Audio (TTS + Alignment)

**What it does:**
1. Processes scenes in batches of 15
2. Generates a single WAV file per batch via TTS (Gemini TTS or Vertex AI TTS)
3. Transcribes the batch audio with Whisper (word-level timestamps)
4. Uses Gemini to **align** Whisper segments to each scene (matching narrations)
5. Splits the batch audio into per-scene WAV files based on the alignment
6. **Slow down** Gemini TTS audio by 5% (atempo=0.95) for better pacing
7. Saves as `scene_{NN}.wav` in `audios/` subdir

**Key files:**
- `pipeline.py:step3_generate_audios()`
- `tools/audio_generation/gemini.py`
- `tools/audio_generation/vertex_ai_tts.py`
- `tools/video_editing/whisper.py`

### Step 4: Generate Scene Videos

**What it does:**
1. Loads the clips (or images), audio per scene, and SFX
2. **Mixes SFX** into each scene's audio (swoosh, mystery, tension sounds from `resource/sfx/`)
3. Concatenates all scene audios into a **Master Audio** (`final_audio.wav`)
4. For each scene, creates a composite video:
   - If source is a video clip: scales to fill 1080×1920, adds optional **glitch transition** (RGB shift + noise)
   - If source is an image: applies **Ken Burns zoom** + **cinematic color grade** + **vignette**
5. Concatenates all scene videos
6. Merges with Master Audio for perfect sync
7. Saves as `raw_video.mp4`

**Key files:**
- `pipeline.py:step4_generate_videos()`
- `tools/video_editing/ffmpeg.py:create_composite_scene_video()`

### Step 5 (PRO): Remotion Karaoke Subtitles

**What it does:**
1. Transcribes `final_audio.wav` with Whisper to get **word-level tokens** (word, start_ms, end_ms)
2. Creates `intrigue_header` for the video (shown at top)
3. For `siete_niveles` mode: builds `level_markers` array with nivel number, title, impact, timestamps
4. Writes all data to `remotion/data/input.json`
5. Runs `npx remotion render` with the `Subtitles` composition
6. This renders a **PNG sequence** (frames with word-by-word karaoke highlighting)
7. Overlays the frames on the raw video via FFmpeg
8. Saves as `pro_subtitled_video.mp4`

**Key files:**
- `pipeline.py:step5_pro_subtitles()`
- `tools/video_editing/remotion.py:render_subtitles()`
- `remotion/src/Subtitles.tsx` — the karaoke engine
- `remotion/src/Root.tsx` — registers the composition

### Step 5 (Standard): SRT Subtitles

Alternative: standard subtitles via FFmpeg `subtitles` filter (Impact font, white with black outline). Used as fallback. Not used in production — PRO is always preferred.

### Step 6: Background Music

**What it does:**
1. Picks a random background music file based on the pipeline **mode** (standard → mystery, siete_niveles → cinematic)
2. Uses **sidechain compression**: music volume automatically ducks when narration is active
3. Mixes at 15% volume
4. Saves as `final_video.mp4`

**Key files:**
- `pipeline.py:step6_add_background_music()`
- `tools/audio_generation/audio_tool.py`
- `tools/video_editing/ffmpeg.py:add_background_music()`

### Step 7: Rename & Cost Report

**What it does:**
1. Renames `final_video.mp4` to `{slugified_title}.mp4`
2. Prints the **cost report** for the video (text, image, audio costs in USD)

### Step 8: Upload to Facebook

**What it does:**
1. Generates AI description (random style: curious, direct, challenging, intriguing)
2. Extracts a thumbnail frame from the video (at ~15% duration)
3. Uploads video via Facebook Graph API (chunked upload — 10MB chunks)
4. Sets custom thumbnail on the published video
5. **Translates subtitles** to English via Gemini and uploads as English captions
6. Posts an **engagement auto-comment** (question to invite replies)
7. Marks idea as `UPLOADED`

---

## 6. Mode 1: Standard (Curiosity Reels)

**Script structure:** 6-8 scenes, each 5-7 seconds
**Total duration:** 50-75 seconds
**Narration:** 130-180 words total

The standard mode generates short, curiosity-driven videos with rapid scene changes. Each video explains a fascinating fact from beginning to end.

### Prompt Flow (standard mode):

1. `manager.py` picks a random focus area from ~50 topics (cognitive biases, animal superpowers, extreme survival, etc.)
2. Generates idea with `StoryIdea` model:
   - `title`: Creative hook title
   - `hook`: Scroll-stopping hook phrase
3. Generates script with `StoryHandler` model (6-8 scenes):
   - Each scene: `visual_type`, `image_prompt`, `pexels_query`, `narration`
   - Scene 1 must be a **brutal hook** (e.g., "Did you know your brain makes decisions 7 seconds BEFORE you're aware of them?")
   - Last scene must include a **CTA** (call-to-action)

### Key visual style for Standard:

Randomly picks from 6 color schemes and 5 compositions, plus 5 base styles:
- Hyper-realistic cinematic lighting, dark moody colors
- National Geographic documentary style
- Vintage anatomical sketch on aged parchment
- Dark digital art with neon accents
- Surreal fantasy realism with cosmic colors

---

## 7. Mode 2: "7 Levels" / Siete Niveles (English Version)

**THIS IS THE MAIN MODE you want to replicate.**

**Script structure:** EXACTLY 8 scenes: 1 INTRO + 7 LEVELS
**Progression:** Level 1 (interesting) → Level 7 (mind-blowing)
**Narration format:** Each scene starts with a level prefix

### Scene Structure:

| Scene | `scene_number` | `nivel` | Narration starts with |
|-------|---------------|---------|----------------------|
| Intro | 1 | 0 | The hook (no prefix) |
| Level 1 | 2 | 1 | "Level 1:" or "We start at level 1:" |
| Level 2 | 3 | 2 | "Moving up to level 2:" |
| Level 3 | 4 | 3 | "We've reached level 3:" |
| Level 4 | 5 | 4 | "Level 4 is even more impactful:" |
| Level 5 | 6 | 5 | "Level 5 is where things get really..." |
| Level 6 | 7 | 6 | "Level 6 takes us to the limit:" |
| Level 7 | 8 | 7 | "And we've reached the final level, level 7:" |

### Focus Areas for 7 Levels:

```
HIDDEN PLACES: Restricted access sites around the world
MYSTERIOUS ISLANDS: Remote islands with strange histories
EARTH'S HIDDEN SECRETS: Underground bunkers, lost cities, buried treasures
STRANGE BORDERS: Absurd geopolitical boundaries, enclaves, exclaves
ABANDONED CITIES: Ghost towns, devastated metropolises, frozen-in-time places
UNEXPLAINED PHENOMENA: Events science can't explain
IMPOSSIBLE CONSTRUCTIONS: Megaliths, pyramids, colossal structures
DANGEROUS PLACES: Lethal islands, cursed mountains, radioactive exclusion zones
ARCHAEOLOGICAL DISCOVERIES: Finds that rewrote history
UNSOLVED MYSTERIES: Open cases, indecipherable codes, lost expeditions
```

### To create the English "7 Levels" module, you need to:

**A. Create `prompt_shorts/seven_levels/` folder** with these files:

**`constants.py`**: Copy and translate from `siete_niveles/constants.py`:
- `IDEA_PROMPT_SEVEN_LEVELS` → English idea generator prompt
- `SCRIPT_PROMPT_SEVEN_LEVELS` → English script generator prompt
- `FOCUS_AREAS_SEVEN_LEVELS` → Same focus areas but in English
- `AUDIO_PROMPT_SEVEN_LEVELS` → English TTS prompt

**`models.py`**: Copy and translate (minimal changes):
- Rename `SieteNivelesIdea` → `SevenLevelsIdea`
- Rename `SieteNivelesScene` → `SevenLevelsScene`
- Rename `SieteNivelesHandler` → `SevenLevelsHandler`
- Field descriptions and level prefixes in English

**B. Register in `prompt_shorts/manager.py`:**
- Import `SevenLevelsHandler, SevenLevelsIdea`
- Add to `CATEGORIES` list
- Add `mode == "seven_levels"` branch in `generate_full_story()`

**C. Register in `pipeline.py`:**
- Add `"seven_levels"` to mode choices in `__init__` (just pass it through)
- Add `"seven_levels"` case in `load_script()` method (load `SevenLevelsHandler`)
- The word "seven_levels" or "7_levels" just needs to match the manager condition

**D. Register in `main.py`:**
- Add `"seven_levels"` to `--mode` choices

**E. Remotion auto-handles it**: In `step5_pro_subtitles()`, the code already checks `if self.mode == "siete_niveles"` to build `level_markers`. Just update this condition to also match your new mode name.

---

## 8. Remotion Subtitles System (Karaoke)

This is the **visual signature** of the videos. It renders word-by-word highlighted subtitles as an overlay.

### How it works:

1. **Whisper** transcribes the Master Audio and returns word-level tokens:
   ```json
   {"text": "Level", "start": 1234, "end": 1450}
   {"text": "1", "start": 1450, "end": 1650}
   ```

2. **Pipeline** writes these to `remotion/data/input.json`:
   ```json
   {
     "words": [...],
     "intrigueHeader": "HIDDEN PLACES",
     "levelMarkers": [
       {"nivel": 1, "titulo": "The Most Secret Base", "impacto": "Bajo", "startTime": 5500, "endTime": 10500}
     ]
   }
   ```

3. **Remotion** renders frames as PNG images:
   - **Word-by-word karaoke**: Each word highlights in gold as it's spoken, with a glowing underline
   - **Level Badge**: At the top of the screen (position: top 200px), shows "LEVEL 1/7" with a gradient based on impact:
     - Bajo (Low) → Green gradient
     - Medio (Medium) → Orange gradient
     - Alto (High) → Red gradient
     - Extremo (Extreme) → Purple gradient
   - **Level Title**: Below the badge, the nivel's title is shown
   - **Progress Bar**: At the bottom, a gold progress bar shows level progression

4. **FFmpeg** overlays the PNG sequence on the raw video

### Key visual constants for Subtitles.tsx:

```typescript
const BRAND = {
  gold: '#FFD700',
  goldLight: '#FFED4A',
  goldDark: '#B8860B',
  dark: '#0D0D0D',
  darkOverlay: 'rgba(13, 13, 13, 0.85)',
  panelBg: 'rgba(13, 13, 13, 0.75)',
  textPrimary: '#FFFFFF',
  textSecondary: '#B8B8B8',
  borderGlow: 'rgba(255, 215, 0, 0.3)',
};
```

**Important for English version:**
- The Subtitles.tsx file already works for any language — it displays whatever text Whisper returns
- The `NIVEL` text ("NIVEL 1/7") on the progress bar should be changed to "LEVEL 1/7"
- The level badge text needs translation (it's currently hardcoded in Spanish in Subtitles.tsx)

---

## 9. Background Music System

Music is organized by mode in subdirectories:
```
resource/bg-music/
├── standard/       # Mystery/cinematic tracks
├── siete_niveles/  # Adventure/cinematic tracks
├── geography/      # Adventure/epic tracks
└── stickman/       # Mystery/dark tracks
```

The `audio_tool.py` auto-downloads a Creative Commons MP3 from raw CDN if the subdirectory is empty.
**Source URLs:**
- Standard: `https://raw.githubusercontent.com/tannerhelland/free-music/master/mp3/Ominosity.mp3`
- Siete Niveles: `https://raw.githubusercontent.com/tannerhelland/free-music/master/mp3/Wild%20Waters.mp3`

For English version, you can use the same URL patterns — just add a `seven_levels` mode entry in `MODE_MUSIC_CONFIG`.

---

## 10. GitHub Actions CI/CD

The workflow in `.github/workflows/daily_post.yml`:

### Schedule
- Triggered by `workflow_dispatch` (manual via GitHub UI)
- Can be set on a cron schedule

### Workflow Steps:
1. Checkout code
2. Install Poetry + Python 3.11
3. Install Node.js 20 + Remotion deps (`npm ci`)
4. Install Linux dependencies (ffmpeg, Chrome libs for Remotion)
5. Install Python deps (`poetry install`)
6. Create GCP credentials from GitHub Secret
7. Run automation:
   - By default: **Video mode** (60% siete_niveles / 40% standard)
   - Optionally: Image mode
8. Commit and push tracking CSVs back to repo (for anti-repetition memory)

### Environment Variables (GitHub Secrets):
```
GEMINI_API_KEY
GEMINI_API_KEY_2
GCP_PROJECT_ID
GCP_LOCATION
GOOGLE_APPLICATION_CREDENTIALS_JSON
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_ACCESS_TOKEN
PEXELS_API_KEY
PIXABAY_API_KEY
```

### Automation Runner (`daily_automated_content.py`):

The `DailyAutomator` class:
1. **Cleanup**: Removes stuck/incomplete ideas (folders + CSV orphans)
2. **Video mode**: Runs the full pipeline (steps 1-8) with random mode selection
3. **Image mode**: Runs steps 1, 2, and 8_image (for standalone curiosity images)
4. **Syncs history**: Pushes CSV changes back to GitHub for persistence

---

## 11. Spanish → English Translation Map

### Code changes needed for English version:

| File | Change |
|------|--------|
| `prompt_shorts/siete_niveles/` → `prompt_shorts/seven_levels/` | Rename folder, translate all prompts to English |
| `prompt_shorts/siete_niveles/models.py` | Rename classes, translate level prefixes |
| `prompt_shorts/siete_niveles/constants.py` | Translate all prompts to English |
| `prompt_shorts/manager.py` | Add `seven_levels` mode, import new module |
| `pipeline.py` | Add `seven_levels` to `load_script()` mode check |
| `main.py` | Add `seven_levels` to mode choices |
| `pipeline.py:step5_pro_subtitles()` | Update `self.mode == "siete_niveles"` check |
| `Subtitles.tsx` | Change "NIVEL" to "LEVEL", "Nivel" to "Level" text |
| `audio_tool.py` | Add `seven_levels` to `MODE_MUSIC_CONFIG` |
| `audio_tool.py:get_random_audio()` | Mode routing already generic, just add config |
| `daily_automated_content.py` | Update mode weights/names for random selection |
| `.env.sample` | Change channel name references |
| `prompt_base/constants.py` | Translate alignment prompt |
| All prompts in `prompt_shorts/stories/constants.py` | If using standard mode, translate to English |

### Critical field translations needed:

The following descriptive texts must be changed from Spanish to English in the prompts:

- "Título creativo" → "Creative title"
- "Gancho de interrupción" → "Scroll-stopping hook"
- "Describe en INGLÉS" → "Describe in ENGLISH" (keeping the instruction in prompt language)
- "Narración para esta escena en ESPAÑOL" → "Narration for this scene in ENGLISH"

### Level prefix system (for `seven_levels/models.py`):

```python
NIVEL_PREFIXES = {
    0: ("",),
    1: ("Level 1:", "We start at level 1:"),
    2: ("Moving up to level 2:",),
    3: ("We've reached level 3:",),
    4: ("Level 4 is even more impactful:",),
    5: ("Level 5 is where things get really",),
    6: ("Level 6 takes us to the limit:",),
    7: ("And we've reached the final level, level 7:",),
}
```

---

## 12. Run Commands

### Local Development

```bash
# Full pipeline (steps 1-8) — Standard mode
poetry run python -m flows.image_content_generator.pipeline.main short all --mode standard

# Full pipeline — 7 Levels mode
poetry run python -m flows.image_content_generator.pipeline.main short all --mode siete_niveles

# Single steps (resumable):
poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode standard
poetry run python -m flows.image_content_generator.pipeline.main short step2 --mode standard
# ... step3 through step8

# With avoidance (prevent repeating topics):
poetry run python -m flows.image_content_generator.pipeline.main short all --mode standard --avoid "topic1, topic2"

# Daily automated runner:
poetry run python flows/image_content_generator/pipeline/daily_automated_content.py

# With environment override:
POST_TYPE=video MODE=siete_niveles poetry run python flows/image_content_generator/pipeline/daily_automated_content.py
```

### Using Make:
```bash
make icg-s-all              # Full pipeline (short, standard)
make icg-s-step1             # Step 1 only
make daily-mix               # Daily automated runner
```

---

## 13. Troubleshooting Tips

### Whisper crashes/loops:
Set `condition_on_previous_text=False` in the `transcribe()` call (already done).

### Remotion rendering fails:
- Ensure Node.js ≥ 20 is installed
- Run `npm ci` in the remotion directory
- Check for dots in file paths (Remotion breaks on paths containing `.`)
- The `remotion.py` tool has a workaround using temp directories

### Facebook upload fails:
- The upload uses **chunked (resumable)** API with 10MB chunks
- Implements exponential backoff (4 attempts)
- If uploading large videos, make sure the video file is under 10 minutes (Facebook Reels limit)
- For Reels, ensure video is 9:16 aspect ratio and under 60 seconds (or 3 minutes if longer format)

### State machine gets stuck:
- Delete the idea's folder and the CSV row manually
- Or use the cleanup script in `daily_automated_content.py:cleanup_stuck_ideas()`

### Gemini rate limits:
- Images: 10-second delay between calls (built in)
- Text: 3 retries with exponential backoff (built in `gemini_base.py`)

### Audio alignment fails:
- The pipeline processes in batches of 15 scenes
- If alignment count doesn't match expected count, the batch is deleted and retried
- If it keeps failing, reduce `BATCH_SIZE` in `pipeline.py`

---

## 14. Quick Start Checklist

- [ ] Clone repo and install dependencies
- [ ] Get all API keys (Gemini, GCP, Pexels, Pixabay, Facebook)
- [ ] Create `.env` with all keys
- [ ] Install Whisper model (downloads on first use)
- [ ] Install Remotion deps (`npm ci` in remotion/ dir)
- [ ] Test step 1: `poetry run python -m flows.image_content_generator.pipeline.main short step1 --mode standard`
- [ ] Test full pipeline: `make icg-s-all`
- [ ] Configure GitHub Actions secrets
- [ ] Create `seven_levels` module (translate from `siete_niveles`)
- [ ] Change "NIVEL" text to "LEVEL" in Subtitles.tsx
- [ ] Push and trigger GitHub Actions

---

**Final note:** The most complex part is the Remotion Subtitles.tsx file (622 lines of React/TypeScript). Everything else is straightforward Python. The subtitles system handles:
- Word-by-word karaoke with spring animations
- Level badges with impact-colored gradients
- Progress bar with pulse animation
- Intrigue header overlay
- Background panel with backdrop blur

This file requires **zero changes for the English version** — it only displays the text you feed it. The only text change needed is "NIVEL" → "LEVEL" in the progress bar component.
