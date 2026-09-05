from __future__ import annotations

import os
import subprocess
import sys

import streamlit as st

from backend.calculations import dashboard, non_moving, overstock, stockout
from backend.database import get_session, init_db
from backend.models import Store


def run_dashboard() -> None:
    init_db()
    st.set_page_config(page_title="Sellix Retail Copilot", page_icon="📦", layout="wide")

    def render_metric(label: str, value: str, delta: str | None = None, color: str = "#4dabf7") -> None:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(17,24,39,0.95), rgba(31,41,55,0.95));
                border: 1px solid rgba(148,163,184,0.25);
                border-radius: 14px;
                padding: 1rem 1.2rem;
                min-height: 120px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.18);
            ">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em;">{label}</div>
                <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-top: 0.6rem;">{value}</div>
                {f'<div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.3rem;">{delta}</div>' if delta else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.sidebar:
        st.header("Filters")
        with get_session() as session:
            stores = session.query(Store).all()
        store_options = [None] + [store.store_id for store in stores]
        selected_store = st.selectbox(
            "Store",
            options=store_options,
            format_func=lambda store_id: "All stores" if store_id is None else next((s.store_name for s in stores if s.store_id == store_id), str(store_id)),
        )

    st.title("Sellix Retail Sales and Inventory Copilot")
    st.caption("Inventory health, sales trends, and action priorities for retail operations.")

    with get_session() as session:
        metrics = dashboard(session, selected_store)
        risk_df = stockout(session, selected_store)
        overstock_df = overstock(session, selected_store)
        non_moving_df = non_moving(session, selected_store)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Sales today", f"₹{metrics['today_sales']:.2f}")
    with col2:
        render_metric("Monthly sales", f"₹{metrics['monthly_sales']:.2f}")
    with col3:
        render_metric("Units sold", f"{metrics['units_sold']:,}")
    with col4:
        render_metric("Current inventory", f"{metrics['current_inventory']:,}")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        render_metric("Low stock", f"{metrics['low_stock']}", "Needs attention")
    with col6:
        render_metric("May run out", f"{metrics['predicted_stockouts']}", "Risk watch")
    with col7:
        render_metric("Overstocked", f"{metrics['overstocked']}", "Excess stock")
    with col8:
        render_metric("Not moving", f"{metrics['non_moving']}", "Inventory dead weight")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["Risk Overview", "Stockout Items", "Overstock", "Non-Moving"])

    with tab1:
        st.subheader("Operational summary")
        st.dataframe(risk_df.head(10), use_container_width=True)

    with tab2:
        st.subheader("Products likely to run out")
        if risk_df.empty:
            st.info("No stockout risk items found for the selected store.")
        else:
            st.dataframe(risk_df, use_container_width=True)

    with tab3:
        st.subheader("Overstocked products")
        if overstock_df.empty:
            st.info("No overstocked products found for the selected store.")
        else:
            st.dataframe(overstock_df, use_container_width=True)

    with tab4:
        st.subheader("Non-moving products")
        if non_moving_df.empty:
            st.info("No non-moving products found for the selected store.")
        else:
            st.dataframe(non_moving_df, use_container_width=True)

    st.markdown("---")

    with st.expander("Business explanation"):
        st.write(
            "The dashboard prioritizes products with the highest risk to stock out, excess inventory, and low recent sales movement. "
            "These signals are calculated from recent sales velocity, reorder thresholds, and current inventory levels."
        )


if __name__ == "__main__":
    if os.environ.get("SELLIX_STREAMLIT_READY") == "1":
        run_dashboard()
    else:
        env = os.environ.copy()
        env["SELLIX_STREAMLIT_READY"] = "1"
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", __file__, "--server.address", "0.0.0.0", "--server.port", "8000"],
            env=env,
            check=False,
        )
