import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ------------------------------
# App Title
# ------------------------------
st.title("💰 Personal Finance Tracker")

# ------------------------------
# Sidebar Navigation
# ------------------------------
menu = ["Dashboard", "Add Transaction", "Accounts", "Fixed Expenses", "Goals", "Net Balance"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------------------
# Sample DataFrames (In-Memory)
# ------------------------------
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Type'])
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = pd.DataFrame(columns=['Bank', 'Balance'])
if 'fixed_expenses' not in st.session_state:
    st.session_state['fixed_expenses'] = pd.DataFrame(columns=['Expense', 'Amount'])
if 'goals' not in st.session_state:
    st.session_state['goals'] = pd.DataFrame(columns=['Goal', 'Target Amount', 'Current Amount'])

# Shortcuts
transactions_df = st.session_state['transactions']
accounts_df = st.session_state['accounts']
fixed_expenses_df = st.session_state['fixed_expenses']
goals_df = st.session_state['goals']

# ------------------------------
# Dashboard Page
# ------------------------------
if choice == "Dashboard":
    st.header("📊 Dashboard Overview")

    st.subheader("Accounts Overview")
    if not accounts_df.empty:
        st.dataframe(accounts_df)
        st.write("**Total Savings:** RM", accounts_df['Balance'].sum())
    else:
        st.info("Add your bank accounts in the 'Accounts' section.")

    st.subheader("Fixed Expenses")
    if not fixed_expenses_df.empty:
        st.dataframe(fixed_expenses_df)
        st.write("**Total Fixed Expenses:** RM", fixed_expenses_df['Amount'].sum())
    else:
        st.info("Add your monthly fixed expenses in the 'Fixed Expenses' section.")

    st.subheader("Goals")
    if not goals_df.empty:
        st.dataframe(goals_df)
    else:
        st.info("Add your financial goals in the 'Goals' section.")

# ------------------------------
# Add Transaction Page
# ------------------------------
elif choice == "Add Transaction":
    st.header("➕ Add Transaction")
    t_date = st.date_input("Date", date.today())
    t_type = st.selectbox("Type", ["Income", "Expense"])
    t_category = st.text_input("Category / Description")
    t_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.1)

    if st.button("Add Transaction"):
        new_transaction = pd.DataFrame({
            'Date': [t_date],
            'Category': [t_category],
            'Amount': [t_amount],
            'Type': [t_type]
        })
        st.session_state['transactions'] = pd.concat([transactions_df, new_transaction], ignore_index=True)
        st.success("Transaction added successfully!")

    if not transactions_df.empty:
        st.subheader("All Transactions")
        st.dataframe(transactions_df)

# ------------------------------
# Accounts Page
# ------------------------------
elif choice == "Accounts":
    st.header("🏦 Bank Accounts / Savings")
    bank = st.text_input("Bank Name")
    balance = st.number_input("Balance (RM)", min_value=0.0, step=0.1)

    if st.button("Add Account"):
        new_acc = pd.DataFrame({'Bank': [bank], 'Balance': [balance]})
        st.session_state['accounts'] = pd.concat([accounts_df, new_acc], ignore_index=True)
        st.success("Account added!")

    if not accounts_df.empty:
        st.subheader("All Accounts")
        st.dataframe(accounts_df)

# ------------------------------
# Fixed Expenses Page
# ------------------------------
elif choice == "Fixed Expenses":
    st.header("📌 Fixed Monthly Expenses")
    expense = st.text_input("Expense Name")
    amount = st.number_input("Amount (RM)", min_value=0.0, step=0.1)

    if st.button("Add Fixed Expense"):
        new_fixed = pd.DataFrame({'Expense': [expense], 'Amount': [amount]})
        st.session_state['fixed_expenses'] = pd.concat([fixed_expenses_df, new_fixed], ignore_index=True)
        st.success("Fixed expense added!")

    if not fixed_expenses_df.empty:
        st.subheader("All Fixed Expenses")
        st.dataframe(fixed_expenses_df)

# ------------------------------
# Goals Page
# ------------------------------
elif choice == "Goals":
    st.header("🎯 Financial Goals")
    goal = st.text_input("Goal Name")
    target = st.number_input("Target Amount (RM)", min_value=0.0, step=0.1)
    current = st.number_input("Current Amount (RM)", min_value=0.0, step=0.1)

    if st.button("Add Goal"):
        new_goal = pd.DataFrame({
            'Goal': [goal],
            'Target Amount': [target],
            'Current Amount': [current]
        })
        st.session_state['goals'] = pd.concat([goals_df, new_goal], ignore_index=True)
        st.success("Goal added!")

    if not goals_df.empty:
        st.subheader("All Goals")
        st.dataframe(goals_df)

# ------------------------------
# Net Balance Over Time Page
# ------------------------------
elif choice == "Net Balance":
    st.header("📈 Net Balance Over Time")

    if transactions_df.empty:
        st.info("Add some transactions first!")
    else:
        # Prepare transactions
        variable_expenses_df = transactions_df[transactions_df['Type'] == "Expense"].copy()
        variable_expenses_df['Date'] = pd.to_datetime(variable_expenses_df['Date'])
        variable_expenses_df = variable_expenses_df.sort_values('Date')
        variable_expenses_df['Cumulative'] = variable_expenses_df['Amount'].cumsum()

        # Total accounts
        total_balance = accounts_df['Balance'].sum() if not accounts_df.empty else 0.0

        # Total fixed expenses
        fixed_total = fixed_expenses_df['Amount'].sum() if not fixed_expenses_df.empty else 0.0

        # Net balance calculation
        net_balance_df = variable_expenses_df[['Date', 'Cumulative']].copy()
        net_balance_df['Net Balance'] = total_balance - fixed_total - net_balance_df['Cumulative']

        st.dataframe(net_balance_df)

        # Line chart
        fig_net = px.line(net_balance_df, x='Date', y='Net Balance', markers=True, title="Net Balance Over Time")
        st.plotly_chart(fig_net, use_container_width=True)
