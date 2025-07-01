import streamlit as st
import pandas as pd
from datetime import datetime
import os
import altair as alt

st.set_page_config(page_title="Trade Journal", layout="wide")

DATA_FILE = "trade_journal.csv"

# --------------------
# Load or Create CSV
# --------------------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Date", "Instrument", "Trade Name", "Position", "Entry Price", "Sell Price", "TP", "SL",
        "Confluence", "Strategy Name", "Result", "Why it happened?", "Profit & Loss", "P&L (%)"
    ])

# --------------------
# Sidebar - Add Trade
# --------------------
st.sidebar.header("Add New Trade")

with st.sidebar.form("trade_form"):
    instrument = st.selectbox("Instrument", ["Crypto", "Stocks", "Forex", "Other"])
    trade_name = st.text_input("Trade Name")
    position = st.selectbox("Position", ["Long", "Short"])
    entry_price = st.number_input("Entry Price", format="%.2f")
    sell_price = st.number_input("Sell Price", format="%.2f")
    tp = st.number_input("Take Profit (TP)", format="%.2f")
    sl = st.number_input("Stop Loss (SL)", format="%.2f")
    confluence = st.text_area("Confluence (Reason for Entry)")
    strategy_name = st.text_input("Strategy Name")
    result = st.selectbox("Result", ["TP hit", "SL hit", "Closed manually"])
    why_happened = st.text_area("Why it happened?")
    submitted = st.form_submit_button("Add Trade")

    if submitted:
        if position == "Long":
            pl = sell_price - entry_price
        else:  # Short
            pl = entry_price - sell_price
        pl_percent = (pl / entry_price * 100) if entry_price != 0 else 0

        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Instrument": instrument,
            "Trade Name": trade_name,
            "Position": position,
            "Entry Price": entry_price,
            "Sell Price": sell_price,
            "TP": tp,
            "SL": sl,
            "Confluence": confluence,
            "Strategy Name": strategy_name,
            "Result": result,
            "Why it happened?": why_happened,
            "Profit & Loss": round(pl, 2),
            "P&L (%)": round(pl_percent, 2)
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Trade added!")

# --------------------
# Dashboard
# --------------------
st.title("📈 Trade Journal Dashboard")

if df.empty:
    st.info("No trades logged yet. Add one using the sidebar.")
else:
    col1, col2, col3, col4 = st.columns(4)

    total_trades = len(df)
    total_pl = df["Profit & Loss"].sum()
    wins = df[df["Profit & Loss"] > 0]
    losses = df[df["Profit & Loss"] < 0]

    win_rate = round((len(wins) / total_trades) * 100, 2) if total_trades > 0 else 0
    avg_profit = round(wins["Profit & Loss"].mean(), 2) if not wins.empty else 0
    avg_loss = round(losses["Profit & Loss"].mean(), 2) if not losses.empty else 0
    rr_ratio = round(abs(avg_profit / avg_loss), 2) if avg_loss != 0 else 0

    col1.metric("Total P&L", f"${total_pl:.2f}")
    col2.metric("Win Rate", f"{win_rate}%")
    col3.metric("Avg Profit", f"${avg_profit}")
    col4.metric("Avg Loss", f"${avg_loss}")

    # Pie Chart
    st.subheader("📊 Win vs Loss Distribution")
    pie_data = pd.DataFrame({
        "Result": ["Wins", "Losses"],
        "Count": [len(wins), len(losses)]
    })

    pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
        theta="Count",
        color="Result",
        tooltip=["Result", "Count"]
    )
    st.altair_chart(pie_chart, use_container_width=True)

    # Trade Table
    st.subheader("📋 Trade Log")
    st.dataframe(df[::-1], use_container_width=True)
