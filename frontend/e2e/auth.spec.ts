import { test, expect } from "@playwright/test";

test.describe("Auth sayfaları", () => {
  test("login sayfası yüklenir", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/BIST/i);
    await expect(page.getByRole("heading")).toBeVisible();
    // E-posta ve şifre alanları mevcut
    await expect(page.getByLabel(/e-posta/i)).toBeVisible();
    await expect(page.getByLabel(/şifre/i).first()).toBeVisible();
  });

  test("register sayfası yüklenir", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByLabel(/ad soyad/i)).toBeVisible();
    await expect(page.getByLabel(/e-posta/i)).toBeVisible();
  });

  test("boş login form hatası gösterir", async ({ page }) => {
    await page.goto("/login");
    // Direkt submit butonuna tıkla
    await page.getByRole("button", { name: /giriş/i }).click();
    // Form doğrulama hataları görünmeli
    await expect(page.getByText(/e-posta gerekli/i)).toBeVisible();
  });

  test("login'den register sayfasına geçiş", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: /kayıt ol/i }).click();
    await expect(page).toHaveURL(/register/);
  });
});

test.describe("Auth koruması", () => {
  test("dashboard'a yetkilendirmesiz erişim login'e yönlendirir", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/login/);
  });
});
