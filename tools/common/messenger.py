from pydantic import BaseModel


class Messenger(BaseModel):
    """
    Standardized tool for terminal feedback.
    Rules:
    - info: No emoji.
    - success: ✅ emoji (for minor actions).
    - step_success: 🚀 emoji (for major pipeline steps).
    - warning: ⚠️ emoji.
    - error: ❌ emoji.
    """

    @staticmethod
    def _safe_print(msg: str) -> None:
        try:
            print(msg, flush=True)
        except UnicodeEncodeError:
            # Fallback for Windows consoles without UTF-8 support
            print(msg.encode("ascii", "ignore").decode("ascii"), flush=True)

    @staticmethod
    def info(message: str) -> None:
        Messenger._safe_print(message)

    @staticmethod
    def success(message: str) -> None:
        Messenger._safe_print(f"🚀 {message}")

    @staticmethod
    def step_success(message: str) -> None:
        Messenger._safe_print(f"✅ {message}")

    @staticmethod
    def warning(message: str) -> None:
        Messenger._safe_print(f"⚠️ {message}")

    @staticmethod
    def error(message: str) -> None:
        Messenger._safe_print(f"❌ {message}")

    @staticmethod
    def image(message: str) -> None:
        Messenger._safe_print(f"🖼️ {message}")

    @staticmethod
    def audio(message: str) -> None:
        Messenger._safe_print(f"🔊 {message}")

    @staticmethod
    def usage(model: str, prompt: int, thoughts: int, output: int, total: int) -> None:
        Messenger._safe_print(f"\n📊 [Usage Report: {model}]")
        Messenger._safe_print(f"   ├─ Prompt: {prompt}")
        Messenger._safe_print(f"   ├─ Thoughts: {thoughts}")
        Messenger._safe_print(f"   ├─ Output: {output}")
        Messenger._safe_print(f"   └─ Total Tokens: {total}\n")
