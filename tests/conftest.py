"""
Shared test fixtures.

Safety rules for every test in this suite:
  * No test may call a real LLM or Reddit. GROQ_API_KEY is blanked *before* any
    Nexora module is imported (the code then uses its rule-based fallbacks), and
    Reddit is never selected.
  * No test may write into tracked repository files. The pipeline and Decision
    Engine write into pytest temporary directories only.
"""
import os

os.environ["GROQ_API_KEY"] = ""          # must run before app.core.config is imported
os.environ.pop("NEXORA_EXTERNAL_SIGNAL_MODE", None)
os.environ["NEXORA_FORECAST_MAX_ITER"] = "30"   # keeps pipeline fixtures fast; accuracy is tested separately

import contextlib
import io
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "inventory_painpoints_service" / "datasamplesv2"
PRODUCTS_CSV = DATA_DIR / "products.csv"


def run_quiet(fn, *args, **kwargs):
    """Runs fn while swallowing the (very chatty) print() output of v0 modules."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@pytest.fixture(scope="session")
def pipeline_dir(tmp_path_factory):
    """Runs the nightly pipeline once on the committed synthetic sample data."""
    from inventory_painpoints_service.app.services.nightly_pipeline import run_nightly_pipeline
    out = tmp_path_factory.mktemp("pipeline_out")
    df = run_quiet(run_nightly_pipeline, str(DATA_DIR), str(out))
    return out, df


@pytest.fixture(scope="session")
def analysis_df(pipeline_dir):
    return pipeline_dir[1]


@pytest.fixture(scope="module")
def engine(pipeline_dir, tmp_path_factory):
    """A DecisionEngine whose input *and* output files live in a temp folder."""
    from app.decision_engine.engine import DecisionEngine
    work = tmp_path_factory.mktemp("engine_work")
    shutil.copy(pipeline_dir[0] / "product_analysis.csv", work / "product_analysis.csv")
    return run_quiet(
        DecisionEngine,
        product_analysis_path=str(work / "product_analysis.csv"),
        products_path=str(PRODUCTS_CSV),
    )


@pytest.fixture
def legacy_mode(monkeypatch):
    """Selects the explicit v0-compatible signal mode (always NEUTRAL / 0.25)."""
    monkeypatch.setenv("NEXORA_EXTERNAL_SIGNAL_MODE", "legacy_neutral")


def make_mentions(n, text_title, text_body, comments, now=None):
    """Builds n deterministic mentions in the provider format."""
    import time
    now = now or time.time()
    return [
        {"thread_id": f"t{i}", "title": text_title, "body": text_body,
         "comments": list(comments), "upvotes": 10,
         "created_utc": now - 86400 * (i % 5)}
        for i in range(n)
    ]


class StubProvider:
    """Returns a fixed list of mentions; lets tests control the 'news' exactly."""
    def __init__(self, mentions):
        self._mentions = mentions

    def fetch_mentions(self, product_name, days_window, subreddits):
        return self._mentions


POSITIVE_MENTIONS = lambda: make_mentions(
    120, "Absolutely love this, amazing and excellent!",
    "Best purchase ever, fantastic quality", ["great", "wonderful"])
NEGATIVE_MENTIONS = lambda: make_mentions(
    120, "Terrible, awful and disgusting quality!",
    "Worst purchase ever, horrible", ["bad", "dreadful"])
