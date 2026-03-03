# Source: Doc 10 §Faz 3 Sprint 3.1 — AI Pydantic şemaları
"""AI analiz ve sohbet şemaları."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ── Enum'lar ──


class AISignalAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class AIConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# ── Analiz Şemaları ──


class AIAnalysisRequest(BaseModel):
    """Sembol AI analiz isteği."""
    symbol: str = Field(..., description="BIST sembol kodu, ör: THYAO")
    period: str = Field(default="daily", description="Periyod: daily / weekly")
    include_indicators: bool = Field(default=True, description="Teknik göstergeleri dahil et")


class AIIndicatorSummary(BaseModel):
    """Gösterge özet bilgisi."""
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    macd_crossover: str | None = None
    stoch_k: float | None = None
    stoch_d: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    ema_12: float | None = None
    adx: float | None = None
    volume_ratio: float | None = None
    support_level: float | None = None
    resistance_level: float | None = None
    obv_trend: str | None = None


class AIAnalysisResponse(BaseModel):
    """AI analiz yanıtı."""
    symbol: str
    action: AISignalAction
    confidence: AIConfidence
    summary: str = Field(..., description="AI tarafından üretilmiş Türkçe analiz özeti")
    reasoning: str = Field(..., description="Detaylı gerekçe (Türkçe)")
    key_factors: list[str] = Field(default_factory=list, description="Anahtar karar faktörleri")
    target_price: float | None = Field(default=None, description="Tahmini hedef fiyat")
    stop_loss: float | None = Field(default=None, description="Önerilen zarar durdur seviyesi")
    risk_level: str = Field(default="medium", description="Risk seviyesi: low/medium/high")
    indicators: AIIndicatorSummary | None = None
    model_used: str = Field(default="", description="Kullanılan LLM modeli")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# ── Sohbet (Chat) Şemaları ──


class AIChatMessage(BaseModel):
    """Tek bir sohbet mesajı."""
    role: ChatRole
    content: str


class AIChatRequest(BaseModel):
    """AI sohbet isteği."""
    messages: list[AIChatMessage] = Field(
        ..., min_length=1, description="Sohbet geçmişi"
    )
    symbol: str | None = Field(
        default=None, description="Bağlam sembolü (opsiyonel)"
    )


class AIChatResponse(BaseModel):
    """AI sohbet yanıtı."""
    reply: str
    model_used: str = ""
    usage: dict = Field(default_factory=dict)


# ── Sinyal Şemaları ──


class AISignalResponse(BaseModel):
    """Tek bir AI sinyal."""
    symbol: str
    action: AISignalAction
    confidence: AIConfidence
    reason: str
    score: float = Field(ge=0.0, le=1.0, description="Sinyal skoru 0-1")


class AISignalListResponse(BaseModel):
    """AI sinyal listesi."""
    signals: list[AISignalResponse] = []
    model_used: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Model Listesi ──


class AIModelInfo(BaseModel):
    """OpenRouter model bilgisi."""
    id: str
    name: str
    context_length: int | None = None
    pricing: dict = Field(default_factory=dict)


class AIModelListResponse(BaseModel):
    """Kullanılabilir model listesi."""
    models: list[AIModelInfo] = []


# ── Ayarlar ──


class AISettingsRequest(BaseModel):
    """AI ayarları güncelleme."""
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=100, le=16384)


class AISettingsResponse(BaseModel):
    """Mevcut AI ayarları."""
    model: str
    temperature: float
    max_tokens: int
    base_url: str
    api_key_set: bool = Field(description="API key ayarlanmış mı?")
