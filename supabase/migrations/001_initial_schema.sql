-- SICOP Health Intelligence - Schema Inicial
-- Fecha: Marzo 2026

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Tabla principal: Licitaciones Médicas
-- ============================================
CREATE TABLE IF NOT EXISTS licitaciones_medicas (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_procedimiento  TEXT UNIQUE NOT NULL,
    descripcion           TEXT,
    institucion           TEXT,
    tipo_procedimiento    TEXT,        -- LN, LA, LD, SI, etc.
    clasificacion_unspsc  TEXT,        -- Código UNSPSC raw
    categoria             TEXT,        -- MEDICAMENTO | EQUIPAMIENTO | INSUMO | SERVICIO
    monto_colones         NUMERIC,
    adjudicatario         TEXT,
    estado                TEXT,        -- Publicado | Adjudicado | Desierto | Cancelado
    fecha_tramite         DATE,
    fecha_limite_oferta   DATE,
    raw_data              JSONB,       -- Fila completa del CSV para debugging
    created_at            TIMESTAMPTZ  DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  DEFAULT NOW()
);

-- Comentarios
COMMENT ON TABLE licitaciones_medicas IS 'Licitaciones médicas extraídas de SICOP';
COMMENT ON COLUMN licitaciones_medicas.categoria IS 'Categoría médica: MEDICAMENTO, EQUIPAMIENTO, INSUMO, SERVICIO';
COMMENT ON COLUMN licitaciones_medicas.raw_data IS 'Datos crudos del CSV para referencia';

-- ============================================
-- Tabla: Histórico de Precios por Item
-- ============================================
CREATE TABLE IF NOT EXISTS precios_historicos (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descripcion_item      TEXT NOT NULL,
    clasificacion_unspsc  TEXT,
    institucion           TEXT,
    proveedor             TEXT,
    precio_unitario       NUMERIC,
    cantidad              NUMERIC,
    unidad                TEXT,
    numero_procedimiento  TEXT REFERENCES licitaciones_medicas(numero_procedimiento) ON DELETE CASCADE,
    fecha                 DATE,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE precios_historicos IS 'Histórico de precios por ítem licitado';

-- ============================================
-- Tabla: Configuración de Alertas por Usuario
-- ============================================
CREATE TABLE IF NOT EXISTS alertas_config (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    keywords    TEXT[],          -- ["insulina", "metformina"]
    categorias  TEXT[],          -- ["MEDICAMENTO", "EQUIPAMIENTO"]
    unspsc      TEXT[],          -- ["5110", "4214"]
    canal       TEXT[],          -- ["email", "whatsapp"]
    activo      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE alertas_config IS 'Configuración de alertas personalizadas por usuario';

-- ============================================
-- Tabla: Instituciones de Salud
-- ============================================
CREATE TABLE IF NOT EXISTS instituciones_salud (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          TEXT NOT NULL,
    codigo_ccss     TEXT,
    tipo            TEXT,        -- Hospital, EBAIS, Área de Salud, etc.
    region          TEXT,
    direccion       TEXT,
    telefono        TEXT,
    email           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE instituciones_salud IS 'Catálogo de instituciones de salud de Costa Rica';

-- ============================================
-- Índices para Performance
-- ============================================

-- Licitaciones
CREATE INDEX IF NOT EXISTS idx_licitaciones_fecha
    ON licitaciones_medicas(fecha_tramite DESC);

CREATE INDEX IF NOT EXISTS idx_licitaciones_categoria
    ON licitaciones_medicas(categoria);

CREATE INDEX IF NOT EXISTS idx_licitaciones_estado
    ON licitaciones_medicas(estado);

CREATE INDEX IF NOT EXISTS idx_licitaciones_inst
    ON licitaciones_medicas(institucion);

CREATE INDEX IF NOT EXISTS idx_licitaciones_unspsc
    ON licitaciones_medicas(clasificacion_unspsc);

CREATE INDEX IF NOT EXISTS idx_licitaciones_numero
    ON licitaciones_medicas(numero_procedimiento);

-- Precios históricos
CREATE INDEX IF NOT EXISTS idx_precios_descripcion
    ON precios_historicos(descripcion_item);

CREATE INDEX IF NOT EXISTS idx_precios_fecha
    ON precios_historicos(fecha DESC);

CREATE INDEX IF NOT EXISTS idx_precios_procedimiento
    ON precios_historicos(numero_procedimiento);

-- Alertas
CREATE INDEX IF NOT EXISTS idx_alertas_user
    ON alertas_config(user_id);

-- ============================================
-- Funciones y Triggers
-- ============================================

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a licitaciones_medicas
DROP TRIGGER IF EXISTS update_licitaciones_updated_at ON licitaciones_medicas;
CREATE TRIGGER update_licitaciones_updated_at
    BEFORE UPDATE ON licitaciones_medicas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Aplicar trigger a alertas_config
DROP TRIGGER IF EXISTS update_alertas_updated_at ON alertas_config;
CREATE TRIGGER update_alertas_updated_at
    BEFORE UPDATE ON alertas_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Políticas de Row Level Security (RLS)
-- ============================================

-- Habilitar RLS
ALTER TABLE licitaciones_medicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE precios_historicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertas_config ENABLE ROW LEVEL SECURITY;

-- Política: Licitaciones son públicas para lectura
DROP POLICY IF EXISTS licitaciones_select_public ON licitaciones_medicas;
CREATE POLICY licitaciones_select_public ON licitaciones_medicas
    FOR SELECT
    USING (true);

-- Política: Solo usuarios autenticados pueden ver precios históricos
DROP POLICY IF EXISTS precios_select_auth ON precios_historicos;
CREATE POLICY precios_select_auth ON precios_historicos
    FOR SELECT
    TO authenticated
    USING (true);

-- Política: Usuarios solo ven/editan sus propias alertas
DROP POLICY IF EXISTS alertas_select_own ON alertas_config;
CREATE POLICY alertas_select_own ON alertas_config
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS alertas_insert_own ON alertas_config;
CREATE POLICY alertas_insert_own ON alertas_config
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS alertas_update_own ON alertas_config;
CREATE POLICY alertas_update_own ON alertas_config
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS alertas_delete_own ON alertas_config;
CREATE POLICY alertas_delete_own ON alertas_config
    FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- ============================================
-- Datos Iniciales
-- ============================================

-- Insertar instituciones de salud comunes de Costa Rica
INSERT INTO instituciones_salud (nombre, codigo_ccss, tipo, region) VALUES
    ('Hospital San Juan de Dios', 'HSD', 'Hospital', 'GAM'),
    ('Hospital México', 'HM', 'Hospital', 'GAM'),
    ('Hospital Calderón Guardia', 'HCG', 'Hospital', 'GAM'),
    ('Hospital Nacional de Niños', 'HNN', 'Hospital', 'GAM'),
    ('Hospital Nacional de la Mujer', 'HNM', 'Hospital', 'GAM'),
    ('Hospital Nacional Geriátrico y de Cuidados Paliativos', 'HNGCP', 'Hospital', 'GAM'),
    ('Hospital Max Peralta', 'HMP', 'Hospital', 'Pacífico Central'),
    ('Hospital San Vicente de Paúl', 'HSVP', 'Hospital', 'Pacífico Central'),
    ('Hospital Dr. Rafael Ángel Calderón Guardia', 'HCG', 'Hospital', 'Pacífico Central'),
    ('Hospital de Alajuela', 'HAL', 'Hospital', 'Central'),
    ('Hospital de Cartago', 'HCT', 'Hospital', 'Central'),
    ('Hospital de Heredia', 'HHE', 'Hospital', 'Central'),
    ('Hospital de Liberia', 'HLB', 'Hospital', 'Pacífico Norte'),
    ('Hospital de Ciudad Neily', 'HCN', 'Hospital', 'Pacífico Sur'),
    ('Hospital de Limón', 'HLM', 'Hospital', 'Caribe')
ON CONFLICT DO NOTHING;

-- ============================================
-- Vistas Útiles
-- ============================================

-- Vista de licitaciones activas (no desiertas ni canceladas)
CREATE OR REPLACE VIEW licitaciones_activas AS
SELECT *
FROM licitaciones_medicas
WHERE estado NOT IN ('Desierto', 'Cancelado', 'Desistido')
ORDER BY fecha_tramite DESC;

-- Vista de resumen por categoría
CREATE OR REPLACE VIEW resumen_por_categoria AS
SELECT
    categoria,
    COUNT(*) as total,
    COUNT(CASE WHEN estado = 'Publicado' THEN 1 END) as publicados,
    COUNT(CASE WHEN estado = 'Adjudicado' THEN 1 END) as adjudicados,
    SUM(monto_colones) as monto_total
FROM licitaciones_medicas
GROUP BY categoria
ORDER BY total DESC;

-- Vista de licitaciones por vencer (próximos 7 días)
CREATE OR REPLACE VIEW licitaciones_por_vencer AS
SELECT *
FROM licitaciones_medicas
WHERE fecha_limite_oferta BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '7 days')
    AND estado = 'Publicado'
ORDER BY fecha_limite_oferta ASC;

COMMENT ON VIEW licitaciones_por_vencer IS 'Licitaciones que vencen en los próximos 7 días';

-- Agregar al schema v2
CREATE TABLE IF NOT EXISTS licitaciones_modificaciones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inst_cartel_no  TEXT NOT NULL,   -- NO es FK obligatoria — puede llegar antes que la licitación
    cartel_no       TEXT,
    proce_type      TEXT,
    inst_nm         TEXT,
    cartel_nm       TEXT,
    openbid_dt      TIMESTAMPTZ,     -- Nueva fecha tras la modificación
    biddoc_start_dt TIMESTAMPTZ,
    mod_reason      TEXT,            -- "Fecha/hora de apertura de ofertas", etc.
    raw_data        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
    -- Sin UNIQUE — el mismo cartel puede tener N modificaciones
);

CREATE INDEX IF NOT EXISTS idx_mod_inst_cartel_no
    ON licitaciones_modificaciones(inst_cartel_no);

CREATE INDEX IF NOT EXISTS idx_mod_created_at
    ON licitaciones_modificaciones(created_at DESC);

-- RLS
ALTER TABLE licitaciones_modificaciones ENABLE ROW LEVEL SECURITY;
CREATE POLICY mod_select_public ON licitaciones_modificaciones
    FOR SELECT USING (true);
