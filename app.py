import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(page_title="Baijiu Stock Analysis System", page_icon="🥃", layout="wide")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Title
st.title("🥃 Baijiu Industry Stock Analysis System")
st.caption("Real Market Data · Professional Analysis Interface")
st.divider()

# Baijiu stock list (formatted for yfinance)
stock_list = {
    "Kweichow Moutai": "600519.SS",
    "Wuliangye": "000858.SZ",
    "Luzhou Laojiao": "000568.SZ",
    "Shanxi Fenjiu": "600809.SS",
    "Yanghe Distillery": "002304.SZ",
}

# Sidebar selection
with st.sidebar:
    st.header("🔍 Select Stock")
    selected_company = st.selectbox("Baijiu Company", list(stock_list.keys()))
    stock_code = stock_list[selected_company]

# Get data with error handling
@st.cache_data(ttl=3600)
def get_stock_data(code):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=700)
        df = yf.download(code, start=start_date, end=end_date)
        if df.empty:
            st.error(f"Failed to fetch data for {selected_company}. Please try again later.")
            st.stop()
        return df
    except Exception as e:
        st.error(f"Data fetch failed: {str(e)}")
        st.stop()

df = get_stock_data(stock_code)

# Calculate indicators with protection
close_prices = df["Close"].dropna()
if len(close_prices) < 60:
    st.error("Insufficient data to calculate moving averages.")
    st.stop()

current_price = close_prices.iloc[-1]
ma60 = close_prices.rolling(60).mean().iloc[-1]
trend = "Upward" if current_price > close_prices.iloc[0] else "Sideways/Downward"
valuation = "Overvalued" if current_price > ma60 * 1.08 else "Undervalued" if current_price < ma60 * 0.93 else "Fairly Valued"

# Visualization
col1, col2 = st.columns([1.5, 1])
with col1:
    st.subheader("📈 Price Trend")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(close_prices, color="#8B0000", linewidth=2, label="Closing Price")
    ax.plot(close_prices.rolling(60).mean(), "--", color="#1f77b4", label="60-Day Moving Average")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with col2:
    st.subheader("📊 Key Metrics")
    st.metric("Current Price", f"{current_price:.2f} CNY")
    st.metric("Trend", trend)
    st.metric("60-Day MA", f"{ma60:.2f} CNY")
    st.metric("Valuation", valuation)

# Investment recommendation
st.divider()
st.subheader("🧾 Professional Investment Recommendation")

if trend == "Upward" and valuation == "Fairly Valued":
    st.success("✅ Healthy trend + Fair valuation → Consider buying on pullbacks for medium-term holding.")
elif trend == "Upward" and valuation == "Overvalued":
    st.warning("⚠️ Upward trend but overvalued → Light position only, avoid chasing highs.")
elif trend == "Sideways/Downward" and valuation == "Undervalued":
    st.info("🔍 Weak trend but undervalued → Wait for confirmation signals before entering.")
else:
    st.error("🛑 Weak trend + Overvalued → Reduce exposure or avoid for now.")

st.caption("Data source: Yahoo Finance | For educational purposes only.")
