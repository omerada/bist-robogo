# Source: Doc 10 §Faz 3 Sprint 3.1 + 3.3 — AI Pydantic şemaları
"""AI analiz, sohbet, deney ve performans şemaları."""

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


class AIExperimentStatus(str, Enum):
    """A/B test deney durumları."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


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


# ── A/B Test Deney Şemaları ──


class AIExperimentCreate(BaseModel):
    """Yeni A/B test deneyi oluşturma."""
    name: str = Field(..., min_length=1, max_length=255, description="Deney adı")
    description: str | None = Field(default=None, description="Açıklama")
    model_a: str = Field(..., description="A modeli, ör: google/gemini-2.5-flash")
    model_b: str = Field(..., description="B modeli, ör: openai/gpt-4o")
    symbols: list[str] = Field(..., min_length=1, description="Test edilecek semboller")
    config: dict = Field(default_factory=dict, description="Ekstra yapılandırma")


class AIExperimentResultResponse(BaseModel):
    """Tek bir deney sonucu."""
    id: str
    experiment_id: str
    symbol: str
    model_id: str
    action: AISignalAction
    confidence: AIConfidence
    score: float
    reasoning: str | None = None
    latency_ms: int = 0
    token_usage: dict = Field(default_factory=dict)
    created_at: datetime


class AIExperimentResponse(BaseModel):
    """Deney detayları."""
    id: str
    user_id: str
    name: str
    description: str | None = None
    model_a: str
    model_b: str
    symbols: list[str] = Field(default_factory=list)
    status: AIExperimentStatus = AIExperimentStatus.PENDING
    config: dict = Field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    results: list[AIExperimentResultResponse] = Field(default_factory=list)


class AIExperimentListResponse(BaseModel):
    """Deney listesi."""
    experiments: list[AIExperimentResponse] = []
    total: int = 0


# ── Performans ve Karşılaştırma Şemaları ──


class AIAccuracyMetric(BaseModel):
    """Model doğruluk metriği."""
    total_analyses: int = 0
    correct_predictions: int = 0
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    buy_accuracy: float = Field(default=0.0, ge=0.0, le=1.0)
    sell_accuracy: float = Field(default=0.0, ge=0.0, le=1.0)
    hold_accuracy: float = Field(default=0.0, ge=0.0, le=1.0)


class AIModelPerformance(BaseModel):
    """Tek bir modelin performans özeti."""
    model_id: str
    total_analyses: int = 0
    avg_latency_ms: float = 0.0
    avg_score: float = 0.0
    avg_confidence_distribution: dict = Field(default_factory=dict)
    total_tokens_used: int = 0
    accuracy: AIAccuracyMetric = Field(default_factory=AIAccuracyMetric)
    period_start: datetime | None = None
    period_end: datetime | None = None


class AIModelComparison(BaseModel):
    """İki modelin karşılaştırma sonucu."""
    model_a: AIModelPerformance
    model_b: AIModelPerformance
    winner: str | None = Field(default=None, description="Daha iyi performans gösteren model")
    comparison_notes: list[str] = Field(default_factory=list)


class AIModelComparisonResponse(BaseModel):
    """Karşılaştırma API yanıtı."""
    comparison: AIModelComparison
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AIAnalysisLogResponse(BaseModel):
    """Tek bir analiz log kaydı."""
    id: str
    symbol: str
    model_id: str
    action: AISignalAction
    confidence: AIConfidence
    score: float
    actual_price_change: float | None = None
    is_correct: bool | None = None
    latency_ms: int = 0
    token_usage: dict = Field(default_factory=dict)
    created_at: datetime


class AIPerformanceRequest(BaseModel):
    """Performans sorgulama parametreleri."""
    model_id: str | None = Field(default=None, description="Filtre: model ID")
    symbol: str | None = Field(default=None, description="Filtre: sembol")
    days: int = Field(default=30, ge=1, le=365, description="Kaç günlük veri")


class AIPerformanceSummary(BaseModel):
    """Genel AI performans özeti."""
    models: list[AIModelPerformance] = []
    total_analyses: int = 0
    overall_accuracy: float = 0.0
    period_days: int = 30
    generated_at: datetime = Field(default_factory=datetime.utcnow)
