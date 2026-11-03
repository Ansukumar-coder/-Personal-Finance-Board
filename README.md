# -Personal-Finance-Board
Personal Finance Dashboard is an end-to-end data project that turns messy bank transaction CSV files into an interactive dashboard.
# 💰 Personal Finance Dashboard

An end-to-end data project: **messy CSV → pandas cleaning → analysis → Plotly charts → Streamlit app.**

## Features
- Upload your own bank/UPI CSV or use generated sample data
- Automated cleaning: mixed date formats, currency symbols (₹, Rs., commas), duplicates,
  inconsistent casing/whitespace, missing categories (inferred from keywords), bad rows dropped
- KPIs: income, expenses, net savings, savings rate
- Charts: monthly income vs expense, cumulative balance, savings rate, category bar + donut,
  budget vs actual, rolling expense trend, weekday/month heatmap, top merchants
- Sidebar filters (date, category, account) and cleaned-CSV download
- In-app **cleaning report** showing exactly what was fixed

## Run it
```bash
python -m venv venv
venv\Scripts\activate          
pip install -r requirements.txt
python generate_sample.py      
streamlit run app.py
```

## CSV format
Required columns: `date`, `description`, `amount`.
Optional: `category`, `type` (income/expense, credit/debit), `account`.

## Project structure
```
app.py               Streamlit UI
generate_sample.py   Synthetic messy data generator
src/cleaning.py      pandas cleaning pipeline + report
src/analysis.py      KPIs, monthly/category summaries, budgets
src/charts.py        Plotly figure builders
```

> Sample data is synthetic. Never commit real financial data (`data/` is git-ignored).

## Ideas to extend
Auto-categorization with scikit-learn, next-month spend forecast, recurring-payment detection,
multi-currency support, deploy on Streamlit Community Cloud.
