
# Nexora
### AI-Powered Demand Forecasting and Supply Chain Optimization

Nexora is an AI-driven retail inventory intelligence project that aims to connect demand signals, product-level risk analysis, and operational research to support smarter inventory and supply-chain decisions.

The project explores how data-driven forecasting and decision models can help retailers identify inventory issues, prioritize products, and generate actionable recommendations.

## Overview

Retail inventory management involves balancing product availability, stock levels, expiry risk, supplier constraints, and operational costs. Traditional approaches may struggle to respond effectively when demand patterns or external conditions change.

Nexora aims to address these challenges by combining inventory analytics, external signals, and decision-support logic in a unified system.

## Key Capabilities

- **Inventory analysis:** Process product and store data to identify potential inventory pain points.
- **Product risk assessment:** Calculate composite risk scores and identify products requiring attention.
- **External signal analysis:** Explore signals from external sources, including Reddit, to provide additional context for inventory decisions.
- **Decision support:** Generate product-level recommendations through a modular decision engine.
- **Recommendation tracking:** Expose recommendation summaries, priorities, rationales, and supporting information through API endpoints.
- **Supply-chain optimization research:** Explore how forecasting, inventory policies, and constrained optimization can improve stocking and pricing decisions.

*Note: The complete news-aware demand forecasting and joint price-and-stock optimization workflow is the broader project direction. Individual capabilities should be considered implemented only where supported by the current code.*

## Connection to Operational Research and DSCM

### Operational Research (OR)

Nexora relates to OR through data-driven decision-making, product prioritization, inventory risk assessment, and the potential application of optimization techniques to stocking and pricing.

### Digital Supply Chain Management (DSCM)

The project supports the broader DSCM goal of connecting digital data and external signals to inventory visibility and actionable recommendations.

Together, OR and DSCM provide the foundation for moving from inventory monitoring toward evidence-based operational decisions.

## System Architecture

The current codebase is organized into modular components:

1. **API layer:** FastAPI application in `main.py`.
2. **Inventory analysis:** Pipeline components for processing product data and identifying inventory pain points.
3. **External signals:** Services for collecting and analyzing external signals.
4. **Decision engine:** Logic for evaluating products and producing recommendations.
5. **Data outputs:** CSV-based analysis results and recommendation records.

The proposed system can be extended with demand forecasting, news-event classification, uncertainty estimation, and constrained optimization.

## Technology Stack

- **Language:** Python
- **API framework:** FastAPI
- **Data processing:** Pandas, NumPy
- **Machine learning:** XGBoost, SHAP
- **External signal analysis:** PRAW, VADER Sentiment
- **Server:** Uvicorn
- **Validation and configuration:** Pydantic, python-dotenv

## Project Structure

```text
Nexora/
├── app/
│   ├── core/
│   └── modules/
├── external_signal_service/
├── inventory_painpoints_service/
├── main.py
├── requirements.txt
├── .gitignore
├── literature_review_and_gap_analysis.md
└── literature_review_and_gap_analysis.txt
```

The exact modules and supporting files may evolve as development progresses.

## Getting Started

### Prerequisites

- Python installed
- Git
- A terminal or code editor such as VS Code

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Nexora
```

Replace the placeholder with the repository URL after publishing the project.

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Dependency compatibility and any additional setup requirements should be verified before running the application.

### 4. Start the API server

```bash
python -m uvicorn main:app --reload
```

The application is configured to run locally using Uvicorn. Successful startup may depend on the availability of the required input data and generated analysis files.

### 5. Explore the API

Once the server starts, open:

- `http://127.0.0.1:8000/docs` — interactive API documentation
- `http://127.0.0.1:8000/health` — service health endpoint

The application also defines endpoints for running the inventory pipeline, retrieving analysis results, obtaining product-level decisions, and viewing recommendations.

## Research and Evaluation Direction

The broader project direction includes evaluating the value of external signals for demand forecasting and inventory decisions.

Potential evaluation areas include:

- Forecast accuracy against baseline methods
- Inventory availability and stockout rates
- Expiry-related waste
- Contribution margin and operational costs
- Performance with and without external signals

These are evaluation objectives, not claimed experimental results. Quantitative improvements should be reported only after appropriate testing.

## Current Status

Nexora is an evolving academic project combining AI, inventory intelligence, and supply-chain decision support. The implementation and research direction may expand as additional forecasting and optimization components are developed and evaluated.

## Team

Developed as a group academic project focused on Operational Research and Digital Supply Chain Management.

## License

A license can be added once the project team has agreed on the terms for sharing and reuse.
