diff --git a/README.md b/README.md
index d9da5fa..28bb899 100644
--- a/README.md
+++ b/README.md
@@ -1,162 +1,193 @@
+# Nexora — AI-Powered Demand Forecasting and Supply Chain Optimization
 
-# Nexora
-### AI-Powered Demand Forecasting and Supply Chain Optimization
+Nexora is an academic retail inventory-intelligence project. A FastAPI service analyses synthetic product, sales, inventory and returns data, detects inventory pain points, combines them with an external-signal score, and produces product-level recommendations (logistics, pricing and product combinations) with explanations.
 
-Nexora is an AI-driven retail inventory intelligence project that aims to connect demand signals, product-level risk analysis, and operational research to support smarter inventory and supply-chain decisions.
+The repository also contains a separate, synthetic-data research study on event-signal quality and perishable replenishment (`research/event_signal_inventory/`).
 
-The project explores how data-driven forecasting and decision models can help retailers identify inventory issues, prioritize products, and generate actionable recommendations.
+> **Status:** academic prototype. All data in this repository is synthetic. No real-world performance claims are made. See [Current implementation limits](#current-implementation-limits).
 
-## Overview
+## What the application does
 
-Retail inventory management involves balancing product availability, stock levels, expiry risk, supplier constraints, and operational costs. Traditional approaches may struggle to respond effectively when demand patterns or external conditions change.
+1. **Inventory pain-point pipeline** (`inventory_painpoints_service/`) loads the synthetic data in `inventory_painpoints_service/datasamplesv2/`. It computes sales, inventory, expiry and return features, then flags five pain points: low stock, stagnant sales, near expiry, high returns and seasonal mismatch. It also computes a weighted composite risk score and writes `pipeline_output/product_analysis.csv`.
+2. **External signal** (`external_signal_service/`) turns product mentions into a sentiment and urgency score. The mentions come from a seeded synthetic generator by default (see [External signal modes](#external-signal-modes)).
+3. **Decision engine** (`app/decision_engine/`) combines the pipeline output and the external signal into a priority score. It then routes each product to action modules using fixed rules and resolves conflicts between actions with fixed rules.
+4. **Action modules** (`app/modules/`):
+   - **logistics:** forward (restock) and reverse (markdown, warehouse return, transfer) heuristics;
+   - **pricing:** an XGBoost model path, plus an LLM path with rule-based fallback and hard price bounds;
+   - **combo:** rule- and LLM-based product combinations;
+   - **m7_xai:** SHAP attributions for the pricing model and an LLM-written or rule-based rationale. Recommendations are appended to `recommendations.csv`.
+5. **API** (`main.py`) exposes the pipeline, results, decisions and recommendations.
 
-Nexora aims to address these challenges by combining inventory analytics, external signals, and decision-support logic in a unified system.
+LLM features use Groq when `GROQ_API_KEY` is set. When it is empty, rule-based fallbacks are used.
 
-## Key Capabilities
+## Current implementation limits
 
-- **Inventory analysis:** Process product and store data to identify potential inventory pain points.
-- **Product risk assessment:** Calculate composite risk scores and identify products requiring attention.
-- **External signal analysis:** Explore signals from external sources, including Reddit, to provide additional context for inventory decisions.
-- **Decision support:** Generate product-level recommendations through a modular decision engine.
-- **Recommendation tracking:** Expose recommendation summaries, priorities, rationales, and supporting information through API endpoints.
-- **Supply-chain optimization research:** Explore how forecasting, inventory policies, and constrained optimization can improve stocking and pricing decisions.
+- **Forecasting is heuristic.** The 7-day forecast (`tft_forecast_7d`) is `avg_daily_sales × 7 × seasonality_index` (`inventory_painpoints_service/app/features/feature_assembler.py`). It is not a trained Temporal Fusion Transformer or any other trained forecasting model.
+- **The decision engine is rule-based.** Priority weights, routing and conflict resolution are fixed rules. No mathematical optimiser is solved.
+- **FP-Growth is not wired in.** `run_fp_growth()` (`app/modules/combo/fp_growth.py`) is never called by the pipeline or the API. Without its itemset cache, combinations fall back to the rule- and LLM-based paths.
+- **XGBoost pricing is unvalidated.** The committed model (`app/modules/pricing/models/predictify_xgb_model.pkl`) has not been validated as a reliable model of how demand responds to price. The synthetic data contains no price–demand relationship.
+- **The default external signal is a placeholder.** In `synthetic` mode the mentions are generic, seeded template text and are not tied to the products. Live Reddit mode has a known integration issue (see below).
+- **Committed outputs are samples.** The CSVs under `inventory_painpoints_service/pipeline_output/` are committed sample outputs and may not match the current data. Running the pipeline regenerates them.
 
-*Note: The complete news-aware demand forecasting and joint price-and-stock optimization workflow is the broader project direction. Individual capabilities should be considered implemented only where supported by the current code.*
-
-## Connection to Operational Research and DSCM
-
-### Operational Research (OR)
-
-Nexora relates to OR through data-driven decision-making, product prioritization, inventory risk assessment, and the potential application of optimization techniques to stocking and pricing.
-
-### Digital Supply Chain Management (DSCM)
-
-The project supports the broader DSCM goal of connecting digital data and external signals to inventory visibility and actionable recommendations.
-
-Together, OR and DSCM provide the foundation for moving from inventory monitoring toward evidence-based operational decisions.
-
-## System Architecture
-
-The current codebase is organized into modular components:
-
-1. **API layer:** FastAPI application in `main.py`.
-2. **Inventory analysis:** Pipeline components for processing product data and identifying inventory pain points.
-3. **External signals:** Services for collecting and analyzing external signals.
-4. **Decision engine:** Logic for evaluating products and producing recommendations.
-5. **Data outputs:** CSV-based analysis results and recommendation records.
-
-The proposed system can be extended with demand forecasting, news-event classification, uncertainty estimation, and constrained optimization.
-
-## Technology Stack
-
-- **Language:** Python
-- **API framework:** FastAPI
-- **Data processing:** Pandas, NumPy
-- **Machine learning:** XGBoost, SHAP
-- **External signal analysis:** PRAW, VADER Sentiment
-- **Server:** Uvicorn
-- **Validation and configuration:** Pydantic, python-dotenv
-
-## Project Structure
+## Repository structure
 
 ```text
 Nexora/
+├── main.py                              # FastAPI application (entry point)
+├── .env.example                         # configuration template (copy to .env)
+├── requirements.txt                     # direct runtime dependencies
+├── requirements-dev.txt                 # test dependencies (pytest, httpx)
+├── requirements-lock.txt                # exact versions (verified on Python 3.13 / Linux)
+├── pytest.ini
 ├── app/
-│   ├── core/
+│   ├── core/config.py                   # paths and LLM settings
+│   ├── decision_engine/                 # unified signal, priority score, routing, conflicts, engine
 │   └── modules/
+│       ├── logistics/                   # forward / reverse logistics heuristics
+│       ├── pricing/                     # XGBoost + LLM pricing; models/*.pkl
+│       ├── combo/                       # combination rules, LLM combos, FP-Growth (not wired in)
+│       └── m7_xai/                      # SHAP explanations and narratives
 ├── external_signal_service/
+│   ├── main.py                          # reddit_trend(): signal modes, urgency and sentiment
+│   ├── providers/                       # synthetic and Reddit mention providers
+│   ├── aggregator.py, sentiment.py, schemas.py, config.py, ...
 ├── inventory_painpoints_service/
-├── main.py
-├── requirements.txt
-├── .gitignore
+│   ├── app/                             # data loading, features, detectors, nightly pipeline
+│   ├── datasamplesv2/                   # synthetic data used by the API (and its generator)
+│   ├── data_samples/                    # older synthetic dataset (not used by the API)
+│   ├── pipeline_output/                 # product_analysis.csv, recommendations.csv
+│   └── output/                          # legacy outputs
+├── tests/                               # application test suite
+├── research/
+│   └── event_signal_inventory/          # separate synthetic-data research study
+│       ├── README.md
+│       ├── RESEARCH_REPORT.md
+│       ├── requirements.txt             # separate environment (pins differ from the app)
+│       ├── esi/, tests/, configs/, results/
 ├── literature_review_and_gap_analysis.md
 └── literature_review_and_gap_analysis.txt
 ```
 
-The exact modules and supporting files may evolve as development progresses.
-
-## Getting Started
+## Setup
 
-### Prerequisites
+**Prerequisites:** Git and Python 3.
 
-- Python installed
-- Git
-- A terminal or code editor such as VS Code
-
-### 1. Clone the repository
+The lockfile `requirements-lock.txt` was verified on **Python 3.13 / Linux** only. It has not been verified on Windows or macOS. If it fails to install on your platform, use the looser direct-dependency files instead.
 
 ```bash
-git clone <YOUR_GITHUB_REPOSITORY_URL>
+git clone https://github.com/kritikadamahe/Nexora.git
 cd Nexora
 ```
 
-Replace the placeholder with the repository URL after publishing the project.
-
-### 2. Create a virtual environment
+Windows (PowerShell):
 
-Windows:
-
-```bash
+```powershell
 python -m venv .venv
-.venv\Scripts\activate
+.venv\Scripts\Activate.ps1
+python -m pip install --upgrade pip
+python -m pip install -r requirements-lock.txt -r requirements-dev.txt
+# alternative: python -m pip install -r requirements.txt -r requirements-dev.txt
+copy .env.example .env
 ```
 
-### 3. Install dependencies
+Linux/macOS:
 
 ```bash
+python3 -m venv .venv && . .venv/bin/activate
 python -m pip install --upgrade pip
-pip install -r requirements.txt
+python -m pip install -r requirements-lock.txt -r requirements-dev.txt
+# alternative: python -m pip install -r requirements.txt -r requirements-dev.txt
+cp .env.example .env
 ```
 
-Dependency compatibility and any additional setup requirements should be verified before running the application.
+### Configuration (`.env`)
+
+| Variable | Default | Purpose |
+|---|---|---|
+| `GROQ_API_KEY` | empty | LLM features. Leave empty to use rule-based fallbacks. |
+| `GROQ_MODEL_NAME` | `llama-3.1-8b-instant` | Groq model |
+| `LLM_TIMEOUT` | `10` | LLM timeout in seconds |
+| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | empty / `nexora` | Only used in `reddit` mode |
+| `NEXORA_EXTERNAL_SIGNAL_MODE` | `synthetic` | Signal source (see below) |
+| `NEXORA_SEED` | `42` | Seed for synthetic randomness |
 
-### 4. Start the API server
+`.env` is git-ignored. Never commit API keys.
+
+### External signal modes
+
+| Mode | Behaviour | Status |
+|---|---|---|
+| `synthetic` (default) | Seeded placeholder mentions; deterministic for a given seed | Default demo path |
+| `legacy_neutral` | Always NEUTRAL sentiment and urgency 0.25, reproducing the original baseline | Supported |
+| `reddit` | Live Reddit via PRAW; needs Reddit credentials | **Known integration issue.** The decision engine calls the signal service without a subreddit list, and the Reddit provider iterates over that list. Treat this mode as unverified; it is not a working demo path. |
+
+## Running the API
 
 ```bash
 python -m uvicorn main:app --reload
 ```
 
-The application is configured to run locally using Uvicorn. Successful startup may depend on the availability of the required input data and generated analysis files.
+Then open `http://127.0.0.1:8000/docs` for the interactive API documentation.
+
+| Method | Endpoint | Description |
+|---|---|---|
+| GET | `/health` | Service status and whether the decision engine is initialised |
+| POST | `/run-pipeline` | Runs the pain-point pipeline. **Overwrites** `inventory_painpoints_service/pipeline_output/product_analysis.csv`. |
+| GET | `/results` | All rows of the latest pipeline output |
+| GET | `/results/{product_id}` | Pipeline output for one product |
+| GET | `/decision/{product_id}` | Runs the decision engine for one product. **Appends** to `pipeline_output/recommendations.csv`. |
+| GET | `/recommendations` | All saved recommendations |
+| GET | `/recommendations/{product_id}` | Saved recommendations for one product |
 
-### 5. Explore the API
+The decision engine is created at startup only if `product_analysis.csv` already exists. If it doesn't, call `POST /run-pipeline` and then restart the server before using `/decision`.
+
+### Suggested demo sequence
+
+Use a **disposable clone**: the pipeline and decision calls modify CSV files that are tracked in the repository. Keep `GROQ_API_KEY` empty and `NEXORA_EXTERNAL_SIGNAL_MODE=synthetic` unless you intend to test those features.
+
+1. `GET /health`
+2. `POST /run-pipeline`. This regenerates the analysis from the current data; note a product ID in `flagged_products`.
+3. `GET /results/{product_id}`
+4. `GET /decision/{product_id}` for that flagged product. Products without pain points are skipped.
+5. `GET /recommendations/{product_id}`
+
+Afterwards, `git status` will show the modified output CSVs.
+
+## Tests
+
+```bash
+python -m pytest
+```
 
-Once the server starts, open:
+The suite in `tests/` covers the pipeline, decision engine, external-signal modes, API endpoints and repository hygiene. It blanks `GROQ_API_KEY`, never calls Reddit or an LLM, and writes only to temporary folders.
 
-- `http://127.0.0.1:8000/docs` — interactive API documentation
-- `http://127.0.0.1:8000/health` — service health endpoint
+The suite was last run locally with **56 passed, 7 warnings**. It has not been verified across platforms, and passing tests do not establish that every workflow works end to end. The research module has its own separate tests (see its README).
 
-The application also defines endpoints for running the inventory pipeline, retrieving analysis results, obtaining product-level decisions, and viewing recommendations.
+The pre-refactor baseline of the application is commit `2eb21e3`.
 
-## Reproducibility and Tests
+## Research module: event-signal quality study
 
-- **Baseline snapshot:** the git tag `nexora-v0` marks the code before the research refactor. Check it out with `git checkout nexora-v0` to reproduce the original behaviour.
-- **Exact environment:** `pip install -r requirements-lock.txt` (verified on Python 3.13, Linux). For a looser install use `pip install -r requirements.txt -r requirements-dev.txt`.
-- **Configuration:** copy `.env.example` to `.env`. The `.env` file is git-ignored; never commit API keys.
-- **External signal mode:** set `NEXORA_EXTERNAL_SIGNAL_MODE` to `synthetic` (default, seeded), `reddit` (live), or `legacy_neutral` (reproduces nexora-v0, where urgency was always 0.25 and sentiment always NEUTRAL). `NEXORA_SEED` seeds all synthetic randomness.
-- **Run the tests:** `python -m pytest` from the repository root. Tests write only to temporary folders and never call an LLM or Reddit.
+`research/event_signal_inventory/` is a **separate, self-contained simulation study**. It is **not integrated into the API**, and the application doesn't import it. It asks whether training a demand forecaster on event information *as it would be available at ordering time* reduces the inventory-cost harm caused by imperfect event signals. The study uses synthetic demand, a perishable-inventory simulator and a shared heuristic ordering policy.
 
-## Research and Evaluation Direction
+Its results are simulation evidence for one set of chosen parameters. They do **not** establish real-world retail improvements. Use a separate virtual environment, because its pinned dependency versions differ from the application's.
 
-The broader project direction includes evaluating the value of external signals for demand forecasting and inventory decisions.
+See:
 
-Potential evaluation areas include:
+- [`research/event_signal_inventory/README.md`](research/event_signal_inventory/README.md) for setup, reproduction commands and a results summary;
+- [`research/event_signal_inventory/RESEARCH_REPORT.md`](research/event_signal_inventory/RESEARCH_REPORT.md) for the full design, 20-seed results, seed-level statistics and limitations.
 
-- Forecast accuracy against baseline methods
-- Inventory availability and stockout rates
-- Expiry-related waste
-- Contribution margin and operational costs
-- Performance with and without external signals
+## Literature review
 
-These are evaluation objectives, not claimed experimental results. Quantitative improvements should be reported only after appropriate testing.
+`literature_review_and_gap_analysis.md` (and its identical `.txt` copy) is an early project review of related work. Its gap and novelty statements were not established by a systematic literature search, and its references have not been independently verified. Treat it as background, not as evidence of novelty.
 
-## Current Status
+## Technology
 
-Nexora is an evolving academic project combining AI, inventory intelligence, and supply-chain decision support. The implementation and research direction may expand as additional forecasting and optimization components are developed and evaluated.
+Python, FastAPI, Uvicorn, Pydantic, python-dotenv, pandas, NumPy, scikit-learn, XGBoost, SHAP, mlxtend, VADER Sentiment, PRAW, and Groq (optional).
 
 ## Team
 
-Developed as a group academic project focused on Operational Research and Digital Supply Chain Management.
+Developed as a group academic project in Operational Research and Digital Supply Chain Management.
 
 ## License
 
-A license can be added once the project team has agreed on the terms for sharing and reuse.
+No license file is currently included in this repository.
