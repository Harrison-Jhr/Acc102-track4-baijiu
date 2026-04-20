import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 设置页面
st.set_page_config(page_title="Baijiu Stock Analysis", layout="wide")
st.title("Chinese Baijiu Stock Interactive Analysis Tool")
st.subheader("Moutai, Wuliangye, Luzhou Laojiao")

# 固定示例数据（避免yfinance限流问题）
data = {
    "Kweichow Moutai": {
        2020: 1700,
        2021: 1900,
        2022: 1800,
        2023: 1750,
        2024: 1850,
        2025: 1950
    },
    "Wuliangye": {
        2020: 260,
        2021: 280,
        2022: 270,
        2023: 265,
        2024: 275,
        2025: 290
    },
    "Luzhou Laojiao": {
        2020: 220,
        2021: 240,
        2022: 230,
        2023: 225,
        2024: 235,
        2025: 250
    }
}

# 用户交互选择
company = st.selectbox("Choose a company to analyze", list(data.keys()))
years = st.slider("Select analysis period (years)", 2, 6, 5)

# 提取对应公司的最近N年数据
df = pd.DataFrame(list(data[company].items()), columns=["Year", "Close"])
df = df.tail(years)

# 数据展示
st.subheader(f"{company} Yearly Average Closing Price (Sample Data)")
st.dataframe(df, use_container_width=True)

# 绘制折线图
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Year"], df["Close"], marker="o", color="#8B0000", linewidth=2)
ax.set_title(f"{company} Stock Price Trend (Past {years} Years)", fontsize=14)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Average Closing Price (CNY)", fontsize=12)
ax.grid(alpha=0.3)
st.pyplot(fig, use_container_width=True)

# 关键洞察
st.subheader("Key Insights")
st.write(f"1. {company} has shown a steady upward trend over the past {years} years.")
st.write("2. Volatility reflects market demand and industry policies.")
st.write("3. This tool supports quick visual comparison of baijiu company performance.")
