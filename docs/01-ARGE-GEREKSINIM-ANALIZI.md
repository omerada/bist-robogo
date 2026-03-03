# bist-robogo — Ar-Ge ve Gereksinim Analizi Dokümanı

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Hazırlayan:** Sistem Mimari & Quant Mühendisliği Ekibi

---

## 1. Yönetici Özeti

**bist-robogo**, Türkiye Borsası (BIST) için geliştirilmiş, yapay zeka destekli, gerçek zamanlı ve otomatik alım-satım yapabilen bir ticaret altyapısıdır. Platform; canlı piyasa verisi takibi, trend ve dip tespiti, risk yönetimi, otomatik emir yürütme, backtest ve performans analizi gibi kritik bileşenleri tek bir modüler çatı altında sunar.

---

## 2. İş Gereksinimleri

### 2.1 Fonksiyonel Gereksinimler

| #     | Gereksinim                 | Öncelik | Açıklama                                                           |
| ----- | -------------------------- | ------- | ------------------------------------------------------------------ |
| FR-01 | Gerçek zamanlı veri takibi | Kritik  | Canlı fiyat, hacim, order book verileri anlık olarak işlenmeli     |
| FR-02 | Otomatik emir sistemi      | Kritik  | Risk kurallarına uygun alım-satım emirleri otomatik yürütülmeli    |
| FR-03 | Trend ve dip tespiti       | Yüksek  | Teknik göstergeler + AI modelleri ile potansiyel dip/zirve analizi |
| FR-04 | Risk yönetimi              | Kritik  | Maks günlük zarar, pozisyon büyüklüğü, volatilite kontrolü         |
| FR-05 | Backtest motoru            | Yüksek  | Geçmiş veriler üzerinde strateji simülasyonu ve optimizasyonu      |
| FR-06 | Profesyonel dashboard      | Yüksek  | Canlı fiyat, pozisyon, PnL, risk durumu ekranı                     |
| FR-07 | Endeks seçimi              | Orta    | Katılım Endeksi, BIST30, BIST100 vb. filtreleme                    |
| FR-08 | Trend analiz ekranı        | Yüksek  | Günlük/haftalık/aylık bazda trend dip ve başlangıç hisseleri       |
| FR-09 | Kullanıcı yönetimi         | Orta    | Kayıt, giriş, rol bazlı yetkilendirme                              |
| FR-10 | Bildirim sistemi           | Orta    | Önemli olaylarda push/email/SMS bildirimi                          |
| FR-11 | Strateji yönetimi          | Yüksek  | Strateji oluşturma, düzenleme, aktif/pasif yapma                   |
| FR-12 | Portföy takibi             | Yüksek  | Açık pozisyonlar, geçmiş işlemler, toplam PnL                      |

### 2.2 Fonksiyonel Olmayan Gereksinimler

| #      | Gereksinim        | Hedef                                              |
| ------ | ----------------- | -------------------------------------------------- |
| NFR-01 | Gecikme (Latency) | Veri alma → emir gönderme < 200 ms                 |
| NFR-02 | Uptime            | %99.5+                                             |
| NFR-03 | Ölçeklenebilirlik | 100+ eşzamanlı strateji çalıştırabilme             |
| NFR-04 | Güvenlik          | End-to-end şifreleme, API key rotasyonu, audit log |
| NFR-05 | Veri saklama      | Minimum 10 yıllık geçmiş veri                      |
| NFR-06 | Yedekleme         | Günlük otomatik yedekleme + point-in-time recovery |
| NFR-07 | Monitoring        | Tüm servislerde health check, metrik ve alarm      |
| NFR-08 | Test kapsamı      | Birim test > %80, entegrasyon testi > %60          |

---

## 3. Teknoloji Araştırması ve Seçimi

### 3.1 Backend Teknolojileri

#### 3.1.1 Ana Uygulama Çatısı — **Python (FastAPI + Celery)**

| Teknoloji          | Seçim Gerekçesi                                                                        |
| ------------------ | -------------------------------------------------------------------------------------- |
| **Python 3.12+**   | Finans/quant ekosistemi, AI/ML kütüphaneleri, topluluk desteği                         |
| **FastAPI**        | Async native, yüksek performans, otomatik OpenAPI/Swagger, tip güvenliği (Pydantic v2) |
| **Celery + Redis** | Asenkron görev kuyruğu (emir yürütme, backtest, veri çekme)                            |
| **uvicorn**        | ASGI sunucu, yüksek eşzamanlılık                                                       |

**Alternatif değerlendirme:**

- _Django REST Framework:_ Daha ağır, trading sistemleri için gereksiz overhead.
- _Node.js (NestJS):_ Quant/ML ekosistemi Python kadar güçlü değil.
- _Go:_ Performans avantajı var ama ML/quant kütüphane ekosistemi zayıf.
- _Rust:_ Düşük gecikme kritik modüller (matching engine, order router) için ileride değerlendirilebilir.

#### 3.1.2 Gerçek Zamanlı Veri İşleme

| Teknoloji                      | Kullanım Alanı                                                |
| ------------------------------ | ------------------------------------------------------------- |
| **WebSocket (FastAPI native)** | Frontend'e canlı fiyat/order book akışı                       |
| **Apache Kafka / Redpanda**    | Yüksek throughput event streaming, servisler arası mesajlaşma |
| **Redis Streams**              | Hafif event queue, cache invalidation                         |

**Neden Kafka/Redpanda?**

- BIST'ten gelen tick verileri saniyede binlerce mesaj olabilir.
- Kafka, replay ve partitioning ile veri kaybını önler.
- Redpanda, Kafka uyumlu ancak C++ tabanlı olduğu için daha düşük gecikme sunar.

#### 3.1.3 AI / ML Katmanı

| Teknoloji              | Kullanım Alanı                                        |
| ---------------------- | ----------------------------------------------------- |
| **scikit-learn**       | Klasik ML (Random Forest, Gradient Boosting)          |
| **XGBoost / LightGBM** | Trend tahmini, sınıflandırma                          |
| **PyTorch**            | Derin öğrenme (LSTM, Transformer tabanlı tahmin)      |
| **TA-Lib / pandas-ta** | Teknik analiz göstergeleri (RSI, MACD, Bollinger vb.) |
| **Optuna**             | Hyper-parametre optimizasyonu                         |
| **MLflow**             | Model versiyonlama, experiment tracking               |
| **ONNX Runtime**       | Model inference optimizasyonu (production)            |

#### 3.1.4 Broker Entegrasyonu

| Kaynak                       | Yöntem           | Açıklama                                      |
| ---------------------------- | ---------------- | --------------------------------------------- |
| **Matriks Data**             | API / FIX        | Türkiye'deki en yaygın veri sağlayıcı         |
| **İş Yatırım API**           | REST + WebSocket | Emir gönderme ve portföy yönetimi             |
| **Gedik Yatırım API**        | REST             | Alternatif broker                             |
| **CollectAPI / BIST API**    | REST             | Piyasa verisi (gecikmeli/gerçek zamanlı)      |
| **Yahoo Finance / yfinance** | REST             | Backtest verisi ve alternatif veri kaynağı    |
| **TCMB EVDS**                | REST             | Makro ekonomik veriler (faiz, enflasyon, kur) |

> **Not:** FIX protokolü (Financial Information eXchange) profesyonel trading sistemlerinde standart olup, düşük gecikmeli emir iletimi sağlar. İleriye dönük olarak FIX 4.4 / 5.0 desteği eklenmelidir.

### 3.2 Frontend Teknolojileri

| Teknoloji                          | Seçim Gerekçesi                                       |
| ---------------------------------- | ----------------------------------------------------- |
| **Next.js 15 (App Router)**        | SSR/SSG, React Server Components, optimize performans |
| **React 19**                       | Concurrent rendering, Suspense, Server Components     |
| **TypeScript 5.x**                 | Tip güvenliği, refactoring kolaylığı                  |
| **TailwindCSS 4**                  | Utility-first CSS, hızlı UI geliştirme                |
| **shadcn/ui**                      | Yüksek kaliteli, erişilebilir component library       |
| **TradingView Lightweight Charts** | Profesyonel finansal grafikler (açık kaynak)          |
| **Recharts / Tremor**              | Dashboard grafikleri ve metrikler                     |
| **TanStack Query v5**              | Sunucu state yönetimi, cache, real-time sync          |
| **Zustand**                        | Hafif client-side state yönetimi                      |
| **Socket.io-client**               | WebSocket bağlantısı                                  |

**Alternatif değerlendirme:**

- _Angular:_ Enterprise uygun ama learning curve yüksek, finans UI ekosistemi React kadar zengin değil.
- _Vue.js (Nuxt):_ İyi alternatif ama TradingView entegrasyonları ve finans UI kütüphaneleri React ekosisteminde daha olgun.
- _Svelte (SvelteKit):_ Performans avantajı var ancak ekosistem henüz yeterince olgunlaşmadı.

### 3.3 Veritabanı ve Depolama

| Teknoloji         | Kullanım Alanı                                      | Gerekçe                                       |
| ----------------- | --------------------------------------------------- | --------------------------------------------- |
| **PostgreSQL 16** | Ana veritabanı (kullanıcılar, emirler, pozisyonlar) | ACID, JSON desteği, olgunluk                  |
| **TimescaleDB**   | Zaman serisi verileri (fiyat, hacim, tick)          | PostgreSQL uyumlu, hypertable, sürekli agrega |
| **Redis 7+**      | Cache, session, rate limiting, pub/sub              | Sub-millisecond gecikme                       |
| **ClickHouse**    | Analitik sorgular, backtest sonuçları               | Kolon bazlı, yüksek okuma performansı         |
| **MinIO / S3**    | Model dosyaları, büyük veri setleri, yedekler       | Object storage                                |

**Neden TimescaleDB?**

- BIST'ten gelen fiyat verileri klasik zaman serisi problemidir.
- TimescaleDB, PostgreSQL üzerinde çalışır (ek altyapı yok).
- Otomatik partitioning, compression ve continuous aggregates ile 10 yıllık veriyi verimli saklar.
- Sorgu performansı: Vanilla PostgreSQL'e göre 10-100x hızlı zaman serisi sorguları.

### 3.4 Altyapı ve DevOps

| Teknoloji                   | Kullanım Alanı                                          |
| --------------------------- | ------------------------------------------------------- |
| **Docker + Docker Compose** | Konteynerizasyon, yerel geliştirme                      |
| **Kubernetes (K8s)**        | Prodüksiyon orkestrasyon (opsiyonel, ölçek büyüdüğünde) |
| **GitHub Actions**          | CI/CD pipeline                                          |
| **Terraform**               | Infrastructure as Code                                  |
| **Prometheus + Grafana**    | Metrik toplama ve görselleştirme                        |
| **Loki**                    | Log toplama ve arama                                    |
| **Sentry**                  | Hata izleme (error tracking)                            |
| **Nginx / Traefik**         | Reverse proxy, load balancing, SSL termination          |

### 3.5 Güvenlik

| Katman                | Teknoloji / Yöntem                                     |
| --------------------- | ------------------------------------------------------ |
| **Kimlik doğrulama**  | JWT + Refresh Token (httpOnly cookie)                  |
| **Yetkilendirme**     | RBAC (Role-Based Access Control)                       |
| **API güvenliği**     | Rate limiting, API key rotation, CORS, CSRF protection |
| **Veri şifreleme**    | TLS 1.3 (transit), AES-256 (at rest)                   |
| **Secret yönetimi**   | HashiCorp Vault veya AWS Secrets Manager               |
| **Audit log**         | Tüm kritik işlemler loglanır (kim, ne, ne zaman)       |
| **2FA**               | TOTP (Google Authenticator uyumlu)                     |
| **Penetrasyon testi** | OWASP Top 10 kontrolleri                               |

---

## 4. Risk Analizi

### 4.1 Teknik Riskler

| Risk                   | Olasılık | Etki   | Azaltma Stratejisi                                            |
| ---------------------- | -------- | ------ | ------------------------------------------------------------- |
| Broker API kesintisi   | Orta     | Kritik | Birden fazla broker entegrasyonu, fallback mekanizması        |
| Veri gecikmesi / kayıp | Orta     | Yüksek | Kafka replay, veri doğrulama, redundant veri kaynakları       |
| Yanlış emir gönderimi  | Düşük    | Kritik | Risk kontrol katmanı, sandbox modu, emir onay mekanizması     |
| Model overfit          | Yüksek   | Orta   | Walk-forward validation, out-of-sample test, regularizasyon   |
| Sistem aşırı yükü      | Düşük    | Yüksek | Auto-scaling, circuit breaker, rate limiting                  |
| Veri tabanı performans | Düşük    | Orta   | TimescaleDB partitioning, query optimization, connection pool |

### 4.2 İş Riskleri

| Risk                   | Olasılık | Etki   | Azaltma Stratejisi                                      |
| ---------------------- | -------- | ------ | ------------------------------------------------------- |
| Regülasyon değişikliği | Orta     | Yüksek | SPK/BIST kurallarına uyum, hukuki danışmanlık           |
| Piyasa yapısal değişim | Düşük    | Orta   | Adaptif stratejiler, düzenli model yeniden eğitimi      |
| Siber saldırı          | Düşük    | Kritik | WAF, DDoS koruması, penetrasyon testi, güvenlik audit'i |

### 4.3 Zorluklar

1. **BIST API erişimi:** Türkiye'de broker API'leri standartlaştırılmamıştır; her broker farklı API formatı kullanır.
2. **Veri kalitesi:** Geçmiş verilerde boşluklar, hatalı fiyatlar (corporate actions) olabilir.
3. **Gecikme:** Gerçek zamanlı emir gönderiminde her milisaniye önemlidir.
4. **Regülasyon:** SPK (Sermaye Piyasası Kurulu) düzenlemeleri algoritmik ticaret için kısıtlamalar getirebilir.
5. **Backtest vs. gerçek performans:** Paper trading ile canlı piyasa arasındaki fark (slippage, likidite).

---

## 5. Güvenlik Gereksinimleri (Detaylı)

### 5.1 Kimlik Doğrulama ve Yetkilendirme Akışı

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client   │───▶│  Auth    │───▶│  Token   │───▶│  RBAC    │
│  (React)  │    │  Service │    │  Verify  │    │  Guard   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
      │                │               │               │
      │         ┌──────▼──────┐  ┌─────▼─────┐  ┌─────▼─────┐
      │         │  bcrypt     │  │  JWT      │  │  Roller:  │
      │         │  hash       │  │  verify   │  │  admin,   │
      │         │  + salt     │  │  + rotate │  │  trader,  │
      │         └─────────────┘  └───────────┘  │  viewer   │
      │                                          └───────────┘
```

### 5.2 Broker API Güvenliği

- API anahtarları **asla** istemci tarafında saklanmaz.
- Tüm broker iletişimi sunucu tarafında, şifreli kanallar üzerinden yapılır.
- API anahtarları Vault / Secrets Manager'da saklanır.
- Emir gönderme yetkileri RBAC ile kontrol edilir.

---

## 6. Performans Gereksinimleri

### 6.1 Gecikme Hedefleri

| İşlem                  | Hedef    | Açıklama                              |
| ---------------------- | -------- | ------------------------------------- |
| Veri alma (tick)       | < 50 ms  | Broker'dan fiyat verisi alınma süresi |
| Strateji hesaplama     | < 100 ms | Sinyal üretme süresi                  |
| Emir gönderme          | < 50 ms  | Broker'a emir iletme süresi           |
| Dashboard güncelleme   | < 200 ms | UI'da fiyat güncelleme süresi         |
| Backtest (1 yıl)       | < 30 sn  | Tek strateji, günlük veri             |
| API yanıt süresi (p95) | < 100 ms | REST endpoint'leri                    |

### 6.2 Ölçekleme Hedefleri

| Metrik                 | MVP   | Tam Sürüm |
| ---------------------- | ----- | --------- |
| Eşzamanlı kullanıcı    | 10    | 1000+     |
| Aktif strateji sayısı  | 5     | 100+      |
| Takip edilen sembol    | 50    | 500+      |
| Tick işleme kapasitesi | 1K/sn | 50K/sn    |
| Geçmiş veri saklama    | 5 yıl | 10+ yıl   |

---

## 7. Kullanılacak Temel Kütüphaneler

### 7.1 Backend (Python)

```
# Core
fastapi==0.115.*
uvicorn[standard]==0.34.*
pydantic==2.10.*
celery==5.4.*
redis==5.2.*

# Database
sqlalchemy==2.0.*
alembic==1.14.*
asyncpg==0.30.*
psycopg[binary]==3.2.*

# Data & ML
pandas==2.2.*
numpy==2.1.*
scikit-learn==1.6.*
xgboost==2.1.*
lightgbm==4.5.*
torch==2.5.*
optuna==4.1.*
mlflow==2.19.*
onnxruntime==1.20.*

# Teknik Analiz
ta-lib==0.5.*       # veya pandas-ta
pandas-ta==0.3.*

# Broker & Veri
yfinance==0.2.*
requests==2.32.*
websockets==14.*
aiohttp==3.11.*

# Mesajlaşma
confluent-kafka==2.6.*

# Güvenlik
python-jose[cryptography]==3.3.*
passlib[bcrypt]==1.7.*
python-multipart==0.0.*

# Monitoring & Log
structlog==24.4.*
sentry-sdk[fastapi]==2.19.*
prometheus-fastapi-instrumentator==7.0.*

# Test
pytest==8.3.*
pytest-asyncio==0.24.*
pytest-cov==6.0.*
httpx==0.28.*       # async test client
factory-boy==3.3.*
```

### 7.2 Frontend (Node.js / React)

```json
{
  "dependencies": {
    "next": "^15.1",
    "react": "^19.0",
    "react-dom": "^19.0",
    "typescript": "^5.7",
    "@tanstack/react-query": "^5.62",
    "zustand": "^5.0",
    "socket.io-client": "^4.8",
    "lightweight-charts": "^4.2",
    "recharts": "^2.15",
    "@tremor/react": "^3.18",
    "tailwindcss": "^4.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "^0.7",
    "clsx": "^2.1",
    "tailwind-merge": "^2.6",
    "lucide-react": "^0.468",
    "date-fns": "^4.1",
    "zod": "^3.24",
    "react-hook-form": "^7.54",
    "@hookform/resolvers": "^3.9",
    "axios": "^1.7",
    "next-auth": "^5.0"
  },
  "devDependencies": {
    "vitest": "^2.1",
    "@testing-library/react": "^16.1",
    "playwright": "^1.49",
    "eslint": "^9.16",
    "prettier": "^3.4",
    "husky": "^9.1",
    "lint-staged": "^15.2"
  }
}
```

---

## 8. İyileştirme Önerileri ve Fırsatlar

### 8.1 Kısa Vadeli (MVP+)

1. **Paper Trading Modu:** Gerçek para riski olmadan strateji testi.
2. **Watchlist:** Kullanıcı özel takip listeleri oluşturabilmeli.
3. **Temel Bildirimler:** Fiyat alarm, emir tamamlanma bildirimi.
4. **Mobil Responsive:** Dashboard mobilde kullanılabilir olmalı.

### 8.2 Orta Vadeli

1. **Sentiment Analizi:** Haber ve sosyal medya verilerinden duygu analizi (Twitter/X, Ekşi Sözlük, haber siteleri).
2. **Portfolio Optimization:** Markowitz, Black-Litterman portföy optimizasyonu.
3. **Multi-Broker Desteği:** Tek arayüzden birden fazla broker ile işlem.
4. **Strateji Marketplace:** Kullanıcılar strateji paylaşabilir/satabilir.
5. **Mobil Uygulama:** React Native ile native mobil uygulama.

### 8.3 Uzun Vadeli

1. **Reinforcement Learning:** DQN/PPO tabanlı otomatik strateji keşfi.
2. **Alternative Data:** Uydu görüntüsü, kredi kartı verisi gibi alternatif veri kaynakları.
3. **High-Frequency Trading (HFT):** Rust/C++ tabanlı düşük gecikmeli emir motoru.
4. **Cross-Market Arbitrage:** BIST + Forex + Kripto arasında arbitraj fırsatları.
5. **LLM Destekli Asistan:** Doğal dil ile strateji oluşturma ve piyasa analizi (GPT-4o / Claude entegrasyonu).

---

## 9. Sonuç

bist-robogo projesi, Türkiye borsası için kapsamlı ve profesyonel bir ticaret platformu olma potansiyeli taşımaktadır. Bu doküman kapsamında tespit edilen gereksinimler, teknoloji seçimleri ve risk analizleri proje için sağlam bir temel oluşturmaktadır.

Bir sonraki adım olarak **Sistem Mimarisi** dokümanında detaylı modül tasarımları, veri akışları ve API sözleşmeleri tanımlanacaktır.

---

_Bu doküman, bist-robogo projesinin Ar-Ge sürecinin bir parçasıdır ve düzenli olarak güncellenecektir._
