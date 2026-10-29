# Nexora
**AI-Powered Demand Forecasting and Supply Chain Optimization**

Nexora is an academic inventory-intelligence system that integrates demand forecasting, inventory risk detection, replenishment planning, and rule-based decision support. It processes retail data to identify inventory issues and generate product-level operational recommendations through a FastAPI service.

## Features

- **Demand Forecasting:** Seven-day demand prediction using gradient-boosted regression and quantile forecasting.
- **Inventory Analysis:** Detection of low stock, stagnant sales, expiry risk, high returns, and seasonal mismatch.
- **Replenishment Planning:** Forecast-driven order quantity calculation with lead-time and shelf-life considerations.
- **Decision Engine:** Product prioritization, action routing, and conflict resolution using rule-based logic.
- **Pricing and Product Recommendations:** XGBoost-based pricing functionality and rule- or LLM-assisted product combinations.
- **Explainability:** SHAP-based feature attribution and recommendation rationales.
- **External Signal Analysis:** Sentiment and urgency scoring using configurable signal sources.

## Architecture

The application follows a modular processing pipeline:

1. Data ingestion and feature engineering
2. Inventory pain-point detection
3. Demand forecasting and replenishment planning
4. External-signal analysis
5. Decision scoring and action routing
6. Recommendation generation and API delivery

The repository also includes a separate simulation-based research module for evaluating event-signal quality in perishable inventory management.

## Technology Stack

- **Language:** Python
- **API:** FastAPI, Uvicorn
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn, XGBoost
- **Explainability:** SHAP
- **NLP and External Signals:** VADER, PRAW
- **LLM Integration:** Groq (optional)
- **Testing:** pytest, HTTPX

## Repository Structure

```text
Nexora/
├── app/
│   ├── decision_engine/
│   └── modules/
│       ├── logistics/
│       ├── pricing/
│       ├── combo/
│       └── m7_xai/
├── external_signal_service/
├── inventory_painpoints_service/
│   └── app/
│       ├── forecasting/
│       ├── inventory_policy/
│       └── ...
├── research/
│   └── event_signal_inventory/
├── tests/
├── main.py
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## Installation

**Prerequisites:** Git and Python 3.

```bash
git clone https://github.com/kritikadamahe/Nexora.git
cd Nexora
python -m venv .venv
```

Activate the environment.

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

Install dependencies and configure the environment:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Copy `.env.example` to `.env` and configure optional integrations as required. The pinned dependencies in `requirements-lock.txt` may be used where supported.

## Configuration

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key for optional LLM functionality |
| `GROQ_MODEL_NAME` | Groq model identifier |
| `LLM_TIMEOUT` | LLM request timeout |
| `REDDIT_CLIENT_ID` | Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret |
| `REDDIT_USER_AGENT` | Reddit API user agent |
| `NEXORA_EXTERNAL_SIGNAL_MODE` | External-signal mode |
| `NEXORA_SEED` | Random seed for synthetic data generation |

The default external-signal mode is `synthetic`. LLM functionality uses rule-based fallbacks when Groq credentials are not configured. Never commit secrets in `.env`.

## Running the Application

Start the API from the repository root:

```bash
python -m uvicorn main:app --reload
```

API documentation is available at:

`http://127.0.0.1:8000/docs`

Run `POST /run-pipeline` to generate the latest analysis and replenishment outputs before using decision endpoints when the required pipeline output is unavailable.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/run-pipeline` | Execute the analysis pipeline |
| GET | `/results` | Retrieve product analysis |
| GET | `/results/{product_id}` | Retrieve analysis for a product |
| GET | `/decision/{product_id}` | Generate a product decision |
| GET | `/recommendations` | Retrieve recommendations |
| GET | `/recommendations/{product_id}` | Retrieve recommendations for a product |
| GET | `/replenishment` | Retrieve the replenishment plan |
| GET | `/replenishment/{product_id}` | Retrieve replenishment details for a product |

## Testing

Run the application test suite:

```bash
python -m pytest
```

The research module has a separate test suite and dependency requirements. Refer to `research/event_signal_inventory/README.md` for instructions.

## Research Module

`research/event_signal_inventory/` contains a standalone simulation study investigating the effects of imperfect event signals on demand forecasting and perishable inventory decisions.

See the [research README](research/event_signal_inventory/README.md) and [research report](research/event_signal_inventory/RESEARCH_REPORT.md) for methodology, results, and reproduction instructions.

## Limitations

- The application and research experiments use synthetic data; real-world performance has not been established.
- Forecasting performance depends substantially on the festival calendar used in the synthetic dataset.
- Supplier lead times and outstanding purchase orders are not fully represented by the available data.
- Decision routing and conflict resolution are rule-based rather than optimization-based.
- The pricing model has not been validated against a reliable real-world price–demand relationship.
- The Reddit integration has a known issue and should be considered unverified.

## License

No license file is currently included in this repository.
