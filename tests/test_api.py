"""API smoke tests. All file paths are redirected to temp folders."""
import pytest
from fastapi.testclient import TestClient

from conftest import DATA_DIR, PRODUCTS_CSV


@pytest.fixture
def client(tmp_path, monkeypatch):
    import main
    monkeypatch.setenv("NEXORA_EXTERNAL_SIGNAL_MODE", "legacy_neutral")
    monkeypatch.setattr(main, "DATA_DIR", str(DATA_DIR))
    monkeypatch.setattr(main, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(main, "PRODUCT_ANALYSIS_PATH", str(tmp_path / "product_analysis.csv"))
    monkeypatch.setattr(main, "PRODUCTS_PATH", str(PRODUCTS_CSV))
    monkeypatch.setattr(main, "RECOMMENDATIONS_PATH", str(tmp_path / "recommendations.csv"))
    monkeypatch.setattr(main, "decision_engine", None)
    with TestClient(main.app) as c:
        yield c, main, tmp_path


def test_health_before_pipeline_reports_not_initialised(client):
    c, _, _ = client
    r = c.get("/health").json()
    assert r["status"] == "ok" and r["pipeline_output"] is False


def test_endpoints_return_404_before_pipeline(client):
    c, _, _ = client
    assert c.get("/results").status_code == 404
    assert c.get("/results/1").status_code == 404
    assert c.get("/decision/1").status_code == 404
    assert c.get("/recommendations").status_code == 404


def test_pipeline_then_results(client):
    c, _, tmp = client
    r = c.post("/run-pipeline")
    assert r.status_code == 200
    body = r.json()
    assert body["total_products"] == 200 and body["flagged_count"] == 24
    assert (tmp / "product_analysis.csv").exists()
    res = c.get("/results").json()
    assert res["total_products"] == 200
    assert c.get("/results/106").json()["product_id"] == 106
    assert c.get("/results/999999").status_code == 404


def test_decision_requires_engine_then_works_after_restart(client):
    """Documented v0 behaviour: the engine only loads at startup, so after the first
    /run-pipeline the server must be restarted (here: re-enter the lifespan)."""
    c, main, _ = client
    c.post("/run-pipeline")
    assert c.get("/decision/106").status_code == 503
    with TestClient(main.app) as c2:             # a 'restart'
        r = c2.get("/decision/106")
        assert r.status_code == 200
        assert r.json()["action_types"] == ["LOGISTICS"]
        recs = c2.get("/recommendations")
        assert recs.status_code == 200 and recs.json()["total"] >= 1
        assert c2.get("/recommendations/106").status_code == 200
