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
    """The decision engine is initialized after the pipeline runs."""
    c, main, _ = client
    c.post("/run-pipeline")

    r = c.get("/decision/106")
    assert r.status_code == 200
    assert r.json()["action_types"] == ["LOGISTICS"]

    recs = c.get("/recommendations")
    assert recs.status_code == 200
    assert recs.json()["total"] >= 1

    assert c.get("/recommendations/106").status_code == 200


def test_replenishment_endpoints(client):
    c, _, _ = client
    assert c.get("/replenishment").status_code == 404           # before the pipeline
    c.post("/run-pipeline")
    r = c.get("/replenishment").json()
    assert sum(r["action_counts"].values()) == 200
    assert len(r["rows"]) == 200 and r["total_units_to_order"] >= 0
    urgent = c.get("/replenishment", params={"action": "ORDER_URGENT"}).json()
    assert all(x["action"] == "ORDER_URGENT" for x in urgent["rows"])
    assert c.get("/replenishment", params={"action": "BOGUS"}).status_code == 422
    one = c.get("/replenishment/106").json()
    assert one["product_id"] == 106 and "order_quantity" in one
    assert c.get("/replenishment/999999").status_code == 404

def test_decision_endpoint_exposes_forecast_fields_and_keeps_old_ones(client):
    c, _, _ = client
    c.post("/run-pipeline")
    body = c.get("/decision/106").json()
    for key in ["product_id", "pain_points", "action_types", "recommendations", "skipped"]:
        assert key in body
    assert body["forecast"]["method"] == "gbm"
    assert body["forecast"]["horizon_days"] == 7
    assert body["replenishment_action"] in {"ORDER", "ORDER_URGENT", "HOLD", "EXPIRY_RISK",
                                            "OVERSTOCK_REVIEW", "INSUFFICIENT_DATA"}
    rec = body["recommendations"][0]
    assert rec["action"] in {"RESTOCK", "NO_RESTOCK"}
    assert "assumptions" in rec["replenishment"]