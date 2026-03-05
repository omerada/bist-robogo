# bist-robogo — Eksik Analiz Raporu

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Son Güncelleme:** 2026-03-05 (Sprint 4.4 — CI/CD & Test Altyapısı)  
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
- ~~B1–B6~~ pyproject.toml kullanılmayan bağımlılıklar → ✅ Temizlendi (passlib, confluent-kafka, yfinance, aiohttp, factory-boy, ML grubu kaldırıldı)
- ~~F1~~ error.tsx boundary → ✅ 3 adet oluşturuldu (global, dashboard, auth)
- ~~F2~~ loading.tsx boundary → ✅ 9 adet oluşturuldu (tüm dashboard sayfaları)
- ~~F3~~ not-found.tsx 404 sayfası → ✅ Oluşturuldu
- ~~F4~~ middleware.ts auth koruması → ✅ Oluşturuldu (cookie-based + auth-store sync)
- ~~F6–F8~~ Eksik type dosyaları → ✅ notification.ts, dashboard.ts, auth.ts oluşturuldu
- ~~F5~~ Frontend test altyapısı → ✅ vitest.config.ts + 6 test dosyası (60 test), playwright.config.ts + e2e/auth.spec.ts
- ~~O1~~ GitHub Actions CI/CD → ✅ `.github/workflows/ci.yml` güncellendi (5 job: backend-lint, backend-test, frontend-lint, frontend-test, docker-build)

---

## 3. MEVCUT EKSİKLİKLER

### 3.1 Backend — Kullanılmayan Bağımlılıklar ✅ TEMİZLENDİ

> **Sprint 4.3'te tamamlandı.** `passlib`, `confluent-kafka`, `yfinance`, `aiohttp`, `scikit-learn`, `factory-boy` ve ML grubu (`xgboost`, `lightgbm`, `optuna`, `mlflow`, `onnxruntime`) kaldırıldı. `bcrypt` doğrudan eklendi.

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

| #   | Eksiklik                            | Öncelik       | Açıklama                                                                            |
| --- | ----------------------------------- | ------------- | ----------------------------------------------------------------------------------- |
| F1  | ~~`error.tsx` boundary dosyaları~~  | ✅ Tamamlandı | 3 boundary oluşturuldu: global, dashboard, auth                                     |
| F2  | ~~`loading.tsx` Suspense boundary~~ | ✅ Tamamlandı | 9 loading.tsx oluşturuldu (tüm dashboard sayfaları)                                 |
| F3  | ~~`not-found.tsx` 404 sayfası~~     | ✅ Tamamlandı | Özel 404 sayfası oluşturuldu                                                        |
| F4  | ~~`middleware.ts`~~                 | ✅ Tamamlandı | Cookie-based auth + auth-store sync eklendi                                         |
| F5  | ~~Frontend test altyapısı~~         | ✅ Tamamlandı | vitest.config.ts + 6 test dosyası (60 test), playwright.config.ts + e2e oluşturuldu |
| F6  | ~~`types/notification.ts`~~         | ✅ Tamamlandı | Ayrı type dosyası oluşturuldu                                                       |
| F7  | ~~`types/dashboard.ts`~~            | ✅ Tamamlandı | Ayrı type dosyası oluşturuldu                                                       |
| F8  | ~~`types/auth.ts`~~                 | ✅ Tamamlandı | Ayrı type dosyası oluşturuldu                                                       |
| F9  | PWA Service Worker                  | 🟢 Düşük      | `public/manifest.json` var ama service worker dosyası yok                           |

### 3.4 DevOps / Altyapı

| #   | Eksiklik                            | Öncelik       | Açıklama                                                                      |
| --- | ----------------------------------- | ------------- | ----------------------------------------------------------------------------- |
| O1  | ~~GitHub Actions CI/CD workflow~~   | ✅ Tamamlandı | 5 job: backend-lint, backend-test, frontend-lint, frontend-test, docker-build |
| O2  | Nginx/Traefik reverse proxy config  | 🟢 Düşük      | Prodüksiyon deploy için gerekecek                                             |
| O3  | Grafana dashboard JSON provisioning | 🟢 Düşük      | Monitoring dashboard tanımları yok                                            |
| O4  | `.env.example` dosyaları            | 🟢 Düşük      | Backend ve frontend için örnek env dosyaları kontrol edilmeli                 |

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

| Sıra  | Madde                                             | Öncelik     | Durum           |
| ----- | ------------------------------------------------- | ----------- | --------------- |
| ~~1~~ | ~~Frontend `error.tsx` boundary'leri (F1)~~       | ~~Kritik~~  | ✅ Tamamlandı   |
| ~~2~~ | ~~Frontend `loading.tsx` boundary'leri (F2)~~     | ~~Yüksek~~  | ✅ Tamamlandı   |
| ~~3~~ | ~~Frontend `not-found.tsx` sayfası (F3)~~         | ~~Yüksek~~  | ✅ Tamamlandı   |
| ~~4~~ | ~~Frontend `middleware.ts` auth koruması (F4)~~   | ~~Yüksek~~  | ✅ Tamamlandı   |
| ~~5~~ | ~~`pyproject.toml` bağımlılık temizliği (B1–B6)~~ | ~~Yüksek~~  | ✅ Tamamlandı   |
| 6     | ~~GitHub Actions CI/CD pipeline (O1, B11)~~       | ~~🟡 Orta~~ | ✅ Tamamlandı   |
| 7     | ~~Frontend test altyapısı kurulumu (F5)~~         | ~~🟡 Orta~~ | ✅ Tamamlandı   |
| ~~8~~ | ~~Frontend eksik type dosyaları (F6–F8)~~         | ~~Düşük~~   | ✅ Tamamlandı   |
| 9     | Gerçek broker adaptörleri (B8)                    | 🟡 Orta     | İhtiyaç halinde |
| 10    | Ek stratejiler (B7)                               | 🟢 Düşük    | İhtiyaç halinde |

---

## 6. SONUÇ

Proje **büyük ölçüde tamamlanmış** durumdadır:

- **Backend:** 106 uygulama dosyası, 272/272 test, 12 servis, 14 API modülü ✅
- **Frontend:** 107+ src dosyası, 14 sayfa, 60/60 vitest, 0 TypeScript hatası ✅
- **CI/CD:** GitHub Actions — 5 job (lint, test, docker-build) ✅
- **Altyapı:** Docker Compose (6 servis), PostgreSQL + TimescaleDB, Redis ✅

Kalan eksiklikler çoğunlukla **opsiyonel ek özellikler** (gerçek broker, ek stratejiler, PWA service worker, monitoring dashboards) kategorisindedir. Hiçbiri mevcut işlevselliği engellemez.

---

_Bu rapor, 2026-03-05 tarihinde gerçek kod tabanı analizi ile oluşturulmuştur._
