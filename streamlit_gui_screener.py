# streamlit_gui_screener.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
from volatility_screener import screen_symbol, forex_pairs, crypto_pairs, stock_symbols, fetch_yahoo_data, fetch_binance_data

# ========== UI CONFIG ==========
st.set_page_config(layout="wide", page_title="Coiling Market Screener")
st.title("🚨 Coiling Market Screener (Free Edition)")

# Sidebar — Controls
st.sidebar.header("⚙️ Screener Settings")

# Timeframe
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "4h", "1d"], index=1)

# Indicator Settings
st.sidebar.subheader("📐 Indicators")
ema_fast = st.sidebar.number_input("Fast EMA", min_value=1, value=9)
ema_slow = st.sidebar.number_input("Slow EMA", min_value=2, value=50)
bb_period = st.sidebar.number_input("BB Period", min_value=5, value=20)
bb_std = st.sidebar.number_input("BB StdDev", min_value=1.0, value=2.0, step=0.1)
avwap_prox = st.sidebar.slider("AVWAP Proximity (%)", min_value=0.1, max_value=1.0, value=0.3) / 100

# Toggles
st.sidebar.subheader("🔍 Filters")
use_avwap = st.sidebar.checkbox("Use AVWAP Confluence", value=True)
use_patterns = st.sidebar.checkbox("Use Chart Patterns", value=True)

pattern_flat = st.sidebar.checkbox("Flat Base", value=True)
pattern_triangle = st.sidebar.checkbox("Symmetrical Triangle", value=True)

# Assets
st.sidebar.subheader("💱 Asset Classes")
use_forex = st.sidebar.checkbox("Forex", value=True)
use_crypto = st.sidebar.checkbox("Crypto", value=True)
use_stocks = st.sidebar.checkbox("Stocks", value=True)

# Auto-refresh
st.sidebar.subheader("🔁 Auto Refresh")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=False)
refresh_interval = st.sidebar.slider("Interval (minutes)", 1, 30, 5) if auto_refresh else None

# Run button
run_now = st.sidebar.button("🚀 Run Screener Now")

# Export options
st.sidebar.subheader("📁 Export")
save_csv = st.sidebar.checkbox("Save Results to CSV", value=True)

# Main logic area
if run_now or auto_refresh:
    st.subheader("📋 Screener Alerts")
    assets = []
    if use_forex:
        assets += [(s, 'yahoo') for s in forex_pairs]
    if use_stocks:
        assets += [(s, 'yahoo') for s in stock_symbols]
    if use_crypto:
        assets += [(s, 'binance') for s in crypto_pairs]

    alert_log = []
    placeholder = st.empty()
    progress = st.progress(0)

    for i, (symbol, source) in enumerate(assets):
        msg, chart = screen_symbol(
            symbol=symbol,
            source=source,
            timeframe=timeframe,
            ema_fast=ema_fast,
            ema_slow=ema_slow,
            bb_period=bb_period,
            bb_std=bb_std,
            avwap_prox=avwap_prox,
            use_avwap=use_avwap,
            use_patterns=use_patterns,
            enabled_patterns={"Flat Base": pattern_flat, "Symmetrical Triangle": pattern_triangle}
        )
        if msg:
            alert_log.append({"Time": datetime.datetime.now(), "Symbol": symbol, "Message": msg})
            st.success(msg)
            if chart:
                st.image(chart, caption=symbol)
        progress.progress((i + 1) / len(assets))

    if save_csv and alert_log:
        df = pd.DataFrame(alert_log)
        df.to_csv("screener_signals.csv", index=False)
        st.info("📁 Alerts saved to screener_signals.csv")

    if not alert_log:
        placeholder.warning("No signals met the criteria at this time.")

    # Auto-refresh logic
    if auto_refresh:
        st.info(f"🔁 Auto-refreshing in {refresh_interval} minute(s)...")
        time.sleep(refresh_interval * 60)
        st.experimental_rerun()
