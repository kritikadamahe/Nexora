# Nexora

**Demand forecasting, inventory risk detection and decision support for retail stores**

Nexora is an academic inventory-intelligence system. It reads a retailer's product, sales, stock and return records, forecasts demand for the next seven days, flags products with inventory problems, plans replenishment orders and recommends actions for each product: restock, reprice, bundle or move stock. Results are served through a FastAPI service.

The repository also contains a standalone research study, `research/event_signal_inventory/`. It asks when imperfect event signals (holidays, festivals, promotions) help or harm perishable inventory decisions. It shares no code with the application.

---

## Contents

1. [What the system does](#what-the-system-does)
2. [Architecture](#architecture)
3. [Data requirements](#data-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the application](#running-the-application)
7. [Model training and evaluation](#model-training-and-evaluation)
8. [Testing](#testing)
9. [Research module](#research-module)
10. [Limitations](#limitations)

---

## What the system does

| Capability | How it works |
|---|---|
| **Demand forecasting** | One gradient-boosted model (scikit-learn `HistGradientBoostingRegressor`) trained across all product-store series. It predicts the median (p50) and 90th-percentile (p90) demand over the next 7 days. If too little history exists, it falls back to a moving-average heuristic. |
| **Pain-point detection** | Rule-based detectors for low stock, near expiry, stagnant sales, high returns and seasonal mismatch, combined into a 0–1 composite risk score. |
| **Replenishment planning** | Order quantities from the forecast, current stock, lead time and shelf life. |
| **Decision engine** | Combines each product's risk with an external sentiment signal, computes a priority score, routes the product to actions and resolves conflicting actions. |
| **Action modules** | Forward and reverse logistics, pricing (an XGBoost model plus an optional LLM path), and product bundles (FP-Growth, rules and an optional LLM). |
| **Explainability** | SHAP feature attributions, rule-based reasons and an optional LLM-written narrative. |
| **External signals** | VADER sentiment over Reddit posts, a seeded synthetic generator (default), or a fixed neutral signal. |

---

## Architecture

```text
Nexora/
├── main.py                          FastAPI entry point
├── inventory_painpoints_service/    Stage 1: batch analytics ("nightly pipeline")
│   ├── app/
│   │   ├── data/loaders, cleaners   read and validate the five input tables
│   │   ├── features/                sales, expiry, return and inventory features
│   │   ├── detectors/               five pain-point detectors + composite risk
│   │   ├── forecasting/             demand panel, features, model, backtest
│   │   ├── inventory_policy/        replenishment rule + policy simulation
│   │   ├── services/nightly_pipeline.py   runs all of the above in order
│   │   └── core/config.py           detection thresholds, DATA_END_DATE
│   ├── datasamplesv2/               default input data (synthetic) + generator
│   ├── data_samples/                older synthetic data set (v1)
│   ├── pipeline_output/             written by the pipeline
│   └── forecast_evaluation/         written by the forecast backtest
├── app/                             Stage 2: decisions for one product at a time
│   ├── core/config.py               data/output paths, LLM settings, model path
│   ├── decision_engine/             unified signal → priority → routing → conflict resolution
│   └── modules/
│       ├── logistics/               forward (reuses replenishment) and reverse
│       ├── pricing/                 XGBoost + LLM pricing, training script, models/
│       ├── combo/                   FP-Growth bundles, rules, LLM, ranking
│       └── m7_xai/                  SHAP, reason builder, LLM narrator
├── external_signal_service/         Reddit / synthetic providers → sentiment → aggregator
├── research/event_signal_inventory/ standalone research study (separate environment)
├── tests/                           application test suite
├── requirements.txt                 runtime dependencies (lower bounds)
├── requirements-dev.txt             pytest, httpx
├── requirements-lock.txt            exact versions the tests were run against
└── .env.example                     configuration template
```

### Data flow

```text
POST /run-pipeline
  load CSVs → clean → compute features → 7-day forecast → detect pain points → plan replenishment
  writes pipeline_output/product_analysis.csv and replenishment_plan.csv
  rebuilds the DecisionEngine from the new output

GET /decision/{product_id}
  DecisionEngine (built once and kept in memory)
    reads the product's row from product_analysis.csv
    fetches the external signal (in-process call to external_signal_service)
    unified signal → priority score → action routing → conflict resolution
    runs the selected modules: Logistics / Pricing / Combo
    explains the result: SHAP + reasons (+ optional Groq narration)
```

Every action module takes the same `UnifiedSignal` object as input. Forward logistics reuses the pipeline's replenishment logic, so batch planning and per-product decisions order in the same way.

---

## Data requirements

### Application input

The pipeline reads five CSV files from `inventory_painpoints_service/datasamplesv2/`, a path set by `DATA_DIR` in `app/core/config.py`. The folder ships with a synthetic data set: one D-Mart-style store in Pune, about 200 products and about 106,000 sales rows from 2024-09-01 to 2026-02-28.

| File | Required columns | Notes |
|---|---|---|
| `products.csv` | `id, name, category, brand, cost_price, base_selling_price, shelf_life_days` | `shelf_life_days` drives the expiry risk score and the replenishment rule. |
| `stores.csv` | `id, name, location_city, location_lat, location_lng, store_type, capacity_units` | |
| `sales.csv` | `id, product_id, store_id, quantity_sold, selling_price, sold_at, channel` | One row per sale. Days with no row are treated as zero demand once a product has started selling. |
| `inventory.csv` | `id, product_id, store_id, current_stock, reorder_level, expiry_date, last_restocked_at` | Current stock snapshot. There is no stock history. |
| `returns.csv` | `id, product_id, store_id, quantity_returned, reason, returned_at` | Used for return-rate features. |

Other requirements:

- **Reference date.** The pipeline treats `DATA_END_DATE` in `inventory_painpoints_service/app/core/config.py` (default `2026-02-28`) as "today". Set it to the last date in your sales data.
- **Forecast history.** A series needs at least 28 days of history to get a model forecast. The global model needs at least 2,000 training rows. Below either threshold, the pipeline falls back to the moving-average heuristic and prints a warning.
- **Festival calendar.** Forecast features read `inventory_painpoints_service/app/forecasting/festival_calendar.csv` (`date, duration_days, name`). It covers Indian festivals for the dates of the bundled data. Extend it if your data covers other dates.
- **Regenerating synthetic data.** `python inventory_painpoints_service/datasamplesv2/generate_synthetic_data_v2.py` regenerates the data set with a fixed seed of 42.
- **Pricing model.** `app/modules/pricing/models/predictify_xgb_model.pkl` must exist for the XGBoost pricing path and SHAP explanations. A trained model is included.

### Research module input

- **Synthetic experiments** need no data.
- **Real-data experiments** need the Kaggle [Corporación Favorita Grocery Sales Forecasting](https://www.kaggle.com/c/favorita-grocery-sales-forecasting) files: `train.csv`, `items.csv`, `stores.csv`, `transactions.csv` and `holidays_events.csv`. Put them in `research/event_signal_inventory/data/favorita/`. That directory is git-ignored; never commit the data.

---

## Installation

**Prerequisites:** Git and Python 3.11 or newer. The lock file was verified on Python 3.13 on Linux x86_64.

```bash
git clone https://github.com/kritikadamahe/Nexora.git
cd Nexora
python -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate          # Linux/macOS
```
```powershell
.venv\Scripts\Activate.ps1         # Windows (PowerShell)
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
# or, for the exact tested versions:
python -m pip install -r requirements-lock.txt
```

Then create a `.env` file from the template:

```bash
cp .env.example .env
```

---

## Configuration

All settings are optional. Without any of them, the system runs fully offline: external signals come from the synthetic generator and the LLM features use rule-based fallbacks.

| Variable | Default | Purpose |
|---|---|---|
| `NEXORA_EXTERNAL_SIGNAL_MODE` | `synthetic` | `synthetic` (seeded, deterministic), `reddit` (live, needs credentials) or `legacy_neutral` (always neutral, urgency 0.25; reproduces the original v0 behaviour) |
| `NEXORA_SEED` | `42` | Base seed for the synthetic signal generator |
| `GROQ_API_KEY` | empty | Enables the LLM paths for pricing, bundles and narration |
| `GROQ_MODEL_NAME` | `llama-3.1-8b-instant` | Groq model |
| `LLM_TIMEOUT` | `10` | LLM request timeout, in seconds |
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | empty / `predictify-ai` | Reddit API credentials (only for `reddit` mode) |
| `NEXORA_FORECAST_MAX_ITER` | `300` | Overrides the forecaster's boosting iterations. The test suite lowers it to stay fast. |

Detection thresholds (stagnant ratio, near-expiry score, return-rate limits, risk weights) are constants in `inventory_painpoints_service/app/core/config.py`.

`.env` is git-ignored. Never commit secrets.

---

## Running the application

Start the API from the repository root:

```bash
python -m uvicorn main:app --reload
```

Interactive documentation: <http://127.0.0.1:8000/docs>

On a fresh checkout, run the pipeline first. The decision endpoints need `pipeline_output/product_analysis.csv`, and the server only builds the decision engine at startup if that file exists.

```bash
curl -X POST http://127.0.0.1:8000/run-pipeline
curl http://127.0.0.1:8000/decision/1
```

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service status, including whether pipeline output exists |
| POST | `/run-pipeline` | Run the full batch pipeline and rebuild the decision engine |
| GET | `/results` | Pipeline analysis for all products |
| GET | `/results/{product_id}` | Pipeline analysis for one product |
| GET | `/decision/{product_id}` | Full decision: priority, actions, module outputs and explanation |
| GET | `/recommendations` | Saved recommendations |
| GET | `/recommendations/{product_id}` | Recommendations for one product |
| GET | `/replenishment` | Replenishment plan |
| GET | `/replenishment/{product_id}` | Replenishment plan for one product |

### Outputs

| File | Written by | Contents |
|---|---|---|
| `inventory_painpoints_service/pipeline_output/product_analysis.csv` | `/run-pipeline` | Features, forecasts, pain points and risk score for each product-store |
| `inventory_painpoints_service/pipeline_output/replenishment_plan.csv` | `/run-pipeline` | Order action and quantity for each product-store |
| `inventory_painpoints_service/pipeline_output/recommendations.csv` | decision engine | Saved recommendations |

---

## Model training and evaluation

### Demand forecaster: backtest

```bash
python -m inventory_painpoints_service.app.forecasting.run_evaluation \
    [--data inventory_painpoints_service/datasamplesv2] \
    [--out  inventory_painpoints_service/forecast_evaluation]
```

The command takes a few minutes. It runs a rolling-origin backtest:

- The last 84 days are split into three 28-day test blocks, and the model is retrained before each block on all data whose targets were fully observed earlier.
- The model is compared with naive, 28- and 91-day moving-average baselines, the original Nexora heuristic, and the same model without festival features.
- It reports WAPE, MAE, RMSE, bias and per-series WAPE; p90 coverage and pinball loss; and a bootstrap confidence interval on the WAPE difference.
- It then runs a replenishment simulation over the same weeks and reports fill rate, stock on hand and stockout days.

Files written to `--out`: `forecast_metrics.csv`, `forecast_extras.json`, `backtest_predictions.csv`, `policy_simulation.csv` and a readable summary, `forecast_evaluation.md`.

In live use the forecaster is retrained on every `/run-pipeline` call, so there is no separate training step.

### Pricing model: training

```bash
cd inventory_painpoints_service
python ../app/modules/pricing/train_xgboost_pricing.py
```

- **What it trains:** two XGBoost regressors, with "native" and "legacy" feature sets. The target is the historical price that brought in the most revenue for each product.
- **Tuning and evaluation:** a 3-fold grid search over number of trees, depth and learning rate. RMSE, MAE and R² are reported on a random 20% hold-out.
- **Prerequisite:** run the pipeline first. The script reads `pipeline_output/product_analysis.csv`.
- **Paths:** the script's input and output paths are relative, as set at the top of the file. Run from `inventory_painpoints_service/`, it saves the models to `inventory_painpoints_service/models/`. Copy them to `app/modules/pricing/models/`, where the application loads them, or edit `MODEL_OUTPUT_DIR`.

---

## Testing

```bash
python -m pytest
```

`pytest.ini` sets the test path to `tests/` and puts the repository root on the import path. The suite covers the API, pipeline, forecasting, replenishment, decision engine and external signal service.

---

## Research module

`research/event_signal_inventory/` is a self-contained study of whether training a demand forecaster on event information as it would be known at ordering time reduces the cost of imperfect event signals for perishable stock. It compares three forecasters (event-blind, clean-calendar-trained and as-available-trained) under one replenishment policy, on synthetic data and on 100 Favorita perishable series.

It has its own pinned dependencies (Python 3.11 or newer). Use a separate virtual environment:

```bash
cd research/event_signal_inventory
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt

python -m pytest -q tests                                                  # 32 tests, about 10 s
python -m esi.experiment --config configs/smoke.json --out results/smoke   # end-to-end check, about 3 s
```

Always write to a new `--out` folder, so the committed results are not overwritten. The module README covers every experiment, the sensitivity sweeps, the strength × false-alarm grid and the clustered confidence intervals. See [research/event_signal_inventory/README.md](research/event_signal_inventory/README.md) and [RESEARCH_REPORT.md](research/event_signal_inventory/RESEARCH_REPORT.md). The paper source is in `research/event_signal_inventory/paper/`.

---

## Limitations

- **Synthetic data.** The application has only been run on synthetic data. Its real-world accuracy and value are not established.
- **Festival calendar.** Forecast accuracy depends substantially on the festival calendar matching the data.
- **Censored sales.** Sales stand in for demand. Demand on out-of-stock days is not observed, and there is no stock history.
- **Missing supply data.** Supplier lead times and open purchase orders are not fully represented in the data.
- **Rules, not optimization.** Decision routing and conflict resolution are rule-based.
- **Pricing model.** It is trained on a few hundred products with a random (not time-based) split. It has not been checked against a real price–demand relationship.
- **Blocking external signal.** The external signal is fetched in-process, so in `reddit` mode a slow Reddit call blocks the decision request. The Reddit integration has a known issue and should be considered unverified.

## License

No license file is currently included in this repository.
