"""Broker bağlantı yönetimi şemaları."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class BrokerType(str, Enum):
    PAPER = "paper"
    IS_YATIRIM = "is_yatirim"
    GEDIK = "gedik"
    DENIZ = "deniz"
    GARANTI = "garanti"


class BrokerStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


# ── Request Schemas ──


class BrokerConnectionCreate(BaseModel):
    broker_name: BrokerType = Field(..., description="Broker tipi")
    credentials: dict = Field(
        ...,
        description="Broker kimlik bilgileri (API key, username, password vb.)",
        examples=[{"api_key": "xxx", "api_secret": "yyy"}],
    )
    is_paper_trading: bool = Field(
        default=False,
        description="Paper trading modunda mı çalışacak",
    )
    label: str = Field(
        default="",
        max_length=100,
        description="Bağlantı için kullanıcı tanımlı etiket",
    )


class BrokerConnectionUpdate(BaseModel):
    credentials: dict | None = Field(None, description="Güncellenmiş kimlik bilgileri")
    is_paper_trading: bool | None = None
    is_active: bool | None = None
    label: str | None = Field(None, max_length=100)


# ── Response Schemas ──


class BrokerConnectionResponse(BaseModel):
    id: UUID
    broker_name: str
    is_active: bool
    is_paper_trading: bool
    label: str
    status: BrokerStatus
    last_connected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BrokerConnectionListResponse(BaseModel):
    items: list[BrokerConnectionResponse]
    total: int


class BrokerTestResult(BaseModel):
    success: bool
    broker_name: str
    message: str
    latency_ms: float | None = None


class BrokerQuoteResponse(BaseModel):
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    source: str = "paper"


# ── Broker Bilgileri ──


class BrokerInfo(BaseModel):
    name: BrokerType
    display_name: str
    description: str
    requires_credentials: bool
    credential_fields: list[str]
    is_available: bool


class BrokerListInfo(BaseModel):
    brokers: list[BrokerInfo]


# ── Yapılandırılmış broker bilgileri ──

BROKER_REGISTRY: dict[str, BrokerInfo] = {
    "paper": BrokerInfo(
        name=BrokerType.PAPER,
        display_name="Paper Trading",
        description="Sanal para ile simülasyon — gerçek emir gönderilmez",
        requires_credentials=False,
        credential_fields=[],
        is_available=True,
    ),
    "is_yatirim": BrokerInfo(
        name=BrokerType.IS_YATIRIM,
        display_name="İş Yatırım",
        description="İş Yatırım Menkul Değerler API entegrasyonu",
        requires_credentials=True,
        credential_fields=["api_key", "api_secret", "account_id"],
        is_available=False,
    ),
    "gedik": BrokerInfo(
        name=BrokerType.GEDIK,
        display_name="Gedik Yatırım",
        description="Gedik Yatırım Menkul Değerler API entegrasyonu",
        requires_credentials=True,
        credential_fields=["username", "password", "account_no"],
        is_available=False,
    ),
    "deniz": BrokerInfo(
        name=BrokerType.DENIZ,
        display_name="Deniz Yatırım",
        description="Deniz Yatırım Menkul Değerler API entegrasyonu",
        requires_credentials=True,
        credential_fields=["api_key", "secret_key"],
        is_available=False,
    ),
    "garanti": BrokerInfo(
        name=BrokerType.GARANTI,
        display_name="Garanti BBVA Yatırım",
        description="Garanti BBVA Yatırım API entegrasyonu",
        requires_credentials=True,
        credential_fields=["client_id", "client_secret", "account_id"],
        is_available=False,
    ),
}
