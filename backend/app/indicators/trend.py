# Source: Doc 02 §2.6 — Trend analysis indicators
"""Trend tespiti göstergeleri: ADX, destek/direnç, dip/kırılım skorlama."""

import pandas as pd

from app.indicators.momentum import (
    calculate_bollinger_bands,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
    calculate_stochastic,
    calculate_volume_ratio,
)


def calculate_adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """ADX (Average Directional Index) — trend gücü (0-100).

    > 25: güçlü trend, < 20: trend yok.
    """
    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.ewm(alpha=1 / period, min_periods=period).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, min_periods=period).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, min_periods=period).mean() / atr

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1)
    adx = dx.ewm(alpha=1 / period, min_periods=period).mean()
    return adx


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume — hacim trendi."""
    direction = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    obv = (volume * direction).cumsum()
    return obv


def detect_obv_trend(close: pd.Series, volume: pd.Series, period: int = 20) -> str:
    """OBV trend yönü: rising / falling / flat."""
    obv = calculate_obv(close, volume)
    if len(obv) < period:
        return "flat"
    obv_sma = obv.rolling(window=period).mean()
    last_obv = obv.iloc[-1]
    last_sma = obv_sma.iloc[-1]
    if pd.isna(last_sma):
        return "flat"
    diff_pct = (last_obv - last_sma) / abs(last_sma) if last_sma != 0 else 0
    if diff_pct > 0.05:
        return "rising"
    elif diff_pct < -0.05:
        return "falling"
    return "flat"


def detect_support_resistance(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    lookback: int = 50,
) -> tuple[float | None, float | None]:
    """Basit destek ve direnç seviyesi tespiti.

    Son N bar'daki pivot noktalarından en yakın destek/direnç bulur.
    Returns: (support_level, resistance_level)
    """
    if len(close) < lookback:
        return None, None

    recent = close.iloc[-lookback:]
    recent_high = high.iloc[-lookback:]
    recent_low = low.iloc[-lookback:]
    current_price = float(close.iloc[-1])

    # Pivot noktaları: yerel min/max (5-bar)
    supports: list[float] = []
    resistances: list[float] = []

    for i in range(2, len(recent) - 2):
        if recent_low.iloc[i] <= recent_low.iloc[i - 1] and recent_low.iloc[i] <= recent_low.iloc[i - 2] and \
           recent_low.iloc[i] <= recent_low.iloc[i + 1] and recent_low.iloc[i] <= recent_low.iloc[i + 2]:
            supports.append(float(recent_low.iloc[i]))

        if recent_high.iloc[i] >= recent_high.iloc[i - 1] and recent_high.iloc[i] >= recent_high.iloc[i - 2] and \
           recent_high.iloc[i] >= recent_high.iloc[i + 1] and recent_high.iloc[i] >= recent_high.iloc[i + 2]:
            resistances.append(float(recent_high.iloc[i]))

    # Fiyatın altındaki en yakın destek, üstündeki en yakın direnç
    support = max([s for s in supports if s < current_price], default=None)
    resistance = min([r for r in resistances if r > current_price], default=None)

    return support, resistance


def detect_macd_crossover(close: pd.Series) -> str:
    """MACD crossover tespiti.

    Returns: bullish_crossover / bearish_crossover / neutral
    """
    macd_line, signal_line, _ = calculate_macd(close)
    if len(macd_line) < 2:
        return "neutral"

    prev_diff = float(macd_line.iloc[-2]) - float(signal_line.iloc[-2])
    curr_diff = float(macd_line.iloc[-1]) - float(signal_line.iloc[-1])

    if pd.isna(prev_diff) or pd.isna(curr_diff):
        return "neutral"

    if prev_diff <= 0 and curr_diff > 0:
        return "bullish_crossover"
    elif prev_diff >= 0 and curr_diff < 0:
        return "bearish_crossover"
    return "neutral"


def detect_trend_status(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
) -> str:
    """Fiyatın trend durumunu tespit et.

    Returns:
        approaching_support, at_support, approaching_resistance, at_resistance,
        new_uptrend, new_downtrend, sideways
    """
    if len(close) < 50:
        return "sideways"

    sma_20 = calculate_sma(close, 20)
    sma_50 = calculate_sma(close, 50)
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)

    price = float(close.iloc[-1])
    s20 = float(sma_20.iloc[-1]) if pd.notna(sma_20.iloc[-1]) else price
    s50 = float(sma_50.iloc[-1]) if pd.notna(sma_50.iloc[-1]) else price
    bbl = float(bb_lower.iloc[-1]) if pd.notna(bb_lower.iloc[-1]) else price * 0.95
    bbu = float(bb_upper.iloc[-1]) if pd.notna(bb_upper.iloc[-1]) else price * 1.05

    support, resistance = detect_support_resistance(high, low, close)

    # Destek/direnç yakınlığı kontrolü (%2 bant)
    if support and abs(price - support) / support < 0.02:
        return "at_support"
    if resistance and abs(price - resistance) / resistance < 0.02:
        return "at_resistance"
    if support and abs(price - support) / support < 0.05:
        return "approaching_support"
    if resistance and abs(price - resistance) / resistance < 0.05:
        return "approaching_resistance"

    # SMA crossover ile trend yönü
    prev_s20 = float(sma_20.iloc[-2]) if pd.notna(sma_20.iloc[-2]) else s20
    prev_s50 = float(sma_50.iloc[-2]) if pd.notna(sma_50.iloc[-2]) else s50

    if prev_s20 <= prev_s50 and s20 > s50:
        return "new_uptrend"
    if prev_s20 >= prev_s50 and s20 < s50:
        return "new_downtrend"

    return "sideways"


def score_dip_candidate(df: pd.DataFrame) -> float:
    """Dip adayı skoru hesapla (0.0 - 1.0).

    Kriterler:
    - RSI < 35 → yüksek skor
    - Fiyat Bollinger alt bandına yakın
    - Hacim artışı
    - Destek seviyesine yakınlık
    - Stochastic oversold
    """
    if df.empty or len(df) < 50:
        return 0.0

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    score = 0.0
    weights_total = 0.0

    # RSI — düşük RSI yüksek dip olasılığı (ağırlık: 0.30)
    rsi = calculate_rsi(close)
    rsi_val = float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50.0
    if rsi_val < 20:
        score += 0.30
    elif rsi_val < 30:
        score += 0.25
    elif rsi_val < 35:
        score += 0.15
    elif rsi_val < 40:
        score += 0.05
    weights_total += 0.30

    # Bollinger — fiyatın alt bandana yakınlığı (ağırlık: 0.20)
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
    price = float(close.iloc[-1])
    bbl = float(bb_lower.iloc[-1]) if pd.notna(bb_lower.iloc[-1]) else price * 0.95
    bbu = float(bb_upper.iloc[-1]) if pd.notna(bb_upper.iloc[-1]) else price * 1.05
    bb_range = bbu - bbl if bbu != bbl else 1
    bb_position = (price - bbl) / bb_range  # 0 = alt bant, 1 = üst bant
    if bb_position < 0.1:
        score += 0.20
    elif bb_position < 0.2:
        score += 0.15
    elif bb_position < 0.3:
        score += 0.08
    weights_total += 0.20

    # Hacim artışı (ağırlık: 0.15)
    vol_ratio = calculate_volume_ratio(volume)
    vr = float(vol_ratio.iloc[-1]) if pd.notna(vol_ratio.iloc[-1]) else 1.0
    if vr > 2.0:
        score += 0.15
    elif vr > 1.5:
        score += 0.10
    elif vr > 1.2:
        score += 0.05
    weights_total += 0.15

    # Destek seviyesi yakınlığı (ağırlık: 0.20)
    support, _ = detect_support_resistance(high, low, close)
    if support and price > 0:
        dist_pct = (price - support) / price
        if dist_pct < 0.02:
            score += 0.20
        elif dist_pct < 0.05:
            score += 0.12
        elif dist_pct < 0.08:
            score += 0.05
    weights_total += 0.20

    # Stochastic oversold (ağırlık: 0.15)
    stoch_k, stoch_d = calculate_stochastic(high, low, close)
    sk = float(stoch_k.iloc[-1]) if pd.notna(stoch_k.iloc[-1]) else 50.0
    if sk < 15:
        score += 0.15
    elif sk < 20:
        score += 0.10
    elif sk < 30:
        score += 0.05
    weights_total += 0.15

    return round(min(score / weights_total * weights_total, 1.0), 4) if weights_total > 0 else 0.0


def score_breakout_candidate(df: pd.DataFrame) -> float:
    """Kırılım adayı skoru hesapla (0.0 - 1.0).

    Kriterler:
    - Fiyat direnç seviyesini kırmış veya Bollinger üst bandını geçmiş
    - Hacim artışı (surge)
    - ADX güçlü trend gösteriyor
    - MACD bullish crossover
    - SMA20 > SMA50 (golden cross yakınlığı)
    """
    if df.empty or len(df) < 50:
        return 0.0

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    score = 0.0

    # Direnç kırılımı (ağırlık: 0.25)
    _, resistance = detect_support_resistance(high, low, close)
    price = float(close.iloc[-1])
    if resistance and price > resistance:
        score += 0.25
    elif resistance and abs(price - resistance) / resistance < 0.02:
        score += 0.15
    elif resistance and abs(price - resistance) / resistance < 0.05:
        score += 0.08

    # Hacim artışı (ağırlık: 0.25)
    vol_ratio = calculate_volume_ratio(volume)
    vr = float(vol_ratio.iloc[-1]) if pd.notna(vol_ratio.iloc[-1]) else 1.0
    if vr > 2.5:
        score += 0.25
    elif vr > 2.0:
        score += 0.20
    elif vr > 1.5:
        score += 0.12
    elif vr > 1.2:
        score += 0.05

    # ADX trend gücü (ağırlık: 0.20)
    adx = calculate_adx(high, low, close)
    adx_val = float(adx.iloc[-1]) if pd.notna(adx.iloc[-1]) else 0.0
    if adx_val > 35:
        score += 0.20
    elif adx_val > 25:
        score += 0.15
    elif adx_val > 20:
        score += 0.08

    # MACD crossover (ağırlık: 0.15)
    crossover = detect_macd_crossover(close)
    if crossover == "bullish_crossover":
        score += 0.15
    elif crossover == "neutral":
        # MACD histogram pozitif
        _, _, hist = calculate_macd(close)
        if pd.notna(hist.iloc[-1]) and float(hist.iloc[-1]) > 0:
            score += 0.05

    # SMA golden cross yakınlığı (ağırlık: 0.15)
    sma_20 = calculate_sma(close, 20)
    sma_50 = calculate_sma(close, 50)
    s20 = float(sma_20.iloc[-1]) if pd.notna(sma_20.iloc[-1]) else price
    s50 = float(sma_50.iloc[-1]) if pd.notna(sma_50.iloc[-1]) else price
    if s20 > s50:
        score += 0.15
    elif s50 > 0 and (s20 / s50) > 0.98:
        score += 0.08

    return round(min(score, 1.0), 4)


def compute_full_indicators(df: pd.DataFrame) -> dict:
    """Tüm trend göstergelerini hesapla (dip/kırılım analizi için genişletilmiş).

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
    adx = calculate_adx(high, low, close)

    support, resistance = detect_support_resistance(high, low, close)
    macd_cross = detect_macd_crossover(close)
    obv_trend = detect_obv_trend(close, volume)

    def safe_float(val, decimals=2):
        return round(float(val), decimals) if pd.notna(val) else None

    last = len(df) - 1
    return {
        "rsi": safe_float(rsi.iloc[last]),
        "macd": safe_float(macd_line.iloc[last], 4),
        "macd_signal": safe_float(signal_line.iloc[last], 4),
        "macd_histogram": safe_float(histogram.iloc[last], 4),
        "macd_crossover": macd_cross,
        "stoch_k": safe_float(stoch_k.iloc[last]),
        "stoch_d": safe_float(stoch_d.iloc[last]),
        "bb_upper": safe_float(bb_upper.iloc[last]),
        "bb_middle": safe_float(bb_middle.iloc[last]),
        "bb_lower": safe_float(bb_lower.iloc[last]),
        "sma_20": safe_float(sma_20.iloc[last]),
        "sma_50": safe_float(sma_50.iloc[last]),
        "ema_12": safe_float(ema_12.iloc[last]),
        "adx": safe_float(adx.iloc[last]),
        "volume_ratio": safe_float(vol_ratio.iloc[last]),
        "support_level": support,
        "resistance_level": resistance,
        "obv_trend": obv_trend,
    }
