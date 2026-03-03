"""Formatlama yardımcı fonksiyonları."""

from decimal import Decimal


def format_currency(amount: Decimal | float, symbol: str = "₺") -> str:
    """Para birimini formatla. Örnek: 1250000.50 → ₺1,250,000.50"""
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: Decimal | float) -> str:
    """Yüzde formatla. Örnek: 1.56 → +1.56%"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_volume(volume: int) -> str:
    """Hacim formatla. Örnek: 45230000 → 45.23M"""
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.1f}K"
    return str(volume)
