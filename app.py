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
st.title("🥃 Baijiu Industry Stock Analysis & Comparison")
st.markdown("Interactive financial dashboard for baijiu sector listed companies.")
st.divider()

# --------------------------
# Stock List (Real Listed Companies)
# --------------------------
stock_config = {
    "Kweichow Moutai":        {"base": 1700, "vol": 0.012, "trend": 0.20},
    "Wuliangye":             {"base": 140,  "vol": 0.018, "trend": 0.12},
    "Luzhou Laojiao":        {"base": 230,  "vol": 0.020, "trend": 0.08},
    "Shanxi Fenjiu":         {"base": 215,  "vol": 0.025, "trend": 0.06},
    "Yanghe Distillery":     {"base": 160,  "vol": 0.019, "trend": 0.10},
    "Gujing Gongjiu":        {"base": 250,  "vol": 0.022, "trend": 0.09},
    "Shede Spirits":         {"base": 140,  "vol": 0.028, "trend": 0.07},
    "Jiugui Liquor":         {"base": 110,  "vol": 0.030, "trend": 0.04},
    "Shunxin Agriculture":   {"base": 55,   "vol": 0.023, "trend": 0.03},
    "Jiannanchun":           {"base": 200,  "vol": 0.021, "trend": 0.08}
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
    days = st.select_slider("Period (Days)", [180, 360, 540, 700], value=540)

    st.subheader("Charts")
    show_price = st.checkbox("Price Trend", True)
    show_return = st.checkbox("Cumulative Return", True)
    show_volatility = st.checkbox("Volatility", True)

# --------------------------
# Data Generator (Realistic trend)
# --------------------------
@st.cache_data(ttl=3600)
def generate_data(conf, name, days):
    np.random.seed(42 + hash(name) % 1000)

    base = conf["base"]
    trend_rate = conf["trend"]
    vol = conf["vol"]

    trend = np.linspace(0, trend_rate, days)
    noise = np.random.normal(0, vol, days) * 0.7
    daily_return = trend + noise

    price = [base]
    for r in daily_return:
        next_p = price[-1] * (1 + r)
        price.append(next_p)

    price = price[1:]
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
# Charts
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
    st.subheader(f"📋 Performance Metrics: {stock1}")
    total_ret = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    avg_vol = vol1.mean()
    data = {
        "Metric": ["Total Return", "Avg Volatility", "Opening Price", "Closing Price"],
        stock1: [
            f"{total_ret:.1f}%",
            f"{avg_vol:.2f}",
            f"{close1.iloc[0]:.1f}",
            f"{close1.iloc[-1]:.1f}"
        ]
    }
    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

else:
    st.subheader("📋 Comparative Performance Metrics")
    ret1 = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    ret2 = (close2.iloc[-1] / close2.iloc[0] - 1) * 100
    avg1 = vol1.mean()
    avg2 = vol2.mean()

    df_summary = pd.DataFrame({
        "Metric": ["Total Return", "Avg Volatility", "Opening Price", "Closing Price"],
        stock1: [f"{ret1:.1f}%", f"{avg1:.2f}", f"{close1.iloc[0]:.1f}", f"{close1.iloc[-1]:.1f}"],
        stock2: [f"{ret2:.1f}%", f"{avg2:.2f}", f"{close2.iloc[0]:.1f}", f"{close2.iloc[-1]:.1f}"]
    })
    st.dataframe(df_summary, hide_index=True, use_container_width=True)

# --------------------------
# Professional Analysis & Recommendations (Report-style)
# --------------------------
st.divider()
st.subheader("📄 Professional Analysis & Strategic Recommendations")

if not compare_mode:
    tr = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    av = vol1.mean()

    st.markdown(f"""
### **1. Performance Review: {stock1}**
Over the analyzed period, {stock1} delivered a total return of **{tr:.1f}%**, paired with an average annualized volatility of **{av:.2f}**. The stock exhibits a {'sustained upward' if tr > 5 else 'range-bound'} trend, consistent with sector dynamics for premium baijiu producers.
""")

    if tr > 5:
        rec = f"""
### **2. Strategic Outlook**
- **Trend Momentum**: The stock maintains a positive price trajectory, supported by stable consumer demand and premium brand positioning.
- **Entry Strategy**: Investors may consider establishing core positions during pullbacks toward the moving average support levels.
- **Positioning**: Suitable for medium-term allocation in a balanced portfolio.
- **Risk Considerations**: Monitor sector-wide sentiment shifts and macro liquidity conditions, which may introduce short-term volatility.
"""
    elif tr > -5:
        rec = f"""
### **2. Strategic Outlook**
- **Trend Momentum**: The stock is consolidating within a defined range, lacking a clear directional bias.
- **Entry Strategy**: Investors are advised to adopt a “wait-and-see” approach, awaiting a confirmed breakout above resistance or breakdown below support.
- **Positioning**: Appropriate for observation rather than immediate allocation.
- **Risk Considerations**: The range-bound structure offers limited near-term catalysts.
"""
    else:
        rec = f"""
### **2. Strategic Outlook**
- **Trend Momentum**: The stock exhibits a weak or negative trend, reflecting cautious market sentiment.
- **Entry Strategy**: Aggressive buying is not recommended at this stage. Investors should wait for clear signs of stabilization and trend reversal.
- **Positioning**: The risk-reward profile is currently unfavorable.
- **Risk Considerations**: Downside pressure may persist amid broader sector rotation.
"""
    st.markdown(rec)

else:
    ret1 = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    ret2 = (close2.iloc[-1] / close2.iloc[0] - 1) * 100
    avg1 = vol1.mean()
    avg2 = vol2.mean()

    better_ret = stock1 if ret1 > ret2 else stock2
    safer = stock1 if avg1 < avg2 else stock2

    st.markdown(f"""
### **1. Comparative Performance Review**
- **Relative Returns**: {better_ret} outperformed {stock2 if better_ret == stock1 else stock1} over the period, delivering a total return of **{max(ret1, ret2):.1f}%** versus **{min(ret1, ret2):.1f}%**.
- **Risk Profile**: {safer} demonstrates lower volatility ({min(avg1, avg2):.2f}), indicating a more stable price path compared to {stock2 if safer == stock1 else stock1} ({max(avg1, avg2):.2f}).
""")

    rec = f"""
### **2. Strategic Recommendations**
- **Core Allocation**: For investors seeking balanced risk-return exposure, {better_ret} represents a preferred choice due to its superior relative performance.
- **Conservative Approach**: For risk-averse investors, {safer} offers a more stable profile, suitable for long-term core holdings.
- **Sector Context**: Both names are leveraged to baijiu consumption trends. Investors should monitor industry-wide inventory cycles and pricing power developments.
- **Portfolio Construction**: Consider combining names with different volatility profiles to balance exposure and mitigate sector-specific risk.
"""
    st.markdown(rec)
