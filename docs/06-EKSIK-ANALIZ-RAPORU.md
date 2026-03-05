# bist-robogo — Eksik Analiz Raporu

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Son Güncelleme:** 2026-03-05  
> **Amaç:** Mevcut kod tabanı ile dokümanların karşılaştırmalı analizi — sadece GERÇEKTEN EKSİK / YAPILMASI GEREKEN maddeler.

---

## 1. Analiz Yöntemi

Bu rapor, mevcut kod tabanının (`backend/` 122 .py, `frontend/src/` 107 dosya) tüm dizin yapısının dokümanlarla (01–12) satır satır karşılaştırılmasıyla oluşturulmuştur. **Tamamlanan maddeler çıkarılmış**, yalnızca gerçek eksiklikler listelenmiştir.

---

## 2. ÖNCEKİ RAPORDA TAMAMLANAN (TEMİZLENEN) MADDELER

Aşağıdaki tüm maddeler **artık tamamlanmıştır** ve eski rapordan çıkarılmıştır:

- ~~B1–B17~~ Backend implementasyon eksiklikleri → Tümü tamamlandı (Faz 0–4.2)
- ~~F1–F7~~ Frontend kritik eksiklikler → Tümü tamamlandı
- ~~F8–F11~~ Frontend yüksek eksiklikler → Tümü tamamlandı
- ~~D1–D4~~ Tasarım sistemi eksiklikleri → Doc 09 + globals.css ile tamamlandı
- ~~O1–O2~~ Docker/Dockerfile eksiklikleri → Tamamlandı
- ~~T1–T2~~ Backend test eksiklikleri → 272/272 test geçiyor
- ~~Doc 07, 08, 09, 10 oluşturulması~~ → Tümü oluşturuldu

---

## 3. MEVCUT EKSİKLİKLER

### 3.1 Backend — Kullanılmayan / Uyumsuz Bağımlılıklar (pyproject.toml)

| #   | Bağımlılık                                                         | Durum                         | Açıklama                                                             |
| --- | ------------------------------------------------------------------ | ----------------------------- | -------------------------------------------------------------------- |
| B1  | `passlib`                                                          | ⚠️ Kaldırılmalı               | Fix #10 ile `bcrypt` modülüne geçildi, `passlib` artık kullanılmıyor |
| B2  | `confluent-kafka`                                                  | ⚠️ Kaldırılmalı               | `core/kafka_client.py` hiç oluşturulmadı, Kafka kullanılmıyor        |
| B3  | `yfinance`                                                         | ⚠️ Kaldırılmalı               | CollectAPI ile değiştirildi (Sprint 4.1)                             |
| B4  | `aiohttp`                                                          | ⚠️ Değerlendirilmeli          | `httpx` tercih edildi, `aiohttp` kullanılıyor mu kontrol edilmeli    |
| B5  | `factory-boy` (dev)                                                | ⚠️ Kaldırılmalı               | Test factory dosyası yok, flat fixture yapısı tercih edildi          |
| B6  | ML grubu: `xgboost`, `lightgbm`, `optuna`, `mlflow`, `onnxruntime` | ⚠️ Kaldırılmalı veya optional | ML servisi kaldırılıp OpenRouter AI ile değiştirildi                 |

### 3.2 Backend — Eksik Dosyalar / Özellikler

| #   | Eksiklik                                                                       | Öncelik  | Açıklama                                                              |
| --- | ------------------------------------------------------------------------------ | -------- | --------------------------------------------------------------------- |
| B7  | Ek strateji dosyaları (`macd_signal`, `bollinger_breakout`, `momentum_ranker`) | 🟢 Düşük | Doc 07'de planlanmış, mevcut 4 strateji yeterli olabilir              |
| B8  | Gerçek broker adaptörleri (İş Yatırım, Gedik)                                  | 🟡 Orta  | `brokers/paper_broker.py` var, gerçek broker yok (Faz 4.3+ ertelendi) |
| B9  | `scripts/seed_historical.py`                                                   | 🟢 Düşük | Geçmiş veri yükleme scripti eksik                                     |
| B10 | `scripts/create_admin.py`                                                      | 🟢 Düşük | Admin kullanıcı oluşturma scripti eksik                               |
| B11 | GitHub Actions CI/CD pipeline                                                  | 🟡 Orta  | `.github/workflows/` dizini yok                                       |
| B12 | Sentry entegrasyonu doğrulaması                                                | 🟢 Düşük | Bağımlılıkta var ama yapılandırılmış mı belirsiz                      |
| B13 | Prometheus metrikleri doğrulaması                                              | 🟢 Düşük | Bağımlılıkta var ama aktif kullanımda mı belirsiz                     |

### 3.3 Frontend — Eksik Dosyalar / Özellikler

| #   | Eksiklik                                  | Öncelik   | Açıklama                                                                                |
| --- | ----------------------------------------- | --------- | --------------------------------------------------------------------------------------- |
| F1  | `error.tsx` boundary dosyaları            | 🔴 Kritik | Hiçbir route grubunda `error.tsx` yok — runtime hata yakalama korunmasız                |
| F2  | `loading.tsx` Suspense boundary dosyaları | 🟡 Yüksek | Hiçbir route grubunda `loading.tsx` yok — sayfa geçişlerinde loading state eksik        |
| F3  | `not-found.tsx` özel 404 sayfası          | 🟡 Yüksek | Next.js özel 404 sayfası bulunmuyor                                                     |
| F4  | `middleware.ts` (Next.js middleware)      | 🟡 Yüksek | Auth redirect'leri yalnızca client-side (`auth-guard.tsx`), sunucu tarafında koruma yok |
| F5  | Frontend test altyapısı                   | 🟡 Yüksek | `vitest.config.ts` ve `playwright.config.ts` yok, hiç test dosyası yok                  |
| F6  | `types/notification.ts`                   | 🟢 Düşük  | Backend'de model var ama frontend types dizininde tanımsız                              |
| F7  | `types/dashboard.ts`                      | 🟢 Düşük  | Dashboard tipleri ayrı dosyada değil                                                    |
| F8  | `types/auth.ts`                           | 🟢 Düşük  | Auth tipleri ayrı dosyada tanımlı değil                                                 |
| F9  | PWA Service Worker                        | 🟢 Düşük  | `public/manifest.json` var ama service worker dosyası yok                               |

### 3.4 DevOps / Altyapı

| #   | Eksiklik                            | Öncelik  | Açıklama                                                      |
| --- | ----------------------------------- | -------- | ------------------------------------------------------------- |
| O1  | GitHub Actions CI/CD workflow       | 🟡 Orta  | `.github/workflows/ci.yml` yok                                |
| O2  | Nginx/Traefik reverse proxy config  | 🟢 Düşük | Prodüksiyon deploy için gerekecek                             |
| O3  | Grafana dashboard JSON provisioning | 🟢 Düşük | Monitoring dashboard tanımları yok                            |
| O4  | `.env.example` dosyaları            | 🟢 Düşük | Backend ve frontend için örnek env dosyaları kontrol edilmeli |

---

## 4. DOC 07 vs GERÇEK KOD — SAPMA RAPORU

Aşağıdaki kalemler Doc 07'de (Backend İmplementasyon Kılavuzu) planlanmış ancak bilinçli kararlarla **farklı uygulanmıştır**. Bunlar hata değil, evrim sürecinde alınmış kararlardır:

| Planlanan (Doc 07)                                  | Gerçek Uygulama                           | Açıklama                                                         |
| --------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------- |
| `*_repo.py` adlandırma                              | `*_repository.py`                         | Daha açık isimlendirme tercih edildi                             |
| `api/v1/ml.py` + `services/ml_service.py`           | `api/v1/ai.py` + `services/ai_service.py` | ML → OpenRouter AI pivotu                                        |
| `tasks/ml_tasks.py`                                 | `tasks/ai_tasks.py`                       | Aynı pivot                                                       |
| `services/scheduler_service.py`                     | Yok (Celery beat)                         | Zamanlama Celery beat ile yönetiliyor                            |
| `schemas/trend.py`                                  | `schemas/analysis.py`                     | İsim değişikliği                                                 |
| `schemas/user.py`                                   | `schemas/auth.py` içinde                  | Birleştirildi                                                    |
| `tests/unit/` + `tests/integration/` hiyerarşisi    | Flat `tests/` yapısı                      | Basitlik tercih edildi                                           |
| `core/kafka_client.py`                              | Yok                                       | Kafka kullanılmadı                                               |
| `indicators/volatility.py`, `volume.py`, `utils.py` | `momentum.py` + `trend.py` içinde         | Fonksiyonlar mevcut dosyalara gömüldü                            |
| `websocket/notification_stream.py`                  | Yok                                       | Bildirim WebSocket'i implemente edilmedi                         |
| 7 strateji planı                                    | 4 strateji mevcut                         | Base + MA Crossover + RSI Reversal + AI Strategy yeterli görüldü |

---

## 5. ÖNCELİK SIRASI — YAPILMASI GEREKENLER

| Sıra | Madde                                                         | Öncelik   | Tahmini Efor    |
| ---- | ------------------------------------------------------------- | --------- | --------------- |
| 1    | Frontend `error.tsx` boundary'leri oluştur (F1)               | 🔴 Kritik | 1 saat          |
| 2    | Frontend `loading.tsx` boundary'leri oluştur (F2)             | 🟡 Yüksek | 30 dk           |
| 3    | Frontend `not-found.tsx` sayfası (F3)                         | 🟡 Yüksek | 30 dk           |
| 4    | Frontend `middleware.ts` auth koruması (F4)                   | 🟡 Yüksek | 1 saat          |
| 5    | `pyproject.toml` kullanılmayan bağımlılıkları temizle (B1–B6) | 🟡 Yüksek | 30 dk           |
| 6    | GitHub Actions CI/CD pipeline (O1, B11)                       | 🟡 Orta   | 2 saat          |
| 7    | Frontend test altyapısı kurulumu (F5)                         | 🟡 Orta   | 3 saat          |
| 8    | Frontend eksik type dosyaları (F6–F8)                         | 🟢 Düşük  | 30 dk           |
| 9    | Gerçek broker adaptörleri (B8)                                | 🟡 Orta   | İhtiyaç halinde |
| 10   | Ek stratejiler (B7)                                           | 🟢 Düşük  | İhtiyaç halinde |

---

## 6. SONUÇ

Proje **büyük ölçüde tamamlanmış** durumdadır:

- **Backend:** 106 uygulama dosyası, 272/272 test, 12 servis, 14 API modülü ✅
- **Frontend:** 107 src dosyası, 14 sayfa, 0 TypeScript hatası, build OK ✅
- **Altyapı:** Docker Compose (6 servis), PostgreSQL + TimescaleDB, Redis ✅

Kalan eksiklikler çoğunlukla **kullanıcı deneyimi iyileştirmeleri** (error/loading boundaries), **CI/CD pipeline**, **bağımlılık temizliği** ve **opsiyonel ek özellikler** (gerçek broker, ek stratejiler) kategorisindedir. Hiçbiri mevcut işlevselliği engellemez.

---

_Bu rapor, 2026-03-05 tarihinde gerçek kod tabanı analizi ile oluşturulmuştur._
