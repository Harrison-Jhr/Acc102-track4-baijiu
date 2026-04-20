import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------
# 页面设置（全英文）
# --------------------------
st.set_page_config(
    page_title="Baijiu Stock Analysis System",
    page_icon="🥃",
    layout="wide"
)
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# --------------------------
# 标题
# --------------------------
st.title("🥃 Baijiu Industry Stock Analysis System")
st.caption("Simulated Market Data · Professional Analysis Interface")
st.divider()

# --------------------------
# 股票列表（直接用代码名，避免接口问题）
# --------------------------
stock_list = {
    "Kweichow Moutai": "600519",
    "Wuliangye": "000858",
    "Luzhou Laojiao": "000568",
    "Shanxi Fenjiu": "600809",
    "Yanghe Distillery": "002304",
}

with st.sidebar:
    st.header("🔍 Select Stock")
    selected_company = st.selectbox("Baijiu Company", list(stock_list.keys()))

# --------------------------
# 模拟数据（替代 yfinance，不会报错）
# --------------------------
@st.cache_data
def generate_dummy_data():
    # 生成700天的模拟股价数据，趋势和波动都像真实白酒股
    days = 700
    base_price = {
        "Kweichow Moutai": 1600,
        "Wuliangye": 130,
        "Luzhou Laojiao": 220,
        "Shanxi Fenjiu": 200,
        "Yanghe Distillery": 150,
    }[selected_company]
    
    # 带趋势的随机游走
    np.random.seed(42)
    trend = np.linspace(-0.2, 0.3, days)
    noise = np.random.normal(0, 0.02, days)
    returns = trend + noise
    prices = base_price * np.cumprod(1 + returns)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
    df = pd.DataFrame({"Close": prices}, index=dates)
    return df

df = generate_dummy_data()
close_prices = df["Close"]

# --------------------------
# 计算指标（修复版）
# --------------------------
current_price = close_prices.iloc[-1]
ma60 = close_prices.rolling(60).mean().iloc[-1]
start_price = close_prices.iloc[0]

# 修复比较错误：确保是标量
trend = "Upward" if current_price > start_price else "Sideways/Downward"
valuation = "Overvalued" if current_price > ma60 * 1.08 else "Undervalued" if current_price < ma60 * 0.93 else "Fairly Valued"

# --------------------------
# 可视化
# --------------------------
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

# --------------------------
# 投资建议
# --------------------------
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

st.caption("Data source: Simulated for educational purposes only.")
