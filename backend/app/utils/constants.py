"""Uygulama sabitleri."""

from datetime import time

# BIST Seans Saatleri (Türkiye saati, UTC+3)
BIST_OPENING_TIME = time(10, 0)   # 10:00
BIST_CLOSING_TIME = time(18, 0)   # 18:00
BIST_LUNCH_START = time(12, 30)   # 12:30
BIST_LUNCH_END = time(14, 0)      # 14:00

# BIST çalışma günleri (Pazartesi=0, Cuma=4)
BIST_TRADING_DAYS = {0, 1, 2, 3, 4}

# Varsayılan Risk Limitleri
DEFAULT_RISK_LIMITS = {
    "max_daily_loss_pct": 2.0,           # Portföyün %2'si
    "max_position_size_pct": 10.0,       # Portföyün %10'u
    "max_open_positions": 10,
    "stop_loss_required": True,
    "max_order_value": 50_000.0,         # TL
    "max_daily_orders": 50,
    "max_correlated_positions": 3,
}

# Desteklenen Timeframe'ler
TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"]

# Desteklenen Emir Tipleri
ORDER_TYPES = ["market", "limit", "stop_loss", "take_profit", "trailing_stop"]

# Desteklenen Roller
USER_ROLES = ["admin", "trader", "viewer", "api_user"]

# Komisyon oranları (varsayılan)
DEFAULT_COMMISSION_RATE = 0.001  # %0.1
DEFAULT_SLIPPAGE_RATE = 0.0005   # %0.05
