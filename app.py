import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
from datetime import datetime, timedelta

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="Baijiu Stock Analysis", page_icon="🥃", layout="wide")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# --------------------------
# Tushare Setup (Replace with your token)
# --------------------------
TS_TOKEN = "你的tushare_token"  # 替换为你的Tushare Token
pro = ts.pro_api(TS_TOKEN)

# --------------------------
# Title
# --------------------------
st.title("🥃 Baijiu Industry Stock Analysis & Comparison")
st.markdown("Real-time CSI 300 Data & Professional Visualization")
st.divider()

# --------------------------
# Stock List (Baijiu Sector)
# --------------------------
stock_config = {
    "Kweichow Moutai (600519)":        {"ts_code": "600519.SH"},
    "Wuliangye (000858)":             {"ts_code": "000858.SZ"},
    "Luzhou Laojiao (000568)":        {"ts_code": "000568.SZ"},
    "Shanxi Fenjiu (600809)":         {"ts_code": "600809.SH"},
    "Yanghe Distillery (002304)":     {"ts_code": "002304.SZ"},
    "Gujing Gongjiu (000596)":        {"ts_code": "000596.SZ"},
    "Shede Spirits (600702)":         {"ts_code": "600702.SH"},
    "Jiugui Liquor (000799)":         {"ts_code": "000799.SZ"},
    "Shunxin Agriculture (000995)":   {"ts_code": "000995.SZ"},
    "Jiannanchun (603597)":           {"ts_code": "603597.SH"}
}

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    compare_mode = st.checkbox("Enable Comparison (2 stocks)", value=False)

    stock1 = st.selectbox("First Stock", list(stock_config.keys()), index=0)
    stock2 = None
    if compare_mode:
        stock2 = st.selectbox("Second Stock", list(stock_config.keys()), index=1)

    st.subheader("Date Range")
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    days = st.select_slider("Period (Days)", [180, 360, 540, 700], value=360)

    st.subheader("Charts")
    chart_toggles = {
        "Price Trend": st.checkbox("Price Trend", True),
        "Cumulative Return": st.checkbox("Cumulative Return", True),
        "Volume": st.checkbox("Volume", True),
        "RSI (14d)": st.checkbox("RSI (14d)", True),
        "Volatility (20d)": st.checkbox("Volatility (20d)", True),
        "Amount": st.checkbox("Amount", True)
    }

# --------------------------
# Data Fetching Function (Tushare)
# --------------------------
@st.cache_data(ttl=3600)
def fetch_data(ts_code, start_date, end_date):
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').set_index('trade_date')
    return df

# --------------------------
# Fetch CSI 300 Data
# --------------------------
@st.cache_data(ttl=3600)
def fetch_csi300(start_date, end_date):
    df = pro.index_daily(ts_code='399300.SZ', start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').set_index('trade_date')
    return df

csi300_df = fetch_csi300(start_date, end_date)

# --------------------------
# Fetch Stock Data
# --------------------------
df1 = fetch_data(stock_config[stock1]["ts_code"], start_date, end_date)
df2 = fetch_data(stock_config[stock2]["ts_code"], start_date, end_date) if compare_mode else None

# --------------------------
# Technical Indicators
# --------------------------
def compute_indicators(df):
    # RSI (14-day)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Volatility (20-day annualized)
    df['volatility'] = df['close'].pct_change().rolling(window=20).std() * np.sqrt(252)
    return df

df1 = compute_indicators(df1)
if compare_mode:
    df2 = compute_indicators(df2)

# --------------------------
# Plotting Functions
# --------------------------
def plot_chart(df, title, y_label, plot_func, color="#c8102e"):
    fig, ax = plt.subplots(figsize=(12, 3))
    plot_func(ax, df, color)
    ax.set_title(title, fontsize=12)
    ax.set_ylabel(y_label)
    ax.grid(alpha=0.3)
    st.pyplot(fig)

def plot_price(ax, df, color):
    ax.plot(df.index, df['close'], color=color, lw=2)

def plot_return(ax, df, color):
    ret = df['close'] / df['close'].iloc[0] * 100
    ax.plot(df.index, ret, color=color, lw=2)
    ax.axhline(100, color='gray', linestyle='--')

def plot_volume(ax, df, color):
    ax.bar(df.index, df['vol'], color=color, alpha=0.7)

def plot_rsi(ax, df, color):
    ax.plot(df.index, df['rsi'], color=color, lw=2)
    ax.axhline(30, color='red', linestyle='--', label='Oversold (30)')
    ax.axhline(70, color='green', linestyle='--', label='Overbought (70)')
    ax.legend()

def plot_volatility(ax, df, color):
    ax.plot(df.index, df['volatility'], color=color, lw=2)

def plot_amount(ax, df, color):
    ax.plot(df.index, df['amount'], color=color, lw=2)

# --------------------------
# Plot Selected Charts
# --------------------------
if not compare_mode:
    if chart_toggles["Price Trend"]:
        plot_chart(df1, f"Price Trend: {stock1}", "Price", plot_price)
    if chart_toggles["Cumulative Return"]:
        plot_chart(df1, f"Cumulative Return (Base=100): {stock1}", "Return Index", plot_return)
    if chart_toggles["Volume"]:
        plot_chart(df1, f"Volume: {stock1}", "Volume", plot_volume)
    if chart_toggles["RSI (14d)"]:
        plot_chart(df1, f"RSI (14d): {stock1}", "RSI", plot_rsi)
    if chart_toggles["Volatility (20d)"]:
        plot_chart(df1, f"20-Day Annualized Volatility: {stock1}", "Volatility", plot_volatility)
    if chart_toggles["Amount"]:
        plot_chart(df1, f"Amount: {stock1}", "Amount", plot_amount)
else:
    if chart_toggles["Price Trend"]:
        st.subheader(f"Price Comparison: {stock1} vs {stock2}")
        fig, ax = plt.subplots(figsize=(12, 4))
        plot_price(ax, df1, "#c8102e")
        plot_price(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if chart_toggles["Cumulative Return"]:
        st.subheader(f"Cumulative Return Comparison")
        fig, ax = plt.subplots(figsize=(12, 3))
        plot_return(ax, df1, "#c8102e")
        plot_return(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if chart_toggles["Volume"]:
        st.subheader(f"Volume Comparison")
        fig, ax = plt.subplots(figsize=(12, 3))
        plot_volume(ax, df1, "#c8102e")
        plot_volume(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if chart_toggles["RSI (14d)"]:
        st.subheader(f"RSI (14d) Comparison")
        fig, ax = plt.subplots(figsize=(12, 3))
        plot_rsi(ax, df1, "#c8102e")
        plot_rsi(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if chart_toggles["Volatility (20d)"]:
        st.subheader(f"Volatility Comparison")
        fig, ax = plt.subplots(figsize=(12, 3))
        plot_volatility(ax, df1, "#c8102e")
        plot_volatility(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if chart_toggles["Amount"]:
        st.subheader(f"Amount Comparison")
        fig, ax = plt.subplots(figsize=(12, 3))
        plot_amount(ax, df1, "#c8102e")
        plot_amount(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

# --------------------------
# Summary Table
# --------------------------
st.divider()
st.subheader("📋 Performance Metrics")

def get_metrics(df):
    total_ret = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
    avg_vol = df['vol'].mean()
    avg_rsi = df['rsi'].mean()
    avg_volatility = df['volatility'].mean()
    return [f"{total_ret:.1f}%", f"{avg_vol:.2f}", f"{avg_rsi:.1f}", f"{avg_volatility:.2f}"]

if not compare_mode:
    metrics = get_metrics(df1)
    df_summary = pd.DataFrame({
        "Metric": ["Total Return", "Avg Volume", "Avg RSI (14d)", "Avg Volatility (20d)"],
        stock1: metrics
    })
    st.dataframe(df_summary, hide_index=True, use_container_width=True)
else:
    m1 = get_metrics(df1)
    m2 = get_metrics(df2)
    df_summary = pd.DataFrame({
        "Metric": ["Total Return", "Avg Volume", "Avg RSI (14d)", "Avg Volatility (20d)"],
        stock1: m1,
        stock2: m2
    })
    st.dataframe(df_summary, hide_index=True, use_container_width=True)

# --------------------------
# Baijiu Industry Metrics
# --------------------------
st.divider()
st.subheader("📊 Baijiu Industry Overview (CSI 300 Sector)")

# Simplified Industry Metrics (Real calculation can be extended)
industry_metrics = {
    "CSI 300 Index (Close)": f"{csi300_df['close'].iloc[-1]:.2f}",
    "CSI 300 Return (YTD)": f"{(csi300_df['close'].iloc[-1] / csi300_df['close'].iloc[0] - 1) * 100:.1f}%",
    "Baijiu Avg Return": f"{np.mean([(df1['close'].iloc[-1]/df1['close'].iloc[0]-1)*100] + [(df2['close'].iloc[-1]/df2['close'].iloc[0]-1)*100] if compare_mode else [(df1['close'].iloc[-1]/df1['close'].iloc[0]-1)*100]):.1f}%",
    "Baijiu Avg Volatility": f"{np.mean([df1['volatility'].mean()] + [df2['volatility'].mean()] if compare_mode else [df1['volatility'].mean()]):.2f}"
}

df_industry = pd.DataFrame(list(industry_metrics.items()), columns=["Indicator", "Value"])
st.dataframe(df_industry, hide_index=True, use_container_width=True)

# --------------------------
# Professional Analysis
# --------------------------
st.divider()
st.subheader("📄 Professional Analysis & Strategic Recommendations")

if not compare_mode:
    tr = (df1['close'].iloc[-1] / df1['close'].iloc[0] - 1) * 100
    av = df1['volatility'].mean()
    st.markdown(f"""
### 1. Performance Review: {stock1}
- Total Return: **{tr:.1f}%**
- Avg Volatility: **{av:.2f}**
- Trend: **{'Sustained Up' if tr > 5 else 'Range-Bound' if tr > -5 else 'Weak Down'}**
""")
    if tr > 5:
        st.markdown("""
### 2. Strategic Outlook
- **Momentum**: Positive trend supported by brand strength.
- **Entry**: Core positions on pullbacks to moving average support.
- **Risk**: Monitor macro liquidity and sector rotation.
""")
    elif tr > -5:
        st.markdown("""
### 2. Strategic Outlook
- **Range-Bound**: No clear direction; wait for breakout/breakdown.
- **Positioning**: Observation only.
""")
    else:
        st.markdown("""
### 2. Strategic Outlook
- **Weak Trend**: Avoid aggressive buying; wait for stabilization.
- **Risk**: Downside pressure may persist.
""")
else:
    ret1 = (df1['close'].iloc[-1] / df1['close'].iloc[0] - 1) * 100
    ret2 = (df2['close'].iloc[-1] / df
