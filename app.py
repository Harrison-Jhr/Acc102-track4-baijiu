import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Baijiu Stock Analysis", layout="wide")
st.title("Chinese Baijiu Stock Interactive Analysis Tool")
st.subheader("Moutai, Wuliangye, Luzhou Laojiao")

tickers = {
    "Kweichow Moutai": "600519.SS",
    "Wuliangye": "000858.SZ",
    "Luzhou Laojiao": "000568.SZ"
}

company = st.selectbox("Choose a company to analyze", list(tickers.keys()))
years = st.slider("Select analysis period (years)", 2, 7, 5)

with st.spinner("Loading data..."):
    df = yf.Ticker(tickers[company]).history(period=f"{years}y")

df = df.dropna()
df["Year"] = df.index.year
yearly_avg = df.groupby("Year")["Close"].mean().round(2)

st.subheader(f"{company} Yearly Average Closing Price")
st.dataframe(yearly_avg, use_container_width=True)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(yearly_avg.index, yearly_avg.values, marker="o", color="#8B0000", linewidth=2)
ax.set_title(f"{company} Stock Price Trend (Past {years} Years)", fontsize=14)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Average Closing Price (CNY)", fontsize=12)
ax.grid(alpha=0.3)
st.pyplot(fig, use_container_width=True)

st.subheader("Key Insights")
st.write(f"1. {company} has shown a clear long-term price trend over the past {years} years.")
st.write("2. Volatility often correlates with industry policies and market sentiment.")
st.write("3. This tool allows quick comparison of performance across major baijiu companies.")
