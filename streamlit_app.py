import os
import random
import json
import pyjokes
import streamlit as st
from typing import Optional

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

OFFLINE_CONTENT_PATH = os.path.join(os.path.dirname(__file__), "offline_content.json")
_offline_data = {}
if os.path.exists(OFFLINE_CONTENT_PATH):
    try:
        with open(OFFLINE_CONTENT_PATH, "r", encoding="utf-8") as f:
            _offline_data = json.load(f)
    except Exception:
        _offline_data = {}

def offline_ai(kind: str):
    bucket = _offline_data.get(kind, [])
    if bucket:
        return random.choice(bucket)
    if kind == "jokes":
        return pyjokes.get_joke()
    if kind == "encouragements":
        return "You matter, and this moment will pass. One small act of self-kindness can help."
    return None

# ---------------------- Config ---------------------- #
st.set_page_config(page_title="Mood Booster App", page_icon="😊", layout="centered")

st.title("😊 Mood Booster App")
st.caption("Jokes · Affirmations · Uplift · Song suggestions")

# ---------------------- Session AI Client Wrapper ---------------------- #
class AIClient:
    def __init__(self, mode: str, api_key: Optional[str]):
        self.mode = mode  # none | offline | real
        self._client = None
        if self.mode == "real" and api_key and OpenAI:
            try:
                os.environ["OPENAI_API_KEY"] = api_key
                self._client = OpenAI()
            except Exception:
                self.mode = "none"

    def get_joke(self):
        if self.mode == "offline":
            return offline_ai("jokes")
        if self.mode == "real" and self._client:
            try:
                resp = self._client.responses.create(  # type: ignore[attr-defined]
                    model="gpt-5",
                    input="Tell me a funny, family-friendly short joke."
                )
                return getattr(resp, "output_text", None)
            except Exception:
                return None
        return None

    def get_encouragement(self):
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
    "other": ["🎵 Keep your Head Up — Andy Grammer"],
}

# ---------------------- Sidebar Inputs ---------------------- #
st.sidebar.header("Your Input")
mood = st.sidebar.radio(
    "How are you feeling today?",
    options=["great", "so-so", "down", "other"],
    index=0,
)

api_key_input = st.sidebar.text_input(
    "OpenAI API Key (optional)",
    type="password",
    help="Not stored. Provide only if using real AI mode.",
)

ai_mode = st.sidebar.selectbox(
    "AI Mode",
    options=["none", "offline", "real"],
    format_func=lambda x: {"none": "No AI", "offline": "Offline Simulated", "real": "Real API"}[x],
    index=0,
)
show_affirmation = st.sidebar.checkbox("Show an affirmation", value=True)
extra_joke = st.sidebar.checkbox("Extra joke", value=False)
show_debug = st.sidebar.checkbox("Debug info", value=False)

# Cache the AI client per session+key
if "_ai_mode" not in st.session_state or st.session_state._ai_mode != ai_mode or st.session_state.get("_api_key") != api_key_input:
    st.session_state._ai_mode = ai_mode
    st.session_state._api_key = api_key_input
    st.session_state.ai_client = AIClient(ai_mode, api_key_input if ai_mode == "real" else None)

ai_client = st.session_state.ai_client  # type: ignore

# ---------------------- Core UI Logic ---------------------- #
st.subheader(f"Mood: {mood}")

ai_text = None
if ai_client.mode == "real" and api_key_input:
    if mood == "great":
        ai_text = ai_client.get_joke()
    elif mood == "down":
        ai_text = ai_client.get_encouragement()
elif ai_client.mode == "offline":
    if mood == "great":
        ai_text = ai_client.get_joke()
    elif mood == "down":
        ai_text = ai_client.get_encouragement()

if ai_text:
    label = "Real AI" if ai_client.mode == "real" else "Offline AI"
    st.success(f"{label}: {ai_text}")

if ai_client.mode == "real" and not api_key_input:
    st.info("Provide an API key to enable real AI mode or switch to offline.")
if ai_client.mode == "real" and api_key_input and not ai_text:
    st.warning("AI response not available (model placeholder or error).")
if ai_client.mode == "offline" and not ai_text:
    st.info("Offline AI pool empty? Using classic jokes.")

# Jokes logic
st.write("### 😂 Joke")
st.write(pyjokes.get_joke())
if mood == "down":
    st.write(pyjokes.get_joke())
if extra_joke:
    st.write(pyjokes.get_joke())

# Affirmation
if show_affirmation:
    st.write("### 🌟 Affirmation")
    if mood == "down" and not ai_text:
        st.write("You matter, and this moment will pass. One small act of self-kindness can help.")
    else:
        st.write(random.choice(affirmations))

# Song suggestion
st.write("### 🎶 Song Suggestion")
if mood in ("great", "so-so", "down"):
    mapping = {"so-so": "soso"}
    key = mapping.get(mood, mood)
    st.write(random.choice(songs[key]))
else:
    st.write(songs["other"][0])

# Footer / info
st.markdown("---")
st.caption("💌 However you feel, you matter. One step at a time ❤️")

if show_debug:
    st.code(f"AI mode: {ai_client.mode}\nAPI key provided: {bool(api_key_input)}")
