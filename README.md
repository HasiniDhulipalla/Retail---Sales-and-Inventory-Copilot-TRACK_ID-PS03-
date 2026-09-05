# Sellix Retail Sales and Inventory Copilot

TRACK_ID=PS03

Sellix is a Python-based retail decision assistant built with Streamlit and FastAPI. It helps small retail businesses understand sales performance, inventory risk, excess stock, non-moving items, and action priorities using explainable business logic.

## Demo Video

Watch the product demo here:

[Sellix Demo Video](https://drive.google.com/file/d/1j8yLVrhs1qVAms8MLOyLxjf5MObqGGLA/view?usp=drive_link)

## Overview

This project turns real retail data into practical recommendations. It highlights:

- products that may run out soon
- inventory that is overstocked
- items that are not selling
- sales trends and attention-priority issues
- business explanations backed by real records and logic

The application is designed for retail managers and store teams who need quick, understandable insights without needing advanced BI tooling.

## Features

- SQLite + SQLAlchemy models for stores, products, sales, and inventory
- deterministic 50-product, 3-store, 90-day demo dataset
- dashboard KPIs and Plotly-based inventory risk visualizations
- stock-out DOI analysis, overstock detection, and non-moving product checks
- explainable recommendations with formulas, records, assumptions, and time period
- multilingual Streamlit interface with fallback behavior when Gemini is unavailable
- FastAPI endpoints for health checks, catalog data, dashboard metrics, and copilot queries
- CSV validation utilities and Excel-capable dependencies
- photo analysis, voice transcription, and translation support through Gemini

## Architecture

Gemini can help interpret user intent, translate responses, process images, and transcribe voice input. Python handles the business calculations and generates explainable outputs from verified data. The system is designed to avoid generated SQL or fabricated business numbers.

The fallback parser supports stock-out, overstock, non-moving, sales, spike/drop, store, and attention-related questions.

## Tech Stack

- Python 3.11
- Streamlit
- FastAPI
- SQLAlchemy
- SQLite
- Plotly
- Pandas
- Google Gemini API

## Project Structure

```text
hasini hackthon vscode/
├── app.py
├── README.md
├── requirements.txt
├── ai/
│   ├── __init__.py
│   ├── gemini_client.py
│   ├── intent_parser.py
│   ├── response_generator.py
│   └── translator.py
├── backend/
│   ├── __init__.py
│   ├── api.py
│   ├── calculations.py
│   ├── data_generator.py
│   ├── database.py
│   ├── forecasting.py
│   ├── main.py
│   ├── models.py
│   ├── recommendations.py
│   └── schemas.py
├── frontend/
│   ├── __init__.py
│   ├── analytics.py
│   ├── attention.py
│   ├── components.py
│   ├── copilot.py
│   ├── dashboard.py
│   ├── forecast.py
│   ├── inventory.py
│   └── reports.py
├── utils/
│   ├── __init__.py
│   ├── formatting.py
│   └── validators.py
└── assets/
```

## Run Locally

Create the virtual environment and install dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the Streamlit app:

```powershell
streamlit run app.py
```

The application creates a `retail.db` file and generates demo data on first launch.

Run the API separately:

```powershell
uvicorn backend.main:app --reload
```

Configure Gemini for translation, image understanding, and transcription:

```powershell
Copy-Item .env.example .env
# Edit .env and replace your_gemini_api_key_here with a valid key from https://aistudio.google.com/apikey
streamlit run app.py --server.port 8000
```

> Never commit a real API key, share it in chat, or store it in a file that is pushed to source control. If a key was exposed, revoke it and generate a new one.

Without a valid Gemini key, the dashboard and rule-based copilot still work, while AI features show a provider error.

## API Endpoints

The backend exposes the following main routes:

- `GET /api/health`
- `GET /api/stores`
- `GET /api/products`
- `GET /api/dashboard`
- `GET /api/stockout`
- `GET /api/overstock`
- `GET /api/non-moving`
- `GET /api/product/{product_id}`
- `POST /api/copilot/query`
- `POST /api/translate`

## Demo Flow

1. Open the dashboard and review the KPI cards.
2. Check the inventory and risk sections for stock-out or overstock signals.
3. Ask the assistant what is running out or what needs attention.
4. Change the display language to test the fallback multilingual behavior.
5. Upload a product image to inspect shelf or packaging issues in the photo checker.

## Future Enhancements

- authenticated CSV import into staging tables
- deeper anomaly and trend analytics
- stronger Gemini intent validation
- report export features
- production-grade translation prompts that preserve verified numeric values

## License

This project is intended for educational and demo purposes within the hackathon context.
