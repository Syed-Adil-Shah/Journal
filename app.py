import streamlit as st
import pandas as pd
from datetime import datetime
import os
import altair as alt

st.set_page_config(page_title="Trade Journal", layout="wide")

DATA_FILE = "trade_journal.csv"

# Custom CSS for better visuals
st.markdown(
    """
    <style>
        .metric-label { font-size: 14px; color: #AAAAAA; }
        .metric-value { font-size: 26px; font-weight: bold; }
        .win { color: #00FFAA; font-weight: bold; }
        .loss { color: #FF4B4B; font-weight: bold; }
        .side-badge {
            padding: 2px 8px;
            border-radius: 8px;
            color: white;
            font-size: 12px;
        }
        .long { background-color: #3AAFA9; }
        .short { background-color: #FF6B6B; }
    </style>
    """,
    unsafe_allow_html=True
)

# Load or create data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Date", "Instrument", "Trade Name", "Position", "Entry Price", "Sell Price", "TP", "SL",
        "Confluence", "Strategy Name", "Result", "Why it happened?", "Profit & Loss", "P&L (%)"
    ])

# Sidebar form
st.sidebar.header("➕ Add New Trade")

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
        else:
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

# Dashboard UI
st.title("📊 Trade Journal Dashboard")

if df.empty:
    st.info("No trades logged yet. Add one using the sidebar.")
else:
    st.subheader("🔹 Performance Overview")
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

    # Line chart for cumulative P&L
    df["Cumulative P&L"] = df["Profit & Loss"].cumsum()
    st.subheader("📈 Cumulative P&L Over Time")
    line_chart = alt.Chart(df).mark_line().encode(
        x="Date:T",
        y="Cumulative P&L:Q",
        tooltip=["Date", "Cumulative P&L"]
    ).properties(height=300)
    st.altair_chart(line_chart, use_container_width=True)

    # Pie chart of win/loss
    st.subheader("🟢 Win vs 🔴 Loss Distribution")
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

    # Styled Table
    st.subheader("📋 Trade Log")
    styled_df = df.copy()
    styled_df["Status"] = styled_df["Profit & Loss"].apply(lambda x: "WIN" if x > 0 else "LOSS")
    styled_df["Side"] = styled_df["Position"].apply(
        lambda x: f'<span class="side-badge {"long" if x == "Long" else "short"}">{x}</span>'
    )
    styled_df["Status"] = styled_df["Status"].apply(
        lambda x: f'<span class="{x.lower()}">{x}</span>'
    )

    st.write(styled_df[[
        "Date", "Trade Name", "Instrument", "Side", "Entry Price", "Sell Price", 
        "TP", "SL", "Strategy Name", "Status", "Profit & Loss", "P&L (%)"
    ]].to_html(escape=False, index=False), unsafe_allow_html=True)
