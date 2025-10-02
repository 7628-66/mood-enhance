import os
import sys
import argparse
import random
import json
import pyjokes
from typing import Optional

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

OFFLINE_CONTENT_PATH = os.path.join(os.path.dirname(__file__), "offline_content.json")

# ---------------------- Offline AI Data ---------------------- #
_offline_data: dict = {}
if os.path.exists(OFFLINE_CONTENT_PATH):
    try:
        with open(OFFLINE_CONTENT_PATH, "r", encoding="utf-8") as f:
            _offline_data = json.load(f)
    except Exception:
        _offline_data = {}


def offline_ai(type_: str) -> Optional[str]:
    bucket = _offline_data.get(type_, [])
    if bucket:
        return random.choice(bucket)
    if type_ == "jokes":
        return pyjokes.get_joke()
    if type_ == "encouragements":
        return "You matter, and this moment will pass. One small act of self-kindness can help."
    return None

# ---------------------- AI Support ---------------------- #
class AIClient:
    """Thin wrapper so the rest of code can stay simple.
    Provides real API call OR offline simulated responses based on flags.
    """

    def __init__(self, use_real: bool, use_offline: bool) -> None:
        self.mode = "none"
        self._client = None
        api_key = os.getenv("OPENAI_API_KEY")
        force_no = os.getenv("MOOD_FORCE_NO_AI") == "1"
        offline_env = os.getenv("MOOD_OFFLINE_AI") == "1"
        if force_no:
            self.mode = "none"
            return
        if use_offline or offline_env:
            self.mode = "offline"
            return
        if use_real and api_key and OpenAI:
            try:
                self._client = OpenAI()
                self.mode = "real"
            except Exception:
                self.mode = "none"

    @property
    def enabled(self) -> bool:
        return self.mode in {"real", "offline"}

    def get_joke(self) -> Optional[str]:
        if self.mode == "offline":
            return offline_ai("jokes")
        if self.mode == "real" and self._client:
            try:
                resp = self._client.responses.create(  # type: ignore[attr-defined]
                    model="gpt-5",  # Placeholder model
                    input="Tell me a funny, family-friendly short joke."
                )
                return getattr(resp, "output_text", None)
            except Exception:
                return None
        return None

    def get_encouragement(self) -> Optional[str]:
        if self.mode == "offline":
            return offline_ai("encouragements")
        if self.mode == "real" and self._client:
            try:
                resp = self._client.responses.create(  # type: ignore[attr-defined]
                    model="gpt-5",
                    input=(
                        "Say something supportive, kind, and uplifting for someone feeling sad. "
                        "Keep it short and friendly."
                    ),
                )
                return getattr(resp, "output_text", None)
            except Exception:
                return None
        return None

# ---------------------- Data ---------------------- #
affirmations = [
    "💪 You are stronger than you think.",
    "🌎 The world is better with you in it.",
    "👣 One step at a time, you’re moving forward.",
    "💙 You are enough, just as you are.",
    "🌸 Your story matters, and so do you.",
    "🌈 You’ve survived 100% of your hardest days so far.",
    "🙌 Keep your head up. Brighter days are ahead.",
]

songs = {
    "great": [
        "🎵 Happy — Pharrell Williams",
        "🎵 Here Comes the Sun — The Beatles",
        "🎵 Good Life — OneRepublic",
    ],
    "soso": [
        "🎵 Count on Me — Bruno Mars",
        "🎵 Unwritten — Natasha Bedingfield",
        "🎵 Lovely Day — Bill Withers",
    ],
    "down": [
        "🎵 Three Little Birds — Bob Marley",
        "🎵 What a Wonderful World — Louis Armstrong",
        "🎵 Fight Song — Rachel Platten",
    ],
}

# ---------------------- Utility ---------------------- #
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"
    RED = "\033[31m"

def c(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{Color.RESET}"

# ---------------------- Core Logic ---------------------- #

def handle_great(ai_client: AIClient) -> None:
    print(c("😃 Love the energy! Let’s keep it going!\n", Color.GREEN))
    ai_text = ai_client.get_joke() if ai_client.enabled else None
    if ai_text:
        label = "AI" if ai_client.mode == "real" else "Offline AI"
        print(f"😂 {label} Joke:", ai_text)
    else:
        print("😂 Classic Joke:", pyjokes.get_joke())
    print("😂 Bonus Joke:", pyjokes.get_joke())
    print("\n🎶 Song of the Day:", random.choice(songs["great"]))

def handle_soso(ai_client: AIClient) -> None:
    print(c("🙂 Thanks for sharing. Let’s mix it up with a joke + affirmation!\n", Color.CYAN))
    print("😂", pyjokes.get_joke())
    print("🌟", random.choice(affirmations))
    print("\n🎶 Song of the Day:", random.choice(songs["soso"]))

def handle_down(ai_client: AIClient) -> None:
    print(c("💜 Sorry you’re feeling low. Let’s lift you up:\n", Color.MAGENTA))
    ai_text = ai_client.get_encouragement() if ai_client.enabled else None
    if ai_text:
        label = "AI" if ai_client.mode == "real" else "Offline AI"
        print(f"🌟 {label} Support:", ai_text)
    else:
        print("🌟 You matter, and this moment will pass. One small act of self-kindness right now can help.")
    print("😂", pyjokes.get_joke())
    print("😂", pyjokes.get_joke())
    print("🙌 Keep your head up. Brighter days are ahead.")
    print("\n🎶 Song of the Day:", random.choice(songs["down"]))

def handle_other(ai_client: AIClient) -> None:
    print(c("🤝 Thanks for sharing. Here’s something for you:\n", Color.YELLOW))
    print("🌟", random.choice(affirmations))
    print("\n🎶 Song of the Day:", "🎵 Keep your Head Up — Andy Grammer")

# ---------------------- CLI ---------------------- #

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mood Booster App")
    parser.add_argument("--mood", "-m", help="Provide mood non-interactively (great|so-so|down|sad|ok)")
    parser.add_argument("--ai", action="store_true", help="Enable REAL AI (requires OPENAI_API_KEY)")
    parser.add_argument("--offline-ai", action="store_true", help="Use offline simulated AI content")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    parser.add_argument("--debug-ai", action="store_true", help="Show AI mode debug info")
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.no_color:
        def plain(text: str, _color: str) -> str:  # type: ignore
            return text
        globals()["c"] = plain  # type: ignore

    # Instantiate AI client respecting both flags and env overrides
    ai_client = AIClient(use_real=args.ai, use_offline=args.offline_ai)

    mood = args.mood.lower() if args.mood else None
    if not mood:
        print("\n--- Mood Booster App ---")
        mood = input("How are you feeling today? (😀 great / 😐 so-so / 😔 down): ").lower()
        print("\n")

    if "great" in mood:
        handle_great(ai_client)
    elif any(key in mood for key in ("so", "ok")):
        handle_soso(ai_client)
    elif any(key in mood for key in ("down", "sad")):
        handle_down(ai_client)
    else:
        handle_other(ai_client)

    print("\n💌 Remember: however you feel, you matter. One step at a time ❤️")

    if args.debug_ai:
        print(f"\n[debug] AI mode: {ai_client.mode}")
        if ai_client.mode == "real" and not os.getenv("OPENAI_API_KEY"):
            print("[debug] Warning: mode real but no OPENAI_API_KEY detected.")

    if ai_client.mode == "none" and args.ai:
        print(c("\n(Info) Real AI requested but unavailable (missing key or init failed).", Color.BLUE))
    if ai_client.mode == "offline" and args.ai:
        print(c("\n(Info) Real AI requested; using offline simulation instead.", Color.BLUE))

    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))


