# Mood Booster App

A tiny interactive CLI and Streamlit web app for boosting mood with jokes, affirmations, and song suggestions. Supports three AI modes:
- No AI (default, free, offline)
- Offline simulated AI (predefined curated lines)
- Real AI (OpenAI API, optional and guarded)

## New AI Modes & Controls
CLI Flags:
- `--ai` Enable real AI (requires `OPENAI_API_KEY`)
- `--offline-ai` Use offline simulated AI pool
- `--debug-ai` Show AI mode diagnostics
- `--mood` Provide mood non-interactively
- `--no-color` Disable colored output

Environment Variables:
- `OPENAI_API_KEY` Real API access (only used with `--ai`)
- `MOOD_FORCE_NO_AI=1` Force-disable any AI (overrides flags)
- `MOOD_OFFLINE_AI=1` Force offline simulated AI even if `--ai` given

Offline Content: `offline_content.json` contains curated `jokes` and `encouragements` used when offline AI mode is active.

## Install
Python 3.8+
```bash
pip install -r requirements.txt
```

## CLI Examples
```bash
# Pure offline (default)
python Jokes.py --mood great

# Explicit offline simulated AI
env MOOD_OFFLINE_AI=1 python Jokes.py --mood down --offline-ai

# Real AI (if key):
export OPENAI_API_KEY="sk-your-key" && python Jokes.py --mood great --ai

# Debug info
python Jokes.py --mood great --ai --debug-ai
```

## Streamlit Web App
```bash
streamlit run streamlit_app.py
```
Sidebar options let you choose AI mode: None / Offline / Real. Real mode requires you to paste a key (not stored). Offline mode uses the bundled JSON.

## Tests
```bash
pytest -q
```

## Files
```
Jokes.py             # CLI app with AI modes
streamlit_app.py     # Streamlit interface
offline_content.json # Offline AI simulation data
requirements.txt     # Dependencies
README.md            # Documentation
test_app.py          # Basic tests
.github/workflows/ci.yml # CI pipeline
LICENSE              # MIT license
```

## Notes on Real AI
The code still references a placeholder model (`gpt-5`) inside try/except. Replace with a valid model & method if you have access (example: chat completions). If calls fail, it silently falls back.

## Security
- No API key is stored in repo.
- Streamlit key entry is session-only.
- Use `MOOD_FORCE_NO_AI=1` for guaranteed no outbound calls.

## Roadmap Ideas
- Add caching layer for real AI responses
- Add mood history chart (Streamlit)
- Dockerfile for container deployment
- JSON export flag (`--json`)

MIT Licensed. Have fun uplifting people. ❤️
