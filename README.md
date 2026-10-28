# Nexora — AI-Powered Demand Forecasting and Supply Chain Optimization

Nexora is an academic retail inventory-intelligence project. A FastAPI service analyses synthetic product, sales, inventory and returns data, detects inventory pain points, combines them with an external-signal score, and produces product-level recommendations (logistics, pricing and product combinations) with explanations.

The repository also contains a separate, synthetic-data research study on event-signal quality and perishable replenishment (`research/event_signal_inventory/`).

> **Status:** academic prototype. All data in this repository is synthetic. No real-world performance claims are made. See [Current implementation limits](#current-implementation-limits).

## What the application does

1. **Inventory pain-point pipeline** (`inventory_painpoints_service/`) loads the synthetic data in `inventory_painpoints_service/datasamplesv2/`. It computes sales, inventory, expiry and return features, then flags five pain points: low stock, stagnant sales, near expiry, high returns and seasonal mismatch. It also computes a weighted composite risk score and writes `pipeline_output/product_analysis.csv`.
2. **External signal** (`external_signal_service/`) turns product mentions into a sentiment and urgency score. The mentions come from a seeded synthetic generator by default (see [External signal modes](#external-signal-modes)).
3. **Decision engine** (`app/decision_engine/`) combines the pipeline output and the external signal into a priority score. It then routes each product to action modules using fixed rules and resolves conflicts between actions with fixed rules.
4. **Action modules** (`app/modules/`):
   - **logistics:** forward (restock) and reverse (markdown, warehouse return, transfer) heuristics;
   - **pricing:** an XGBoost model path, plus an LLM path with rule-based fallback and hard price bounds;
   - **combo:** rule- and LLM-based product combinations;
   - **m7_xai:** SHAP attributions for the pricing model and an LLM-written or rule-based rationale. Recommendations are appended to `recommendations.csv`.
5. **Demand forecasting** (`inventory_painpoints_service/app/forecasting/`) trains a 7-day demand model (P50 and P90) on the sales history during the pipeline run, and **replenishment** (`inventory_painpoints_service/app/inventory_policy/`) turns it into order / hold / expiry-risk / overstock actions using stock and product data. Forward logistics uses the same order-up-to rule.
6. **API** (`main.py`) exposes the pipeline, results, decisions, recommendations and the replenishment plan.

LLM features use Groq when `GROQ_API_KEY` is set. When it is empty, rule-based fallbacks are used.

## Current implementation limits

- **The forecast is a trained gradient-boosted model, not a TFT.** It is trained on synthetic data only. Its advantage over simple baselines depends on a festival calendar that is known in advance; without that calendar it is *not* better than a moving average (see [Demand forecasting and replenishment](#demand-forecasting-and-replenishment)). The column name `tft_forecast_7d` is legacy and now equals `forecast_7d`; the old heuristic is only a fallback.
- **Replenishment assumptions are placeholders.** Supplier lead time (default 3 days), open purchase orders (assumed none), MOQ and capacity are not in the data. Stock-outs are not observed historically, so sales are used as a proxy for demand.
- **The decision engine is rule-based.** Priority weights, routing and conflict resolution are fixed rules. No mathematical optimiser is solved.
- **FP-Growth is not wired in.** `run_fp_growth()` (`app/modules/combo/fp_growth.py`) is never called by the pipeline or the API. Without its itemset cache, combinations fall back to the rule- and LLM-based paths.
- **XGBoost pricing is unvalidated.** The committed model (`app/modules/pricing/models/predictify_xgb_model.pkl`) has not been validated as a reliable model of how demand responds to price. The synthetic data contains no price–demand relationship.
- **The default external signal is a placeholder.** In `synthetic` mode the mentions are generic, seeded template text and are not tied to the products. Live Reddit mode has a known integration issue (see below).
- **Committed outputs are samples.** `pipeline_output/product_analysis.csv` and `replenishment_plan.csv` were regenerated with the current code; `recommendations.csv` is an older sample. Running the pipeline regenerates the first two.

## Repository structure

```text
Nexora/
├── main.py                              # FastAPI application (entry point)
├── .env.example                         # configuration template (copy to .env)
├── requirements.txt                     # direct runtime dependencies
├── requirements-dev.txt                 # test dependencies (pytest, httpx)
├── requirements-lock.txt                # exact versions (verified on Python 3.13 / Linux)
├── pytest.ini
├── app/
│   ├── core/config.py                   # paths and LLM settings
│   ├── decision_engine/                 # unified signal, priority score, routing, conflicts, engine
│   └── modules/
│       ├── logistics/                   # forward / reverse logistics heuristics
│       ├── pricing/                     # XGBoost + LLM pricing; models/*.pkl
│       ├── combo/                       # combination rules, LLM combos, FP-Growth (not wired in)
│       └── m7_xai/                      # SHAP explanations and narratives
├── external_signal_service/
│   ├── main.py                          # reddit_trend(): signal modes, urgency and sentiment
│   ├── providers/                       # synthetic and Reddit mention providers
│   ├── aggregator.py, sentiment.py, schemas.py, config.py, ...
├── inventory_painpoints_service/
│   ├── app/                             # data loading, features, detectors, nightly pipeline
│   ├── datasamplesv2/                   # synthetic data used by the API (and its generator)
│   ├── data_samples/                    # older synthetic dataset (not used by the API)
│   ├── pipeline_output/                 # product_analysis.csv, recommendations.csv
│   └── output/                          # legacy outputs
├── tests/                               # application test suite
├── research/
│   └── event_signal_inventory/          # separate synthetic-data research study
│       ├── README.md
│       ├── RESEARCH_REPORT.md
│       ├── requirements.txt             # separate environment (pins differ from the app)
│       ├── esi/, tests/, configs/, results/
├── literature_review_and_gap_analysis.md
└── literature_review_and_gap_analysis.txt
```

## Setup

**Prerequisites:** Git and Python 3.

The lockfile `requirements-lock.txt` was verified on **Python 3.13 / Linux** only. It has not been verified on Windows or macOS. If it fails to install on your platform, use the looser direct-dependency files instead.

```bash
git clone https://github.com/kritikadamahe/Nexora.git
cd Nexora
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt -r requirements-dev.txt
# alternative: python -m pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
```

Linux/macOS:

```bash
python3 -m venv .venv && . .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt -r requirements-dev.txt
# alternative: python -m pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

### Configuration (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | empty | LLM features. Leave empty to use rule-based fallbacks. |
| `GROQ_MODEL_NAME` | `llama-3.1-8b-instant` | Groq model |
| `LLM_TIMEOUT` | `10` | LLM timeout in seconds |
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | empty / `nexora` | Only used in `reddit` mode |
| `NEXORA_EXTERNAL_SIGNAL_MODE` | `synthetic` | Signal source (see below) |
| `NEXORA_SEED` | `42` | Seed for synthetic randomness |

`.env` is git-ignored. Never commit API keys.

### External signal modes

| Mode | Behaviour | Status |
|---|---|---|
| `synthetic` (default) | Seeded placeholder mentions; deterministic for a given seed | Default demo path |
| `legacy_neutral` | Always NEUTRAL sentiment and urgency 0.25, reproducing the original baseline | Supported |
| `reddit` | Live Reddit via PRAW; needs Reddit credentials | **Known integration issue.** The decision engine calls the signal service without a subreddit list, and the Reddit provider iterates over that list. Treat this mode as unverified; it is not a working demo path. |

## Demand forecasting and replenishment

**Forecast.** For every product-store series the pipeline predicts total units demanded over the next 7 days. One global `HistGradientBoostingRegressor` (absolute-error loss, target scaled by the trailing 28-day level) gives the point forecast, and a second with a 0.9 quantile loss gives P90. Features use only data up to the forecast date (trailing means, ratios, zero-sales share, same window one year earlier, category) plus a known-in-advance festival calendar (`app/forecasting/festival_calendar.csv`). Sales are zero-filled on missing days; pre-launch days are not.

**Evaluation (reproducible).** Chronological, rolling-origin: the last 12 weeks are three 4-week test blocks; the model is retrained before each block using only origins whose 7-day target was fully observed before that block. Hyper-parameters were chosen on a validation window before the first test block. Results (15,400 series-origins, synthetic data):

| Method | WAPE | MAE (units) |
|---|---|---|
| Naive (last 7 days) | 0.121 | 14.1 |
| Moving average 28d | 0.117 | 13.7 |
| Moving average 91d | 0.129 | 15.1 |
| Original Nexora heuristic | 0.134 | 15.7 |
| GBM without festival calendar | 0.166 | 19.4 |
| **GBM (final)** | **0.074** | **8.6** |

Paired bootstrap over products: WAPE(GBM) minus WAPE(best baseline, MA28) = −0.043, 95% CI [−0.057, −0.017]; minus original heuristic = −0.060, CI [−0.071, −0.046]. P90 coverage is 0.908 (target 0.90). Caveats: the gain is concentrated in the festival blocks (block 3, with no major festival, improves only from 0.077 to 0.072); the calendar is the same festival list the synthetic generator used, so the size of the gain reflects the generator, and on real data a real holiday calendar would be needed. Without the calendar the model does not beat simple baselines.

**Replenishment.** Weekly order-up-to policy: `S = forecast × (lead + 7)/7 + (P90 − P50) × sqrt((lead + 7)/7)`; order `S − stock`, capped by units sellable within shelf life; stock that cannot sell before expiry at the forecast rate is flagged `EXPIRY_RISK`; very high cover is `OVERSTOCK_REVIEW`. Assumptions are listed in `app/inventory_policy/replenishment.py`.

Back-simulation over the same 12 weeks (same starting stock, deterministic lead time, lost sales):

| Policy | Fill rate | Avg on-hand value at cost | Stock-out series-days |
|---|---|---|---|
| Forecast-driven (GBM) | 0.964 | 588,908 | 539 |
| Textbook (MA28 + z·σ) | 0.963 | 585,343 | 452 |
| Original forward-logistics rule | 0.899 | 409,553 | 2052 |

The forecast-driven policy clearly beats the original rule on service (at higher inventory), but it is **not** measurably better than the textbook policy; the more accurate forecast did not translate into a better inventory outcome here.

Reproduce: `python -m inventory_painpoints_service.app.forecasting.run_evaluation` (about 2 minutes; writes to `inventory_painpoints_service/forecast_evaluation/`). Run the pipeline with `POST /run-pipeline`.

## Running the API

```bash
python -m uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive API documentation.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service status and whether the decision engine is initialised |
| POST | `/run-pipeline` | Runs the pipeline (trains the demand model, ~20 s). **Overwrites** `pipeline_output/product_analysis.csv` and `replenishment_plan.csv`. |
| GET | `/results` | All rows of the latest pipeline output |
| GET | `/results/{product_id}` | Pipeline output for one product |
| GET | `/decision/{product_id}` | Runs the decision engine for one product. **Appends** to `pipeline_output/recommendations.csv`. |
| GET | `/recommendations` | All saved recommendations |
| GET | `/recommendations/{product_id}` | Saved recommendations for one product |
| GET | `/replenishment` | Forecast-driven replenishment plan; optional `?action=ORDER_URGENT\|ORDER\|HOLD\|OVERSTOCK_REVIEW\|EXPIRY_RISK` |
| GET | `/replenishment/{product_id}` | Plan row for one product |

The decision engine is created at startup only if `product_analysis.csv` already exists. If it doesn't, call `POST /run-pipeline` and then restart the server before using `/decision`.

### Suggested demo sequence

Use a **disposable clone**: the pipeline and decision calls modify CSV files that are tracked in the repository. Keep `GROQ_API_KEY` empty and `NEXORA_EXTERNAL_SIGNAL_MODE=synthetic` unless you intend to test those features.

1. `GET /health`
2. `POST /run-pipeline`. This regenerates the analysis from the current data; note a product ID in `flagged_products`.
3. `GET /results/{product_id}`
4. `GET /decision/{product_id}` for that flagged product. Products without pain points are skipped.
5. `GET /recommendations/{product_id}`

Afterwards, `git status` will show the modified output CSVs.

## Tests

```bash
python -m pytest
```

The suite in `tests/` covers the pipeline, decision engine, external-signal modes, API endpoints and repository hygiene. It blanks `GROQ_API_KEY`, never calls Reddit or an LLM, and writes only to temporary folders.

The suite was last run locally with **82 passed, 2 skipped** (the skips need a git checkout). It has not been verified across platforms, and passing tests do not establish that every workflow works end to end. The research module has its own separate tests (see its README).

The pre-refactor baseline of the application is commit `2eb21e3`.

## Research module: event-signal quality study

`research/event_signal_inventory/` is a **separate, self-contained simulation study**. It is **not integrated into the API**, and the application doesn't import it. It asks whether training a demand forecaster on event information *as it would be available at ordering time* reduces the inventory-cost harm caused by imperfect event signals. The study uses synthetic demand, a perishable-inventory simulator and a shared heuristic ordering policy.

Its results are simulation evidence for one set of chosen parameters. They do **not** establish real-world retail improvements. Use a separate virtual environment, because its pinned dependency versions differ from the application's.

See:

- [`research/event_signal_inventory/README.md`](research/event_signal_inventory/README.md) for setup, reproduction commands and a results summary;
- [`research/event_signal_inventory/RESEARCH_REPORT.md`](research/event_signal_inventory/RESEARCH_REPORT.md) for the full design, 20-seed results, seed-level statistics and limitations.

## Literature review

`literature_review_and_gap_analysis.md` (and its identical `.txt` copy) is an early project review of related work. Its gap and novelty statements were not established by a systematic literature search, and its references have not been independently verified. Treat it as background, not as evidence of novelty.

## Technology

Python, FastAPI, Uvicorn, Pydantic, python-dotenv, pandas, NumPy, scikit-learn, XGBoost, SHAP, mlxtend, VADER Sentiment, PRAW, and Groq (optional).

## Team

Developed as a group academic project in Operational Research and Digital Supply Chain Management.

## License

No license file is currently included in this repository.
