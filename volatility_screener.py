# volatility_screener.py

import yfinance as yf
import requests
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
import mplfinance as mpf

# ========== SETTINGS ==========
TIMEFRAME = '15m'
EMA_FAST = 9
EMA_SLOW = 50
BB_PERIOD = 20
BB_STD = 2
USE_AVWAP_CONFLUENCE = True
AVWAP_PROXIMITY = 0.003  # 0.3%

# ========== SYMBOLS ==========
forex_pairs = ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "USDCHF=X", "USDCAD=X", "AUDUSD=X", "NZDUSD=X",
               "EURJPY=X", "GBPJPY=X", "EURGBP=X", "AUDJPY=X", "CHFJPY=X", "EURCHF=X", "CADJPY=X", "NZDJPY=X"]

crypto_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "TONUSDT",
                "AVAXUSDT", "LINKUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT", "MATICUSDT", "BCHUSDT"]

stock_symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "JPM", "NFLX", "AMD",
                 "BA", "BRK-B", "ORCL", "UNH", "PFE"]

# ========== FUNCTIONS ==========

def fetch_yahoo_data(symbol):
    try:
        df = yf.download(tickers=symbol, interval=TIMEFRAME, period="5d", progress=False)
        return df
    except:
        return None

def fetch_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=200"
    try:
        res = requests.get(url).json()
        df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'])
        df['Date'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('Date', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df.columns = [c.capitalize() for c in df.columns]
        return df
    except:
        return None

def is_compressed(df, bb_period=BB_PERIOD, bb_std=BB_STD):
    bb = ta.volatility.BollingerBands(df['Close'], window=bb_period, window_dev=bb_std)
    width = bb.bollinger_hband() - bb.bollinger_lband()
    width_pct = width / df['Close']
    return width_pct.iloc[-1] < width_pct.quantile(0.15)

def ema_structure(df, ema_fast=EMA_FAST, ema_slow=EMA_SLOW):
    ema_fast_series = df['Close'].ewm(span=ema_fast).mean()
    ema_slow_series = df['Close'].ewm(span=ema_slow).mean()
    slope_fast = ema_fast_series.diff().iloc[-1]
    slope_slow = ema_slow_series.diff().iloc[-1]
    tight = abs(ema_fast_series.iloc[-1] - ema_slow_series.iloc[-1]) / df['Close'].iloc[-1] < 0.002
    return tight, slope_fast, slope_slow

def compute_avwap(df, anchor_time):
    try:
        anchor_idx = df.index.get_loc(anchor_time, method='nearest')
        sub_df = df.iloc[anchor_idx:]
        price = (sub_df['High'] + sub_df['Low'] + sub_df['Close']) / 3
        if 'Volume' in sub_df.columns and sub_df['Volume'].sum() > 0:
            vwap = (price * sub_df['Volume']).cumsum() / sub_df['Volume'].cumsum()
        else:
            vwap = price.expanding().mean()
        return vwap
    except:
        return None

def get_ny_session_open_time(df):
    try:
        df = df.copy()
        df['Hour'] = df.index.hour
        df['Minute'] = df.index.minute
        session_open = df[(df['Hour'] == 15) & (df['Minute'] == 0)].index
        return session_open[-1] if not session_open.empty else None
    except:
        return None

def plot_chart(df, symbol):
    filename = f"chart_{symbol.replace('=X','')}.png"
    mpf.plot(df[-50:], type='candle', mav=(EMA_FAST, EMA_SLOW), volume=False, style='yahoo', savefig=filename)
    return filename

def screen_symbol(symbol, source='yahoo', timeframe='15m', ema_fast=EMA_FAST, ema_slow=EMA_SLOW,
                  bb_period=BB_PERIOD, bb_std=BB_STD, avwap_prox=AVWAP_PROXIMITY,
                  use_avwap=USE_AVWAP_CONFLUENCE, use_patterns=True, enabled_patterns={}):
    df = fetch_yahoo_data(symbol) if source == 'yahoo' else fetch_binance_data(symbol)
    if df is None or len(df) < ema_slow:
        return None, None

    compressed = is_compressed(df, bb_period=bb_period, bb_std=bb_std)
    tight, slope_fast, slope_slow = ema_structure(df, ema_fast=ema_fast, ema_slow=ema_slow)
    avwap_confluence = False

    if use_avwap:
        anchor_time = get_ny_session_open_time(df)
        if anchor_time:
            vwap_series = compute_avwap(df, anchor_time)
            if vwap_series is not None:
                last_close = df['Close'].iloc[-1]
                vwap_now = vwap_series.iloc[-1]
                distance = abs(last_close - vwap_now) / last_close
                avwap_confluence = distance < avwap_prox

    if compressed and tight and (not use_avwap or avwap_confluence):
        msg = f"⚠️ {symbol} is coiling on {timeframe}\nEMA diff tight | Volatility low"
        if use_avwap:
            msg += f" | AVWAP Confluence ✅"
        msg += f"\nFast EMA slope: {slope_fast:.5f}, Slow EMA slope: {slope_slow:.5f}"
        chart_path = plot_chart(df, symbol)
        return msg, chart_path
    return None, None
