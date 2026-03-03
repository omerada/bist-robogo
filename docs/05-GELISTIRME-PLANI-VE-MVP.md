# bist-robogo — Geliştirme Planı, MVP ve Yol Haritası

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03

---

## 1. Geliştirme Fazları

### 1.1 Faz Genel Bakışı

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          PROJE YOL HARİTASI                                │
│                                                                            │
│  Faz 0          Faz 1           Faz 2           Faz 3          Faz 4      │
│  Altyapı        MVP             Genişletme      AI & Otomasyon  Ölçekleme │
│  2 hafta        6 hafta         6 hafta         8 hafta         Sürekli   │
│                                                                            │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  Proje kurulum  Veri toplama    Otomatik emir   ML modelleri    K8s       │
│  Docker env     Dashboard       Risk motoru     Backtest opt.   Multi-    │
│  DB şema        Temel grafik    Trend analiz    Sentiment       broker    │
│  CI/CD          Auth sistemi    Backtest        RL strateji     HFT       │
│  Monitoring     Paper trading   Bildirimler     Portföy opt.    Marketplace│
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Faz 0 — Altyapı Kurulumu (2 Hafta)

### 2.1 Hedefler

- Geliştirme ortamını hazırlamak
- CI/CD pipeline kurmak
- Veritabanı şemalarını oluşturmak
- Monitoring altyapısını hazırlamak

### 2.2 Görevler

| #    | Görev                                       | Süre    | Bağımlılık | Öncelik |
| ---- | ------------------------------------------- | ------- | ---------- | ------- |
| 0.1  | Proje repository yapılandırması (monorepo)  | 1 gün   | —          | P0      |
| 0.2  | Docker Compose ortamı (tüm servisler)       | 2 gün   | —          | P0      |
| 0.3  | Backend proje iskeleti (FastAPI + Poetry)   | 1 gün   | —          | P0      |
| 0.4  | Frontend proje iskeleti (Next.js + pnpm)    | 1 gün   | —          | P0      |
| 0.5  | PostgreSQL + TimescaleDB şema migrasyonları | 2 gün   | 0.2        | P0      |
| 0.6  | Redis yapılandırması                        | 0.5 gün | 0.2        | P0      |
| 0.7  | Kafka/Redpanda yapılandırması               | 1 gün   | 0.2        | P1      |
| 0.8  | GitHub Actions CI/CD pipeline               | 1 gün   | 0.1        | P0      |
| 0.9  | Prometheus + Grafana kurulumu               | 1 gün   | 0.2        | P1      |
| 0.10 | ESLint, Prettier, pre-commit hook'lar       | 0.5 gün | 0.3, 0.4   | P1      |

### 2.3 Çıktılar

- ✅ `docker-compose up` ile tüm servisler ayağa kalkar
- ✅ Backend: `/health` endpoint çalışır
- ✅ Frontend: Ana sayfa render edilir
- ✅ DB: Tüm tablolar oluşturulmuş
- ✅ CI: Push'ta otomatik test + lint çalışır

---

## 3. Faz 1 — MVP (6 Hafta)

### 3.1 Hedefler

- Gerçek zamanlı veri toplama ve saklama
- Temel dashboard ve grafik ekranı
- Kullanıcı kimlik doğrulama
- Manuel emir (paper trading)
- Temel teknik göstergeler

### 3.2 Sprint 1 — Veri Katmanı (2 Hafta)

| #   | Görev                                                       | Süre  | Bağımlılık |
| --- | ----------------------------------------------------------- | ----- | ---------- |
| 1.1 | Market Data Service — Yahoo Finance/yfinance entegrasyonu   | 2 gün | Faz 0      |
| 1.2 | Geçmiş veri çekici (EOD OHLCV — son 5 yıl)                  | 2 gün | 1.1        |
| 1.3 | TimescaleDB'ye veri yazma pipeline                          | 1 gün | 1.2        |
| 1.4 | Sembol ve endeks tabloları (BIST30, BIST100, Katılım)       | 1 gün | Faz 0      |
| 1.5 | Redis cache katmanı (anlık fiyat)                           | 1 gün | 1.1        |
| 1.6 | Market Data REST API endpoints                              | 2 gün | 1.3        |
| 1.7 | WebSocket canlı fiyat akışı                                 | 1 gün | 1.5        |
| 1.8 | Teknik gösterge hesaplama servisi (RSI, MACD, SMA, EMA, BB) | 2 gün | 1.3        |

### 3.3 Sprint 2 — Frontend Temeli + Auth (2 Hafta)

| #   | Görev                                            | Süre  | Bağımlılık |
| --- | ------------------------------------------------ | ----- | ---------- |
| 2.1 | Auth Service (kayıt, giriş, JWT)                 | 2 gün | Faz 0      |
| 2.2 | Frontend auth sayfaları (login, register)        | 1 gün | 2.1        |
| 2.3 | Dashboard layout (sidebar, header)               | 1 gün | Faz 0      |
| 2.4 | Dashboard ekranı — portföy kartları (mock data)  | 2 gün | 2.3        |
| 2.5 | Piyasa ekranı — sembol listesi tablosu           | 2 gün | 1.6        |
| 2.6 | Piyasa ekranı — TradingView mum grafiği          | 2 gün | 1.6        |
| 2.7 | Piyasa ekranı — WebSocket canlı fiyat güncelleme | 1 gün | 1.7        |
| 2.8 | Endeks seçici (BIST30, BIST100, Katılım)         | 1 gün | 1.4        |

### 3.4 Sprint 3 — Paper Trading + Portföy (2 Hafta)

| #   | Görev                                                     | Süre  | Bağımlılık |
| --- | --------------------------------------------------------- | ----- | ---------- |
| 3.1 | Order Service — paper trading modu                        | 2 gün | Sprint 1   |
| 3.2 | Frontend — emir formu (al/sat)                            | 2 gün | 3.1        |
| 3.3 | Portfolio Service — pozisyon takibi                       | 2 gün | 3.1        |
| 3.4 | Frontend — portföy ekranı (açık pozisyonlar, PnL)         | 2 gün | 3.3        |
| 3.5 | Frontend — emir geçmişi ekranı                            | 1 gün | 3.1        |
| 3.6 | Dashboard — gerçek veriyle bağlantı                       | 1 gün | 3.3        |
| 3.7 | Temel risk kontrolleri (maks pozisyon, maks günlük zarar) | 1 gün | 3.1        |
| 3.8 | Bildirimler — in-app (WebSocket)                          | 1 gün | Sprint 2   |

### 3.5 MVP Çıktıları

- ✅ Kullanıcı kayıt/giriş yapabilir
- ✅ BIST hisselerini canlı takip edebilir
- ✅ Mum grafiğinde teknik göstergeleri görebilir
- ✅ Endeks bazlı filtreleme yapabilir (BIST30, BIST100, Katılım)
- ✅ Paper trading ile al/sat yapabilir
- ✅ Portföy durumunu (pozisyon, PnL) görebilir
- ✅ Temel dashboard'u kullanabilir

---

## 4. Faz 2 — Genişletme (6 Hafta)

### 4.1 Hedefler

- Trend analiz ekranı
- Otomatik emir sistemi (broker entegrasyonu)
- Tam risk motoru
- Backtest motoru
- Strateji yönetimi
- Bildirim sistemi

### 4.2 Sprint 4 — Trend Analiz + Strateji (2 Hafta)

| #   | Görev                                                 | Süre  | Bağımlılık |
| --- | ----------------------------------------------------- | ----- | ---------- |
| 4.1 | Trend analiz algoritması (dip tespit)                 | 3 gün | Sprint 1   |
| 4.2 | Trend analiz algoritması (kırılım tespit)             | 2 gün | 4.1        |
| 4.3 | Trend analiz API endpoint'leri                        | 1 gün | 4.2        |
| 4.4 | Frontend — Trend Analiz Ekranı (dip/kırılım kartları) | 3 gün | 4.3        |
| 4.5 | Frontend — Trend Isı Haritası (Treemap)               | 1 gün | 4.3        |
| 4.6 | Strategy Engine — BaseStrategy abstract class         | 1 gün | —          |
| 4.7 | İlk yerleşik stratejiler (MA Crossover, RSI)          | 2 gün | 4.6        |

### 4.3 Sprint 5 — Backtest + Risk (2 Hafta)

| #   | Görev                                                 | Süre  | Bağımlılık |
| --- | ----------------------------------------------------- | ----- | ---------- |
| 5.1 | Backtest Engine — core simülasyon döngüsü             | 3 gün | Sprint 4   |
| 5.2 | Backtest — slippage + komisyon simülasyonu            | 1 gün | 5.1        |
| 5.3 | Backtest — performans metrikleri hesaplama            | 2 gün | 5.1        |
| 5.4 | Frontend — Backtest ekranı (konfigürasyon + sonuçlar) | 3 gün | 5.3        |
| 5.5 | Risk Manager — tam kural seti implementasyonu         | 2 gün | Sprint 3   |
| 5.6 | Frontend — Risk durumu kartı + ayarlar                | 1 gün | 5.5        |

### 4.4 Sprint 6 — Broker Entegrasyonu + Bildirimler (2 Hafta)

| #   | Görev                                         | Süre  | Bağımlılık |
| --- | --------------------------------------------- | ----- | ---------- |
| 6.1 | Broker adapter arayüzü (abstract)             | 1 gün | —          |
| 6.2 | İş Yatırım API entegrasyonu (veya alternatif) | 3 gün | 6.1        |
| 6.3 | Gerçek emir gönderme + durum takibi           | 2 gün | 6.2        |
| 6.4 | Otomatik strateji → emir akışı                | 2 gün | 6.3        |
| 6.5 | Bildirim servisi (email + in-app)             | 2 gün | —          |
| 6.6 | Telegram bot entegrasyonu                     | 1 gün | 6.5        |
| 6.7 | Frontend — strateji yönetim ekranı            | 1 gün | Sprint 4   |

### 4.5 Faz 2 Çıktıları

- ✅ Trend analiz ekranı çalışır (günlük/haftalık/aylık)
- ✅ Backtest çalıştırılabilir ve sonuçlar grafik + tablo ile gösterilir
- ✅ Risk yönetimi tüm kurallarıyla aktif
- ✅ En az 1 broker ile gerçek emir gönderilebilir
- ✅ Stratejiler otomatik sinyal üretir ve emir gönderir
- ✅ Email + Telegram ile bildirim alınır

---

## 5. Faz 3 — AI ve Otomasyon (8 Hafta)

### 5.1 Hedefler

- ML model pipeline (eğitim → değerlendirme → serving)
- AI stratejiler (dip tahmini, trend tahmini)
- Parametre optimizasyonu (Optuna)
- Gelişmiş teknik göstergeler
- Portföy optimizasyonu

### 5.2 Görevler (Yüksek Düzey)

| #    | Görev                                              | Süre    | Sprint    |
| ---- | -------------------------------------------------- | ------- | --------- |
| 7.1  | Feature engineering pipeline                       | 1 hafta | Sprint 7  |
| 7.2  | Trend Classifier (XGBoost) — eğitim + evaluation   | 1 hafta | Sprint 7  |
| 7.3  | Dip Detector (Random Forest) — eğitim + evaluation | 1 hafta | Sprint 8  |
| 7.4  | MLflow experiment tracking entegrasyonu            | 3 gün   | Sprint 7  |
| 7.5  | ONNX model export + FastAPI serving                | 3 gün   | Sprint 8  |
| 7.6  | AI Trend Predictor stratejisi                      | 1 hafta | Sprint 8  |
| 7.7  | Dip Hunter stratejisi                              | 1 hafta | Sprint 9  |
| 7.8  | Optuna ile parametre optimizasyonu                 | 1 hafta | Sprint 9  |
| 7.9  | Walk-forward validation framework                  | 3 gün   | Sprint 9  |
| 7.10 | LSTM/Transformer fiyat tahmini (deneysel)          | 1 hafta | Sprint 10 |
| 7.11 | Volatilite tahmini (GARCH + ML)                    | 3 gün   | Sprint 10 |
| 7.12 | Portföy optimizasyonu (Markowitz)                  | 3 gün   | Sprint 10 |
| 7.13 | Model drift monitoring                             | 2 gün   | Sprint 10 |

### 5.3 Faz 3 Çıktıları

- ✅ En az 2 ML model production'da çalışır
- ✅ AI stratejiler backtest'te avantajlı performans gösterir
- ✅ Parametre optimizasyonu çalışır
- ✅ Model metrikleri MLflow'da takip edilir
- ✅ Otomatik model yeniden eğitim (haftalık)

---

## 6. Faz 4 — Ölçekleme ve İleri Seviye (Sürekli)

### 6.1 Görevler

| #    | Görev                         | Öncelik | Açıklama                                      |
| ---- | ----------------------------- | ------- | --------------------------------------------- |
| 8.1  | Kubernetes deployment         | P1      | Prodüksiyon orkestrasyon                      |
| 8.2  | Multi-broker desteği          | P1      | Gedik, Deniz Yatırım vb.                      |
| 8.3  | Sentiment analizi             | P2      | Heber/sosyal medya duygu analizi              |
| 8.4  | Mobil uygulama (React Native) | P2      | iOS + Android                                 |
| 8.5  | HFT modülü (Rust)             | P3      | Düşük gecikmeli emir motoru                   |
| 8.6  | LLM asistan                   | P2      | "THYAO'yı analiz et" gibi doğal dil komutları |
| 8.7  | Reinforcement Learning        | P3      | DQN/PPO strateji keşfi                        |
| 8.8  | Strateji marketplace          | P3      | Topluluk strateji paylaşımı                   |
| 8.9  | Alternative data              | P3      | Uydu, kredi kartı verileri                    |
| 8.10 | FIX protokolü desteği         | P2      | Profesyonel emir iletimi                      |
| 8.11 | White-label çözüm             | P3      | Kurumsal müşteriler için                      |

---

## 7. Modül Bağımlılık Grafiği

```
                    ┌──────────────┐
                    │   Altyapı    │
                    │  (Docker,    │
                    │  DB, Redis)  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌────▼─────┐ ┌────▼─────┐
        │  Auth    │ │  Market  │ │  Frontend│
        │ Service  │ │  Data    │ │  Temel   │
        └─────┬────┘ └────┬─────┘ └────┬─────┘
              │            │            │
              │      ┌─────▼─────┐     │
              │      │  Teknik   │     │
              │      │ Göstergeler│     │
              │      └─────┬─────┘     │
              │            │            │
              │     ┌──────▼──────┐    │
              └────▶│   Trading   │◀───┘
                    │   Engine    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌────▼─────┐ ┌────▼─────┐
        │  Risk    │ │ Strategy │ │ Portfolio │
        │ Manager  │ │ Engine   │ │ Service   │
        └──────────┘ └────┬─────┘ └───────────┘
                          │
                    ┌─────▼─────┐
                    │ Backtest  │
                    │ Engine    │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  AI/ML    │
                    │ Service   │
                    └───────────┘
```

**Kritik Bağımlılık Sırası:**

1. **Altyapı** → Hepsi
2. **Auth + Market Data** → Trading Engine
3. **Teknik Göstergeler** → Strategy Engine
4. **Trading Engine** → Risk Manager, Portfolio
5. **Strategy Engine** → Backtest Engine
6. **Backtest Engine** → AI/ML Service

---

## 8. Test Stratejisi

### 8.1 Test Piramidi

```
            ┌────────────┐
            │   E2E      │  Playwright — 10%
            │   Tests    │  Kritik kullanıcı akışları
            ├────────────┤
            │Integration │  pytest + httpx — 30%
            │   Tests    │  API endpoint, DB, service
            ├────────────┤
            │   Unit     │  pytest + vitest — 60%
            │   Tests    │  İş mantığı, hesaplamalar
            └────────────┘
```

### 8.2 Test Kapsamı Hedefleri

| Katman              | Araç             | Kapsam Hedefi               |
| ------------------- | ---------------- | --------------------------- |
| Backend Unit        | pytest           | > %80                       |
| Backend Integration | pytest + httpx   | > %60                       |
| Frontend Unit       | vitest           | > %70                       |
| Frontend Component  | Testing Library  | > %60                       |
| E2E                 | Playwright       | Kritik 10 senaryo           |
| Strateji Backtest   | Custom framework | Her strateji için           |
| ML Model            | Custom metrics   | Accuracy, Precision, Recall |

### 8.3 Kritik Test Senaryoları

1. **Emir akışı:** Sinyal → Risk kontrol → Emir gönder → Durum güncelle → Portföy güncelle
2. **Risk limiti:** Günlük zarar limiti aşıldığında emir reddedilir
3. **WebSocket:** Bağlantı kopma ve yeniden bağlanma
4. **Backtest doğruluğu:** Bilinen sonuçlarla karşılaştırma
5. **Auth güvenlik:** Token expire, refresh, 2FA
6. **Veri bütünlüğü:** Eksik OHLCV verisi tespiti
7. **Concurrent emirler:** Aynı anda birden fazla emir gönderildiğinde
8. **Broker failover:** Broker bağlantı koptuğunda graceful handling

---

## 9. Önerilen AI Strateji Modülleri

### 9.1 MVP+ Stratejiler

| Strateji            | Yöntem                     | Giriş Koşulu                 | Çıkış Koşulu                     |
| ------------------- | -------------------------- | ---------------------------- | -------------------------------- |
| **Trend Follower**  | SMA Crossover + ADX filtre | SMA20 > SMA50, ADX > 25      | SMA20 < SMA50 veya trailing stop |
| **Mean Reversion**  | RSI + Bollinger            | RSI < 30, fiyat BB alt bandı | RSI > 50 veya -3% stop           |
| **Momentum Ranker** | 3-6 ay momentum + hacim    | En yüksek momentum %20       | Aylık rebalance                  |

### 9.2 Gelişmiş AI Stratejiler

| Strateji            | Model Tipi        | Özellikler                                          |
| ------------------- | ----------------- | --------------------------------------------------- |
| **XGBoost Trend**   | Gradient Boosting | 50+ feature, günlük tahmin, walk-forward validation |
| **LSTM Price**      | Deep Learning     | Sequence modelling, 5 gün ileri tahmin              |
| **Regime Detector** | Hidden Markov     | Bull/bear/sideways rejim, strateji seçimi           |
| **Ensemble Signal** | Multi-model       | 3+ modelin ağırlıklı kombinasyonu                   |
| **RL Trader**       | PPO/DQN           | Otomatik strateji keşfi (Faz 4)                     |

### 9.3 Strateji Değerlendirme Kriterleri

Bir stratejinin production'a alınması için:

| Kriter                   | Minimum       | Arzu Edilen         |
| ------------------------ | ------------- | ------------------- |
| Sharpe Ratio             | > 1.0         | > 1.5               |
| Win Rate                 | > %50         | > %60               |
| Max Drawdown             | < -%15        | < -%10              |
| Profit Factor            | > 1.3         | > 1.8               |
| Minimum Trade Sayısı     | > 50          | > 100               |
| Out-of-Sample Performans | Pozitif       | In-sample'ın %80'i+ |
| Walk-Forward Consistency | > %60 windows | > %75 windows       |

---

## 10. Güvenlik ve Uyum Planı

### 10.1 SPK Uyumu

| Gereksinim                   | Durum         | Açıklama                    |
| ---------------------------- | ------------- | --------------------------- |
| Algoritmik ticaret bildirimi | Araştırılmalı | SPK'ya bildirim gerekebilir |
| İşlem kaydı saklama          | Planlı        | Minimum 10 yıl (audit_logs) |
| Risk yönetimi                | Planlı        | Otomatik risk kontrolleri   |
| Müşteri veri koruma          | Planlı        | KVKK uyumu, şifreleme       |

### 10.2 KVKK Uyumu

- Kişisel veri envanteri
- Açık rıza metni
- Veri saklama ve imha politikası
- Veri ihlali bildirim prosedürü

### 10.3 Güvenlik Audit Planı

| Periyot    | Faaliyet                             |
| ---------- | ------------------------------------ |
| Her sprint | Code review + SAST (static analysis) |
| Aylık      | Dependency vulnerability scan        |
| 3 ayda bir | Penetrasyon testi (OWASP Top 10)     |
| 6 ayda bir | Tam güvenlik audit'i                 |

---

## 11. Performans İzleme ve SLA

### 11.1 Anahtar Performans Göstergeleri (KPI)

| KPI                              | Hedef       | Ölçüm                 |
| -------------------------------- | ----------- | --------------------- |
| API Uptime                       | > %99.5     | Prometheus + Grafana  |
| API Latency (p95)                | < 100ms     | Prometheus histogram  |
| WebSocket Latency                | < 200ms     | Custom metric         |
| Emir İletim Süresi               | < 200ms     | Trading Engine metric |
| Backtest Süresi (1Y, 1 strateji) | < 30sn      | Celery task metric    |
| Günlük Veri Güncelleme           | %100 sembol | Scheduler metric      |
| Model Accuracy                   | > %60       | MLflow metric         |

### 11.2 Grafana Dashboard'ları

1. **System Overview:** CPU, RAM, Disk, Ağ, Container durumları
2. **API Performance:** Request rate, latency, error rate, endpoint breakdown
3. **Trading Metrics:** Günlük emir sayısı, PnL, pozisyon özeti
4. **Data Pipeline:** Veri gecikme, boşluk, hata sayısı
5. **ML Models:** Accuracy, prediction count, inference time, drift score

---

## 12. Tahmini Kaynak ve Bütçe

### 12.1 Ekip Yapısı (Önerilen)

| Rol                  | Sayı | Sorumluluk                 |
| -------------------- | ---- | -------------------------- |
| Full-Stack Developer | 2    | Backend + Frontend         |
| Quant Developer      | 1    | Strateji + Backtest + ML   |
| DevOps Engineer      | 0.5  | Altyapı, CI/CD, monitoring |
| UI/UX Designer       | 0.5  | Tasarım, kullanıcı testi   |

### 12.2 Altyapı Maliyeti (Aylık Tahmini)

| Kaynak                     | Geliştirme     | Prodüksiyon      |
| -------------------------- | -------------- | ---------------- |
| Cloud Server (VPS/EC2)     | $50-100        | $200-500         |
| Veritabanı (managed)       | $0 (yerel)     | $100-200         |
| Veri sağlayıcı API         | $0-50          | $100-500         |
| Domain + SSL               | $5             | $5               |
| Monitoring (Grafana Cloud) | $0 (free tier) | $50-100          |
| Toplam                     | **$55-155/ay** | **$455-1305/ay** |

---

## 13. Sonuç ve Sonraki Adımlar

### 13.1 Hemen Başlanacak İşler

1. ✅ Ar-Ge ve mimari dokümanlar tamamlandı (bu döküman)
2. 📋 Faz 0 görevlerini başlat (proje iskeleti, Docker, DB)
3. 📋 GitHub repository oluştur, branch stratejisi belirle
4. 📋 İlk sprint planlama toplantısı

### 13.2 Açık Sorular

| #   | Soru                                                    | Karar Gerekli  |
| --- | ------------------------------------------------------- | -------------- |
| 1   | Hangi broker ile başlanacak? (İş Yatırım, Gedik, vb.)   | Faz 2 öncesi   |
| 2   | Gerçek zamanlı veri kaynağı? (Matriks, CollectAPI, vb.) | Faz 1 Sprint 1 |
| 3   | Cloud sağlayıcı tercihi? (AWS, Hetzner, DigitalOcean)   | Faz 2 öncesi   |
| 4   | SPK algoritmik ticaret bildirimi gerekli mi?            | Hemen          |
| 5   | Paper trading mı, gerçek para ile mi başlanacak?        | Faz 2 öncesi   |

---

_Bu doküman, bist-robogo projesinin Ar-Ge sürecinin bir parçasıdır ve düzenli olarak güncellenecektir._
