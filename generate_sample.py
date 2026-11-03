"""Generate a deliberately MESSY synthetic transactions CSV.

Run:  python generate_sample.py
Output: data/raw/transactions.csv

The mess (mixed date formats, currency symbols, duplicates, missing
categories, inconsistent casing/whitespace) gives the cleaning step
real work to do.
"""
from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd

OUT_PATH = Path("data/raw/transactions.csv")

EXPENSE_TEMPLATES = {
    "Food":          ["Swiggy Order", "Zomato Order", "Dominos Pizza", "Local Dhaba", "Cafe Coffee Day"],
    "Groceries":     ["Big Bazaar", "DMart", "Reliance Fresh", "Vegetable Vendor"],
    "Transport":     ["Uber Ride", "Ola Cab", "Petrol Pump", "Metro Recharge"],
    "Shopping":      ["Amazon Purchase", "Flipkart Order", "Myntra Fashion", "Decathlon"],
    "Entertainment": ["Netflix", "Spotify", "BookMyShow Tickets", "Steam Games"],
    "Health":        ["Apollo Pharmacy", "Gym Membership", "Doctor Consultation"],
    "Education":     ["Udemy Course", "Coursera", "Stationery Store"],
}
AMOUNT_RANGE = {
    "Food": (120, 900), "Groceries": (300, 2500), "Transport": (80, 900),
    "Shopping": (500, 4500), "Entertainment": (149, 900),
    "Health": (200, 2000), "Education": (300, 3000),
}
DATE_FORMATS = ["%d-%m-%Y", "%d %b %Y", "%Y/%m/%d"]


def _messy_amount(value: float) -> str:
    style = random.choice(["plain", "rupee", "rs", "comma"])
    if style == "rupee":
        return f"₹{value:,.2f}"
    if style == "rs":
        return f"Rs. {value:.0f}"
    if style == "comma":
        return f"{value:,.2f}"
    return f"{value:.2f}"


def generate(path: Path = OUT_PATH, months: int = 12, seed: int = 42) -> Path:
    random.seed(seed)
    end = date.today()
    start = (end - timedelta(days=30 * months)).replace(day=1)
    rows = []

    day = start
    while day <= end:
        # monthly fixed items
        if day.day == 1:
            rows.append((day, "Salary - Company Pvt Ltd", "Salary", 65000, "income", "Bank"))
            rows.append((day, "Rent Payment", "Rent", 15000, "expense", "Bank"))
        if day.day == 5:
            rows.append((day, "Electricity Bill", "Bills", random.randint(900, 2200), "expense", "Bank"))
            rows.append((day, "Mobile Recharge", "Bills", 399, "expense", "UPI"))
        if day.day == 15 and random.random() < 0.4:
            rows.append((day, "Freelance Project", "Freelance", random.randint(3000, 12000), "income", "UPI"))

        # random daily spending
        for _ in range(random.choice([0, 0, 1, 1, 2])):
            cat = random.choice(list(EXPENSE_TEMPLATES))
            desc = random.choice(EXPENSE_TEMPLATES[cat])
            lo, hi = AMOUNT_RANGE[cat]
            rows.append((day, desc, cat, round(random.uniform(lo, hi), 2), "expense",
                         random.choice(["UPI", "Credit Card", "Cash", "Bank"])))
        day += timedelta(days=1)

    df = pd.DataFrame(rows, columns=["Date", "Description", "Category", "Amount", "Type", "Account"])

    # ---- make it messy ----
    df["Date"] = [d.strftime(random.choice(DATE_FORMATS)) for d in df["Date"]]
    df["Amount"] = [_messy_amount(a) for a in df["Amount"]]
    df["Description"] = [
        random.choice([s, s.upper(), s.lower(), f"  {s}  "]) if random.random() < 0.3 else s
        for s in df["Description"]
    ]
    df["Type"] = [random.choice([t, t.upper(), t.capitalize()]) if random.random() < 0.3 else t
                  for t in df["Type"]]

    # blank out some categories (cleaning step will infer them)
    mask = df.sample(frac=0.08, random_state=seed).index
    df.loc[mask, "Category"] = random.choice([None])
    # a few unparseable / missing values
    bad = df.sample(n=4, random_state=seed + 1).index
    df.loc[bad[:2], "Date"] = "not available"
    df.loc[bad[2:], "Amount"] = "N/A"
    # duplicates
    df = pd.concat([df, df.sample(n=12, random_state=seed)], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    p = generate()
    print(f"Sample data written to {p}")
