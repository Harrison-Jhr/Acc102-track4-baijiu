import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

st.title("Chinese Baijiu Stock Analysis Tool")
st.subheader("Moutai, Wuliangye, Luzhou Laojiao")

tickers = {
    "Moutai": "600519.SS",
    "Wuliangye": "000858.SZ",
    "Luzhou Laojiao": "000568.SZ"
}

company = st.selectbox("Choose Company", list(tickers.keys()))
years = st.slider("Time Period (Years)", 2, 7, 5)

df = yf.Ticker(tickers[company]).history(period=f"{years}y")
df = df.dropna()
df["Year"] = df.index.year

year_avg = df.groupby("Year")["Close"].mean().round(2)

st.subheader("Yearly Average Close Price")
st.dataframe(year_avg)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(year_avg.index, year_avg, marker="o", color="darkred")
ax.set_title(f"{company} Price Trend")
st.pyplot(fig)

st.subheader("Key Insights")
st.write("1. Long-term price trend shows industry growth pattern.")
st.write("2. Volatility relates to market and policy environment.")
st.write("3. This tool supports quick visual comparison across firms.")
