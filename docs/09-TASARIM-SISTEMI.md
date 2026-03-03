# bist-robogo — Tasarım Sistemi

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Felsefe:** Net, akıcı, soft, kurumsal, sade — mükemmel kullanıcı deneyimi.

---

## 1. Tasarım Felsefesi

### 1.1 Temel İlkeler

| İlke         | Açıklama                               | Nasıl Uygulanır                                   |
| ------------ | -------------------------------------- | ------------------------------------------------- |
| **Net**      | Bilgi anında okunabilir olmalı         | Tabular-nums, yüksek kontrast, net hiyerarşi      |
| **Akıcı**    | Geçişler yumuşak, etkileşimler doğal   | 200-300ms ease-out transition, fade-in animasyon  |
| **Soft**     | Sert kenarlar yok, gözü yormayan       | Rounded köşeler, soft gölgeler, düşük doygunluk   |
| **Kurumsal** | Profesyonel ve güvenilir hissettirmeli | Tutarlı spacing, düzgün grid, nötr palet          |
| **Sade**     | Gereksiz dekorasyon yok                | Minimal ikonografi, boşluk (whitespace) kullanımı |

### 1.2 Uyulması Gereken Kurallar

1. **Dark theme varsayılan.** Light theme ikincil destek.
2. **Finansal verilerde HER ZAMAN `tabular-nums`** kullanılır — rakamlar hizalanmalıdır.
3. **Yeşil = Kâr, Kırmızı = Zarar** — evrensel finans renk kuralı.
4. **Animasyonlar 300ms'yi geçmemeli** — hızlı, profesyonel.
5. **Boşluk (whitespace) önemli** — eleman arası en az 16px (gap-4).
6. **Bileşenler tutarlı border-radius kullanmalı** — `var(--radius)`.
7. **Fontlar sadece 2 aile** — Inter (genel), JetBrains Mono (sayısal veri).
8. **İkonlar sadece Lucide React** — tutarlı çizgi kalınlığı.

---

## 2. Renk Sistemi

### 2.1 Dark Tema (Varsayılan)

| Token                    | HSL         | Hex (yaklaşık) | Kullanım Alanı                    |
| ------------------------ | ----------- | -------------- | --------------------------------- |
| `--background`           | 224 71% 4%  | `#070b18`      | Sayfa arka planı                  |
| `--foreground`           | 210 20% 98% | `#f8fafc`      | Ana metin                         |
| `--card`                 | 224 71% 6%  | `#0c1121`      | Kart arka planı                   |
| `--card-foreground`      | 210 20% 98% | `#f8fafc`      | Kart metin                        |
| `--primary`              | 217 91% 60% | `#3b82f6`      | Ana aksiyon rengi (mavi)          |
| `--primary-foreground`   | 222 47% 11% | `#0f172a`      | Primary üzeri metin               |
| `--secondary`            | 217 33% 17% | `#1e293b`      | İkincil arkaplan                  |
| `--secondary-foreground` | 210 40% 98% | `#f8fafc`      | İkincil metin                     |
| `--muted`                | 217 33% 17% | `#1e293b`      | Soluk arka plan                   |
| `--muted-foreground`     | 215 20% 65% | `#94a3b8`      | Soluk metin, etiketler            |
| `--accent`               | 217 33% 17% | `#1e293b`      | Hover/aktif arka plan             |
| `--destructive`          | 0 63% 55%   | `#d44848`      | Tehlikeli aksiyon (sil, iptal et) |
| `--border`               | 217 33% 17% | `#1e293b`      | Kenarlık çizgileri                |
| `--input`                | 217 33% 17% | `#1e293b`      | Form input kenarlık               |
| `--ring`                 | 224 76% 48% | `#2563eb`      | Focus ring                        |
| `--profit`               | 142 72% 45% | `#22c55e`      | Kâr (yeşil)                       |
| `--loss`                 | 0 84% 60%   | `#ef4444`      | Zarar (kırmızı)                   |
| `--warning`              | 38 92% 55%  | `#f59e0b`      | Uyarı (turuncu)                   |

### 2.2 Light Tema

| Token                | HSL         | Hex (yaklaşık) | Kullanım Alanı       |
| -------------------- | ----------- | -------------- | -------------------- |
| `--background`       | 0 0% 100%   | `#ffffff`      | Sayfa arka planı     |
| `--foreground`       | 224 71% 4%  | `#070b18`      | Ana metin            |
| `--card`             | 0 0% 100%   | `#ffffff`      | Kart arka planı      |
| `--primary`          | 220 70% 50% | `#2563eb`      | Ana aksiyon          |
| `--secondary`        | 220 14% 96% | `#f1f5f9`      | İkincil arkaplan     |
| `--muted-foreground` | 220 9% 46%  | `#64748b`      | Soluk metin          |
| `--border`           | 220 13% 91% | `#e2e8f0`      | Kenarlık             |
| `--profit`           | 142 72% 40% | `#16a34a`      | Kâr (koyu yeşil)     |
| `--loss`             | 0 84% 55%   | `#dc2626`      | Zarar (koyu kırmızı) |

### 2.3 Grafik Renkleri

5 tane tutarlı grafik rengi — çoklu seri gösterimlerde seçim sırası:

| Token       | HSL         | Hex       | Kullanım              |
| ----------- | ----------- | --------- | --------------------- |
| `--chart-1` | 220 70% 60% | `#3b82f6` | Ana seri (mavi)       |
| `--chart-2` | 160 60% 50% | `#10b981` | İkinci seri (yeşil)   |
| `--chart-3` | 30 80% 60%  | `#f59e0b` | Üçüncü seri (turuncu) |
| `--chart-4` | 280 65% 65% | `#a855f7` | Dördüncü seri (mor)   |
| `--chart-5` | 340 75% 60% | `#ec4899` | Beşinci seri (pembe)  |

---

## 3. Tipografi

### 3.1 Font Aileleri

| Aile | Font           | Kullanım Alanı                    |
| ---- | -------------- | --------------------------------- |
| Sans | Inter          | Genel metin, başlıklar, etiketler |
| Mono | JetBrains Mono | Fiyatlar, sayısal veriler, kod    |

### 3.2 Font Ölçekleri

| Sınıf       | Boyut | Line Height | Kullanım                                     |
| ----------- | ----- | ----------- | -------------------------------------------- |
| `text-2xs`  | 10px  | 14px        | Dipnotlar, zaman damgaları                   |
| `text-xs`   | 12px  | 16px        | Etiketler, yardımcı metin, tablo alt başlık  |
| `text-sm`   | 14px  | 20px        | Genel gövde metni, tablo hücreleri           |
| `text-base` | 16px  | 24px        | Önemli metin, form label'ları                |
| `text-lg`   | 18px  | 28px        | Kart başlıkları                              |
| `text-xl`   | 20px  | 28px        | Bölüm başlıkları                             |
| `text-2xl`  | 24px  | 32px        | Sayfa başlıkları (h2), büyük sayısal veriler |
| `text-3xl`  | 30px  | 36px        | Hero sayısal veri (portföy değeri)           |

### 3.3 Font Ağırlıkları

| Ağırlık | Sınıf           | Kullanım                                |
| ------- | --------------- | --------------------------------------- |
| 400     | `font-normal`   | Gövde metni                             |
| 500     | `font-medium`   | Etiketler, tablo başlıkları, navigasyon |
| 600     | `font-semibold` | Kart başlıkları, önemli veriler         |
| 700     | `font-bold`     | Sayfa başlıkları, hero metrikleri       |

### 3.4 Özel Kurallar

- Fiyatlar → `font-mono tabular-nums font-semibold`
- PnL değerleri → `font-mono tabular-nums font-medium` + profit/loss rengi
- Yüzde → `font-mono tabular-nums text-xs` + profit/loss rengi
- Tablo başlıkları → `text-xs font-medium text-muted-foreground uppercase tracking-wider`

---

## 4. Spacing Sistemi

### 4.1 Grid Sistemi

**4px temel grid** kullanılır. Tüm spacing değerleri 4'ün katları olmalıdır.

| Token           | Boyut | Kullanım                               |
| --------------- | ----- | -------------------------------------- |
| `gap-1` / `p-1` | 4px   | Çok küçük iç boşluk (ikon+metin arası) |
| `gap-2` / `p-2` | 8px   | Küçük iç boşluk, kompakt bileşenler    |
| `gap-3` / `p-3` | 12px  | Orta iç boşluk                         |
| `gap-4` / `p-4` | 16px  | Standart kart padding, öğe arası       |
| `gap-5` / `p-5` | 20px  | Büyük kart padding                     |
| `gap-6` / `p-6` | 24px  | Sayfa bölümleri arası                  |
| `gap-8` / `p-8` | 32px  | Büyük bölüm arası                      |

### 4.2 Kurallar

- **Kart iç boşluk**: `p-4` (16px) — CardContent standardı
- **Kart başlık boşluk**: `pb-2` (8px) — CardHeader alt boşluk
- **Sayfa bölümleri arası**: `space-y-6` (24px)
- **Grid gap'leri**: `gap-4` (16px) veya `gap-6` (24px)
- **İstatistik kartları grid**: `gap-4` (16px)
- **Sidebar padding**: `px-2 py-4` (8px yatay, 16px dikey)
- **Header yükseklik**: `h-14` (56px)
- **Sidebar genişlik**: `w-60` (240px), collapsed: `w-16` (64px)

---

## 5. Border Radius

| Token          | Boyut  | Kullanım                            |
| -------------- | ------ | ----------------------------------- |
| `rounded-sm`   | 4px    | Küçük etiketler, badge              |
| `rounded-md`   | 6px    | Input, select                       |
| `rounded-lg`   | 10px   | Kartlar, diyaloglar, ana bileşenler |
| `rounded-xl`   | 16px   | Büyük container'lar                 |
| `rounded-full` | 9999px | Avatar, durum göstergesi dairesel   |

---

## 6. Gölge (Shadow) Sistemi

Dark tema'da gölgeler minimal kullanılır (arka plan zaten koyu). Light tema'da daha belirgin.

| Sınıf         | Dark Tema | Light Tema | Kullanım          |
| ------------- | --------- | ---------- | ----------------- |
| `shadow-none` | -         | -          | Varsayılan kart   |
| `shadow-sm`   | Hafif     | Belirgin   | Hover durumları   |
| `shadow-md`   | Orta      | Belirgin   | Dropdown, popover |
| `shadow-lg`   | Orta      | Güçlü      | Dialog, sheet     |

```css
/* Dark temada kart gölgeleri yerine border kullanılır */
.dark .card-elevated {
  @apply border border-border/50;
}

/* Light temada gölge kullanılır */
.card-elevated {
  @apply shadow-sm hover:shadow-md transition-shadow;
}
```

---

## 7. Animasyon ve Geçiş Sistemi

### 7.1 Temel Geçiş

```
Tüm geçişler: transition-all duration-200 ease-out
```

| Durum                  | Süre    | Easing   | Açıklama                  |
| ---------------------- | ------- | -------- | ------------------------- |
| Hover                  | 150ms   | ease-out | Buton/link renk değişimi  |
| Focus                  | instant | -        | Focus ring anında görünür |
| Sidebar açılma/kapanma | 300ms   | ease-out | Genişlik animasyonu       |
| Sayfa geçişi           | 300ms   | ease-out | fade-in + translateY(4px) |
| Toast bildirimi        | 300ms   | ease-out | slide-in-right            |
| Fiyat flash            | 800ms   | ease-out | Arka plan renk geçişi     |
| Modal açılma           | 200ms   | ease-out | Opacity + scale           |
| Dropdown               | 150ms   | ease-out | Opacity + translateY      |

### 7.2 Fiyat Flash Animasyonu

Fiyat güncellendiğinde arka plan kısa süre yeşil/kırmızı yanar:

```tsx
// Kullanım:
<span
  className={
    priceWentUp ? "animate-price-flash-up" : "animate-price-flash-down"
  }
>
  {price}
</span>
```

### 7.3 Loading Durumları

| Durum             | Bileşen                    | Açıklama                  |
| ----------------- | -------------------------- | ------------------------- |
| Sayfa yükleniyor  | `Skeleton`                 | Tam sayfa skeleton layout |
| Tablo yükleniyor  | `Skeleton` satırları       | 5 satır skeleton          |
| Grafik yükleniyor | Tek `Skeleton`             | Chart alanı boyutunda     |
| Buton yükleniyor  | Loading spinner + disabled | İçeride küçük spinner     |
| İnfinite scroll   | Alt'ta spinner             | Sayfa sonu                |

```tsx
// Skeleton örneği:
<Skeleton className="h-4 w-32" />              // Text
<Skeleton className="h-24 rounded-lg" />        // Card
<Skeleton className="h-72 rounded-lg" />        // Chart
<Skeleton className="h-8 w-8 rounded-full" />   // Avatar
```

---

## 8. Bileşen Kataloğu

### 8.1 Button Varyantları

| Varyant       | Sınıf                            | Kullanım                          |
| ------------- | -------------------------------- | --------------------------------- |
| `default`     | Mavi arka plan, beyaz metin      | Ana aksiyon (Emir Ver, Kaydet)    |
| `secondary`   | Gri arka plan                    | İkincil aksiyon (İptal, Filtrele) |
| `destructive` | Kırmızı arka plan                | Tehlikeli (Sil, İptal Et)         |
| `outline`     | Kenarlık, transparan arka plan   | Üçüncül aksiyon                   |
| `ghost`       | Sadece metin, hover'da arka plan | Navigasyon, ikon buton            |
| `link`        | Sadece metin, altı çizili hover  | Referans bağlantıları             |

**Boyutlar:**

| Boyut     | Sınıf                 | Yükseklik | Kullanım                  |
| --------- | --------------------- | --------- | ------------------------- |
| `sm`      | `h-8 px-3 text-xs`    | 32px      | Kompakt tablo aksiyonları |
| `default` | `h-10 px-4 text-sm`   | 40px      | Genel butonlar            |
| `lg`      | `h-12 px-6 text-base` | 48px      | CTA butonları             |
| `icon`    | `h-10 w-10`           | 40x40px   | İkon butonları            |

### 8.2 Card Varyantları

```tsx
// Standart kart
<Card>
  <CardHeader>
    <CardTitle className="text-base font-medium">Başlık</CardTitle>
  </CardHeader>
  <CardContent className="p-4">
    {/* İçerik */}
  </CardContent>
</Card>

// İstatistik kartı (Dashboard)
<Card className="transition-shadow hover:shadow-md">
  <CardContent className="p-4">
    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">TOPLAM DEĞER</p>
    <p className="mt-2 text-2xl font-bold tabular-nums">₺42.150.000</p>
    <p className="mt-1 text-xs font-medium text-profit tabular-nums">+₺1.250.000 (+3,05%)</p>
  </CardContent>
</Card>

// Pozisyon kartı
<Card className="border-l-4 border-l-profit">
  {/* Yeşil sol kenarlık → kârlı pozisyon */}
</Card>
```

### 8.3 Badge Varyantları

| Varyant           | Renk       | Kullanım              |
| ----------------- | ---------- | --------------------- |
| `default`         | Mavi       | Aktif durum, bilgi    |
| `secondary`       | Gri        | Pasif, nötr           |
| `destructive`     | Kırmızı    | Hata, risk            |
| **Özel: profit**  | Yeşil bg   | Kârlı, buy sinyali    |
| **Özel: loss**    | Kırmızı bg | Zararlı, sell sinyali |
| **Özel: warning** | Turuncu bg | Dikkat, orta risk     |

```tsx
// Özel badge sınıfları
<Badge className="bg-profit/10 text-profit border-profit/20">Buy</Badge>
<Badge className="bg-loss/10 text-loss border-loss/20">Sell</Badge>
<Badge className="bg-warning/10 text-warning border-warning/20">Hold</Badge>
```

### 8.4 Tablo Stili

```tsx
<Table>
  <TableHeader>
    <TableRow className="hover:bg-transparent">
      <TableHead className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
        Sembol
      </TableHead>
      <TableHead className="text-right">Fiyat</TableHead>
      <TableHead className="text-right">Değişim</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow className="hover:bg-accent/50 cursor-pointer transition-colors">
      <TableCell className="font-medium">THYAO</TableCell>
      <TableCell className="text-right font-mono tabular-nums">
        ₺345,20
      </TableCell>
      <TableCell className="text-right font-mono tabular-nums text-profit">
        +2,15%
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
```

**Tablo Kuralları:**

- Sayısal sütunlar → `text-right font-mono tabular-nums`
- Başlıklar → `text-xs uppercase tracking-wider text-muted-foreground`
- Satır hover → `hover:bg-accent/50 transition-colors`
- Tıklanabilir satır → `cursor-pointer`

### 8.5 Form Input Stili

```tsx
// Standart input
<div className="space-y-2">
  <Label htmlFor="email" className="text-sm font-medium">
    E-posta
  </Label>
  <Input
    id="email"
    type="email"
    placeholder="ornek@email.com"
    className="h-10"
  />
  {/* Hata mesajı */}
  <p className="text-xs text-destructive">Geçerli bir e-posta giriniz</p>
</div>

// Sayısal input (fiyat, miktar)
<Input
  type="number"
  step="0.01"
  className="h-10 font-mono tabular-nums text-right"
  placeholder="0,00"
/>
```

### 8.6 Select (Dropdown) Stili

```tsx
<Select>
  <SelectTrigger className="w-40 h-10">
    <SelectValue placeholder="Seçiniz" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="market">Piyasa Emri</SelectItem>
    <SelectItem value="limit">Limit Emri</SelectItem>
    <SelectItem value="stop_loss">Stop Loss</SelectItem>
  </SelectContent>
</Select>
```

---

## 9. İkon Kullanım Kılavuzu

Sadece **Lucide React** kullanılır. Aşağıda standart ikon eşlemeleri:

| Kavram          | İkon              | Import         |
| --------------- | ----------------- | -------------- |
| Dashboard       | `LayoutDashboard` | `lucide-react` |
| Piyasa / Grafik | `LineChart`       | `lucide-react` |
| Trend           | `TrendingUp`      | `lucide-react` |
| Strateji        | `Layers`          | `lucide-react` |
| Backtest        | `FlaskConical`    | `lucide-react` |
| Portföy         | `Briefcase`       | `lucide-react` |
| Emir            | `ClipboardList`   | `lucide-react` |
| Ayarlar         | `Settings`        | `lucide-react` |
| Arama           | `Search`          | `lucide-react` |
| Bildirim        | `Bell`            | `lucide-react` |
| Kullanıcı       | `User`            | `lucide-react` |
| Çıkış           | `LogOut`          | `lucide-react` |
| Artış / Kâr     | `ArrowUpRight`    | `lucide-react` |
| Düşüş / Zarar   | `ArrowDownRight`  | `lucide-react` |
| Yenile          | `RefreshCw`       | `lucide-react` |
| Filtre          | `Filter`          | `lucide-react` |
| Sil             | `Trash2`          | `lucide-react` |
| Düzenle         | `Pencil`          | `lucide-react` |
| Kopyala         | `Copy`            | `lucide-react` |
| Dışa aktar      | `Download`        | `lucide-react` |
| Bilgi           | `Info`            | `lucide-react` |
| Uyarı           | `AlertTriangle`   | `lucide-react` |
| Başarı          | `CheckCircle`     | `lucide-react` |
| Hata            | `XCircle`         | `lucide-react` |

**İkon Boyutları:**

| Kullanım                | Sınıf       |
| ----------------------- | ----------- |
| Sidebar navigasyon      | `h-5 w-5`   |
| Buton içi ikon          | `h-4 w-4`   |
| Tablo aksiyonu          | `h-4 w-4`   |
| İstatistik kartı header | `h-4 w-4`   |
| Empty state             | `h-12 w-12` |
| Hero ikon               | `h-16 w-16` |

---

## 10. Boş Durum (Empty State) Tasarımı

Veri yokken gösterilecek mesajlar:

```tsx
// Genel empty state bileşeni
interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Icon className="h-12 w-12 text-muted-foreground/50" />
      <h3 className="mt-4 text-lg font-semibold text-foreground">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground max-w-sm">
        {description}
      </p>
      {action && (
        <Button className="mt-4" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
}
```

**Sayfa bazlı örnekler:**

| Sayfa        | İkon          | Başlık                      | Açıklama                                                  |
| ------------ | ------------- | --------------------------- | --------------------------------------------------------- |
| Portföy      | Briefcase     | Henüz pozisyonunuz yok      | İlk emrinizi vererek ticaret yapmaya başlayın.            |
| Emirler      | ClipboardList | Emir geçmişiniz boş         | Piyasa sayfasından ilk emrinizi oluşturun.                |
| Stratejiler  | Layers        | Strateji bulunamadı         | Yeni bir strateji oluşturarak otomatik ticarete başlayın. |
| Backtest     | FlaskConical  | Backtest sonucu yok         | Bir strateji seçerek geriye dönük test başlatın.          |
| Trend Analiz | TrendingUp    | Analiz sonuçları bekleniyor | Veriler hazırlandığında trend adayları burada görünecek.  |

---

## 11. Toast / Bildirim Sistemi

**Sonner** kullanılır. Sağ üstte (`top-right`) gösterilir.

| Tip    | Renk    | İkon          | Süre | Kullanım                     |
| ------ | ------- | ------------- | ---- | ---------------------------- |
| Başarı | Yeşil   | CheckCircle   | 3sn  | Emir başarılı, kayıt tamam   |
| Hata   | Kırmızı | XCircle       | 5sn  | API hatası, doğrulama hatası |
| Uyarı  | Turuncu | AlertTriangle | 4sn  | Risk limiti yaklaşıyor       |
| Bilgi  | Mavi    | Info          | 3sn  | Yeni sinyal, fiyat uyarısı   |

```tsx
import { toast } from "sonner";

// Kullanım:
toast.success("Emir başarıyla oluşturuldu", {
  description: "THYAO - 100 lot Buy",
});
toast.error("Emir oluşturulamadı", { description: "Yetersiz bakiye" });
toast.warning("Risk limiti yaklaşıyor", {
  description: "Pozisyon ağırlığı %24",
});
toast.info("Yeni sinyal", { description: "EREGL - Buy sinyali (güven: %85)" });
```

---

## 12. Responsive Tasarım Kuralları

### 12.1 Breakpoint'ler

| Breakpoint | Min Width | Kullanım            |
| ---------- | --------- | ------------------- |
| `sm`       | 640px     | Telefon (landscape) |
| `md`       | 768px     | Tablet              |
| `lg`       | 1024px    | Küçük laptop        |
| `xl`       | 1280px    | Masaüstü            |
| `2xl`      | 1536px    | Geniş ekran         |

### 12.2 Layout Davranışları

| Bileşen               | Mobile (<768px)            | Tablet (768-1024px) | Desktop (>1024px) |
| --------------------- | -------------------------- | ------------------- | ----------------- |
| Sidebar               | Gizli, hamburger ile Sheet | Collapsed (w-16)    | Expanded (w-60)   |
| İstatistik kartlar    | 2 sütun                    | 3 sütun             | 5 sütun           |
| Ana grafik + yanPanel | Dikey stack                | Dikey stack         | Yatay 2/3 + 1/3   |
| Tablo                 | Yatay scroll               | Tam genişlik        | Tam genişlik      |
| Emir formu            | Full width sheet           | Sidebar panel       | Sidebar panel     |
| Arama input           | Gizli, ikon butonu         | 200px               | 256px             |

### 12.3 Grid Sistemi Kuralları

```tsx
// Dashboard istatistik kartları:
<div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">

// Ana içerik + yan panel:
<div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
  <div className="lg:col-span-2">{/* Ana içerik */}</div>
  <div>{/* Yan panel */}</div>
</div>

// Tablo container:
<div className="overflow-x-auto scrollbar-thin">
  <Table className="min-w-[600px]">
```

---

## 13. Erişilebilirlik (Accessibility)

### 13.1 WCAG 2.1 AA Uyumluluk

| Kriter            | Standart                   | Uygulama                          |
| ----------------- | -------------------------- | --------------------------------- |
| Renk kontrastı    | 4.5:1 (metin)              | Tüm metin renkleri kontrol edildi |
| Focus göstergesi  | Görünür focus ring         | `ring-2 ring-ring ring-offset-2`  |
| Klavye navigasyon | Tüm etkileşime Enter/Space | shadcn/ui built-in                |
| Screen reader     | Anlamlı label'lar          | `aria-label`, `sr-only` span      |
| Animasyon         | `prefers-reduced-motion`   | `motion-reduce:transition-none`   |

### 13.2 Uygulanacak Kurallar

```tsx
// Her ikon butonuna sr-only label
<Button variant="ghost" size="icon">
  <Bell className="h-4 w-4" />
  <span className="sr-only">Bildirimleri göster</span>
</Button>

// Tüm form alanlarına label
<Label htmlFor="quantity">Miktar</Label>
<Input id="quantity" ... />

// Renk bağımlılığı olmaması — renk + ikon birlikte
<span className="text-profit flex items-center gap-1">
  <ArrowUpRight className="h-3 w-3" />
  +2,15%
</span>

// Finansal tablolarda scope
<TableHead scope="col">Fiyat</TableHead>
```

---

## 14. Sayfa Bazlı Tasarım Detayları

### 14.1 Login Sayfası

```
┌────────────────────────────────────────────┐
│                                            │
│          ┌──────────────────────┐          │
│          │   [B] bist-robogo    │          │
│          │                      │          │
│          │   E-posta            │          │
│          │   ┌────────────────┐ │          │
│          │   │                │ │          │
│          │   └────────────────┘ │          │
│          │   Şifre              │          │
│          │   ┌────────────────┐ │          │
│          │   │           [👁] │ │          │
│          │   └────────────────┘ │          │
│          │                      │          │
│          │   [  Giriş Yap  ]   │          │
│          │                      │          │
│          │   Hesabınız yok mu?  │          │
│          │   Kayıt olun         │          │
│          └──────────────────────┘          │
│                                            │
└────────────────────────────────────────────┘
```

- Tam ekran, ortada kart (max-w-sm)
- Arka plan: background, kart: card
- Logo üstte
- Input'lar: email, password (şifre göster toggle)
- "Giriş Yap" butonu: `w-full` primary
- Alt'ta kayıt linki
- Hata: Input altında kırmızı metin

### 14.2 Dashboard Sayfası

```
┌─── Sidebar ───┬─── Header ─────────────────────────────┐
│ [B] bist      │  🔍 Sembol ara...    🌙 🔔 [AK]       │
│               ├──────────────────────────────────────────┤
│ ■ Dashboard   │  [Portföy ] [Günlük ] [Toplam ] [Poz.] │
│   Piyasa      │  [₺42.15M] [+₺1.25M] [+₺8.5M] [12  ] │
│   Trend       │                                         │
│   Stratejiler │  ┌── Equity Curve ──────┐ ┌─ Dağılım ─┐│
│   Backtest    │  │      📈              │ │    🟢      ││
│   Portföy     │  │                      │ │  🔵  🟡   ││
│   Emirler     │  └──────────────────────┘ └───────────┘ │
│   Ayarlar     │                                         │
│               │  ┌── Son Sinyaller ─────┐ ┌─ Risk ────┐│
│               │  │ THYAO  Buy   %85     │ │  Gauge    ││
│               │  │ EREGL  Sell  %72     │ │  %65      ││
│               │  └──────────────────────┘ └───────────┘ │
│  [◀]          │                                         │
└───────────────┴─────────────────────────────────────────┘
```

### 14.3 Piyasa Detay Sayfası

```
┌─── Sidebar ───┬─── Header ─────────────────────────────┐
│               │                                         │
│               │  THYAO — Türk Hava Yolları              │
│               │  ₺345,20  +₺7,30 (+2,15%)              │
│               │                                         │
│               │  ┌── Candlestick Chart ────────────────┐│
│               │  │  [1g] [1s] [1a] [1g] [1h] [tümü]   ││
│               │  │                                     ││
│               │  │       📈🕯️                          ││
│               │  │                                     ││
│               │  └─────────────────────────────────────┘│
│               │                                         │
│               │  ┌── Teknik ──┐ ┌── Emir Formu ───────┐│
│               │  │ RSI:  58   │ │  [Buy] [Sell]        ││
│               │  │ MACD: ↑    │ │  Tip:  [Limit ▾]    ││
│               │  │ EMA20: 338 │ │  Fiyat: 345,00      ││
│               │  │ BB:   340  │ │  Lot:   100          ││
│               │  │ Vol:  1.2x │ │  SL:    335,00      ││
│               │  └────────────┘ │  TP:    360,00      ││
│               │                 │  [    Emir Ver    ]  ││
│               │                 └──────────────────────┘│
└───────────────┴─────────────────────────────────────────┘
```

---

## 15. Veri Görselleştirme Standartları

### 15.1 Grafik Türleri ve Kullanım Alanları

| Grafik Türü          | Kütüphane                | Kullanım Alanı                             |
| -------------------- | ------------------------ | ------------------------------------------ |
| Candlestick + Volume | lightweight-charts       | Fiyat grafiği (Piyasa detay)               |
| Line (Area)          | lightweight-charts       | Equity curve (Dashboard)                   |
| Bar chart            | Recharts                 | Sektör performansı, backtest karşılaştırma |
| Pie / Donut          | Recharts                 | Portföy dağılımı                           |
| Gauge                | Tremor                   | Risk skoru                                 |
| Heatmap              | Özel bileşen             | Piyasa ısı haritası                        |
| Sparkline            | lightweight-charts / SVG | Tablo içi mini grafik                      |

### 15.2 Grafik Standartları

- **Arka plan**: Şeffaf veya card arka planı — ayrı renk yok
- **Grid çizgileri**: `rgba(255,255,255,0.04)` (dark), `rgba(0,0,0,0.04)` (light)
- **Eksen metni**: `text-muted-foreground`, `text-xs`
- **Tooltip**: Card arka planı, `border`, `shadow-md`, `rounded-lg`
- **Seri renkleri**: CSS variable chart-1..5 kullanılır
- **Responsive**: Container genişliğine %100 uyum
- **Loading**: Skeleton component (grafik boyutunda)
- **Boş veri**: Empty state göster, boş grafik çizme

---

_Bu doküman, bist-robogo projesinin tüm UI bileşenlerinin görsel ve etkileşim kurallarını tanımlar. Tüm geliştirme bu standartlara göre yapılmalıdır._
