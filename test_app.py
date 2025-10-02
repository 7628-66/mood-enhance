import subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "Jokes.py"


def run(mood: str):
    # Default mode now has no AI; we pass --no-color to simplify assertions
    cmd = [sys.executable, str(SCRIPT), "--mood", mood, "--no-color"]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=20)


def test_great():
    r = run("great")
    assert r.returncode == 0
    assert "Song of the Day" in r.stdout


def test_down():
    r = run("down")
    assert r.returncode == 0
    # Either fallback encouragement or song mention
    assert ("One small act of self-kindness" in r.stdout) or ("Song of the Day" in r.stdout)


def test_other():
    r = run("meh")
    assert r.returncode == 0
    assert ("You matter" in r.stdout) or ("Head Up" in r.stdout)
