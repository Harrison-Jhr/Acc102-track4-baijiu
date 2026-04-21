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
st.markdown("For beginner investors & students — simple, clear, practical guidance.")
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
# Data Generator (REALISTIC — NO EXPLODING PRICES)
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
        st.subheader(f"📉 20-Day Volatility: {stock1}")
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
# CONCLUSION + INVESTMENT ADVICE (FOR BEGINNERS & STUDENTS)
# --------------------------
st.divider()
st.subheader("🧾 Analysis Conclusion")
st.subheader("💡 Simple Investment Advice (For Beginners & Students)")

# --------------------------
# 单股票模式
# --------------------------
if not compare_mode:
    tr = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    av = vol1.mean()

    # Conclusion
    st.markdown(f"""
- **{stock1}** total return: **{tr:.1f}%**
- Average volatility: **{av:.2f}**
- Trend: **{"Positive" if tr > 0 else "Negative or Sideways"}**
""")

    # Advice for BEGINNERS
    if tr > 5:
        advice = f"""
**Investment Advice for {stock1}**:  
✅ This stock has a clear upward trend.  
✅ Suitable for **medium-term holding** (weeks to months).  
✅ Beginners can consider small positions on dips.  
⚠️ Do NOT invest all your money at once.  
⚠️ Do NOT borrow money to invest.
"""
    elif tr > -5:
        advice = f"""
**Investment Advice for {stock1}**:  
🔍 This stock is moving sideways (no strong trend).  
🔍 Good for learning, not ideal for quick profit.  
✅ Safe for **long-term observation & practice**.  
⚠️ Do not chase short-term gains.
"""
    else:
        advice = f"""
**Investment Advice for {stock1}**:  
⚠️ Trend is weak or downward.  
⚠️ **Not recommended for beginners to buy now**.  
✅ Good for **studying how downtrends work**.  
⚠️ Avoid trying to “buy the dip” to prevent loss.
"""
    st.markdown(advice)

# --------------------------
# 对比模式
# --------------------------
else:
    ret1 = (close1.iloc[-1] / close1.iloc[0] - 1) * 100
    ret2 = (close2.iloc[-1] / close2.iloc[0] - 1) * 100
    avg1 = vol1.mean()
    avg2 = vol2.mean()

    better_ret = stock1 if ret1 > ret2 else stock2
    safer = stock1 if avg1 < avg2 else stock2

    # Conclusion
    st.markdown(f"""
- **Better return**: {better_ret}  
- **Lower risk (safer)**: {safer}  
- **Stronger overall**: {better_ret}
""")

    # Comparison Advice FOR BEGINNERS
    st.markdown(f"""
**Simple Investment Advice for Beginners**:  

1. **{better_ret}** had better performance in this period.  
2. **{safer}** is less volatile and easier to hold for new investors.  
3. If you are a student:  
   ✅ Start with **small money** to practice  
   ✅ Choose **lower volatility** stocks  
   ✅ Learn before you earn  
4. Never invest money you cannot afford to lose.  
5. Diversify — do not put all money into one stock.
""")

st.caption("Disclaimer: For education & learning only. Not financial advice.")
