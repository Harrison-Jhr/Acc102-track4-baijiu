# Acc102-track4-baijiu
# Baijiu Stock Analysis Tool (2022–2026)
## 1. Product Overview
This is an interactive Python data product built with **Streamlit** for financial and investment analysis. It provides visual analysis and comparison for major Chinese baijiu stocks, with the CSI 300 Index as a market benchmark. The product is designed for finance students, investors, and researchers who need clear, long‑term stock performance insights.

## 2. Analytical Problem & Target User
- **Problem**: Users need a simple, interactive tool to view long‑term price trends, risk indicators, and return performance of baijiu stocks.
- **Target User**: Finance students, individual investors, and anyone analyzing the Chinese consumer baijiu sector.

## 3. Dataset & Source
- **Data Period**: 2022‑01‑01 to 2026‑04‑21
- **Assets**: 9 listed baijiu companies including Kweichow Moutai, Wuliangye, Luzhou Laojiao, Shanxi Fenjiu, Yanghe Distillery, Gujing Gongjiu, Shede Spirits, Jiugui Liquor, Shunxin Agriculture.
- **Benchmark**: CSI 300 Index
- **Data Logic**: Simulated based on real historical price trends, return rates, volatility, and industry performance.
- **Access Date**: April 21, 2026

## 4. Python Methods Used
- Data generation & simulation with NumPy
- Data processing & indicator calculation with Pandas
- Visualization with Matplotlib
- Interactive web interface with Streamlit
- Financial indicators: Price trend, cumulative return, trading volume, RSI (14d), 20‑day volatility, maximum drawdown

## 5. Key Features
- Single stock analysis mode
- Dual stock comparison mode
- 6 professional financial charts
- Automatic performance metrics table
- AI‑supported professional analysis & investment suggestions

## 6. How to Run
1. Install dependencies:
pip install streamlit pandas matplotlib numpy
2. Run the app:
streamlit run app.py
3. Open browser at http://localhost:8501

## 7. Product Link
[Your Streamlit deployment link / GitHub repo link]

## 8. Limitations & Improvements
- Data is simulated based on real trends; not real‑time market data.
- Future version can connect to Yahoo Finance or real API.
- Add more financial indicators (PE, PB, profit margin).

## 9. File Structure
- app.py: Main interactive tool
- README.md: Project documentation
- requirements.txt: Dependencies
