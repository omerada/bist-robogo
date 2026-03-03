# bist-robogo — Veri Modelleri ve API Sözleşmeleri

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03

---

## 1. Veritabanı Şemaları (Entity Relationship)

### 1.1 ER Diyagramı — Genel Görünüm

```
┌──────────┐     ┌───────────────┐     ┌───────────────┐
│  users   │────▶│  portfolios   │────▶│  positions    │
│          │     │               │     │               │
└──────┬───┘     └───────────────┘     └───────┬───────┘
       │                                        │
       │         ┌───────────────┐     ┌───────▼───────┐
       ├────────▶│  strategies   │────▶│   signals     │
       │         │               │     │               │
       │         └───────┬───────┘     └───────────────┘
       │                 │
       │         ┌───────▼───────┐     ┌───────────────┐
       │         │  backtest_    │────▶│  backtest_    │
       │         │  runs         │     │  trades       │
       │         └───────────────┘     └───────────────┘
       │
       │         ┌───────────────┐     ┌───────────────┐
       ├────────▶│   orders      │────▶│  trades       │
       │         │               │     │               │
       │         └───────────────┘     └───────────────┘
       │
       │         ┌───────────────┐     ┌───────────────┐
       ├────────▶│  risk_rules   │     │ notifications │
       │         └───────────────┘     └───────────────┘
       │
       │         ┌───────────────┐
       └────────▶│  audit_logs   │
                 └───────────────┘
```

---

## 2. Tablo Tanımları

### 2.1 users

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'viewer',  -- admin, trader, viewer, api_user
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret  VARCHAR(255),
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### 2.2 api_keys

```sql
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    key_hash        VARCHAR(255) NOT NULL,      -- bcrypt hash
    key_prefix      VARCHAR(10) NOT NULL,       -- ilk 8 karakter (gösterim için)
    permissions     JSONB DEFAULT '[]',          -- ["read", "trade", "admin"]
    is_active       BOOLEAN DEFAULT TRUE,
    expires_at      TIMESTAMPTZ,
    last_used_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
```

### 2.3 broker_connections

```sql
CREATE TABLE broker_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    broker_name     VARCHAR(100) NOT NULL,       -- 'is_yatirim', 'gedik', 'matriks'
    encrypted_credentials BYTEA NOT NULL,         -- AES-256 encrypted
    is_active       BOOLEAN DEFAULT TRUE,
    is_paper_trading BOOLEAN DEFAULT FALSE,
    last_connected_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_broker_conn_user ON broker_connections(user_id);
```

### 2.4 symbols

```sql
CREATE TABLE symbols (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker          VARCHAR(20) UNIQUE NOT NULL,  -- 'THYAO', 'GARAN', 'ASELS'
    name            VARCHAR(255) NOT NULL,
    sector          VARCHAR(255),
    industry        VARCHAR(255),
    market_cap      BIGINT,
    free_float_rate DECIMAL(5, 2),
    lot_size        INTEGER DEFAULT 1,
    is_active       BOOLEAN DEFAULT TRUE,
    meta            JSONB DEFAULT '{}',
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_symbols_ticker ON symbols(ticker);
CREATE INDEX idx_symbols_sector ON symbols(sector);
```

### 2.5 indices

```sql
CREATE TABLE indices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(20) UNIQUE NOT NULL,  -- 'XU030', 'XU100', 'XKTUM'
    name            VARCHAR(255) NOT NULL,         -- 'BIST 30', 'BIST 100', 'Katılım Endeksi'
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE index_components (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_id        UUID NOT NULL REFERENCES indices(id) ON DELETE CASCADE,
    symbol_id       UUID NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    weight          DECIMAL(10, 6),
    added_at        DATE NOT NULL,
    removed_at      DATE,
    UNIQUE(index_id, symbol_id, added_at)
);

CREATE INDEX idx_index_comp ON index_components(index_id, symbol_id);
```

### 2.6 strategies

```sql
CREATE TABLE strategies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    strategy_type   VARCHAR(50) NOT NULL,         -- 'ma_crossover', 'rsi_reversal', 'ai_trend', 'custom'
    parameters      JSONB NOT NULL DEFAULT '{}',
    symbols         JSONB DEFAULT '[]',           -- hedef semboller
    index_filter    VARCHAR(20),                  -- endeks filtresi ('XU030', 'XKTUM' vb.)
    timeframe       VARCHAR(10) DEFAULT '1d',     -- '1m', '5m', '1h', '1d'
    is_active       BOOLEAN DEFAULT FALSE,
    is_paper        BOOLEAN DEFAULT TRUE,         -- paper trading modu
    risk_params     JSONB DEFAULT '{}',           -- strateji bazlı risk parametreleri
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_strategies_user ON strategies(user_id);
CREATE INDEX idx_strategies_active ON strategies(is_active) WHERE is_active = TRUE;
```

### 2.7 signals

```sql
CREATE TABLE signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id     UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    symbol          VARCHAR(20) NOT NULL,
    signal_type     VARCHAR(10) NOT NULL,         -- 'buy', 'sell', 'hold'
    confidence      DECIMAL(5, 4) NOT NULL,       -- 0.0000 - 1.0000
    price           DECIMAL(15, 4) NOT NULL,
    stop_loss       DECIMAL(15, 4),
    take_profit     DECIMAL(15, 4),
    indicators      JSONB DEFAULT '{}',           -- sinyal üretiminde kullanılan göstergeler
    metadata        JSONB DEFAULT '{}',
    is_executed     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_strategy ON signals(strategy_id, created_at DESC);
CREATE INDEX idx_signals_symbol ON signals(symbol, created_at DESC);
```

### 2.8 orders

```sql
CREATE TABLE orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    strategy_id     UUID REFERENCES strategies(id),
    signal_id       UUID REFERENCES signals(id),
    broker_conn_id  UUID REFERENCES broker_connections(id),
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(10) NOT NULL,          -- 'buy', 'sell'
    order_type      VARCHAR(20) NOT NULL,          -- 'market', 'limit', 'stop_loss', 'take_profit', 'trailing_stop'
    quantity        INTEGER NOT NULL,
    price           DECIMAL(15, 4),                -- limit fiyatı
    stop_price      DECIMAL(15, 4),                -- stop fiyatı
    time_in_force   VARCHAR(10) DEFAULT 'day',     -- 'day', 'gtc', 'ioc', 'fok'
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- status: pending, submitted, partial_fill, filled, cancelled, rejected, expired
    filled_quantity INTEGER DEFAULT 0,
    filled_price    DECIMAL(15, 4),
    commission      DECIMAL(15, 4) DEFAULT 0,
    broker_order_id VARCHAR(255),                   -- broker tarafındaki emir ID
    rejection_reason TEXT,
    is_paper        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_symbol ON orders(symbol, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status) WHERE status IN ('pending', 'submitted', 'partial_fill');
CREATE INDEX idx_orders_strategy ON orders(strategy_id);
```

### 2.9 trades

```sql
CREATE TABLE trades (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    order_id        UUID NOT NULL REFERENCES orders(id),
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(10) NOT NULL,
    quantity        INTEGER NOT NULL,
    price           DECIMAL(15, 4) NOT NULL,
    commission      DECIMAL(15, 4) DEFAULT 0,
    pnl             DECIMAL(15, 4),                -- kapatma işleminde hesaplanan PnL
    executed_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trades_user ON trades(user_id, executed_at DESC);
CREATE INDEX idx_trades_symbol ON trades(symbol, executed_at DESC);
CREATE INDEX idx_trades_order ON trades(order_id);
```

### 2.10 positions

```sql
CREATE TABLE positions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(10) NOT NULL,          -- 'long', 'short'
    quantity        INTEGER NOT NULL,
    avg_entry_price DECIMAL(15, 4) NOT NULL,
    current_price   DECIMAL(15, 4),
    unrealized_pnl  DECIMAL(15, 4),
    realized_pnl    DECIMAL(15, 4) DEFAULT 0,
    stop_loss       DECIMAL(15, 4),
    take_profit     DECIMAL(15, 4),
    strategy_id     UUID REFERENCES strategies(id),
    opened_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    UNIQUE(user_id, symbol) -- Bir kullanıcı aynı sembolde tek açık pozisyon
);

CREATE INDEX idx_positions_user ON positions(user_id) WHERE closed_at IS NULL;
CREATE INDEX idx_positions_symbol ON positions(symbol) WHERE closed_at IS NULL;
```

### 2.11 portfolios

```sql
CREATE TABLE portfolios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE NOT NULL REFERENCES users(id),
    total_value     DECIMAL(15, 4) NOT NULL DEFAULT 0,
    cash_balance    DECIMAL(15, 4) NOT NULL DEFAULT 0,
    invested_value  DECIMAL(15, 4) NOT NULL DEFAULT 0,
    daily_pnl       DECIMAL(15, 4) DEFAULT 0,
    total_pnl       DECIMAL(15, 4) DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE portfolio_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    snapshot_date   DATE NOT NULL,
    total_value     DECIMAL(15, 4) NOT NULL,
    cash_balance    DECIMAL(15, 4) NOT NULL,
    invested_value  DECIMAL(15, 4) NOT NULL,
    daily_pnl       DECIMAL(15, 4),
    positions_count INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, snapshot_date)
);

CREATE INDEX idx_portfolio_snap ON portfolio_snapshots(user_id, snapshot_date DESC);
```

### 2.12 risk_rules

```sql
CREATE TABLE risk_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    rule_type       VARCHAR(50) NOT NULL,
    -- max_daily_loss, max_position_size, max_open_positions,
    -- max_order_size, stop_loss_required, max_daily_orders, volatility_filter
    value           JSONB NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE risk_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    event_type      VARCHAR(50) NOT NULL,         -- 'limit_warning', 'limit_breach', 'order_rejected'
    rule_id         UUID REFERENCES risk_rules(id),
    details         JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risk_events_user ON risk_events(user_id, created_at DESC);
```

### 2.13 backtest_runs

```sql
CREATE TABLE backtest_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    strategy_id     UUID NOT NULL REFERENCES strategies(id),
    name            VARCHAR(255),
    parameters      JSONB NOT NULL,
    symbols         JSONB NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    initial_capital DECIMAL(15, 4) NOT NULL,
    commission_rate DECIMAL(8, 6) DEFAULT 0.001,  -- %0.1
    slippage_rate   DECIMAL(8, 6) DEFAULT 0.0005, -- %0.05
    status          VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    -- Sonuçlar
    total_return    DECIMAL(10, 4),
    cagr            DECIMAL(10, 4),
    sharpe_ratio    DECIMAL(10, 4),
    sortino_ratio   DECIMAL(10, 4),
    max_drawdown    DECIMAL(10, 4),
    win_rate        DECIMAL(10, 4),
    profit_factor   DECIMAL(10, 4),
    total_trades    INTEGER,
    avg_trade_pnl   DECIMAL(15, 4),
    avg_holding_days DECIMAL(10, 2),
    equity_curve    JSONB,                         -- [{date, value}, ...]
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE backtest_trades (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id     UUID NOT NULL REFERENCES backtest_runs(id) ON DELETE CASCADE,
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(10) NOT NULL,
    entry_date      DATE NOT NULL,
    entry_price     DECIMAL(15, 4) NOT NULL,
    exit_date       DATE,
    exit_price      DECIMAL(15, 4),
    quantity        INTEGER NOT NULL,
    pnl             DECIMAL(15, 4),
    pnl_pct         DECIMAL(10, 4),
    holding_days    INTEGER,
    signal_metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_bt_trades ON backtest_trades(backtest_id);
```

### 2.14 notifications

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    type            VARCHAR(50) NOT NULL,          -- 'order_filled', 'signal', 'risk_alert', 'system'
    title           VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    channel         VARCHAR(20) NOT NULL,          -- 'in_app', 'email', 'push', 'sms', 'telegram'
    is_read         BOOLEAN DEFAULT FALSE,
    metadata        JSONB DEFAULT '{}',
    sent_at         TIMESTAMPTZ DEFAULT NOW(),
    read_at         TIMESTAMPTZ
);

CREATE INDEX idx_notif_user ON notifications(user_id, sent_at DESC);
CREATE INDEX idx_notif_unread ON notifications(user_id) WHERE is_read = FALSE;
```

### 2.15 audit_logs

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,         -- 'login', 'order_create', 'strategy_update', etc.
    resource_type   VARCHAR(50),
    resource_id     UUID,
    details         JSONB DEFAULT '{}',
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_logs(action, created_at DESC);
```

### 2.16 TimescaleDB — Zaman Serisi Tabloları

```sql
-- 1 dakikalık OHLCV mum verisi
CREATE TABLE ohlcv_1m (
    time            TIMESTAMPTZ NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    open            DECIMAL(15, 4) NOT NULL,
    high            DECIMAL(15, 4) NOT NULL,
    low             DECIMAL(15, 4) NOT NULL,
    close           DECIMAL(15, 4) NOT NULL,
    volume          BIGINT NOT NULL,
    vwap            DECIMAL(15, 4),
    trade_count     INTEGER
);

SELECT create_hypertable('ohlcv_1m', 'time');
CREATE INDEX idx_ohlcv_1m_symbol ON ohlcv_1m(symbol, time DESC);

-- Günlük OHLCV (Continuous Aggregate)
CREATE MATERIALIZED VIEW ohlcv_1d
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS time,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume,
    sum(volume * vwap) / NULLIF(sum(volume), 0) AS vwap
FROM ohlcv_1m
GROUP BY time_bucket('1 day', time), symbol;

-- Haftalık OHLCV (Continuous Aggregate)
CREATE MATERIALIZED VIEW ohlcv_1w
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 week', time) AS time,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume
FROM ohlcv_1m
GROUP BY time_bucket('1 week', time), symbol;

-- Tick verisi
CREATE TABLE ticks (
    time            TIMESTAMPTZ NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    price           DECIMAL(15, 4) NOT NULL,
    volume          INTEGER NOT NULL,
    side            VARCHAR(5),                    -- 'buy', 'sell'
    bid             DECIMAL(15, 4),
    ask             DECIMAL(15, 4)
);

SELECT create_hypertable('ticks', 'time');
CREATE INDEX idx_ticks_symbol ON ticks(symbol, time DESC);

-- Compression policy (7 gün sonra compress)
ALTER TABLE ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol'
);
SELECT add_compression_policy('ticks', INTERVAL '7 days');

-- Retention policy (tick: 1 yıl, 1m: 3 yıl)
SELECT add_retention_policy('ticks', INTERVAL '1 year');
SELECT add_retention_policy('ohlcv_1m', INTERVAL '3 years');
```

---

## 3. API Sözleşmeleri (OpenAPI Özet)

### 3.1 Ortak Yanıt Formatı

```json
// Başarılı yanıt
{
    "success": true,
    "data": { ... },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 150,
        "total_pages": 8
    }
}

// Hata yanıtı
{
    "success": false,
    "error": {
        "code": "RISK_LIMIT_EXCEEDED",
        "message": "Günlük zarar limiti aşıldı",
        "details": {
            "current_loss": -5200.50,
            "limit": -5000.00
        }
    }
}
```

### 3.2 Hata Kodları

| HTTP Status | Kod                  | Açıklama                                      |
| ----------- | -------------------- | --------------------------------------------- |
| 400         | VALIDATION_ERROR     | İstek doğrulama hatası                        |
| 401         | UNAUTHORIZED         | Kimlik doğrulama gerekli                      |
| 403         | FORBIDDEN            | Yetkisiz erişim                               |
| 404         | NOT_FOUND            | Kaynak bulunamadı                             |
| 409         | CONFLICT             | Çakışma (ör. aynı sembolde açık pozisyon var) |
| 422         | RISK_LIMIT_EXCEEDED  | Risk limiti aşıldı                            |
| 422         | INSUFFICIENT_BALANCE | Yetersiz bakiye                               |
| 422         | MARKET_CLOSED        | Piyasa kapalı                                 |
| 429         | RATE_LIMITED         | İstek limiti aşıldı                           |
| 500         | INTERNAL_ERROR       | Sunucu hatası                                 |
| 502         | BROKER_ERROR         | Broker bağlantı hatası                        |
| 503         | SERVICE_UNAVAILABLE  | Servis geçici olarak kullanılamıyor           |

### 3.3 Piyasa Verisi API

#### GET /api/v1/market/symbols/{symbol}/quote

```json
// Response
{
  "success": true,
  "data": {
    "symbol": "THYAO",
    "name": "Türk Hava Yolları",
    "price": 312.5,
    "change": 4.8,
    "change_pct": 1.56,
    "open": 307.7,
    "high": 314.0,
    "low": 306.5,
    "close_prev": 307.7,
    "volume": 45_230_000,
    "turnover": 14_120_000_000,
    "bid": 312.4,
    "ask": 312.6,
    "bid_size": 1500,
    "ask_size": 2300,
    "market_cap": 431_250_000_000,
    "pe_ratio": 8.45,
    "updated_at": "2026-03-03T15:30:00+03:00"
  }
}
```

#### GET /api/v1/market/symbols/{symbol}/history

```
Query params:
  interval: 1m | 5m | 15m | 1h | 1d | 1w | 1M
  start:    2025-01-01
  end:      2026-03-03
  limit:    500
```

```json
// Response
{
  "success": true,
  "data": [
    {
      "time": "2026-03-03T00:00:00+03:00",
      "open": 307.7,
      "high": 314.0,
      "low": 306.5,
      "close": 312.5,
      "volume": 45230000
    }
  ],
  "meta": {
    "symbol": "THYAO",
    "interval": "1d",
    "count": 250
  }
}
```

### 3.4 Emir API

#### POST /api/v1/orders

```json
// Request
{
    "symbol": "THYAO",
    "side": "buy",
    "order_type": "limit",
    "quantity": 100,
    "price": 310.00,
    "stop_loss": 300.00,
    "take_profit": 330.00,
    "time_in_force": "day",
    "strategy_id": "uuid-optional"
}

// Response (201 Created)
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "symbol": "THYAO",
        "side": "buy",
        "order_type": "limit",
        "quantity": 100,
        "price": 310.00,
        "stop_loss": 300.00,
        "take_profit": 330.00,
        "status": "submitted",
        "created_at": "2026-03-03T10:15:00+03:00"
    }
}
```

### 3.5 Portföy API

#### GET /api/v1/portfolio/summary

```json
// Response
{
  "success": true,
  "data": {
    "total_value": 1_250_000.0,
    "cash_balance": 450_000.0,
    "invested_value": 800_000.0,
    "daily_pnl": 12_500.0,
    "daily_pnl_pct": 1.01,
    "total_pnl": 250_000.0,
    "total_pnl_pct": 25.0,
    "open_positions": 8,
    "winning_positions": 5,
    "losing_positions": 3,
    "updated_at": "2026-03-03T15:30:00+03:00"
  }
}
```

### 3.6 Trend Analiz API

#### GET /api/v1/analysis/trends

```
Query params:
  period:    daily | weekly | monthly
  index:     XU030 | XU100 | XKTUM | ALL
  type:      dip | breakout | all
  min_score: 0.6
  limit:     50
```

```json
// Response
{
  "success": true,
  "data": {
    "period": "daily",
    "index": "XU030",
    "analysis_date": "2026-03-03",
    "dip_candidates": [
      {
        "symbol": "GARAN",
        "name": "Garanti BBVA",
        "price": 125.4,
        "dip_score": 0.85,
        "support_level": 122.0,
        "resistance_level": 132.0,
        "rsi": 28.5,
        "macd_signal": "bullish_crossover",
        "volume_ratio": 1.45,
        "trend_status": "approaching_support",
        "indicators": {
          "sma_20": 128.5,
          "sma_50": 130.2,
          "bollinger_lower": 123.1,
          "adx": 32.5,
          "stochastic_k": 15.2
        }
      }
    ],
    "breakout_candidates": [
      {
        "symbol": "ASELS",
        "name": "Aselsan",
        "price": 78.9,
        "breakout_score": 0.78,
        "breakout_level": 77.5,
        "target_price": 85.0,
        "volume_surge": 2.1,
        "trend_status": "new_uptrend",
        "indicators": {
          "sma_20": 75.3,
          "sma_50": 72.8,
          "adx": 28.7,
          "macd_histogram": 0.45,
          "obv_trend": "rising"
        }
      }
    ]
  },
  "meta": {
    "total_dip_candidates": 5,
    "total_breakout_candidates": 8,
    "analysis_timestamp": "2026-03-03T18:30:00+03:00"
  }
}
```

### 3.7 Risk API

#### GET /api/v1/risk/status

```json
// Response
{
  "success": true,
  "data": {
    "daily_pnl": -2_100.0,
    "daily_pnl_limit": -5_000.0,
    "daily_pnl_usage_pct": 42.0,
    "open_positions": 6,
    "max_open_positions": 10,
    "largest_position": {
      "symbol": "THYAO",
      "value": 156_250.0,
      "portfolio_pct": 12.5
    },
    "total_exposure": 800_000.0,
    "cash_available": 450_000.0,
    "daily_orders_count": 12,
    "daily_orders_limit": 50,
    "risk_score": 0.35,
    "risk_level": "moderate",
    "alerts": [
      {
        "type": "position_concentration",
        "message": "THYAO pozisyonu portföyün %12.5'ini oluşturuyor (limit: %10)",
        "severity": "warning"
      }
    ]
  }
}
```

### 3.8 WebSocket API

#### WS /ws/v1/market/stream

```json
// Client → Server (Subscribe)
{
    "action": "subscribe",
    "channels": ["quote:THYAO", "quote:GARAN", "orderbook:THYAO"]
}

// Server → Client (Quote Update)
{
    "channel": "quote:THYAO",
    "data": {
        "symbol": "THYAO",
        "price": 312.60,
        "change": 4.90,
        "change_pct": 1.59,
        "volume": 45_350_000,
        "bid": 312.50,
        "ask": 312.70,
        "timestamp": "2026-03-03T15:30:05+03:00"
    }
}

// Server → Client (Order Book Update)
{
    "channel": "orderbook:THYAO",
    "data": {
        "symbol": "THYAO",
        "bids": [
            [312.50, 1500],
            [312.40, 2200],
            [312.30, 3100]
        ],
        "asks": [
            [312.70, 1800],
            [312.80, 2500],
            [312.90, 1900]
        ],
        "timestamp": "2026-03-03T15:30:05+03:00"
    }
}

// Server → Client (Signal Notification)
{
    "channel": "signal",
    "data": {
        "strategy_id": "uuid",
        "symbol": "GARAN",
        "signal_type": "buy",
        "confidence": 0.82,
        "price": 125.40,
        "timestamp": "2026-03-03T14:00:00+03:00"
    }
}
```

---

## 4. Pydantic Modelleri (Backend)

### 4.1 Temel Modeller

```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum

# --- Enums ---

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

class OrderStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class TimeInForce(str, Enum):
    DAY = "day"
    GTC = "gtc"       # Good Till Cancel
    IOC = "ioc"       # Immediate or Cancel
    FOK = "fok"       # Fill or Kill

class TrendPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

# --- Request Models ---

class OrderCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, examples=["THYAO"])
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(..., gt=0)
    price: Decimal | None = Field(None, gt=0)
    stop_loss: Decimal | None = Field(None, gt=0)
    take_profit: Decimal | None = Field(None, gt=0)
    time_in_force: TimeInForce = TimeInForce.DAY
    strategy_id: UUID | None = None

class StrategyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    strategy_type: str
    parameters: dict = Field(default_factory=dict)
    symbols: list[str] = Field(default_factory=list)
    index_filter: str | None = None
    timeframe: str = "1d"
    risk_params: dict = Field(default_factory=dict)

class BacktestRequest(BaseModel):
    strategy_id: UUID
    parameters: dict = Field(default_factory=dict)
    symbols: list[str]
    start_date: date
    end_date: date
    initial_capital: Decimal = Field(default=Decimal("1000000"))
    commission_rate: Decimal = Field(default=Decimal("0.001"))
    slippage_rate: Decimal = Field(default=Decimal("0.0005"))

class TrendAnalysisRequest(BaseModel):
    period: TrendPeriod = TrendPeriod.DAILY
    index: str = "ALL"
    type: str = "all"              # 'dip', 'breakout', 'all'
    min_score: float = Field(default=0.6, ge=0, le=1)
    limit: int = Field(default=50, ge=1, le=200)

# --- Response Models ---

class QuoteResponse(BaseModel):
    symbol: str
    name: str
    price: Decimal
    change: Decimal
    change_pct: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    close_prev: Decimal
    volume: int
    bid: Decimal
    ask: Decimal
    updated_at: datetime

class OrderResponse(BaseModel):
    id: UUID
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Decimal | None
    stop_loss: Decimal | None
    take_profit: Decimal | None
    status: OrderStatus
    filled_quantity: int
    filled_price: Decimal | None
    commission: Decimal
    created_at: datetime
    updated_at: datetime

class PositionResponse(BaseModel):
    id: UUID
    symbol: str
    side: str
    quantity: int
    avg_entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: Decimal
    realized_pnl: Decimal
    stop_loss: Decimal | None
    take_profit: Decimal | None
    opened_at: datetime

class PortfolioSummaryResponse(BaseModel):
    total_value: Decimal
    cash_balance: Decimal
    invested_value: Decimal
    daily_pnl: Decimal
    daily_pnl_pct: Decimal
    total_pnl: Decimal
    total_pnl_pct: Decimal
    open_positions: int

class TrendCandidateResponse(BaseModel):
    symbol: str
    name: str
    price: Decimal
    score: Decimal
    trend_status: str
    rsi: Decimal | None
    volume_ratio: Decimal | None
    indicators: dict
```

---

## 5. Event Flow (Olay Akışı)

### 5.1 Kafka Event Tipleri

```
# Market Events
market.tick.received         → Yeni fiyat verisi alındı
market.ohlcv.updated         → OHLCV verisi güncellendi
market.index.updated         → Endeks değeri güncellendi

# Strategy Events
strategy.activated           → Strateji aktifleştirildi
strategy.deactivated         → Strateji deaktifleştirildi
strategy.signal.generated    → Yeni sinyal üretildi

# Order Events
order.created                → Emir oluşturuldu
order.submitted              → Emir broker'a gönderildi
order.filled                 → Emir gerçekleşti
order.partial_fill           → Kısmi gerçekleşme
order.cancelled              → Emir iptal edildi
order.rejected               → Emir reddedildi

# Risk Events
risk.limit.warning           → Risk limiti uyarısı
risk.limit.breach            → Risk limiti aşıldı
risk.order.rejected          → Emir risk kontrolünden reddedildi

# Portfolio Events
portfolio.position.opened    → Yeni pozisyon açıldı
portfolio.position.closed    → Pozisyon kapatıldı
portfolio.snapshot.taken     → Günlük snapshot alındı

# System Events
system.health.check          → Sağlık kontrolü
system.error                 → Sistem hatası
system.broker.connected      → Broker bağlantısı kuruldu
system.broker.disconnected   → Broker bağlantısı koptu
```

### 5.2 Event Schema Örneği

```json
{
  "event_id": "uuid",
  "event_type": "order.filled",
  "timestamp": "2026-03-03T15:30:05+03:00",
  "source": "trading-engine",
  "data": {
    "order_id": "uuid",
    "user_id": "uuid",
    "symbol": "THYAO",
    "side": "buy",
    "quantity": 100,
    "price": 312.5,
    "commission": 31.25
  },
  "metadata": {
    "correlation_id": "uuid",
    "version": "1.0"
  }
}
```

---

## 6. Sonuç

Bu doküman, bist-robogo platformunun tüm veri modellerini, API sözleşmelerini ve event akışlarını detaylı şekilde tanımlamaktadır. Tüm modeller ve API'ler modüler ve genişletilebilir şekilde tasarlanmıştır.

---

_Bu doküman, bist-robogo projesinin Ar-Ge sürecinin bir parçasıdır ve düzenli olarak güncellenecektir._
