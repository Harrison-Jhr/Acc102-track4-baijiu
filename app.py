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
st.title("🥃 Baijiu Industry Stock Analysis System")
st.markdown("Professional dashboard with price trends, volume, volatility, and drawdown analysis.")
st.divider()

# --------------------------
# Stock List (MORE BAIJIU BRANDS)
# --------------------------
stock_config = {
    "Kweichow Moutai":            {"base": 1700, "vol": 0.014, "trend": 0.15},
    "Wuliangye":                 {"base": 140,  "vol": 0.020, "trend": 0.09},
    "Luzhou Laojiao":            {"base": 230,  "vol": 0.024, "trend": 0.06},
    "Shanxi Fenjiu":             {"base": 215,  "vol": 0.030, "trend": 0.04},
    "Yanghe Distillery":         {"base": 160,  "vol": 0.021, "trend": 0.08},
    "Gujing Gongjiu":           {"base": 250,  "vol": 0.027, "trend": 0.07},
    "Shede Spirits":             {"base": 140,  "vol": 0.032, "trend": 0.05},
    "Jiugui Liquor":             {"base": 110,  "vol": 0.035, "trend": 0.03},
    "Shunxin Agriculture":      {"base": 55,   "vol": 0.025, "trend": 0.02},
    "Jiannanchun":               {"base": 200,  "vol": 0.023, "trend": 0.06}
}

with st.sidebar:
    st.header("🔍 Analysis Controls")
    selected = st.selectbox("Select Company", list(stock_config.keys()))
    
    # Date range selector
    st.subheader("Date Range")
    date_range = st.select_slider(
        "Select Analysis Period (Days)",
        options=[180, 360, 540, 700],
        value=700
    )
    
    # Chart toggle buttons
    st.subheader("Chart Options")
    show_volume = st.checkbox("Show Volume Chart", value=True)
    show_volatility = st.checkbox("Show Volatility Chart", value=True)
    show_drawdown = st.checkbox("Show Drawdown Chart", value=True)

# --------------------------
# Generate Realistic Data
# --------------------------
@st.cache_data(ttl=3600)
def generate_data(conf, days):
    base = conf["base"]
    vol  = conf["vol"]
    trend = conf["trend"]

    np.random.seed(42 + hash(selected) % 1000)

    trend_line  = np.linspace(0, trend, days)
    cycle       = 0.06 * np.sin(np.linspace(0, 8 * np.pi, days))
    noise       = np.random.normal(0, vol, days)
    ret         = trend_line + cycle + noise
    close       = base * np.cumprod(1 + ret)

    vol_noise    = np.random.lognormal(0, 0.7, days)
    vol_trend    = 1 + 0.8 * np.sin(np.linspace(0, 4 * np.pi, days))
    volume       = (vol_noise * vol_trend * 1000).astype(int)

    idx = pd.date_range(end=pd.Timestamp.now(), periods=days)
    df = pd.DataFrame({
        "Close": close,
        "Volume": volume
    }, index=idx)
    return df

df = generate_data(stock_config[selected], date_range)
close = df["Close"]
vol   = df["Volume"]

# --------------------------
# Technical Indicators
# --------------------------
current   = close.iloc[-1]
ma20      = close.rolling(20).mean().iloc[-1]
ma60      = close.rolling(60).mean().iloc[-1]
ma120     = close.rolling(120).mean().iloc[-1]
dev       = (current - ma60) / ma60
volatility = close.pct_change().rolling(20).std() * np.sqrt(252)
peak = close.cummax()
drawdown = (close - peak) / peak

# Trend
if ma20 > ma60 and ma60 > ma120:
    trend = "Strong Uptrend"
elif ma20 > ma60:
    trend = "Moderate Uptrend"
elif ma20 < ma60 and ma60 < ma120:
    trend = "Strong Downtrend"
else:
    trend = "Sideways / Range Bound"

# Valuation
if dev > 0.15:
    val = "Significantly Overvalued"
elif dev > 0.05:
    val = "Slightly Overvalued"
elif dev < -0.15:
    val = "Significantly Undervalued"
elif dev < -0.05:
    val = "Slightly Undervalued"
else:
    val = "Fairly Valued"

# --------------------------
# Charts
# --------------------------
if show_volume:
    st.subheader("📈 Price & Volume Trend")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    ax1.plot(close, color="#880808", lw=1.8, label="Close")
    ax1.plot(close.rolling(20).mean(), color="#FF9500", lw=1.2, ls="--", label="MA20")
    ax1.plot(close.rolling(60).mean(), color="#007AFF", lw=1.4, ls="--", label="MA60")
    ax1.plot(close.rolling(120).mean(), color="#34C759", lw=1.2, ls=":", label="MA120")
    ax1.legend()
    ax1.grid(alpha=0.25)

    ax2.bar(vol.index, vol, color="#555", alpha=0.7)
    ax2.set_title("Trading Volume", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

if show_volatility:
    st.subheader("📊 20-Day Annualized Volatility")
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(volatility, color="#FF3B30", lw=1.5, label="Volatility")
    ax.axhline(volatility.mean(), color="#555", ls="--", label="Average Volatility")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

if show_drawdown:
    st.subheader("📉 Price Drawdown")
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.fill_between(drawdown.index, drawdown, 0, color="#FF9500", alpha=0.4)
    ax.plot(drawdown, color="#FF3B30", lw=1, label="Drawdown")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

# --------------------------
# Metrics
# --------------------------
st.divider()
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Current Price", f"{current:.2f}")
with c2: st.metric("Trend", trend)
with c3: st.metric("Valuation", val)
with c4: st.metric("Deviation to MA60", f"{dev:.1%}")

# --------------------------
# Investment Analysis
# --------------------------
st.divider()
st.subheader("🧾 Comprehensive Investment Analysis & Recommendation")

comment = ""

if trend == "Strong Uptrend" and val in ["Fairly Valued", "Slightly Undervalued"]:
    comment = f"""
**Overall View**:  
{selected} is in a **sustained strong uptrend** supported by a healthy moving average structure. The stock is fairly valued with moderate momentum.

**Technical Situation**:  
Price is trending higher with stable volatility. Deviation from MA60 is {dev:.1%}, indicating a healthy structure.

**Investment Strategy**:  
• Use pullbacks to MA20/MA60 as buying opportunities  
• Hold for medium-term upside  
• Take partial profits near resistance levels  
• Avoid chasing new highs aggressively

**Risk Points**:  
Sector rotation, market sentiment shifts, and short-term overheating may cause pullbacks.
    """

elif trend == "Strong Uptrend" and val in ["Slightly Overvalued", "Significantly Overvalued"]:
    comment = f"""
**Overall View**:  
{selected} is in an uptrend but appears overvalued relative to its medium-term average.

**Technical Situation**:  
Price extended {dev:.1%} above MA60, suggesting short-term overbought conditions.

**Investment Strategy**:  
• Hold core positions but avoid new entries  
• Trim positions into strength  
• Wait for a 5%–10% pullback before adding  
• Control position size

**Risk Points**:  
High valuation increases downside risk during market corrections.
    """

elif "Sideways" in trend and val in ["Slightly Undervalued", "Significantly Undervalued"]:
    comment = f"""
**Overall View**:  
{selected} is consolidating at undervalued levels, potentially forming a bottom.

**Technical Situation**:  
Price is trading below MA60 with a deviation of {dev:.1%}, offering contrarian potential.

**Investment Strategy**:  
• Accumulate gradually in the range  
• Watch for breakout with volume confirmation  
• Use strict stop-losses below support  
• Be patient for trend recovery

**Risk Points**:  
Support breakdown and continued industry headwinds may delay recovery.
    """

else:
    comment = f"""
**Overall View**:  
{selected} shows a weak technical structure with unfavorable risk-reward.

**Investment Strategy**:  
• Reduce or avoid positions  
• Do not buy dips without stabilization  
• Wait for clear reversal signals  
• Focus on better relative strength stocks

**Risk Points**:  
Trend erosion and market volatility may extend downside.
    """

st.markdown(comment)

st.caption("Disclaimer: For educational and demonstration purposes only. Not investment advice.")
