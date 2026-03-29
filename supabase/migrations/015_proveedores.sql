-- supabase/migrations/015_proveedores.sql
-- Canonical supplier table populated from Datos Abiertos Report 9 (CE_DA_P_CONTROLLER_JSON)
-- Fields: cedula (PK), nombre, tamano (MICRO/PEQUEÑO/MEDIANO/GRANDE), provincia, canton

CREATE TABLE IF NOT EXISTS proveedores (
  cedula      TEXT PRIMARY KEY,
  nombre      TEXT NOT NULL,
  tamano      TEXT,          -- MICRO | PEQUEÑO | MEDIANO | GRANDE
  provincia   TEXT,
  canton      TEXT,
  rawdata     JSONB,
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proveedores_tamano
  ON proveedores (tamano);
CREATE INDEX IF NOT EXISTS idx_proveedores_provincia
  ON proveedores (provincia);
