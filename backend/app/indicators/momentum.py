"""Momentum göstergeleri: RSI, MACD, Stochastic, Bollinger Bands, MA."""

import pandas as pd


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """RSI (Relative Strength Index) hesapla.

    Args:
        prices: Kapanış fiyatları serisi
        period: RSI periyodu (varsayılan: 14)

    Returns:
        RSI değerleri (0-100 arası)
    """
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD (Moving Average Convergence Divergence) hesapla.

    Args:
        prices: Kapanış fiyatları serisi
        fast_period: Hızlı EMA periyodu
        slow_period: Yavaş EMA periyodu
        signal_period: Sinyal çizgisi periyodu

    Returns:
        (macd_line, signal_line, histogram)
    """
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator (%K ve %D) hesapla.

    Returns:
        (%K, %D)
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()

    return k, d


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands hesapla.

    Returns:
        (upper_band, middle_band, lower_band)
    """
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower


def calculate_sma(prices: pd.Series, period: int = 20) -> pd.Series:
    """Simple Moving Average."""
    return prices.rolling(window=period).mean()


def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
    """Exponential Moving Average."""
    return prices.ewm(span=period, adjust=False).mean()


def calculate_volume_ratio(volumes: pd.Series, period: int = 20) -> pd.Series:
    """Hacim oranı — mevcut hacim / ortalama hacim."""
    avg_volume = volumes.rolling(window=period).mean()
    return volumes / avg_volume


def compute_indicators(df: pd.DataFrame) -> dict:
    """DataFrame'den tüm göstergeleri hesapla.

    df: OHLCV DataFrame (time, open, high, low, close, volume sütunları)
    Returns: dict of indicator values (son değerler)
    """
    if df.empty or len(df) < 26:
        return {}

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    rsi = calculate_rsi(close)
    macd_line, signal_line, histogram = calculate_macd(close)
    stoch_k, stoch_d = calculate_stochastic(high, low, close)
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
    sma_20 = calculate_sma(close, 20)
    sma_50 = calculate_sma(close, 50)
    ema_12 = calculate_ema(close, 12)
    vol_ratio = calculate_volume_ratio(volume)

    last = len(df) - 1
    return {
        "rsi": round(float(rsi.iloc[last]), 2) if pd.notna(rsi.iloc[last]) else None,
        "macd": round(float(macd_line.iloc[last]), 4) if pd.notna(macd_line.iloc[last]) else None,
        "macd_signal": round(float(signal_line.iloc[last]), 4) if pd.notna(signal_line.iloc[last]) else None,
        "macd_histogram": round(float(histogram.iloc[last]), 4) if pd.notna(histogram.iloc[last]) else None,
        "stoch_k": round(float(stoch_k.iloc[last]), 2) if pd.notna(stoch_k.iloc[last]) else None,
        "stoch_d": round(float(stoch_d.iloc[last]), 2) if pd.notna(stoch_d.iloc[last]) else None,
        "bb_upper": round(float(bb_upper.iloc[last]), 2) if pd.notna(bb_upper.iloc[last]) else None,
        "bb_middle": round(float(bb_middle.iloc[last]), 2) if pd.notna(bb_middle.iloc[last]) else None,
        "bb_lower": round(float(bb_lower.iloc[last]), 2) if pd.notna(bb_lower.iloc[last]) else None,
        "sma_20": round(float(sma_20.iloc[last]), 2) if pd.notna(sma_20.iloc[last]) else None,
        "sma_50": round(float(sma_50.iloc[last]), 2) if pd.notna(sma_50.iloc[last]) else None,
        "ema_12": round(float(ema_12.iloc[last]), 2) if pd.notna(ema_12.iloc[last]) else None,
        "volume_ratio": round(float(vol_ratio.iloc[last]), 2) if pd.notna(vol_ratio.iloc[last]) else None,
    }
