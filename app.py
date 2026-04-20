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
st.markdown("Professional dashboard for price trends, volume structure, and investment strategy.")
st.divider()

# --------------------------
# Stock List
# --------------------------
stock_config = {
    "Kweichow Moutai":    {"base": 1700, "vol": 0.014, "trend": 0.15},
    "Wuliangye":         {"base": 140,  "vol": 0.020, "trend": 0.09},
    "Luzhou Laojiao":    {"base": 230,  "vol": 0.024, "trend": 0.06},
    "Shanxi Fenjiu":     {"base": 215,  "vol": 0.030, "trend": 0.04},
    "Yanghe Distillery": {"base": 160,  "vol": 0.021, "trend": 0.08},
}

with st.sidebar:
    st.header("🔍 Select Stock")
    selected = st.selectbox("Company", list(stock_config.keys()))

# --------------------------
# Generate Realistic Data + Volume
# --------------------------
@st.cache_data(ttl=3600)
def generate_data(conf):
    days = 700
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

df = generate_data(stock_config[selected])
close = df["Close"]
vol   = df["Volume"]

# --------------------------
# Indicators
# --------------------------
current   = close.iloc[-1]
ma20      = close.rolling(20).mean().iloc[-1]
ma60      = close.rolling(60).mean().iloc[-1]
ma120     = close.rolling(120).mean().iloc[-1]
dev       = (current - ma60) / ma60

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
# Chart: Price + Volume
# --------------------------
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
# LONG & DETAILED INVESTMENT COMMENTARY
# --------------------------
st.divider()
st.subheader("🧾 Comprehensive Investment Analysis & Recommendation")

comment = ""

if trend == "Strong Uptrend" and val in ["Fairly Valued", "Slightly Undervalued"]:
    comment = f"""
**Overall View**:  
{selected} is in a **sustained strong uptrend** supported by a healthy moving average structure (MA20 above MA60, MA60 above MA120). The stock is relatively valued at present, with no extreme overheating.

**Technical Situation**:  
Price is steadily trending higher with controlled volatility. Volume patterns show accumulation during pullbacks, indicating institutional interest. The current deviation from the 60-day MA is {dev:.1%}, which is moderate and not excessive.

**Fundamental Logic (Simulated)**:  
Baijiu industry remains resilient with stable consumption upgrades. Leading brands enjoy pricing power and margin stability.

**Investment Strategy**:  
• Use short-term pullbacks toward the 20-day or 60-day moving average as buying opportunities.  
• Maintain a medium-term holding perspective.  
• Set partial profit-taking targets near historical resistance zones.  
• Avoid chasing intraday spikes; focus on structured entry points.

**Risk Points**:  
Short-term market sentiment shifts, sector rotation, and liquidity tightening could cause temporary pullbacks.
    """

elif trend == "Strong Uptrend" and val in ["Slightly Overvalued", "Significantly Overvalued"]:
    comment = f"""
**Overall View**:  
{selected} remains in a clear uptrend but has moved into **overvalued territory** relative to its medium-term average. The momentum is still positive but becoming extended.

**Technical Situation**:  
Price has deviated {dev:.1%} from the 60-day MA, which suggests short-term overbought conditions. Volume may start to show divergence on new highs.

**Investment Strategy**:  
• Hold core positions but avoid adding new exposure at current levels.  
• Consider trimming positions into strength to lock in profits.  
• Wait for a retracement of 5%–10% before reconsidering additions.  
| Strictly avoid chasing prices at current valuation.

**Risk Points**:  
High valuation amplifies downside risk during market corrections. A trend reversal could lead to relatively deep adjustments.
    """

elif "Sideways" in trend and val in ["Slightly Undervalued", "Significantly Undervalued"]:
    comment = f"""
**Overall View**:  
{selected} is in a **consolidation phase** with low volatility and appears undervalued relative to its medium-term trend. The stock is building a bottom structure.

**Technical Situation**:  
Price is trading below the 60-day MA with a deviation of {dev:.1%}, indicating a potential contrarian opportunity if support holds. Volume is light, typical of accumulation phases.

**Investment Strategy**:  
• Use this range to gradually build positions in tranches.  
| Focus on downside protection rather than quick gains.  
• Watch for a breakout above the range resistance with volume confirmation.  
• Patience is required; sideways action can last for weeks.

**Risk Points**:  
A break below support could trigger further stop-loss selling. Industry headwinds may delay a trend recovery.
    """

elif "Downtrend" in trend or (trend == "Sideways" and val in ["Overvalued"]):
    comment = f"""
**Overall View**:  
{selected} shows weak technical structure with either a clear downtrend or unfavorable valuation. The risk-reward ratio is currently unattractive.

**Technical Situation**:  
Moving averages are aligned negatively, and price action lacks sustained buying pressure. Deviation from the medium-term average does not yet support a contrarian case.

**Investment Strategy**:  
• Reduce or avoid positions for the time being.  
• Do not attempt to “buy the dip” without clear stabilization signals.  
• Wait for a confirmed trend reversal (e.g., higher lows, moving average crossover).  
• Shift focus to better-structured opportunities in the same sector.

**Risk Points**:  
Continued trend erosion, sentiment deterioration, and broader market volatility can extend downside.
    """

else:
    comment = "The stock is in a balanced state with no strong directional signal. Maintain a neutral view and observe further price action."

st.markdown(comment)

st.caption("Disclaimer: For educational and demonstration purposes only. Not investment advice.")
