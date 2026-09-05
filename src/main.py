from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from ai.intent_parser import parse_intent
from ai.response_generator import verified_response
from ai.translator import translate
from .calculations import dashboard, frame, non_moving, overstock, product_performance, stockout
from .database import get_session, init_db
from .forecasting import forecast
from .models import Inventory, Product, Sale, Store
from .schemas import CopilotRequest, CopilotResponse, TranslateRequest

app = FastAPI(title="Retail Sales and Inventory Copilot", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()

INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Sellix Retail Copilot</title>
    <style>
      :root {
        --bg: #0f172a;
        --panel: #111827;
        --muted: #94a3b8;
        --accent: #22c55e;
        --text: #e5e7eb;
        --card: #1f2937;
        --border: #374151;
      }
      body { font-family: Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; }
      .container { max-width: 1200px; margin: 0 auto; padding: 32px 20px 48px; }
      .topbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
      .brand { font-size: 2rem; font-weight: 700; }
      .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin:18px 0 30px; }
      .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; }
      .label { color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; }
      .value { font-size: 2rem; font-weight: 700; margin-top: 8px; }
      table { width:100%; border-collapse: collapse; margin-top:12px; }
      th, td { border-bottom:1px solid var(--border); padding:10px; text-align:left; }
      th { color: var(--muted); font-size: 0.8rem; text-transform: uppercase; }
      pre { white-space: pre-wrap; background:#0b1120; border:1px solid var(--border); border-radius:10px; padding:12px; }
      .muted { color: var(--muted); }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="topbar">
        <div class="brand">Sellix Retail Copilot</div>
        <div class="muted">Live retail dashboard</div>
      </div>
      <div class="grid" id="metrics"></div>
      <div class="card">
        <h2>Products at risk</h2>
        <div id="risk-table"></div>
      </div>
      <div class="card" style="margin-top:20px;">
        <h2>AI copilot</h2>
        <p class="muted">Ask: Which products may run out soon?</p>
        <input id="question" type="text" value="Which products may run out soon?" style="width:100%; padding:12px; border-radius:8px; border:1px solid var(--border); background:#0b1120; color:var(--text); margin-bottom:12px;" />
        <button id="ask" style="padding:10px 18px; border:none; border-radius:8px; background:var(--accent); color:#06270f; font-weight:700; cursor:pointer;">Ask Sellix</button>
        <pre id="copilot-response">Loading...</pre>
      </div>
    </div>
    <script>
      async function fetchJson(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Request failed: ' + url);
        return response.json();
      }

      async function loadDashboard() {
        const metrics = await fetchJson('/api/dashboard');
        const risk = await fetchJson('/api/stockout');
        const metricList = [
          ['Sales today', '₹' + Number(metrics.today_sales || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })],
          ['Sales this month', '₹' + Number(metrics.monthly_sales || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })],
          ['Units sold', Number(metrics.units_sold || 0).toLocaleString()],
          ['Current inventory', Number(metrics.current_inventory || 0).toLocaleString()],
          ['Low stock', Number(metrics.low_stock || 0)],
          ['May run out soon', Number(metrics.predicted_stockouts || 0)],
          ['Overstocked', Number(metrics.overstocked || 0)],
          ['Not moving', Number(metrics.non_moving || 0)]
        ];

        document.getElementById('metrics').innerHTML = metricList
          .map(([label, value]) => `
            <div class="card">
              <div class="label">${label}</div>
              <div class="value">${value}</div>
            </div>
          `).join('');

        const rows = risk.slice(0, 8);
        document.getElementById('risk-table').innerHTML = rows.length ? `
          <table>
            <thead>
              <tr><th>Product</th><th>Status</th><th>DOI</th><th>Closing stock</th></tr>
            </thead>
            <tbody>
              ${rows.map(item => `
                <tr>
                  <td>${item.product_name || 'Unknown'}</td>
                  <td>${item.status || 'WARNING'}</td>
                  <td>${Number(item.doi || 0).toFixed(1)}</td>
                  <td>${Number(item.closing_stock || 0)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        ` : '<p class="muted">No stock risk items found.</p>';
      }

      document.getElementById('ask').addEventListener('click', async () => {
        const question = document.getElementById('question').value;
        const response = await fetch('/api/copilot/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, store_id: null, language: 'English' })
        });
        const json = await response.json();
        document.getElementById('copilot-response').textContent = json.answer || JSON.stringify(json, null, 2);
      });

      loadDashboard().catch(err => {
        document.getElementById('copilot-response').textContent = err.message;
      });
    </script>
  </body>
</html>
"""


def records(df):
    if df is None or df.empty:
        return []
    return [{
        k: (
            v.item() if hasattr(v, "item")
            else v.isoformat() if hasattr(v, "isoformat")
            else v
        )
        for k, v in row.items()
    } for row in df.to_dict("records")]


@app.get("/", response_class=HTMLResponse)
def landing_page():
    return HTMLResponse(INDEX_HTML)


@app.get("/api/health")
def health():
    return {"status": "ok", "date": date.today().isoformat()}


@app.get("/api/stores")
def stores():
    with get_session() as s:
        return [{"store_id": x.store_id, "store_name": x.store_name, "city": x.city, "region": x.region} for x in s.query(Store).all()]


@app.get("/api/products")
def products():
    with get_session() as s:
        return [{"product_id": x.product_id, "product_name": x.product_name, "category": x.category, "brand": x.brand, "unit_price": float(x.unit_price)} for x in s.query(Product).all()]


@app.get("/api/sales")
def sales():
    with get_session() as s:
        return records(frame(s, Sale))


@app.get("/api/inventory")
def inventory():
    with get_session() as s:
        return records(frame(s, Inventory))


@app.get("/api/dashboard")
def dashboard_api(store_id: int | None = None):
    with get_session() as s:
        return dashboard(s, store_id)


@app.get("/api/stockout")
def stockout_api(store_id: int | None = None):
    with get_session() as s:
        return records(stockout(s, store_id))


@app.get("/api/overstock")
def overstock_api(store_id: int | None = None):
    with get_session() as s:
        return records(overstock(s, store_id))


@app.get("/api/non-moving")
def non_moving_api(store_id: int | None = None):
    with get_session() as s:
        return records(non_moving(s, store_id))


@app.get("/api/forecast")
def forecast_api(product_id: int | None = None, store_id: int | None = None):
    with get_session() as s:
        return forecast(s, product_id, store_id)


@app.get("/api/attention")
def attention_api(store_id: int | None = None):
    with get_session() as s:
        return records(stockout(s, store_id).head(20))


@app.get("/api/anomalies")
def anomalies_api(store_id: int | None = None):
    with get_session() as s:
        return {"sales_spikes": [], "sales_drops": [], "note": "Anomaly results require sufficient daily history; use the verified inventory risk endpoints for current alerts."}


@app.get("/api/product/{product_id}")
def product_api(product_id: int):
    with get_session() as s:
        result = product_performance(s, product_id)
        if result is None:
            raise HTTPException(404, "Product not found")
        return result


@app.post("/api/copilot/query", response_model=CopilotResponse)
def copilot(request: CopilotRequest):
    intent = parse_intent(request.question)["intent"]
    with get_session() as s:
        if intent == "stockout":
            df = stockout(s, request.store_id)
        elif intent == "overstock":
            df = overstock(s, request.store_id)
        elif intent == "non_moving":
            df = non_moving(s, request.store_id)
        elif intent == "attention_today":
            df = stockout(s, request.store_id)
        else:
            df = stockout(s, request.store_id) if intent == "unknown" else overstock(s, request.store_id)
        details = records(df.head(20))
        answer, calc = verified_response(intent, details, "last 30 days")
    return CopilotResponse(
        intent=intent,
        answer=translate(answer, request.language),
        numbers=details[:5],
        calculation=calc,
        data_period="Last 30 days",
        assumptions=["Recent demand is approximately stable."],
        data_sufficiency="Sufficient Data" if details else "Insufficient Data",
        details=details,
    )


@app.post("/api/translate")
def translate_api(request: TranslateRequest):
    return {"text": translate(request.text, request.language), "language": request.language}

