# bist-robogo — Frontend Tasarım ve UI/UX Dokümanı

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03

---

## 1. Genel UI/UX İlkeleri

### 1.1 Tasarım Prensipleri

| Prensip                 | Açıklama                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| **Veri Yoğunluğu**      | Finans uygulamalarında bilgi yoğunluğu yüksektir; temiz tipografi ve düzenli hiyerarşi ile dengelenmeli |
| **Gerçek Zamanlılık**   | Canlı veriler görsel olarak ayırt edilebilir olmalı (yeşil/kırmızı renk, animasyon)                     |
| **Erişilebilirlik**     | WCAG 2.1 AA uyumu, klavye navigasyonu, ekran okuyucu desteği                                            |
| **Dark Mode Öncelikli** | Finans platformlarında koyu tema standarttır; göz yorulmasını azaltır                                   |
| **Responsive**          | Desktop öncelikli ama tablet ve mobil uyumu mevcut                                                      |
| **Tutarlılık**          | shadcn/ui component library ile tutarlı tasarım dili                                                    |
| **Performans**          | İlk yükleme < 2sn, sayfa geçişi < 300ms                                                                 |

### 1.2 Renk Paleti

```
Tema: Dark Mode (Varsayılan)

Background:
  --bg-primary:    #0A0E17     (Ana arka plan)
  --bg-secondary:  #111827     (Kart arka planı)
  --bg-tertiary:   #1F2937     (Input/hover)

Text:
  --text-primary:  #F9FAFB     (Ana metin)
  --text-secondary:#9CA3AF     (İkincil metin)
  --text-muted:    #6B7280     (Soluk metin)

Accent:
  --accent-blue:   #3B82F6     (Ana vurgu)
  --accent-hover:  #2563EB     (Hover)

Semantic:
  --color-profit:  #22C55E     (Yükseliş / Kâr)
  --color-loss:    #EF4444     (Düşüş / Zarar)
  --color-warning: #F59E0B     (Uyarı)
  --color-info:    #3B82F6     (Bilgi)
  --color-neutral: #6B7280     (Nötr)

Chart:
  --chart-grid:    #1F2937     (Grafik ızgarası)
  --chart-candle-up:   #22C55E
  --chart-candle-down: #EF4444
  --chart-volume:  #3B82F680   (Yarı saydam)
```

### 1.3 Tipografi

```
Font Ailesi: Inter (Google Fonts)
  - Başlık (H1):    24px, Semi-Bold (600)
  - Başlık (H2):    20px, Semi-Bold (600)
  - Başlık (H3):    16px, Medium (500)
  - Body:           14px, Regular (400)
  - Small:          12px, Regular (400)
  - Monospace:      JetBrains Mono (fiyatlar ve sayısal veriler)

Sayısal Veriler:
  - Fiyat:          JetBrains Mono, 16px, Medium
  - Değişim:        JetBrains Mono, 14px, Bold (renk kodlu)
  - Hacim:          JetBrains Mono, 12px, Regular
```

---

## 2. Ekran Planlaması

### 2.1 Ana Navigasyon Yapısı

```
┌────────────────────────────────────────────────────────────────────┐
│  [Logo] bist-robogo    Dashboard | Piyasa | Trend | Strateji |   │
│                        Backtest | Portföy | Ayarlar    [👤 User]  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│                          [Sayfa İçeriği]                           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Navigasyon Öğeleri:**

| Menü         | Rota          | İkon | Açıklama                     |
| ------------ | ------------- | ---- | ---------------------------- |
| Dashboard    | `/dashboard`  | 📊   | Ana kontrol paneli           |
| Piyasa       | `/market`     | 📈   | Canlı piyasa verileri        |
| Trend Analiz | `/trends`     | 🔍   | Trend dip ve kırılım analizi |
| Strateji     | `/strategies` | 🧠   | Strateji yönetimi            |
| Backtest     | `/backtest`   | ⏮   | Geriye dönük test            |
| Portföy      | `/portfolio`  | 💼   | Pozisyonlar ve PnL           |
| Emirler      | `/orders`     | 📋   | Emir geçmişi                 |
| Ayarlar      | `/settings`   | ⚙️   | Kullanıcı ve sistem ayarları |

---

### 2.2 Dashboard Ekranı (`/dashboard`)

Ana kontrol paneli — kullanıcının tüm kritik bilgileri tek bakışta görebildiği ekran.

```
┌────────────────────────────────────────────────────────────────────┐
│  Dashboard                                            [Yenile] ↻  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Portföy   │ │Günlük    │ │Toplam    │ │Açık      │ │Aktif    │ │
│  │Değeri    │ │PnL       │ │PnL       │ │Pozisyon  │ │Strateji │ │
│  │₺1.25M   │ │+₺12,500  │ │+₺250K   │ │8         │ │3        │ │
│  │          │ │+1.01%  ▲ │ │+25%   ▲ │ │5W / 3L   │ │         │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
│                                                                    │
│  ┌─────────────────────────────────┐ ┌────────────────────────────┐│
│  │   Portföy Equity Curve          │ │  Pozisyon Dağılımı (Pie)  ││
│  │   [TradingView Chart]           │ │                            ││
│  │   ──────────────────            │ │    THYAO  25%              ││
│  │   Zaman: 1H | 1G | 1A | 1Y | T │ │    GARAN  18%              ││
│  │                                   │ │    ASELS  15%              ││
│  └─────────────────────────────────┘ │    DİĞER  42%              ││
│                                       └────────────────────────────┘│
│                                                                    │
│  ┌─────────────────────────────────┐ ┌────────────────────────────┐│
│  │   Son Sinyaller                 │ │  Risk Durumu               ││
│  │   ┌────┬────┬─────┬─────┬────┐ │ │                            ││
│  │   │Zaman│Sembol│Sinyal│Güven│Fiy│ │ │  Günlük PnL Kullanımı:   ││
│  │   ├────┼────┼─────┼─────┼────┤ │ │  ██████████░░░ 42%         ││
│  │   │14:00│GARAN│ AL │ 82% │125│ │ │                            ││
│  │   │13:45│THYAO│ SAT│ 71% │312│ │ │  Pozisyon Yoğunluğu:       ││
│  │   │13:30│ASELS│ AL │ 68% │ 79│ │ │  ████████░░░░░ 60%         ││
│  │   └────┴────┴─────┴─────┴────┘ │ │                            ││
│  └─────────────────────────────────┘ │  Risk Skoru: 0.35 (Orta)  ││
│                                       └────────────────────────────┘│
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │   Son Emirler                                                   ││
│  │   ┌───┬──────┬───┬──────┬──────┬───────┬──────┬───────────────┐││
│  │   │ # │Sembol│Yön│ Tip  │Miktar│ Fiyat │Durum │    Zaman      │││
│  │   ├───┼──────┼───┼──────┼──────┼───────┼──────┼───────────────┤││
│  │   │ 1 │THYAO │AL │Limit │ 100  │310.00 │Gerçek│03.03 10:15   │││
│  │   │ 2 │GARAN │SAT│Market│ 200  │125.40 │Bekle.│03.03 14:05   │││
│  │   └───┴──────┴───┴──────┴──────┴───────┴──────┴───────────────┘││
│  └─────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
```

**Dashboard Bileşenleri:**

| Bileşen                   | Veri Kaynağı               | Güncelleme           |
| ------------------------- | -------------------------- | -------------------- |
| Portföy Kartları (5 adet) | `/portfolio/summary`       | WebSocket (her 5sn)  |
| Equity Curve              | `/portfolio/pnl/daily`     | WebSocket            |
| Pozisyon Dağılımı         | `/portfolio/allocation`    | WebSocket            |
| Son Sinyaller             | WebSocket `signal` channel | Gerçek zamanlı       |
| Risk Durumu               | `/risk/status`             | WebSocket (her 10sn) |
| Son Emirler               | `/orders?limit=10`         | WebSocket            |

---

### 2.3 Piyasa Ekranı (`/market`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Piyasa     Endeks: [BIST 30 ▼]    Arama: [_________________] 🔍 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  BIST 30: 10,250.45  +1.2%  │  BIST 100: 11,345.20  +0.8%       │
│  $/TL: 38.45  -0.3%        │  €/TL: 41.20  +0.1%               │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   Sembol Tablosu                             │  │
│  │  ┌──────┬───────┬──────┬───────┬─────────┬──────┬────────┐ │  │
│  │  │Sembol│ Fiyat │Değiş.│  %    │  Hacim  │ PD/DD│52H Max │ │  │
│  │  ├──────┼───────┼──────┼───────┼─────────┼──────┼────────┤ │  │
│  │  │THYAO │312.50 │+4.80 │+1.56% │ 45.2M   │ 8.45 │ 340.00│ │  │
│  │  │GARAN │125.40 │-2.10 │-1.65% │ 38.7M   │ 5.20 │ 145.00│ │  │
│  │  │ASELS │ 78.90 │+3.20 │+4.23% │ 22.1M   │12.30 │  85.00│ │  │
│  │  │EREGL │ 56.70 │+0.40 │+0.71% │ 15.8M   │ 7.80 │  62.00│ │  │
│  │  │KCHOL │145.00 │-1.50 │-1.02% │ 12.4M   │ 6.90 │ 160.00│ │  │
│  │  │ ...  │       │      │       │         │      │        │ │  │
│  │  └──────┴───────┴──────┴───────┴─────────┴──────┴────────┘ │  │
│  │  Sıralama: [Değişim % ▼]  Sayfa: [1] [2] [3] [»]          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Sembol Detay:  THYAO — Türk Hava Yolları            [★]   │  │
│  │  ┌──────────────────────────────┐ ┌─────────────────────┐   │  │
│  │  │   [TradingView Chart]        │ │  Göstergeler:       │   │  │
│  │  │                              │ │  RSI(14): 62.5      │   │  │
│  │  │                              │ │  MACD: +1.2         │   │  │
│  │  │  Periyot: 1D|5D|1A|3A|5A|M  │ │  SMA20: 308.50      │   │  │
│  │  │  Grafik: Mum|Çizgi|Alan     │ │  SMA50: 298.20      │   │  │
│  │  │  Gösterge: [Ekle +]         │ │  Bollinger: 295-320  │   │  │
│  │  │                              │ │  ADX: 28.5          │   │  │
│  │  └──────────────────────────────┘ │  ATR: 8.2           │   │  │
│  │                                    └─────────────────────┘   │  │
│  │  ┌──────────────────┐ ┌───────────────────────────────────┐  │  │
│  │  │  Emir Ver         │ │  Order Book                      │  │  │
│  │  │  🟢 AL  🔴 SAT   │ │  AL        Fiyat       SAT      │  │  │
│  │  │  Tip: [Limit ▼]  │ │  1,500    312.50      1,800     │  │  │
│  │  │  Miktar: [___]    │ │  2,200    312.40      2,500     │  │  │
│  │  │  Fiyat:  [___]    │ │  3,100    312.30      1,900     │  │  │
│  │  │  SL:     [___]    │ │  1,800    312.20      3,200     │  │  │
│  │  │  TP:     [___]    │ │  2,500    312.10      2,100     │  │  │
│  │  │  [Emir Gönder]    │ └───────────────────────────────────┘  │  │
│  │  └──────────────────┘                                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Trend Analiz Ekranı (`/trends`) — ⭐ Öne Çıkan Ekran

Bu ekran, kullanıcının **günlük, haftalık ve aylık bazda trend dibinde olan ve yeni trend başlatan hisseleri** temiz ve kullanıcı dostu bir arayüzde görmesini sağlar.

```
┌────────────────────────────────────────────────────────────────────┐
│  🔍 Trend Analiz                                                   │
│                                                                    │
│  Periyot: [● Günlük] [○ Haftalık] [○ Aylık]                      │
│  Endeks:  [BIST 30 ▼]                                             │
│  Min Skor: [━━━━━━━●━━━] 0.6                                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────┐ ┌────────────────────────────┐│
│  │  📉 DİP ADAYLARI (5)           │ │  📈 KIRILIM ADAYLARI (8)   ││
│  │  Trend dibinde olan hisseler    │ │  Yeni trend başlatan        ││
│  │                                 │ │                             ││
│  │  ┌─────────────────────────┐   │ │  ┌────────────────────────┐ ││
│  │  │ 🟡 GARAN        85%    │   │ │  │ 🟢 ASELS        78%   │ ││
│  │  │ Garanti BBVA            │   │ │  │ Aselsan                │ ││
│  │  │ ₺125.40  (-1.65%)      │   │ │  │ ₺78.90  (+4.23%)      │ ││
│  │  │                         │   │ │  │                        │ ││
│  │  │ RSI: 28.5 │ Destek:122 │   │ │  │ Kırılım: ₺77.50       │ ││
│  │  │ MACD: Bullish Cross    │   │ │  │ Hedef: ₺85.00          │ ││
│  │  │ Hacim: 1.45x ortalama  │   │ │  │ Hacim: 2.1x ortalama   │ ││
│  │  │                         │   │ │  │                        │ ││
│  │  │ [Detay] [Grafik] [AL]  │   │ │  │ [Detay] [Grafik] [AL] │ ││
│  │  └─────────────────────────┘   │ │  └────────────────────────┘ ││
│  │                                 │ │                             ││
│  │  ┌─────────────────────────┐   │ │  ┌────────────────────────┐ ││
│  │  │ 🟡 EREGL        72%    │   │ │  │ 🟢 BIMAS        75%   │ ││
│  │  │ Ereğli Demir Çelik     │   │ │  │ BİM Mağazalar          │ ││
│  │  │ ₺56.70  (+0.71%)       │   │ │  │ ₺410.00  (+2.50%)     │ ││
│  │  │                         │   │ │  │                        │ ││
│  │  │ RSI: 32.1 │ Destek: 55 │   │ │  │ Kırılım: ₺400.00      │ ││
│  │  │ BB Alt: 54.20          │   │ │  │ Hedef: ₺440.00         │ ││
│  │  │ Hacim: 1.2x ortalama   │   │ │  │ Hacim: 1.8x ortalama   │ ││
│  │  │                         │   │ │  │                        │ ││
│  │  │ [Detay] [Grafik] [AL]  │   │ │  │ [Detay] [Grafik] [AL] │ ││
│  │  └─────────────────────────┘   │ │  └────────────────────────┘ ││
│  │                                 │ │                             ││
│  │  ┌─────────────────────────┐   │ │  ┌────────────────────────┐ ││
│  │  │ 🟡 SAHOL        68%    │   │ │  │ 🟢 TUPRS        73%   │ ││
│  │  │ Sabancı Holding         │   │ │  │ Tüpraş                 │ ││
│  │  │ ₺88.20  (-0.45%)       │   │ │  │ ₺180.50  (+3.10%)     │ ││
│  │  │ ...                     │   │ │  │ ...                    │ ││
│  │  │ [Detay] [Grafik] [AL]  │   │ │  │ [Detay] [Grafik] [AL] │ ││
│  │  └─────────────────────────┘   │ │  └────────────────────────┘ ││
│  └─────────────────────────────┘ └────────────────────────────────┘│
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  📊 Trend Haritası (Isı Haritası / Treemap)                 │  │
│  │                                                               │  │
│  │  ┌────────┐┌──────┐┌────────────────┐┌───────┐┌──────────┐  │  │
│  │  │ THYAO  ││GARAN ││    ASELS       ││ EREGL ││  KCHOL   │  │  │
│  │  │ +1.56% ││-1.65%││   +4.23%      ││ +0.71%││  -1.02%  │  │  │
│  │  │ 🟢     ││ 🔴   ││   🟢          ││ 🟢    ││   🔴     │  │  │
│  │  └────────┘└──────┘└────────────────┘└───────┘└──────────┘  │  │
│  │  ┌──────┐┌────────────┐┌──────┐┌─────┐┌──────────────────┐  │  │
│  │  │SAHOL ││   BIMAS    ││TUPRS ││SISE ││     AKBNK        │  │  │
│  │  │-0.45%││  +2.50%    ││+3.10%││+1.2%││    -0.80%        │  │  │
│  │  │ 🔴   ││   🟢       ││ 🟢   ││ 🟢  ││     🔴           │  │  │
│  │  └──────┘└────────────┘└──────┘└─────┘└──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

**Trend Analiz Bileşenleri:**

| Bileşen              | Açıklama                                             |
| -------------------- | ---------------------------------------------------- |
| **Periyot Seçimi**   | Günlük/Haftalık/Aylık toggle butonları               |
| **Endeks Filtresi**  | BIST30, BIST100, Katılım Endeksi, Tümü               |
| **Skor Filtresi**    | Minimum güven skoru slider (0-1)                     |
| **Dip Adayları**     | Trend dibinde olan hisseler (kart formatında)        |
| **Kırılım Adayları** | Yeni trend başlatan hisseler (kart formatında)       |
| **Trend Haritası**   | Treemap görselleştirme (boyut: hacim, renk: değişim) |

**Kart İçeriği (Her Hisse İçin):**

- Sembol ve şirket adı
- Güncel fiyat ve değişim
- Güven skoru (progress bar ile)
- Kritik teknik göstergeler (RSI, destek/direnç, MACD, hacim oranı)
- Aksiyon butonları (Detay, Grafik, Emir Ver)

---

### 2.5 Strateji Yönetim Ekranı (`/strategies`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Strateji Yönetimi                          [+ Yeni Strateji]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌───────────────────────────────────────────────────────────────┐│
│  │                     Strateji Listesi                          ││
│  │  ┌─────────────────────────────────────────────────────────┐  ││
│  │  │  🟢 MA Crossover (BIST30)                    [Aktif]   │  ││
│  │  │  Tip: Trend Takip  │  Periyot: Günlük                  │  ││
│  │  │  Semboller: XU030 (30 hisse)                            │  ││
│  │  │  Son sinyal: THYAO AL (%82 güven) — 2 saat önce        │  ││
│  │  │  Kazanma Oranı: %62 │ Toplam PnL: +₺45,200            │  ││
│  │  │  [Düzenle] [Backtest] [Sinyaller] [Durdur]             │  ││
│  │  └─────────────────────────────────────────────────────────┘  ││
│  │                                                               ││
│  │  ┌─────────────────────────────────────────────────────────┐  ││
│  │  │  🟢 RSI Mean Reversion (Katılım)              [Aktif]  │  ││
│  │  │  Tip: Ortalamaya Dönüş  │  Periyot: 1 Saatlik          │  ││
│  │  │  Semboller: XKTUM (50 hisse)                            │  ││
│  │  │  Son sinyal: GARAN AL (%75 güven) — 30 dk önce         │  ││
│  │  │  Kazanma Oranı: %58 │ Toplam PnL: +₺28,750            │  ││
│  │  │  [Düzenle] [Backtest] [Sinyaller] [Durdur]             │  ││
│  │  └─────────────────────────────────────────────────────────┘  ││
│  │                                                               ││
│  │  ┌─────────────────────────────────────────────────────────┐  ││
│  │  │  ⚪ AI Trend Predictor (Tüm Piyasa)         [Pasif]    │  ││
│  │  │  Tip: ML Tabanlı  │  Periyot: Günlük                   │  ││
│  │  │  Model: XGBoost v2.3 │ Doğruluk: %68                   │  ││
│  │  │  [Düzenle] [Backtest] [Sinyaller] [Başlat]             │  ││
│  │  └─────────────────────────────────────────────────────────┘  ││
│  └───────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
```

---

### 2.6 Backtest Ekranı (`/backtest`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Backtest                                                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─── Konfigürasyon ────────────────────────────────────────────┐ │
│  │  Strateji: [MA Crossover ▼]                                   │ │
│  │  Semboller: [XU030 Bileşenleri ▼]  veya  [THYAO, GARAN, ...] │ │
│  │  Tarih Aralığı: [2024-01-01] — [2026-03-01]                  │ │
│  │  Başlangıç Sermayesi: [₺1,000,000]                           │ │
│  │  Komisyon: [%0.1]    Slippage: [%0.05]                        │ │
│  │                                                                │ │
│  │  Parametreler:                                                 │ │
│  │  SMA Hızlı: [20]    SMA Yavaş: [50]    RSI Eşik: [30]       │ │
│  │                                                                │ │
│  │  [🚀 Backtest Çalıştır]    [⚡ Parametre Optimizasyonu]       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─── Sonuçlar ─────────────────────────────────────────────────┐ │
│  │                                                               │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│ │
│  │  │Toplam    │ │ Sharpe   │ │   Maks   │ │ Kazanma          ││ │
│  │  │Getiri    │ │ Ratio    │ │ Drawdown │ │ Oranı            ││ │
│  │  │ +45.2%   │ │  1.85    │ │  -12.3%  │ │  62%             ││ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘│ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────────┐│ │
│  │  │  Equity Curve                                            ││ │
│  │  │  [TradingView Chart — Strateji vs Buy&Hold]              ││ │
│  │  │                                                          ││ │
│  │  │  ── Strateji  ── Buy & Hold  ── Drawdown                ││ │
│  │  └──────────────────────────────────────────────────────────┘│ │
│  │                                                               │ │
│  │  ┌─── Metrikler ──────────────────────────────────────────┐  │ │
│  │  │ CAGR: 21.5% │ Sortino: 2.10 │ Calmar: 1.75            │  │ │
│  │  │ Profit Factor: 1.82 │ Avg Trade: +₺2,150               │  │ │
│  │  │ Total Trades: 125 │ Avg Holding: 8.5 gün               │  │ │
│  │  │ Best Trade: +₺18,500 │ Worst Trade: -₺7,200            │  │ │
│  │  └────────────────────────────────────────────────────────┘  │ │
│  │                                                               │ │
│  │  ┌─── İşlem Listesi ─────────────────────────────────────┐   │ │
│  │  │ # │Sembol│ Yön │Giriş Tar│Giriş Fiy│Çıkış Fiy│  PnL │   │ │
│  │  │ 1 │THYAO │  AL │01.02.26 │ 290.00  │ 312.50  │+7.76%│   │ │
│  │  │ 2 │GARAN │  AL │15.01.26 │ 118.00  │ 125.40  │+6.27%│   │ │
│  │  │ 3 │ASELS │ SAT │20.02.26 │  82.00  │  78.90  │+3.78%│   │ │
│  │  └────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

### 2.7 Portföy Ekranı (`/portfolio`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Portföy                                                           │
├────────────────────────────────────────────────────────────────────┤
│  ┌────────────── Özet Kartları ───────────────────────────────┐   │
│  │ Toplam: ₺1.25M │ Nakit: ₺450K │ Yatırım: ₺800K           │   │
│  │ Günlük: +₺12.5K (+1.01%) │ Toplam: +₺250K (+25%)         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌────────────── Açık Pozisyonlar ────────────────────────────┐   │
│  │ ┌──────┬──────┬──────┬────────┬────────┬──────┬──────────┐│   │
│  │ │Sembol│ Yön  │Miktar│Giriş   │Güncel  │ PnL  │  PnL%   ││   │
│  │ ├──────┼──────┼──────┼────────┼────────┼──────┼──────────┤│   │
│  │ │THYAO │ Long │ 500  │ 290.00 │ 312.50 │+11.2K│  +7.76% ││   │
│  │ │GARAN │ Long │1000  │ 118.00 │ 125.40 │+7.4K │  +6.27% ││   │
│  │ │ASELS │ Long │ 800  │  72.00 │  78.90 │+5.5K │  +9.58% ││   │
│  │ │EREGL │ Long │ 600  │  58.00 │  56.70 │ -780 │  -2.24% ││   │
│  │ └──────┴──────┴──────┴────────┴────────┴──────┴──────────┘│   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌─── PnL Grafiği ──────┐  ┌─── Aylık Performans ───────────┐   │
│  │ [Çubuk Grafik]        │  │ Oca: +5.2% │ Şub: +8.1%       │   │
│  │ Günlük PnL barları    │  │ Mar: +3.5%* │                   │   │
│  └───────────────────────┘  └────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

---

### 2.8 Ayarlar Ekranı (`/settings`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Ayarlar                                                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌── Tab: [Profil] [Güvenlik] [Broker] [Risk] [Bildirimler] ──┐  │
│                                                                    │
│  Profil:                                                           │
│  ├── Ad Soyad, Email                                              │
│  ├── Tema: Dark / Light                                           │
│  └── Dil: Türkçe                                                  │
│                                                                    │
│  Güvenlik:                                                         │
│  ├── Şifre değiştir                                               │
│  ├── 2FA ayarları                                                 │
│  └── API anahtarları                                              │
│                                                                    │
│  Broker Bağlantıları:                                              │
│  ├── Broker seç ve bağlan                                         │
│  ├── Paper trading modu                                           │
│  └── Bağlantı durumu                                              │
│                                                                    │
│  Risk Kuralları:                                                   │
│  ├── Maks günlük zarar limiti                                     │
│  ├── Maks pozisyon büyüklüğü                                     │
│  ├── Maks açık pozisyon sayısı                                    │
│  ├── Stop-loss zorunluluğu                                        │
│  └── Günlük emir limiti                                           │
│                                                                    │
│  Bildirimler:                                                      │
│  ├── Kanal tercihleri (In-App, Email, Push, Telegram)             │
│  ├── Bildirim tipleri (hangi olaylar için bildirim)               │
│  └── Fiyat alarmları                                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Responsive Tasarım

### 3.1 Breakpoints

| Breakpoint | Piksel | Hedef       |
| ---------- | ------ | ----------- |
| `sm`       | 640px  | Mobil       |
| `md`       | 768px  | Tablet      |
| `lg`       | 1024px | Laptop      |
| `xl`       | 1280px | Desktop     |
| `2xl`      | 1536px | Geniş ekran |

### 3.2 Mobil Adaptasyonlar

- **Dashboard:** Kartlar tek sütun, grafik tam genişlik
- **Piyasa:** Tablo yatay scroll, sembol detay modal
- **Trend Analiz:** Dip/Kırılım tab şeklinde (yan yana değil)
- **Emir Formu:** Full-screen modal
- **Navigasyon:** Hamburger menü + bottom tab bar

---

## 4. Component Mimari

### 4.1 Dizin Yapısı (Frontend)

```
src/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth layout group
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/              # Dashboard layout group
│   │   ├── layout.tsx            # Sidebar + Header layout
│   │   ├── dashboard/page.tsx
│   │   ├── market/
│   │   │   ├── page.tsx
│   │   │   └── [symbol]/page.tsx
│   │   ├── trends/page.tsx
│   │   ├── strategies/
│   │   │   ├── page.tsx
│   │   │   ├── new/page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── backtest/
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── portfolio/page.tsx
│   │   ├── orders/page.tsx
│   │   └── settings/page.tsx
│   ├── layout.tsx
│   ├── page.tsx                  # Landing page
│   └── globals.css
│
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   ├── tabs.tsx
│   │   ├── badge.tsx
│   │   ├── progress.tsx
│   │   └── ...
│   ├── charts/                   # Grafik bileşenleri
│   │   ├── candlestick-chart.tsx
│   │   ├── equity-curve.tsx
│   │   ├── pnl-bar-chart.tsx
│   │   ├── allocation-pie.tsx
│   │   └── trend-heatmap.tsx
│   ├── market/                   # Piyasa bileşenleri
│   │   ├── symbol-table.tsx
│   │   ├── symbol-card.tsx
│   │   ├── order-book.tsx
│   │   ├── order-form.tsx
│   │   └── quote-ticker.tsx
│   ├── trends/                   # Trend analiz bileşenleri
│   │   ├── trend-filters.tsx
│   │   ├── dip-candidate-card.tsx
│   │   ├── breakout-candidate-card.tsx
│   │   └── trend-treemap.tsx
│   ├── portfolio/                # Portföy bileşenleri
│   │   ├── position-table.tsx
│   │   ├── portfolio-summary.tsx
│   │   └── pnl-summary.tsx
│   ├── strategy/                 # Strateji bileşenleri
│   │   ├── strategy-card.tsx
│   │   ├── strategy-form.tsx
│   │   └── signal-table.tsx
│   ├── dashboard/                # Dashboard bileşenleri
│   │   ├── stat-card.tsx
│   │   ├── risk-gauge.tsx
│   │   └── recent-signals.tsx
│   └── layout/                   # Layout bileşenleri
│       ├── header.tsx
│       ├── sidebar.tsx
│       ├── mobile-nav.tsx
│       └── notification-bell.tsx
│
├── hooks/                        # Custom React hooks
│   ├── use-websocket.ts
│   ├── use-market-data.ts
│   ├── use-portfolio.ts
│   └── use-auth.ts
│
├── lib/                          # Yardımcı kütüphaneler
│   ├── api/                      # API client
│   │   ├── client.ts             # Axios instance
│   │   ├── market.ts
│   │   ├── orders.ts
│   │   ├── portfolio.ts
│   │   ├── strategies.ts
│   │   ├── backtest.ts
│   │   ├── risk.ts
│   │   └── auth.ts
│   ├── ws/                       # WebSocket client
│   │   └── market-stream.ts
│   ├── utils/
│   │   ├── formatters.ts         # Para, sayı, tarih formatlama
│   │   ├── indicators.ts         # Frontend gösterge hesaplama
│   │   └── constants.ts
│   └── validators/
│       └── schemas.ts            # Zod şemaları
│
├── stores/                       # Zustand stores
│   ├── auth-store.ts
│   ├── market-store.ts
│   └── ui-store.ts
│
├── types/                        # TypeScript tip tanımları
│   ├── market.ts
│   ├── order.ts
│   ├── portfolio.ts
│   ├── strategy.ts
│   └── api.ts
│
└── styles/
    └── globals.css               # Tailwind + custom stiller
```

---

## 5. Performans Optimizasyonları (Frontend)

| Teknik                      | Uygulama                                                |
| --------------------------- | ------------------------------------------------------- |
| **React Server Components** | Statik içerikler sunucu tarafında render                |
| **Streaming SSR**           | Progressive rendering, Suspense boundary'ler            |
| **Code Splitting**          | Her sayfa lazy load; ağır chart lib'leri dynamic import |
| **Image Optimization**      | Next.js Image component, WebP/AVIF formatı              |
| **Data Prefetching**        | TanStack Query ile sayfa geçişlerinde prefetch          |
| **Virtual Scrolling**       | Büyük tablolarda (sembol listesi, işlem geçmişi)        |
| **WebSocket Throttle**      | Çok sık gelen verileri 100ms batch ile güncelleme       |
| **Memoization**             | React.memo + useMemo, ağır hesaplamalarda               |
| **Bundle Size**             | Tree-shaking, barrel export önleme, bundle analyzer     |

---

## 6. Sonuç

Bu doküman, bist-robogo platformunun frontend tasarımını, ekran planlamalarını, bileşen mimarisini ve UI/UX ilkelerini kapsamlı şekilde tanımlamaktadır. Tasarım, profesyonel finans platformları standartlarında, erişilebilir ve performanslı bir kullanıcı deneyimi sunmayı hedeflemektedir.

---

_Bu doküman, bist-robogo projesinin Ar-Ge sürecinin bir parçasıdır ve düzenli olarak güncellenecektir._
