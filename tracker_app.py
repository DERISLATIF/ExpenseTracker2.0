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
menu = ["Dashboard", "Add Transaction", "Accounts", "Goals", "Net Balance"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------------------
# Sample DataFrames (In-Memory)
# ------------------------------
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Account', 'Note', 'Type'])
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = pd.DataFrame(columns=['Bank', 'Balance'])
if 'goals' not in st.session_state:
    st.session_state['goals'] = pd.DataFrame(columns=['Goal', 'Target Amount', 'Current Amount'])

transactions_df = st.session_state['transactions']
accounts_df = st.session_state['accounts']
goals_df = st.session_state['goals']

# Predefined expense categories
expense_categories = ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Education", "Other"]

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

    st.subheader("Goals")
    if not goals_df.empty:
        st.dataframe(goals_df)
    else:
        st.info("Add your financial goals in the 'Goals' section.")

    st.subheader("Expenses by Category")
    expense_df = transactions_df[transactions_df['Type'] == "Expense"]
    if not expense_df.empty:
        category_summary = expense_df.groupby('Category')['Amount'].sum().reset_index()
        fig_expense = px.pie(category_summary, names='Category', values='Amount', title="Expenses by Category")
        st.plotly_chart(fig_expense, use_container_width=True)

        # Monthly spending per category
        expense_df['Month'] = expense_df['Date'].dt.to_period('M').astype(str)
        monthly_summary = expense_df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
        fig_monthly = px.bar(monthly_summary, x='Month', y='Amount', color='Category', barmode='group',
                             title="Monthly Spending by Category")
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.info("Add some expenses to see category distribution and monthly trend.")

# ------------------------------
# Add Transaction Page
# ------------------------------
elif choice == "Add Transaction":
    st.header("➕ Add Transaction")
    t_date = st.date_input("Date", date.today())
    t_type = st.selectbox("Type", ["Income", "Expense"])

    # Select account for the transaction
    account_options = accounts_df['Bank'].tolist() if not accounts_df.empty else []
    selected_account = st.selectbox("Select Account", ["--Select--"] + account_options)

    # Expense category
    if t_type == "Expense":
        t_category = st.selectbox("Category", expense_categories)
        note = st.text_input("Note (if 'Other', describe the expense)")
    else:
        t_category = st.text_input("Category / Description")
        note = ""

    t_amount = st.number_input("Amount (RM)", min_value=0.0, step=0.1)

    if st.button("Add Transaction"):
        if t_type == "Expense" and selected_account == "--Select--":
            st.warning("Please select an account for the expense.")
        else:
            new_transaction = pd.DataFrame({
                'Date': [t_date],
                'Category': [t_category],
                'Amount': [t_amount],
                'Account': [selected_account if t_type=="Expense" else ""],
                'Note': [note],
                'Type': [t_type]
            })
            st.session_state['transactions'] = pd.concat([transactions_df, new_transaction], ignore_index=True)

            # Deduct from account if expense
            if t_type == "Expense" and selected_account in accounts_df['Bank'].values:
                idx = accounts_df.index[accounts_df['Bank'] == selected_account][0]
                accounts_df.at[idx, 'Balance'] -= t_amount
                st.session_state['accounts'] = accounts_df

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
    balance = st.number_input("Initial Balance (RM)", min_value=0.0, step=0.1)

    if st.button("Add Account"):
        new_acc = pd.DataFrame({'Bank': [bank], 'Balance': [balance]})
        st.session_state['accounts'] = pd.concat([accounts_df, new_acc], ignore_index=True)
        st.success("Account added!")

    if not accounts_df.empty:
        st.subheader("All Accounts")
        st.dataframe(accounts_df)

        st.subheader("Top-Up Accounts (Manual after Salary)")
        top_up_amounts = {}
        for i, row in accounts_df.iterrows():
            amt = st.number_input(f"Top-Up for {row['Bank']}", min_value=0.0, step=0.1, key=f"topup_{i}")
            top_up_amounts[row['Bank']] = amt

        if st.button("Update Balances"):
            for bank_name, amt in top_up_amounts.items():
                if amt > 0:
                    idx = accounts_df.index[accounts_df['Bank'] == bank_name][0]
                    accounts_df.at[idx, 'Balance'] += amt
            st.session_state['accounts'] = accounts_df
            st.success("Account balances updated!")

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
        transactions_df['Date'] = pd.to_datetime(transactions_df['Date'])
        transactions_df_sorted = transactions_df.sort_values('Date')
        transactions_df_sorted['Cumulative'] = transactions_df_sorted.apply(
            lambda row: row['Amount'] if row['Type'] == "Income" else -row['Amount'], axis=1
        ).cumsum()

        # Total accounts
        total_balance = accounts_df['Balance'].sum() if not accounts_df.empty else 0.0

        # Net balance calculation
        net_balance_df = transactions_df_sorted[['Date', 'Cumulative']].copy()
        net_balance_df['Net Balance'] = total_balance + net_balance_df['Cumulative']

        st.dataframe(net_balance_df)

        # Line chart
        fig_net = px.line(net_balance_df, x='Date', y='Net Balance', markers=True, title="Net Balance Over Time")
        st.plotly_chart(fig_net, use_container_width=True)
