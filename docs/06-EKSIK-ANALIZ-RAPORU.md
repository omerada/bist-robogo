# bist-robogo — Eksik Analiz Raporu

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Amaç:** Mevcut dokümanların kapsamlı incelenmesi ve bir AI Agent'ın sıfır hata ile geliştirme yapabilmesi için eksik kısımların tespiti.

---

## 1. İncelenen Dokümanlar

| #   | Doküman                     | Satır Sayısı | Değerlendirme                                                   |
| --- | --------------------------- | ------------ | --------------------------------------------------------------- |
| 01  | Ar-Ge ve Gereksinim Analizi | 396          | ✅ İyi — gereksinimler, teknoloji seçimleri, riskler detaylı    |
| 02  | Sistem Mimarisi             | 767          | ✅ İyi — modüller, veri akışları, deployment mimarisi kapsanmış |
| 03  | Veri Modelleri ve API       | 1082         | ✅ İyi — 16 tablo, REST/WS API, Pydantic modelleri detaylı      |
| 04  | Frontend Tasarım ve UX      | 639          | ⚠️ Orta — wireframe'ler var ama component-level detay eksik     |
| 05  | Geliştirme Planı ve MVP     | 500          | ✅ İyi — fazlar, sprintler, test stratejisi kapsanmış           |

---

## 2. Tespit Edilen Eksiklikler

### 2.1 Backend Implementasyon Eksiklikleri (KRİTİK)

| #   | Eksik                                     | Kritiklik | Açıklama                                                           |
| --- | ----------------------------------------- | --------- | ------------------------------------------------------------------ |
| B1  | Proje dizin yapısı                        | 🔴 Kritik | Backend klasör/dosya ağacı tam belirlenmemiş                       |
| B2  | pyproject.toml / requirements.txt         | 🔴 Kritik | Paket yönetimi yapılandırması yok                                  |
| B3  | FastAPI uygulama başlatma kodu            | 🔴 Kritik | main.py, app factory pattern, middleware sırası yok                |
| B4  | Veritabanı bağlantı yönetimi              | 🔴 Kritik | SQLAlchemy engine/session factory, connection pool ayarları yok    |
| B5  | Alembic migration yapılandırması          | 🔴 Kritik | alembic.ini, env.py, ilk migration script yok                      |
| B6  | Her servis modülünün dosya yapısı         | 🔴 Kritik | Router, service, repository, schema dosyaları belirsiz             |
| B7  | Authentication middleware implementasyonu | 🔴 Kritik | JWT encode/decode, dependency injection, guard fonksiyonları yok   |
| B8  | Error handling pattern                    | 🟡 Yüksek | Custom exception sınıfları, global handler yok                     |
| B9  | Celery yapılandırması                     | 🟡 Yüksek | celeryconfig.py, task tanımları, beat schedule yok                 |
| B10 | WebSocket server implementasyonu          | 🟡 Yüksek | Bağlantı yönetimi, room/channel mekanizması yok                    |
| B11 | Broker adapter pattern                    | 🟡 Yüksek | Abstract broker sınıfı ve mock adapter yok                         |
| B12 | Loglama yapılandırması                    | 🟡 Yüksek | structlog setup, log formatı, log seviyeleri yok                   |
| B13 | Ortam değişkeni yükleme                   | 🟡 Yüksek | Pydantic Settings class, config validation yok                     |
| B14 | Seed data scriptleri                      | 🟡 Yüksek | BIST sembolleri, endeks bileşenleri, varsayılan risk kuralları yok |
| B15 | Health check endpoint detayı              | 🟢 Orta   | DB, Redis, Kafka bağlantı kontrolü detayları yok                   |
| B16 | Rate limiting implementasyonu             | 🟢 Orta   | Redis tabanlı rate limiter middleware yok                          |
| B17 | CORS yapılandırması                       | 🟢 Orta   | İzin verilen origin'ler, header'lar belirsiz                       |

### 2.2 Frontend Implementasyon Eksiklikleri (KRİTİK)

| #   | Eksik                                      | Kritiklik | Açıklama                                                          |
| --- | ------------------------------------------ | --------- | ----------------------------------------------------------------- |
| F1  | next.config.ts tam içerik                  | 🔴 Kritik | Image domains, redirects, env ayarları yok                        |
| F2  | tailwind.config.ts tam içerik              | 🔴 Kritik | Custom renk, font, spacing, animasyon yapılandırması yok          |
| F3  | shadcn/ui kurulum ve konfigürasyonu        | 🔴 Kritik | components.json, hangi bileşenlerin ekleneceği belirsiz           |
| F4  | API client implementasyonu                 | 🔴 Kritik | Axios instance, interceptors, error handling, token refresh yok   |
| F5  | Auth akışı implementasyonu                 | 🔴 Kritik | next-auth config, session provider, middleware, guard yok         |
| F6  | WebSocket hook implementasyonu             | 🔴 Kritik | Bağlantı yönetimi, reconnect, heartbeat lojiği yok                |
| F7  | Her sayfa bileşeninin tam component spec'i | 🔴 Kritik | Props, state, data fetching, loading/error states eksik           |
| F8  | Zustand store yapıları                     | 🟡 Yüksek | Store tanımları, action'lar, selector'lar belirsiz                |
| F9  | TanStack Query hook'ları                   | 🟡 Yüksek | Query key stratejisi, stale time, prefetch yapılandırması yok     |
| F10 | Form validation şemaları                   | 🟡 Yüksek | Zod şemaları, react-hook-form entegrasyonu detayı yok             |
| F11 | TradingView chart entegrasyonu             | 🟡 Yüksek | Chart oluşturma, serie ekleme, gösterge overlay kodu yok          |
| F12 | Loading/skeleton states                    | 🟡 Yüksek | Her sayfa için loading state tanımı yok                           |
| F13 | Error boundary'ler                         | 🟡 Yüksek | Global ve sayfa bazlı error boundary yok                          |
| F14 | Dark/light tema implementasyonu            | 🟡 Yüksek | CSS variable switch, tema provider mekanizması yok                |
| F15 | Responsive davranış detayları              | 🟢 Orta   | Her bileşenin breakpoint davranışı belirsiz                       |
| F16 | Animasyon ve transition tanımları          | 🟢 Orta   | Framer Motion / CSS transition spec yok                           |
| F17 | SEO & meta tag yönetimi                    | 🟢 Orta   | Metadata API kullanımı belirsiz                                   |
| F18 | Internationalization altyapısı             | 🟢 Orta   | next-intl veya benzeri i18n yapısı yok (ancak şimdilik sadece TR) |

### 2.3 Tasarım Sistemi Eksiklikleri

| #   | Eksik                               | Kritiklik | Açıklama                                                              |
| --- | ----------------------------------- | --------- | --------------------------------------------------------------------- |
| D1  | Token sistemi (CSS variables)       | 🔴 Kritik | Tam renk token'ları (background, foreground, border, ring, chart) yok |
| D2  | Spacing scale                       | 🟡 Yüksek | Tutarlı boşluk değerleri (4px grid sistemi) tanımlı değil             |
| D3  | Component variant tanımları         | 🟡 Yüksek | Button, Card, Badge varyantları ve kullanım kılavuzu yok              |
| D4  | Animasyon / Transition spec         | 🟡 Yüksek | Timing, easing, hangi elementlerde kullanılacağı yok                  |
| D5  | Erişilebilirlik (a11y) kuralları    | 🟡 Yüksek | WCAG 2.1 AA uyum detayları, focus, aria yok                           |
| D6  | İkon kullanım kılavuzu              | 🟢 Orta   | Lucide icon adları, boyutları, kullanım yerleri yok                   |
| D7  | Boş durum (empty state) tasarımları | 🟢 Orta   | Veri yokken gösterilecek ekranlar belirsiz                            |
| D8  | Toast/notification tasarımı         | 🟢 Orta   | Bildirim stillleri, süreler, pozisyon belirsiz                        |

### 2.4 DevOps ve Altyapı Eksiklikleri

| #   | Eksik                               | Kritiklik | Açıklama                                                       |
| --- | ----------------------------------- | --------- | -------------------------------------------------------------- |
| O1  | docker-compose.yml tam içerik       | 🔴 Kritik | Servis tanımları, volume'lar, network'ler, healthcheck'ler yok |
| O2  | Dockerfile'lar (backend + frontend) | 🔴 Kritik | Multi-stage build, optimize image yok                          |
| O3  | GitHub Actions workflow YAML        | 🟡 Yüksek | CI/CD pipeline dosyaları yok                                   |
| O4  | Nginx/Traefik yapılandırması        | 🟢 Orta   | Reverse proxy config yok                                       |
| O5  | Grafana dashboard JSON              | 🟢 Orta   | Provisioned dashboard tanımları yok                            |

### 2.5 Test Eksiklikleri

| #   | Eksik                      | Kritiklik | Açıklama                                                |
| --- | -------------------------- | --------- | ------------------------------------------------------- |
| T1  | conftest.py yapılandırması | 🟡 Yüksek | Test fixture'ları, test DB setup, factory tanımları yok |
| T2  | Test dosya yapısı          | 🟡 Yüksek | Hangi testlerin hangi dosyalarda olacağı belirsiz       |
| T3  | vitest.config.ts           | 🟢 Orta   | Frontend test yapılandırması yok                        |
| T4  | Playwright config          | 🟢 Orta   | E2E test yapılandırması yok                             |

---

## 3. Oluşturulması Gereken Yeni Dokümanlar

### 3.1 Doküman 07: Backend Implementasyon Kılavuzu

**Amaç:** AI Agent'ın backend'i dosya dosya, satır satır geliştirebilmesi.

**İçerik:**

- Tam dizin ağacı (her dosya ve klasör)
- pyproject.toml / Poetry yapılandırması (tam içerik)
- FastAPI uygulama fabrikası (app factory)
- Middleware zinciri ve sırası
- Veritabanı bağlantı yönetimi (engine, session, base model)
- Alembic yapılandırması ve ilk migration
- Her servis modülünün implementasyon şablonu (router → service → repository)
- Authentication/Authorization implementasyonu
- Error handling sistemi
- Celery yapılandırması ve görevler
- WebSocket sunucu implementasyonu
- Broker adapter pattern
- Loglama ve monitoring
- Seed data scriptleri
- Health check endpoint'leri
- Ortam değişkeni yönetimi (Settings class)

### 3.2 Doküman 08: Frontend Implementasyon Kılavuzu

**Amaç:** AI Agent'ın frontend'i component component, sayfa sayfa geliştirebilmesi.

**İçerik:**

- next.config.ts tam yapılandırma
- tailwind.config.ts tam yapılandırma (token'larla)
- shadcn/ui kurulum ve component listesi
- globals.css tam içerik (CSS variables, base stiller)
- API client (axios instance, interceptors, error handler)
- Auth implementasyonu (middleware, provider, guard)
- WebSocket hook (bağlantı, reconnect, heartbeat)
- Her sayfa için: component tree, props, state, data fetching, loading/error state
- Zustand store tanımları
- TanStack Query hook'ları ve cache stratejisi
- TradingView chart entegrasyonu
- Form validation (Zod + react-hook-form)
- Responsive pattern'ler
- Accessibility kuralları

### 3.3 Doküman 09: UI/UX Tasarım Sistemi

**Amaç:** Tutarlı, temiz, kurumsal ve akıcı bir arayüz için kapsamlı tasarım sistemi.

**İçerik:**

- Tasarım felsefesi ve ilkeleri (net, akıcı, soft, kurumsal, sade)
- Tam CSS variable token sistemi (dark + light tema)
- Renk paleti (semantic renk isimleri)
- Tipografi ölçeği (font-size, line-height, letter-spacing)
- Spacing sistemi (4px grid)
- Border radius, shadow, blur değerleri
- Component variant kataloğu (Button, Card, Badge, Input, Table, vb.)
- Animasyon ve transition spec'leri
- İkon kılavuzu
- Boş durum (empty state) tasarımları
- Toast/notification stil kılavuzu
- Erişilebilirlik kuralları (WCAG 2.1 AA)
- Renk kontrast gereksinimleri

### 3.4 Doküman 10: Adım Adım Geliştirme Rehberi

**Amaç:** AI Agent'ın hangi sırada, hangi dosyayı oluşturacağını bilen bir yol haritası.

**İçerik:**

- Faz 0: Komut komut proje kurulumu
- Docker Compose dosyası (tam YAML)
- Dockerfile'lar (backend + frontend)
- GitHub Actions CI/CD pipeline
- Her sprint için adım adım görev sırası
- Her görev için: hangi dosyalar oluşturulacak, bağımlılıklar, doğrulama kriterleri
- Sıralı task listesi (Task 1 → Task 2 → ... → Task N)

---

## 4. Mevcut Dokümanlardaki Düzeltme ve İyileştirmeler

### 4.1 Doküman 01 İyileştirmeleri

- ✅ Genel olarak yeterli, büyük eksik yok
- 📌 `yfinance` gecikmeli veri sağladığı açıkça belirtilmeli
- 📌 Paper trading ve gerçek trading ayrımı daha net yapılmalı

### 4.2 Doküman 02 İyileştirmeleri

- ✅ Mimari kapsamlı
- 📌 Docker Compose servislerin environment değişkenleri eklenmeli
- 📌 Servisler arası iletişim pattern'leri (sync vs async) daha net tanımlanmalı

### 4.3 Doküman 03 İyileştirmeleri

- ✅ Veri modelleri ve API çok detaylı
- 📌 Pagination response metadata standardize edilmeli
- 📌 API versioning stratejisi eklenmeli

### 4.4 Doküman 04 İyileştirmeleri

- ⚠️ Wireframe'ler ASCII tabanlı — yeterli ama tasarım token'ları eksik
- 📌 Her component'in exact props + state tanımı eklenmeli
- 📌 Animasyon ve transition bilgisi eklenmeli
- 📌 Renk token'ları shadcn/ui formatına dönüştürülmeli

### 4.5 Doküman 05 İyileştirmeleri

- ✅ Geliştirme planı genel olarak yeterli
- 📌 Her görevin "Definition of Done" kriterleri eklenmeli
- 📌 Adım adım komut bazlı rehber ayrı doküman olmalı

---

## 5. Öncelik Sıralaması

| Öncelik | Doküman                               | Gerekçe                                     |
| ------- | ------------------------------------- | ------------------------------------------- |
| 1       | Backend Implementasyon Kılavuzu (07)  | Tüm servisler, DB, auth temeldir            |
| 2       | Frontend Implementasyon Kılavuzu (08) | UI geliştirme backend'e paralel yapılabilir |
| 3       | UI/UX Tasarım Sistemi (09)            | Frontend geliştirmede tutarlılık sağlar     |
| 4       | Adım Adım Geliştirme Rehberi (10)     | Sıralı geliştirme için kritik               |

---

_Bu analiz, bist-robogo projesinin mevcut dokümanlarının kapsamlı incelenmesinden üretilmiştir._
