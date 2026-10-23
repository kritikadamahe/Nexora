"""Guards for reproducibility and secret hygiene."""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import REPO_ROOT

# import-name -> distribution name, for the packages Nexora imports directly
REQUIRED_DISTRIBUTIONS = {
    "pandas", "numpy", "fastapi", "uvicorn", "pydantic", "python-dotenv", "xgboost",
    "scikit-learn", "joblib", "shap", "mlxtend", "vaderSentiment", "praw", "requests", "groq",
}


def _declared(path):
    names = set()
    for line in (REPO_ROOT / path).read_text().splitlines():
        line = line.split("#")[0].strip()
        if line:
            names.add(re.split(r"[<>=!~\[ ]", line, maxsplit=1)[0].lower().replace("_", "-"))
    return names


def test_requirements_declare_every_directly_imported_package():
    declared = _declared("requirements.txt")
    missing = {d for d in REQUIRED_DISTRIBUTIONS if d.lower().replace("_", "-") not in declared}
    assert not missing, f"undeclared dependencies: {missing}"


def test_requirements_do_not_pin_windows_only_packages():
    assert "colorama" not in _declared("requirements.txt")


def _tracked_files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True,
                             text=True, check=True).stdout.splitlines()
    except Exception:
        pytest.skip("not a git checkout")
    return out


def test_no_env_files_or_virtualenvs_are_tracked():
    bad = [f for f in _tracked_files()
           if Path(f).name == ".env" or (Path(f).name.startswith(".env.") and Path(f).name != ".env.example")
           or "/venv/" in f or f.startswith(("venv/", ".venv/"))]
    assert bad == []


def test_env_example_contains_no_secret_values():
    for line in (REPO_ROOT / ".env.example").read_text().splitlines():
        if line.startswith(("GROQ_API_KEY", "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET")):
            assert line.split("=", 1)[1].strip() == ""


def test_no_obvious_api_keys_in_tracked_source():
    pattern = re.compile(r"gsk_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}")
    for f in _tracked_files():
        if f.endswith((".py", ".md", ".txt", ".ini", ".example")):
            assert not pattern.search((REPO_ROOT / f).read_text(errors="ignore")), f
