import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="Baijiu Stock Analysis", page_icon="🥃", layout="wide")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# --------------------------
# Title
# --------------------------
st.title("🥃 Baijiu Stock Analysis & Comparison")
st.markdown("Analyze individual stocks or compare two listed baijiu companies — trends, returns, volatility and risk.")
st.divider()

# --------------------------
# Stock List (All Public Listed)
# --------------------------
stock_config = {
    "Kweichow Moutai":        {"base": 1700, "vol": 0.014, "trend": 0.15},
    "Wuliangye":             {"base": 140,  "vol": 0.020, "trend": 0.09},
    "Luzhou Laojiao":        {"base": 230,  "vol": 0.024, "trend": 0.06},
    "Shanxi Fenjiu":         {"base": 215,  "vol": 0.030, "trend": 0.04},
    "Yanghe Distillery":     {"base": 160,  "vol": 0.021, "trend": 0.08},
    "Gujing Gongjiu":        {"base": 250,  "vol": 0.027, "trend": 0.07},
    "Shede Spirits":         {"base": 140,  "vol": 0.032, "trend": 0.05},
    "Jiugui Liquor":         {"base": 110,  "vol": 0.035, "trend": 0.03},
    "Shunxin Agriculture":   {"base": 55,   "vol": 0.025, "trend": 0.02},
    "Jiannanchun":           {"base": 200,  "vol": 0.023, "trend": 0.06}
}

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("🔍 Settings")
    compare_mode = st.checkbox("Enable Comparison (2 stocks)", value=False)

    stock1 = st.selectbox("First Stock", list(stock_config.keys()), index=0)
    stock2 = None
    if compare_mode:
        stock2 = st.selectbox("Second Stock", list(stock_config.keys()), index=1)

    st.subheader("Date Range")
    days = st.select_slider("Period (Days)", [180, 360, 540, 700], value=540)

    st.subheader("Charts")
    show_price = st.checkbox("Price Trend", True)
    show_return = st.checkbox("Cumulative Return", True)
    show_volatility = st.checkbox("Volatility", True)

# --------------------------
# Data Generator (Fixed Seed)
# --------------------------
@st.cache_data(ttl=3600)
def generate_data(conf, name, days):
    # 修复：用公司名作为种子，而不是字典
    np.random.seed(42 + hash(name) % 1000)
    trend = np.linspace(0, conf["trend"], days)
    cycle = 0.06 * np.sin(np.linspace(0, 8 * np.pi, days))
    noise = np.random.normal(0, conf["vol"], days)
    ret = trend + cycle + noise
    price = conf["base"] * np.cumprod(1 + ret)
    idx = pd.date_range(end=pd.Timestamp.now(), periods=days)
    return pd.DataFrame({"Close": price}, index=idx)

df1 = generate_data(stock_config[stock1], stock1, days)
df2 = generate_data(stock_config[stock2], stock2, days) if compare_mode else None

# --------------------------
# Indicators
# --------------------------
close1 = df1["Close"]
ret1_norm = close1 / close1.iloc[0] * 100
vol1 = close1.pct_change().rolling(20).std() * np.sqrt(252)

close2, ret2_norm, vol2 = None, None, None
if compare_mode:
    close2 = df2["Close"]
    ret2_norm = close2 / close2.iloc[0] * 100
    vol2 = close2.pct_change().rolling(20).std() * np.sqrt(252)

# --------------------------
# Price Chart
# --------------------------
if show_price:
    if not compare_mode:
        st.subheader(f"📈 Price Trend: {stock1}")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(close1, color="#c8102e", lw=2, label=stock1)
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.subheader(f"📈 Price Comparison: {stock1} vs {stock2}")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(close1, color="#c8102e", lw=2, label=stock1)
        ax.plot(close2, color="#0066cc", lw=2, label=stock2)
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

# --------------------------
# Cumulative Return
# --------------------------
if show_return:
    if not compare_mode:
        st.subheader(f"📊 Cumulative Return (Base=100): {stock1}")
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.plot(ret1_norm, color="#c8102e", lw=2)
        ax.axhline(100, color="gray", linestyle="--")
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.subheader(f"📊 Cumulative Return Comparison")
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.plot(ret1_norm, color="#c8102e", lw=2, label=stock1)
        ax.plot(ret2_norm, color="#0066cc", lw=2, label=stock2)
        ax.axhline(100, color="gray", linestyle="--")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

# --------------------------
# Volatility
# --------------------------
if show_volatility:
    if not compare_mode:
        st.subheader(f"📉 20-Day Annualized Volatility: {stock1}")
        fig, ax = plt.subplots(figsize=(12, 2.5))
        ax.plot(vol1, color="#ff3b30", lw=1.5)
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.subheader(f"📉 Volatility Comparison")
        fig, ax = plt.subplots(figsize=(12, 2.5))
        ax.plot(vol1, color="#ff3b30", label=stock1)
        ax.plot(vol2, color="#007aff", label=stock2)
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

# --------------------------
# Summary Table
# --------------------------
st.divider()
if not compare_mode:
    st.subheader(f"📋 Summary Metrics: {stock1}")
    total_ret = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    avg_vol = vol1.mean()
    data = {
        "Metric": ["Total Return", "Avg Volatility", "Start Price", "Latest Price"],
        stock1: [
            f"{total_ret:.1f}%",
            f"{avg_vol:.2f}",
            f"{close1.iloc[0]:.1f}",
            f"{close1.iloc[-1]:.1f}"
        ]
    }
    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

else:
    st.subheader("📋 Comparison Summary")
    ret1 = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    ret2 = (close2.iloc[-1] / close2.iloc[0] - 1) * 100
    avg1 = vol1.mean()
    avg2 = vol2.mean()

    df_summary = pd.DataFrame({
        "Metric": ["Total Return", "Avg Volatility", "Start Price", "Latest Price"],
        stock1: [f"{ret1:.1f}%", f"{avg1:.2f}", f"{close1.iloc[0]:.1f}", f"{close1.iloc[-1]:.1f}"],
        stock2: [f"{ret2:.1f}%", f"{avg2:.2f}", f"{close2.iloc[0]:.1f}", f"{close2.iloc[-1]:.1f}"]
    })
    st.dataframe(df_summary, hide_index=True, use_container_width=True)

# --------------------------
# Conclusion
# --------------------------
st.divider()
st.subheader("🧾 Analysis Conclusion")

if not compare_mode:
    tr = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    av = vol1.mean()
    st.markdown(f"""
- **{stock1}** achieved a total return of **{tr:.1f}%** over the period.
- Average annualized volatility: **{av:.2f}**.
- The stock shows {'strong upward' if tr > 0 else 'weak or downward'} performance.
""")
else:
    better_ret = stock1 if ret1 > ret2 else stock2
    safer = stock1 if avg1 < avg2 else stock2
    st.markdown(f"""
- **Better return**: {better_ret}
- **Lower volatility (safer)**: {safer}
- **Relative strength**: **{better_ret}** outperformed in the selected period.
""")

st.caption("Disclaimer: For educational and demonstration purposes only. Not financial advice.")
