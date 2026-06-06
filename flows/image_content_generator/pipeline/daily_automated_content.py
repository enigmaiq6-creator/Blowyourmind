import os
import sys
import random
import subprocess
from pathlib import Path
from dotenv import load_dotenv

from tools.common.messenger import Messenger
from tools.text_generation.gemini import GeminiTextGenerator
from tools.social_media.facebook import FacebookTool
import time

load_dotenv()

class DailyAutomator:
    def __init__(self):
        self.text_gen = GeminiTextGenerator()
        self.out_dir = Path("flows/image_content_generator/out_short/daily_content")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = Path("flows/image_content_generator/out_short/automated_posts_history.csv")
        if not self.history_file.exists():
            self.history_file.write_text("date,type,topic\n")

    def get_recent_topics(self) -> str:
        import pandas as pd
        topics = []
        # 1. Get automated posts history
        if self.history_file.exists():
            try:
                df_auto = pd.read_csv(self.history_file)
                topics.extend(df_auto["topic"].tolist())
            except Exception:
                pass
        
        # 2. Get video titles history
        video_csv = Path("flows/image_content_generator/out_short/ideas_tracking.csv")
        if video_csv.exists():
            try:
                df_video = pd.read_csv(video_csv)
                topics.extend(df_video["title"].tolist())
            except Exception:
                pass
            
        if not topics:
            return ""
        
        # Deduplicate and format
        unique_topics = list(set([str(t).strip() for t in topics if str(t).strip()]))
        # Pass up to 250 topics (enough memory without breaking CLI limits)
        avoid_list = "\n- ".join(unique_topics[-250:]) 
        
        return f"\n\n**CRITICAL - ANTI-REPETITION RULES:**\nDO NOT repeat, reuse or get inspired by the following themes, metaphors or titles (THEY ARE ALREADY POSTED):\n- {avoid_list}\n\nBe creative. EXPLORE NEW VISUAL TERRITORIES."


    def sync_to_github(self):
        """
        Commits and pushes the history files back to GitHub to persist memory between runs.
        """
        if os.getenv("GITHUB_ACTIONS"):
            Messenger.info("🚀 Running in GitHub Actions: Skipping internal git sync (handled by workflow).")
            return

        try:
            # Files to track
            files_to_sync = [
                str(self.history_file),
                "flows/image_content_generator/out_short/ideas_tracking.csv"
            ]
            
            # Check which files exist before adding
            existing_files = [f for f in files_to_sync if Path(f).exists()]
            
            if not existing_files:
                Messenger.warning("⚠️ No history files found to sync.")
                return

            # Git commands
            subprocess.run(["git", "config", "--global", "user.name", "Automated Bot"], check=True)
            subprocess.run(["git", "config", "--global", "user.email", "bot@automation.com"], check=True)
            
            for f in existing_files:
                subprocess.run(["git", "add", "-f", f], check=True)
            
            # Check if there are STAGED changes to commit
            staged = subprocess.run(["git", "diff", "--cached", "--quiet"])
            if staged.returncode == 0:
                Messenger.info("✨ No staged changes in history to sync.")
                return

            subprocess.run(["git", "commit", "-m", "chore: update post history and state [skip ci]"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            Messenger.success("✅ History successfully synced to GitHub!")
        except Exception as e:
            Messenger.error(f"❌ Failed to sync to GitHub: {e}")

    def log_post(self, post_type: str, topic: str):
        from datetime import datetime
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()},{post_type},{topic.replace(',', ' ')}\n")

    def _pick_mode(self) -> str:
        """
        Picks a mode based on weights when MODE env var is not set.
        Format: MODE_WEIGHTS=geography=0.3,seven_levels=0.5,standard=0.2
        Defaults: geography=0.3, seven_levels=0.5, standard=0.2
        """
        explicit_mode = os.getenv("MODE", "").lower().strip()
        if explicit_mode:
            return explicit_mode

        weights_str = os.getenv("MODE_WEIGHTS", "geography=0.3,seven_levels=0.5,standard=0.2")
        try:
            import random
            pairs = [p.strip().split("=") for p in weights_str.split(",")]
            modes = [p[0].strip() for p in pairs]
            weights = [float(p[1].strip()) for p in pairs]
            return random.choices(modes, weights=weights, k=1)[0]
        except Exception as e:
            Messenger.warning(f"Invalid MODE_WEIGHTS '{weights_str}': {e}. Falling back to geography.")
            return "geography"

    def run_daily_mix(self):
        """
        Main entry point for GitHub Actions.
        Generates a video using weighted random mode selection.
        Set MODE env var to force a specific mode, or MODE_WEIGHTS to customize probabilities.
        """
        env_mode = self._pick_mode()

        if env_mode == "seven_levels":
            mode_label = "7 Levels"
        elif env_mode == "geography":
            mode_label = "Geography Reel"
        elif env_mode == "standard":
            mode_label = "Standard"
        else:
            mode_label = env_mode.upper()

        Messenger.info(f"🎬 GENERATING NEW {mode_label} VIDEO (Full Pipeline)...")
        self.cleanup_stuck_ideas()

        avoid_msg = self.get_recent_topics()
        try:
            cmd = [sys.executable, "-m", "flows.image_content_generator.pipeline.main", "short", "all", "--avoid", avoid_msg, "--mode", env_mode]
            subprocess.run(cmd, check=True)
            Messenger.success(f"✅ {mode_label} video completed!")
            self.log_post("video", f"{mode_label} Video")
            self.sync_to_github()
        except Exception as e:
            Messenger.error(f"Error during video task: {e}")
            sys.exit(1)


    def cleanup_stuck_ideas(self):
        """
        Cleans up incomplete ideas to prevent redundancy.
        """
        Messenger.info("🧹 Cleaning up stuck or incomplete ideas...")
        ideas_dir = Path("flows/image_content_generator/out_short/ideas")
        if not ideas_dir.exists():
            return

        import shutil
        video_csv = Path("flows/image_content_generator/out_short/ideas_tracking.csv")
        if not video_csv.exists():
            return

        try:
            import pandas as pd
            df = pd.read_csv(video_csv)
            # Solo mantenemos como "seguros" los que ya están terminados o subidos
            # Esto evita que ideas "atrapadas" en estados intermedios bloqueen nuevas ejecuciones
            safe_states = ["UPLOADED", "COMPLETED"]
            valid_ids = df[df["state"].isin(safe_states)]["id"].tolist()
            
            for idea_path in ideas_dir.iterdir():
                if idea_path.is_dir():
                    try:
                        idea_id = int(idea_path.name.split("_")[-1])
                        if idea_id not in valid_ids:
                            Messenger.warning(f"🗑️ Deleting stuck idea: {idea_path.name}")
                            shutil.rmtree(idea_path)
                    except (ValueError, IndexError):
                        pass
        except Exception as e:
            Messenger.warning(f"Could not parse tracking CSV for cleanup: {e}")

if __name__ == "__main__":
    automator = DailyAutomator()
    automator.run_daily_mix()
