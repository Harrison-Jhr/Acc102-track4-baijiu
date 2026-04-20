import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# --------------------------
# 页面设置（英文）
# --------------------------
st.set_page_config(
    page_title="Baijiu Stock Analysis System",
    page_icon="🥃",
    layout="wide"
)
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# --------------------------
# 标题与介绍
# --------------------------
st.title("🥃 Baijiu Industry Stock Analysis System")
st.markdown("""
This interactive dashboard provides a professional analysis of leading Chinese baijiu companies, 
including price trends, key technical indicators, and data-driven investment recommendations.
""")
st.divider()

# --------------------------
# 股票列表
# --------------------------
stock_list = {
    "Kweichow Moutai": {"base": 1650, "vol": 0.015, "trend": 0.12},
    "Wuliangye": {"base": 135, "vol": 0.022, "trend": 0.08},
    "Luzhou Laojiao": {"base": 225, "vol": 0.025, "trend": 0.05},
    "Shanxi Fenjiu": {"base": 210, "vol": 0.03, "trend": 0.03},
    "Yanghe Distillery": {"base": 155, "vol": 0.02, "trend": 0.06},
}

with st.sidebar:
    st.header("🔍 Select Stock")
    selected_company = st.selectbox("Baijiu Company", list(stock_list.keys()))
    st.caption("Data is simulated based on historical market behavior.")

# --------------------------
# 生成「更真实」的股价数据
# --------------------------
@st.cache_data
def generate_realistic_data(company_params):
    days = 700
    base_price = company_params["base"]
    volatility = company_params["vol"]
    trend_strength = company_params["trend"]

    # 1. 基础趋势（长期缓慢上涨，符合白酒股特性）
    trend = np.linspace(0, trend_strength, days)
    
    # 2. 周期性波动（模拟市场情绪、季度效应）
    cycles = 0.05 * np.sin(np.linspace(0, 10 * np.pi, days))
    
    # 3. 随机波动（市场噪音）
    np.random.seed(hash(selected_company) % 42)
    noise = np.random.normal(0, volatility, days)
    
    # 合成价格序列
    daily_returns = trend + cycles + noise
    prices = base_price * np.cumprod(1 + daily_returns)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
    df = pd.DataFrame({"Close": prices}, index=dates)
    return df

df = generate_realistic_data(stock_list[selected_company])
close_prices = df["Close"]

# --------------------------
# 计算专业指标
# --------------------------
current_price = close_prices.iloc[-1]
start_price = close_prices.iloc[0]
ma20 = close_prices.rolling(20).mean().iloc[-1]
ma60 = close_prices.rolling(60).mean().iloc[-1]
ma120 = close_prices.rolling(120).mean().iloc[-1]

# 趋势判断（基于均线排列，比简单首尾比较更专业）
if ma20 > ma60 and ma60 > ma120:
    trend = "Strong Uptrend"
elif ma20 < ma60 and ma60 < ma120:
    trend = "Strong Downtrend"
elif current_price > ma60:
    trend = "Moderate Uptrend"
else:
    trend = "Sideways/Weak"

# 估值状态（基于当前价与均线的偏离度）
deviation = (current_price - ma60) / ma60
if deviation > 0.15:
    valuation = "Significantly Overvalued"
elif deviation > 0.05:
    valuation = "Modestly Overvalued"
elif deviation < -0.15:
    valuation = "Significantly Undervalued"
elif deviation < -0.05:
    valuation = "Modestly Undervalued"
else:
    valuation = "Fairly Valued"

# --------------------------
# 可视化（优化图表）
# --------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Price Trend & Moving Averages")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(close_prices, color="#8B0000", linewidth=1.5, label="Closing Price")
    ax.plot(close_prices.rolling(20).mean(), color="#FFA500", linestyle="--", linewidth=1, label="20-Day MA")
    ax.plot(close_prices.rolling(60).mean(), color="#1f77b4", linestyle="--", linewidth=1.5, label="60-Day MA")
    ax.plot(close_prices.rolling(120).mean(), color="#2ca02c", linestyle=":", linewidth=1.5, label="120-Day MA")
    ax.set_title(f"{selected_company} Stock Price Analysis", fontsize=14)
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with col2:
    st.subheader("📊 Key Metrics")
    st.metric("Current Price", f"{current_price:.2f} CNY")
    st.metric("Trend", trend)
    st.metric("60-Day MA", f"{ma60:.2f} CNY")
    st.metric("Valuation", valuation)
    st.metric("Price vs. 60-Day MA", f"{deviation:.1%}")

# --------------------------
# 专业投资建议（优化版）
# --------------------------
st.divider()
st.subheader("🧾 Professional Investment Recommendation")

rec = ""
if trend in ["Strong Uptrend", "Moderate Uptrend"] and valuation in ["Fairly Valued", "Modestly Undervalued"]:
    rec = """
    **Bullish Outlook**: The stock exhibits strong momentum with a healthy price structure. 
    **Recommendation**: Consider initiating or adding to positions on pullbacks to the 20-day moving average.
    """
elif trend in ["Strong Uptrend", "Moderate Uptrend"] and valuation in ["Modestly Overvalued", "Significantly Overvalued"]:
    rec = """
    **Cautious Bullish**: While the trend is positive, the stock appears extended. 
    **Recommendation**: Hold existing positions but avoid new entries. Consider partial profit-taking.
    """
elif trend == "Sideways/Weak" and valuation in ["Modestly Undervalued", "Significantly Undervalued"]:
    rec = """
    **Accumulation Zone**: The stock is consolidating at potentially attractive levels. 
    **Recommendation**: Monitor closely for a breakout signal before committing capital.
    """
else:
    rec = """
    **Bearish Caution**: The technical setup suggests caution. 
    **Recommendation**: Reduce exposure or remain on the sidelines until the trend improves.
    """

if "Bullish" in rec:
    st.success(rec)
elif "Cautious" in rec or "Accumulation" in rec:
    st.info(rec)
else:
    st.warning(rec)

st.caption("Disclaimer: This analysis is for educational purposes only and does not constitute financial advice.")
