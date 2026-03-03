"""Broker factory — broker adına göre doğru adapter'ı döner."""

from app.brokers.base import AbstractBroker
from app.brokers.paper_broker import PaperBroker


def get_broker(broker_name: str, credentials: dict | None = None) -> AbstractBroker:
    """Broker adapter factory.

    Args:
        broker_name: 'paper', 'is_yatirim', 'gedik'
        credentials: Broker API kimlik bilgileri (şifresi çözülmüş)

    Returns:
        AbstractBroker implementasyonu
    """
    brokers = {
        "paper": PaperBroker,
        # "is_yatirim": IsYatirimBroker,  # Faz 2'de eklenecek
        # "gedik": GedikBroker,            # Faz 4'te eklenecek
    }

    broker_class = brokers.get(broker_name)
    if not broker_class:
        raise ValueError(f"Bilinmeyen broker: {broker_name}")

    return broker_class()
