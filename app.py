import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# 页面设置
st.set_page_config(page_title="白酒股票分析系统", page_icon="🥃", layout="wide")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 标题
st.title("🥃 白酒行业股票专业分析系统")
st.caption("真实市场数据 · 专业分析界面")
st.divider()

# 白酒股票列表（美股/港股可在Streamlit云正常读取）
stock_list = {
    "贵州茅台": "600519.SS",
    "五粮液": "000858.SZ",
    "泸州老窖": "000568.SZ",
    "山西汾酒": "600809.SS",
    "洋河股份": "002304.SZ",
}

# 选择股票
with st.sidebar:
    st.header("🔍 选择股票")
    selected = st.selectbox("白酒公司", list(stock_list.keys()))
    code = stock_list[selected]

# 获取真实数据（yfinance 可在云端稳定运行）
@st.cache_data(ttl=3600)
def get_data(code):
    end = datetime.now()
    start = end - timedelta(days=700)
    df = yf.download(code, start=start, end=end)
    return df

df = get_data(code)

# 计算指标
close = df["Close"]
current = close.iloc[-1]
ma60 = close.rolling(60).mean().iloc[-1]
trend = "上涨" if close.iloc[-1] > close.iloc[0] else "下跌/震荡"
val = "高估" if current > ma60*1.08 else "低估" if current < ma60*0.93 else "合理"

# 图表
c1, c2 = st.columns([1.5, 1])
with c1:
    st.subheader("📈 股价走势")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(close, color="#8B0000", linewidth=2, label="Close Price")
    ax.plot(close.rolling(60).mean(), "--", color="#1f77b4", label="MA60")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with c2:
    st.subheader("📊 核心指标")
    st.metric("当前价格", f"{current:.2f} 元")
    st.metric("中期趋势", trend)
    st.metric("60日均线", f"{ma60:.2f}")
    st.metric("估值状态", val)

# 投资建议
st.divider()
st.subheader("🧾 专业投资建议")

if trend == "上涨" and val == "合理":
    st.success("✅ 趋势健康 + 估值合理 → 建议逢调整布局，中期持有")
elif trend == "上涨" and val == "高估":
    st.warning("⚠️ 趋势偏强但估值偏高 → 轻仓参与，不追高")
elif trend == "下跌/震荡" and val == "低估":
    st.info("🔍 趋势偏弱但价格低估 → 等待企稳信号")
else:
    st.error("🛑 趋势走弱 + 估值偏高 → 建议控制仓位或暂时回避")

st.caption("数据来源：Yahoo Finance | 仅供学习使用")
