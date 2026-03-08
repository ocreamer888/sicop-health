-- Análisis completo de campos disponibles en raw_data de SICOP API
-- Ejecutar en Supabase SQL Editor

-- 1. Todos los keys únicos que existen en cualquier raw_data
SELECT DISTINCT jsonb_object_keys(raw_data) as campo_disponible
FROM licitaciones_medicas
ORDER BY campo_disponible;

-- 2. Conteo de cuántos registros tienen cada campo (para ver qué tan completo está)
SELECT 
    jsonb_object_keys(raw_data) as campo,
    COUNT(*) as registros_con_campo
FROM licitaciones_medicas
GROUP BY jsonb_object_keys(raw_data)
ORDER BY registros_con_campo DESC;

-- 3. Ver un registro completo de ejemplo (última licitación pública)
SELECT 
    instcartelno,
    cartelnm,
    raw_data
FROM licitaciones_medicas
WHERE typekey = 'RPT_PUB'
ORDER BY biddoc_start_dt DESC NULLS LAST
LIMIT 1;

-- 4. Ver qué campos tiene una licitación adjudicada específicamente
SELECT 
    jsonb_object_keys(raw_data) as campo_adjudicada
FROM licitaciones_medicas
WHERE typekey = 'RPT_ADJ'
GROUP BY jsonb_object_keys(raw_data)
ORDER BY campo_adjudicada;

-- 5. Buscar campos que podrían tener info de "electronic contests status"
-- Como bid status, electronic bid info, etc.
SELECT 
    instcartelno,
    cartelnm,
    raw_data->>'elecBidYn' as elec_bid_yn,
    raw_data->>'bidStatCd' as bid_status_code,
    raw_data->>'bidStatNm' as bid_status_name,
    raw_data->>'bidCnt' as bid_count,
    raw_data->>'joinBidCnt' as join_bid_count,
    raw_data->>'elecBidCloseYn' as elec_bid_closed,
    raw_data->>'bidOpenStatCd' as bid_open_status,
    raw_data->>'bidOpenStatNm' as bid_open_status_name
FROM licitaciones_medicas
WHERE raw_data ?| array['elecBidYn', 'bidStatCd', 'bidCnt', 'elecBidCloseYn', 'bidOpenStatCd']
LIMIT 10;
