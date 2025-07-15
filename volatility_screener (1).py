import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta
import mplfinance as mpf
import datetime

# ========== Symbols ==========
forex_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X',
               'USDCAD=X', 'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X',
               'USDNOK=X', 'USDSEK=X', 'USDMXN=X', 'USDCNY=X', 'USDHKD=X']

crypto_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
                'DOGEUSDT', 'ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'SHIBUSDT',
                'DOTUSDT', 'TRXUSDT', 'LINKUSDT', 'LTCUSDT', 'UNIUSDT']

stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
                 'META', 'NVDA', 'NFLX', 'AMD', 'BABA',
                 'JPM', 'BAC', 'WMT', 'DIS', 'V']

# ========== Data Fetching ==========
def fetch_yahoo_data(symbol, interval="15m", lookback="7d"):
    try:
        df = yf.download(symbol, interval=interval, period=lookback)
        df = df.dropna()
        return df
    except:
        return pd.DataFrame()

def fetch_binance_data(symbol, interval="15m", lookback="1d"):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=500"
    try:
        data = pd.read_json(url)
        data.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                        'Close time', 'Quote asset volume', 'Number of trades',
                        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
        df = pd.DataFrame()
        df['Open'] = data['Open'].astype(float)
        df['High'] = data['High'].astype(float)
        df['Low'] = data['Low'].astype(float)
        df['Close'] = data['Close'].astype(float)
        df['Volume'] = data['Volume'].astype(float)
        df.index = pd.to_datetime(data['Open time'], unit='ms')
        df = df.dropna()
        return df
    except:
        return pd.DataFrame()

# ========== AVWAP ==========
def calculate_avwap(df):
    df = df.copy()
    df['cum_vol'] = df['Volume'].cumsum()
    df['cum_vol_price'] = (df['Close'] * df['Volume']).cumsum()
    df['avwap'] = df['cum_vol_price'] / df['cum_vol']
    return df

# ========== Compression Detection ==========
def is_compressed(df, bb_period=20, bb_std=2):
    df = df.copy()
    df = df.dropna()

    if df.empty or len(df) < bb_period:
        return False

    try:
        # Ensure 'Close' is a Series, not a DataFrame or 2D array
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.squeeze()
        bb = ta.volatility.BollingerBands(close=close_series, window=bb_period, window_dev=bb_std)
        hband = bb.bollinger_hband()
        lband = bb.bollinger_lband()
        width = hband - lband
        width_pct = width / close_series

        if width_pct.isnull().all():
            return False

        return width_pct.iloc[-1] < width_pct.quantile(0.15)
    except Exception as e:
        print("Error in is_compressed:", e)
        return False

# ========== Chart Pattern Detection ==========
def detect_flat_base(df):
    if df.empty or len(df) < 10:
        return False
    recent_closes = df['Close'].tail(10)
    return recent_closes.max() - recent_closes.min() < 0.005 * recent_closes.mean()

def detect_sym_triangle(df):
    if df.empty or len(df) < 20:
        return False
    highs = df['High'].tail(20).reset_index(drop=True)
    lows = df['Low'].tail(20).reset_index(drop=True)
    upper_slope = highs.diff().mean()
    lower_slope = lows.diff().mean()
    return upper_slope < 0 and lower_slope > 0

# ========== Screener Logic ==========
def screen_symbol(symbol, source="yahoo", timeframe="15m", ema_fast=9, ema_slow=50,
                  bb_period=20, bb_std=2, avwap_prox=0.003,
                  use_avwap=True, use_patterns=True, enabled_patterns={}):
    if source == "yahoo":
        df = fetch_yahoo_data(symbol, interval=timeframe)
    else:
        df = fetch_binance_data(symbol, interval=timeframe)

    if df.empty or len(df) < max(ema_fast, ema_slow, bb_period):
        return None, None

    df['EMA_fast'] = df['Close'].ewm(span=ema_fast).mean()
    df['EMA_slow'] = df['Close'].ewm(span=ema_slow).mean()
    df = calculate_avwap(df)

    compressed = is_compressed(df, bb_period=bb_period, bb_std=bb_std)

    near_avwap = abs(df['Close'].iloc[-1] - df['avwap'].iloc[-1]) < avwap_prox * df['Close'].iloc[-1]

    patterns = []
    if enabled_patterns.get("Flat Base", False) and detect_flat_base(df):
        patterns.append("Flat Base")
    if enabled_patterns.get("Symmetrical Triangle", False) and detect_sym_triangle(df):
        patterns.append("Symmetrical Triangle")

    signal_triggered = compressed
    if use_avwap:
        signal_triggered &= near_avwap
    if use_patterns and enabled_patterns:
        signal_triggered &= bool(patterns)

    if signal_triggered:
        msg = f"✅ {symbol}: Compression detected"
        if use_avwap:
            msg += " + AVWAP"
        if use_patterns and patterns:
            msg += f" + Pattern(s): {', '.join(patterns)}"

        chart = mpf.plot(df.tail(100), type='candle', mav=(ema_fast, ema_slow), volume=True, returnfig=True)[0]
        img_path = f"{symbol}_chart.png"
        chart.savefig(img_path)
        return msg, img_path

    return None, None
