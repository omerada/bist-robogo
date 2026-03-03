-- Source: Doc 10 §1.2 — Veritabanı başlangıç scripti
-- TimescaleDB extension'ı etkinleştir
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Bilgi mesajı
DO $$
BEGIN
  RAISE NOTICE 'bist_robogo veritabanı başarıyla hazırlandı.';
END $$;
