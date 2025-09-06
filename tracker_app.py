import streamlit as st
import pandas as pd

# File where expenses will be saved
CSV_FILE = "expenses.csv"

# Load or create a simple CSV file
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Category", "Amount"])

st.title("💰 Personal Expense Tracker")

# Section: Add new expense
st.subheader("Add Expense")
date = st.date_input("Date")
category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"])
amount = st.number_input("Amount (RM)", min_value=0.0, step=0.5)

if st.button("Add"):
    new_expense = pd.DataFrame({"Date": [date], "Category": [category], "Amount": [amount]})
    df = pd.concat([df, new_expense], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success("✅ Expense added!")

# Section: Show all expenses
st.subheader("All Expenses")
st.dataframe(df)

# Section: Summary by category
st.subheader("Summary by Category")
if not df.empty:
    summary = df.groupby("Category")["Amount"].sum()
    st.bar_chart(summary)
else:
    st.info("No data yet. Add your first expense above ⬆️")
