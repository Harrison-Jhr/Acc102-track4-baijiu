import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="Baijiu Stock Analysis 2022–2026", page_icon="🥃", layout="wide")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# --------------------------
# Title
# --------------------------
st.title("🥃 Baijiu Industry Stock Analysis (2022–2026)")
st.markdown("Local CSV Dataset & CSI 300 Benchmark Comparison")
st.divider()

# --------------------------
# Stock List
# --------------------------
stock_list = {
    "Kweichow Moutai": "600519",
    "Wuliangye": "000858",
    "Luzhou Laojiao": "000568",
    "Shanxi Fenjiu": "600809",
    "Yanghe Distillery": "002304",
    "Gujing Gongjiu": "000596",
    "Shede Spirits": "600702",
    "Jiugui Liquor": "000799",
    "Shunxin Agriculture": "000860"
}

# --------------------------
# LOAD DATA FROM LOCAL CSV FILES
# --------------------------
@st.cache_data
def load_local_dataset(stock_name):
    df = pd.read_csv("baijiu_dataset.csv")
    df = df[df["stock"] == stock_name].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df.set_index("date", inplace=True)

    # Calculate indicators
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_g = gain.rolling(14).mean()
    avg_l = loss.rolling(14).mean()
    rs = avg_g / avg_l
    df["rsi"] = 100 - (100 / (1 + rs))
    df["volatility"] = df["close"].pct_change().rolling(20).std() * np.sqrt(252)
    peak = df["close"].cummax()
    df["drawdown"] = (df["close"] - peak) / peak
    return df

@st.cache_data
def load_csi300():
    df = pd.read_csv("csi300_dataset.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df.set_index("date", inplace=True)
    return df

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("Settings")
    compare_mode = st.checkbox("Compare Two Stocks", False)
    stock1 = st.selectbox("Stock 1", list(stock_list.keys()))
    stock2 = st.selectbox("Stock 2", list(stock_list.keys())) if compare_mode else None

    st.info("Data source: Local CSV dataset (2022–2026)")

    st.subheader("Charts")
    c1 = st.checkbox("Price Trend", True)
    c2 = st.checkbox("Cumulative Return vs CSI 300", True)
    c3 = st.checkbox("Volume", True)
    c4 = st.checkbox("RSI (14d)", True)
    c5 = st.checkbox("Volatility (20d)", True)
    c6 = st.checkbox("Drawdown", True)

# --------------------------
# Load Data
# --------------------------
df1 = load_local_dataset(stock1)
df2 = load_local_dataset(stock2) if compare_mode else None
csi = load_csi300()

# --------------------------
# Plot Functions
# --------------------------
def plot_price(ax, df, label, color):
    ax.plot(df.index, df["close"], label=label, color=color, lw=2)

def plot_return(ax, df, label, color):
    norm = df["close"] / df["close"].iloc[0] * 100
    ax.plot(df.index, norm, label=label, color=color, lw=2)

def plot_vol(ax, df, color):
    ax.bar(df.index, df["vol"], color=color, alpha=0.6)

def plot_rsi(ax, df, color):
    ax.plot(df.index, df["rsi"], color=color, lw=2)
    ax.axhline(30, c="red", ls="--", label="Oversold (30)")
    ax.axhline(70, c="green", ls="--", label="Overbought (70)")

def plot_vola(ax, df, color):
    ax.plot(df.index, df["volatility"], color=color, lw=2)

def plot_dd(ax, df, color):
    ax.fill_between(df.index, df["drawdown"], 0, color=color, alpha=0.4)
    ax.plot(df.index, df["drawdown"], color=color, lw=1)

# --------------------------
# Draw Charts
# --------------------------
if not compare_mode:
    if c1:
        st.subheader(f"📈 Price Trend | {stock1}")
        fig, ax = plt.subplots(figsize=(14,5))
        plot_price(ax, df1, stock1, "#c8102e")
        ax.grid(alpha=0.3)
        ax.legend()
        st.pyplot(fig)

    if c2:
        st.subheader("📊 Cumulative Return vs CSI 300")
        fig, ax = plt.subplots(figsize=(14,4))
        plot_return(ax, df1, stock1, "#c8102e")
        plot_return(ax, csi, "CSI 300", "#0066cc")
        ax.axhline(100, c="gray", ls="--")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c3:
        st.subheader(f"📦 Volume | {stock1}")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_vol(ax, df1, "#c8102e")
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c4:
        st.subheader(f"📉 RSI (14d) | {stock1}")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_rsi(ax, df1, "#ff3b30")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c5:
        st.subheader(f"⚡ Volatility (20d) | {stock1}")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_vola(ax, df1, "#007aff")
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c6:
        st.subheader(f"📉 Drawdown | {stock1}")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_dd(ax, df1, "#ff9500")
        ax.grid(alpha=0.3)
        st.pyplot(fig)

else:
    if c1:
        st.subheader(f"📈 Price Comparison | {stock1} vs {stock2}")
        fig, ax = plt.subplots(figsize=(14,5))
        plot_price(ax, df1, stock1, "#c8102e")
        plot_price(ax, df2, stock2, "#0066cc")
        ax.grid(alpha=0.3)
        ax.legend()
        st.pyplot(fig)

    if c2:
        st.subheader("📊 Return Comparison vs CSI 300")
        fig, ax = plt.subplots(figsize=(14,4))
        plot_return(ax, df1, stock1, "#c8102e")
        plot_return(ax, df2, stock2, "#0066cc")
        plot_return(ax, csi, "CSI 300", "#34c759")
        ax.axhline(100, c="gray", ls="--")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c3:
        st.subheader("📦 Volume Comparison")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_vol(ax, df1, "#c8102e")
        plot_vol(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c4:
        st.subheader("📉 RSI (14d) Comparison")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_rsi(ax, df1, "#c8102e")
        plot_rsi(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c5:
        st.subheader("⚡ Volatility Comparison")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_vola(ax, df1, "#c8102e")
        plot_vola(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    if c6:
        st.subheader("📉 Drawdown Comparison")
        fig, ax = plt.subplots(figsize=(14,3))
        plot_dd(ax, df1, "#c8102e")
        plot_dd(ax, df2, "#0066cc")
        ax.legend([stock1, stock2])
        ax.grid(alpha=0.3)
        st.pyplot(fig)

# --------------------------
# Performance Metrics
# --------------------------
st.divider()
st.subheader("📋 Performance Metrics")

def get_metrics(df):
    total_ret = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
    avg_vol = df["vol"].mean()
    avg_rsi = df["rsi"].mean()
    avg_volatility = df["volatility"].mean()
    max_drawdown = df["drawdown"].min() * 100
    return [f"{total_ret:.1f}%", f"{avg_vol:.0f}", f"{avg_rsi:.1f}", f"{avg_volatility:.2f}", f"{max_drawdown:.1f}%"]

if not compare_mode:
    metrics = get_metrics(df1)
    df_summary = pd.DataFrame({
        "Metric": ["Total Return", "Avg Volume", "Avg RSI", "Avg Volatility", "Max Drawdown"],
        stock1: metrics
    })
else:
    m1 = get_metrics(df1)
    m2 = get_metrics(df2)
    df_summary = pd.DataFrame({
        "Metric": ["Total Return", "Avg Volume", "Avg RSI", "Avg Volatility", "Max Drawdown"],
        stock1: m1, stock2: m2
    })

st.dataframe(df_summary, hide_index=True, use_container_width=True)

# --------------------------
# ANALYSIS & INVESTMENT RECOMMENDATIONS (FULLY RETAINED)
# --------------------------
st.divider()
st.subheader("📄 Professional Analysis & Strategic Recommendations")

if not compare_mode:
    tr = (df1["close"].iloc[-1] / df1["close"].iloc[0] - 1) * 100
    av = df1["volatility"].mean()
    max_dd = df1["drawdown"].min() * 100

    st.markdown(f"""
### 1. Performance Review: {stock1}
- Total Return: {tr:.1f}%
- Avg Volatility: {av:.2f}
- Max Drawdown: {max_dd:.1f}%
""")

    if tr > 5:
        st.markdown("""
### 2. Investment Recommendations
- Trend: Positive long-term uptrend with strong fundamentals.
- Strategy: Suitable for medium-to-long-term holding.
- Risk: Moderate volatility; watch for market sentiment changes.
""")
    elif tr > -5:
        st.markdown("""
### 2. Investment Recommendations
- Trend: Sideways movement with no strong direction.
- Strategy: Wait for clear breakout signals before entering.
""")
    else:
        st.markdown("""
### 2. Investment Recommendations
- Trend: Weak performance with downward pressure.
- Strategy: Avoid heavy positions; wait for stabilization.
""")

else:
    tr1 = (df1["close"].iloc[-1] / df1["close"].iloc[0] - 1) * 100
    tr2 = (df2["close"].iloc[-1] / df2["close"].iloc[0] - 1) * 100
    av1 = df1["volatility"].mean()
    av2 = df2["volatility"].mean()

    better_ret = stock1 if tr1 > tr2 else stock2
    safer = stock1 if av1 < av2 else stock2

    st.markdown(f"""
### 1. Comparative Analysis
- Better Return: {better_ret}
- Lower Risk: {safer}
""")

    st.markdown(f"""
### 2. Investment Recommendations
- For Growth: Choose {better_ret}
- For Stability: Choose {safer}
""")
