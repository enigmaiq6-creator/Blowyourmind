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
        
        self.tracking_dir = Path("flows/image_content_generator/tracking")
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.tracking_dir / "automated_posts_history.csv"
        if not self.history_file.exists():
            self.history_file.write_text("date,type,topic\n")

    def get_recent_topics(self) -> str:
        """
        Extrae un historial exhaustivo de títulos y conceptos ya publicados
        para alimentar la regla estricta de anti-repetición de Gemini.
        """
        import pandas as pd
        topics = []
        
        # 1. Títulos reales desde ideas_tracking.csv
        video_csv = self.tracking_dir / "ideas_tracking.csv"
        if video_csv.exists():
            try:
                df_video = pd.read_csv(video_csv)
                for t in df_video["title"].dropna().tolist():
                    t_clean = str(t).replace("[Hook B]", "").strip()
                    if t_clean and len(t_clean) > 4:
                        topics.append(t_clean)
            except Exception:
                pass
        
        # 2. Historial de publicaciones automáticas (excluyendo placeholders genéricos)
        if self.history_file.exists():
            try:
                df_auto = pd.read_csv(self.history_file)
                generic_labels = ["Finance Video", "What If Video", "Geography Reel Video", "What If Scenario Video"]
                for t in df_auto["topic"].dropna().tolist():
                    t_str = str(t).strip()
                    if t_str and t_str not in generic_labels:
                        topics.append(t_str)
            except Exception:
                pass
            
        if not topics:
            return ""
        
        # Deduplicar preservando orden y tomar los 100 más recientes
        unique_topics = list(dict.fromkeys(topics))[-100:]
        avoid_list = "\n- ".join(unique_topics)
        
        return f"\n\n**CRITICAL - ANTI-REPETITION RULES:**\nDO NOT repeat, reuse or get inspired by the following themes, metaphors or titles (THEY ARE ALREADY POSTED):\n- {avoid_list}\n\nBe creative. EXPLORE NEW VISUAL TERRITORIES."

    def sync_to_github(self):
        """
        Commits and pushes the history files back to GitHub to persist memory between runs.
        """
        if os.getenv("GITHUB_ACTIONS"):
            Messenger.info("🚀 Running in GitHub Actions: Skipping internal git sync (handled by workflow).")
            return

        try:
            files_to_sync = [
                str(self.history_file),
                str(self.tracking_dir / "ideas_tracking.csv"),
            ]
            
            existing_files = [f for f in files_to_sync if Path(f).exists()]
            if not existing_files:
                Messenger.warning("⚠️ No history files found to sync.")
                return

            subprocess.run(["git", "config", "--global", "user.name", "Automated Bot"], check=True)
            subprocess.run(["git", "config", "--global", "user.email", "bot@automation.com"], check=True)
            
            for f in existing_files:
                subprocess.run(["git", "add", "-f", f], check=True)
            
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

    def determine_mode(self) -> str:
        """
        Determina el modo de contenido de forma dinámica:
        Si se especifica CONTENT_MODE en entorno, se usa.
        De lo contrario, alterna inteligentemente entre 'finance' y 'fact_split'.
        """
        env_mode = os.getenv("CONTENT_MODE", "auto").strip().lower()
        if env_mode in ["finance", "fact_split"]:
            return env_mode

        # Modo automático: Alternar con sesgo 60/40 para variedad
        return random.choices(["finance", "fact_split"], weights=[0.6, 0.4])[0]

    def run_daily_mix(self):
        """
        Punto de entrada principal de automatización.
        Ejecuta el pipeline con selección dinámica de formato y estética.
        """
        selected_mode = self.determine_mode()
        Messenger.info(f"🎬 GENERATING NEW VIDEO (Mode: {selected_mode.upper()})...")
        self.cleanup_stuck_ideas()

        avoid_msg = self.get_recent_topics()
        try:
            cmd = [
                sys.executable, "-m", "flows.image_content_generator.pipeline.main",
                "short", "all",
                "--avoid", avoid_msg,
                "--mode", selected_mode
            ]
            subprocess.run(cmd, check=True)
            Messenger.success(f"✅ Video completed successfully!")

            # Obtener el título real de la idea recién generada y subida
            real_title = f"{selected_mode.title()} Video"
            try:
                import pandas as pd
                video_csv = self.tracking_dir / "ideas_tracking.csv"
                if video_csv.exists():
                    df = pd.read_csv(video_csv)
                    if not df.empty:
                        last_row = df.iloc[-1]
                        real_title = str(last_row.get("title", real_title)).replace("[Hook B]", "").strip()
            except Exception:
                pass

            self.log_post("video", real_title)
            self.sync_to_github()
        except Exception as e:
            Messenger.error(f"Error during video task: {e}")
            sys.exit(1)

    def cleanup_stuck_ideas(self):
        """
        Limpia ideas incompletas para prevenir redundancia.
        """
        Messenger.info("🧹 Cleaning up stuck or incomplete ideas...")
        ideas_dir = Path("flows/image_content_generator/out_short/ideas")
        if not ideas_dir.exists():
            return

        import shutil
        video_csv = self.tracking_dir / "ideas_tracking.csv"
        if not video_csv.exists():
            return

        try:
            import pandas as pd
            df = pd.read_csv(video_csv)
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
