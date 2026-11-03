import io
from pathlib import Path

import pandas as pd
import streamlit as st

from generate_sample import generate
from src import analysis, charts, cleaning

SAMPLE_PATH = Path("data/raw/transactions.csv")
CURRENCY = "₹"

st.set_page_config(page_title="Personal Finance Dashboard", page_icon="💰", layout="wide")


@st.cache_data(show_spinner="Cleaning data...")
def load_and_clean(file_bytes: bytes):
    raw = pd.read_csv(io.BytesIO(file_bytes))
    return cleaning.clean_transactions(raw)
def money(x: float) -> str:
    return f"{CURRENCY}{x:,.0f}"
st.sidebar.title("💰 Finance Dashboard")
source = st.sidebar.radio("Data source", ["Sample data", "Upload my CSV"])

if source == "Upload my CSV":
    uploaded = st.sidebar.file_uploader("CSV with: date, description, amount "
                                        "(+ category, type, account)", type="csv")
    if uploaded is None:
        st.info("Upload a CSV in the sidebar, or switch to **Sample data**.")
        st.stop()
    file_bytes = uploaded.getvalue()
else:
    if not SAMPLE_PATH.exists():
        generate(SAMPLE_PATH)
    file_bytes = SAMPLE_PATH.read_bytes()

try:
    df, report = load_and_clean(file_bytes)
except Exception as e:  # bad file, missing columns, etc.
    st.error(f"Could not process this file: {e}")
    st.stop()

if df.empty:
    st.warning("No valid rows after cleaning.")
    st.stop()
st.sidebar.subheader("Filters")
min_d, max_d = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_d, max_d

cats = sorted(df["category"].unique())
sel_cats = st.sidebar.multiselect("Categories", cats, default=cats)
accts = sorted(df["account"].unique())
sel_accts = st.sidebar.multiselect("Accounts", accts, default=accts)

mask = (
    df["date"].dt.date.between(start, end)
    & df["category"].isin(sel_cats)
    & df["account"].isin(sel_accts)
)
view = df[mask]
if view.empty:
    st.warning("No transactions match the current filters.")
    st.stop()
st.title("Personal Finance Dashboard")
k = analysis.kpis(view)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total income", money(k["income"]))
c2.metric("Total expenses", money(k["expenses"]))
c3.metric("Net savings", money(k["net"]))
c4.metric("Savings rate", f"{k['savings_rate']:.1f}%")

monthly = analysis.monthly_summary(view)
cat_summary = analysis.category_summary(view)

tab_over, tab_cat, tab_trend, tab_data = st.tabs(["Overview", "Categories", "Trends", "Data & cleaning"])

with tab_over:
    st.plotly_chart(charts.monthly_income_expense(monthly), use_container_width=True)
    left, right = st.columns(2)
    left.plotly_chart(charts.cumulative_balance(analysis.cumulative_balance(view)), use_container_width=True)
    right.plotly_chart(charts.savings_rate(monthly), use_container_width=True)

with tab_cat:
    if cat_summary.empty:
        st.info("No expenses in this selection.")
    else:
        left, right = st.columns(2)
        left.plotly_chart(charts.category_bar(cat_summary), use_container_width=True)
        right.plotly_chart(charts.category_donut(cat_summary), use_container_width=True)

        st.subheader("Budget vs actual")
        st.caption("Edit the monthly budgets below. Actual = average monthly spend in the selected range.")
        budget_df = pd.DataFrame({"category": list(analysis.DEFAULT_BUDGETS),
                                  "budget": list(analysis.DEFAULT_BUDGETS.values())})
        edited = st.data_editor(budget_df, hide_index=True, disabled=["category"], key="budgets")
        bva = analysis.budget_vs_actual(view, dict(zip(edited["category"], edited["budget"])))
        st.plotly_chart(charts.budget_chart(bva), use_container_width=True)
        over = bva[bva["status"] == "Over budget"]
        if not over.empty:
            st.warning("Over budget: " + ", ".join(
                f"{r.category} (+{money(-r.difference)})" for r in over.itertuples()))

with tab_trend:
    st.plotly_chart(charts.expense_trend(monthly), use_container_width=True)
    left, right = st.columns(2)
    left.plotly_chart(charts.weekday_heatmap(analysis.weekday_month_matrix(view)), use_container_width=True)
    right.plotly_chart(charts.top_merchants_bar(analysis.top_merchants(view)), use_container_width=True)

with tab_data:
    st.subheader("Cleaning report")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Raw rows", report["rows_raw"])
    r2.metric("Duplicates removed", report["duplicates_removed"])
    r3.metric("Bad dates dropped", report["invalid_dates_dropped"])
    r4.metric("Bad amounts dropped", report["invalid_amounts_dropped"])
    r5.metric("Categories filled", report["categories_filled"])

    st.subheader("Transactions")
    st.dataframe(view.drop(columns=["signed_amount"]), use_container_width=True, hide_index=True)
    st.download_button("Download cleaned CSV", view.to_csv(index=False).encode("utf-8"),
                       file_name="cleaned_transactions.csv", mime="text/csv")
