SICOP Health Intelligence
Plan de Desarrollo y Arquitectura
Técnica
Proyecto: Plataforma SaaS B2B para monitoreo de licitaciones del sector salud en Costa
Rica
Fecha: Marzo 2026
Resumen Ejecutivo
SICOP Health Intelligence es una plataforma que automatiza el monitoreo de licitaciones
públicas del sector salud en Costa Rica, extrayendo datos del Sistema Integrado de Compras
Públicas (SICOP) y proporcionando inteligencia de mercado a proveedores. El sistema
detecta nuevas oportunidades de negocio, analiza tendencias de precios históricos, y entrega
alertas en tiempo real vía WhatsApp/email.
Diferenciadores clave:
• Especialización vertical en sector salud (medicamentos, equipamiento médico,
insumos)
• Sistema de alertas configurables por categoría de producto
• Análisis de precios históricos por ítem y proveedor
• Base legal sólida: datos públicos por ley, sin scraping agresivo
Contexto Legal y Técnico
Marco Regulatorio
El proyecto se basa en el acceso a datos públicos garantizados por la legislación costarricense:
• Ley 8292 de Control Interno — obliga a instituciones públicas a usar SICOP
• Ley 9097 de Transparencia — garantiza acceso ciudadano a información pública
• Directriz Presidencial N° 025-H — establece SICOP como sistema único de
compras
• Compromiso Open Contracting Partnership — SICOP publica datos abiertos
desde 2019
Fuente de Datos Oficial
SICOP provee un módulo de Datos Abiertos en sicop.go.cr/moduloPcont que permite
descargar:
• Catálogo de bienes y servicios (clasificación UNSPSC)
• Concursos y licitaciones (CSV/JSON/Excel)
• Ofertas y adjudicaciones
• Datos de proveedores
Sin autenticación requerida. Sin limitaciones de rate. Sin términos de uso
restrictivos.
Clasificación UNSPSC del Sector Salud
El sistema UNSPSC (United Nations Standard Products and Services Code) clasifica
productos médicos en los siguientes rangos:
51000000 42000000 41000000 53000000 85000000 Código Categoría
Drogas y Productos Farmacéuticos
Equipos y Accesorios Médicos/Quirúrgicos
Instrumentos de Laboratorio y Diagnóstico
Insumos de Enfermería y Limpieza Hospitalaria
Servicios de Salud
Table 1: Códigos UNSPSC relevantes para el sector salud
Plan de Desarrollo
Infrastructure + ETL Core
Objetivo: Pipeline de extracción funcional que popula la base de datos diariamente.
Tareas
1. Setup Supabase project
• Crear proyecto en Supabase
• Ejecutar migrations del schema completo
• Configurar Row Level Security (RLS) policies
• Setup environment variables
2. Python ETL Script (local first)
• Script fetch_sicop.py — GET request a endpoint de Datos Abiertos
• Parseo de CSV con pandas
• Filtro por códigos UNSPSC médicos (42*, 51*, 53*, 85*, 41*)
• Keyword matching en descripción (medicamento, fármaco, equipo médico,
etc.)
• Conexión a Supabase con supabase-py
• Upsert con constraint en numero_procedimiento
3. Migrar ETL a Supabase Edge Function
• Crear supabase/functions/sicop-poller/index.ts
• Port lógica de Python a TypeScript/Deno
• Deploy edge function
• Setup pg_cron para ejecutar cada hora
4. Testing del pipeline
• Validar que detecta licitaciones nuevas correctamente
• Validar que no duplica registros existentes
• Validar filtrado por UNSPSC
• Log de ejecuciones y errores
Entregable: Base de datos poblada con histórico de licitaciones médicas, actualizándose
automáticamente cada hora.
Frontend Core + Autenticación
Objetivo: Dashboard funcional con autenticación y visualización de datos.
Tareas
1. Setup Next.js project
• Inicializar con App Router
• Configurar Tailwind CSS + shadcn/ui
• Setup Supabase client (Auth + Database)
• Configurar environment variables
2. Autenticación con Supabase Auth
• Login/Signup con email + password
• OAuth con Google (opcional)
• Protected routes con middleware
• Session management
3. Dashboard principal (/dashboard)
• Métricas clave: total licitaciones activas, nuevas hoy, monto total
• Gráfico de licitaciones por institución (CCSS, MINSA, INS)
• Gráfico de licitaciones por categoría (medicamentos, equipamiento, insumos)
• Timeline de últimas 10 licitaciones
4. Tabla de licitaciones (/licitaciones)
• Server Component con Server Actions para data fetching
• Tabla con columnas: número, institución, descripción, monto, estado, fecha
• Paginación server-side (50 items por página)
• Filtros: institución, categoría, rango de fechas, estado
• Búsqueda full-text en descripción
• Ordenamiento por fecha, monto, institución
5. Detalle de licitación (/licitacion/[id])
• Información completa del concurso
• Link al cartel original en SICOP
• Datos del adjudicatario (si existe)
• Historial de cambios de estado
Entregable: Web app funcional con auth y visualización completa de licitaciones.
Sistema de Alertas
Objetivo: Usuarios pueden configurar alertas personalizadas y recibir notificaciones.
Tareas
1. Configuración de alertas (/alertas)
• Formulario para crear nueva alerta
• Campos: nombre, keywords, códigos UNSPSC, instituciones, rango de montos
• Selección de canales (email, WhatsApp)
• Lista de alertas activas con toggle on/off
• Editar/eliminar alertas existentes
2. Motor de matching de alertas
• Función matchAlertas() que evalúa cada licitación nueva contra config de
usuarios
• Lógica AND/OR para múltiples criterios
• Deduplicación: no notificar dos veces la misma licitación
3. Integración de Resend (email)
• Setup Resend API key
• Template de email con datos de licitación
• Link directo a detalle en la plataforma
• Botón de "Ver en SICOP"
4. Integración de WhatsApp Business API
• Setup cuenta de WhatsApp Business
• Template de mensaje aprobado por Meta
• Envío vía API oficial o proveedor (Twilio, Vonage)
• Validación de número de teléfono del usuario
5. Testing del flujo completo
• Usuario crea alerta con keyword "insulina"
• ETL detecta nueva licitación de CCSS con "insulina glargina"
• Sistema matchea y envía email + WhatsApp
• Usuario recibe notificación en <5 minutos
Entregable: Sistema de alertas funcional end-to-end con notificaciones multi-canal.
Vista de precios históricos (/precios)
• Buscador de productos (autocomplete desde tabla precios_historicos)
• Gráfico de evolución de precio unitario en el tiempo
• Tabla con todas las adjudicaciones del producto
• Comparación de precios entre instituciones
• Identificación de outliers (precios anormalmente altos/bajos)
ETL de precios desde carteles (Playwright)
• Script que navega al detalle de licitación adjudicada
• Extrae tabla de ítems adjudicados con precios
• Parseo de PDF si los precios están en documento adjunto
• Populate tabla precios_historicos
Análisis de Precios + Proveedores
Objetivo: Inteligencia de mercado con históricos de precios y análisis competitivo.
Tareas
1. 2. 3. Análisis de proveedores (/proveedores)
• Ranking de proveedores por categoría
• Métricas: total contratos, monto adjudicado, win rate
• Gráfico de evolución de contratos por trimestre
• Productos principales por proveedor
• Instituciones donde más gana
4. Dashboard de competidores
• Usuario puede marcar proveedores como "competidores a seguir"
• Vista comparativa de performance: tu empresa vs competidores
• Alertas cuando competidor gana licitación en tu categoría
5. Exportación de datos
• Botón "Exportar a Excel" en tablas principales
• Generación de reporte PDF con gráficos
• API endpoint para integraciones externas (tier Enterprise)
Entregable: Plataforma completa con análisis avanzado de mercado y competidores.
Consideraciones Técnicas Clave
Polling Inteligente vs "Tiempo Real"
SICOP no tiene API de eventos ni webhooks. El sistema usa polling con diff detection:
• Frecuencia: cada 1-2 horas (suficiente dado que plazos legales son de días)
• Comparación: nuevos numero_procedimiento vs set existente en DB
• Detección de cambios de estado: comparar estado actual vs anterior
• Latencia percibida: usuario recibe notificación <2 horas desde publicación oficial
Para el contexto de licitaciones gubernamentales, esto es indistinguible de
"tiempo real".
Rate Limiting y Respeto al Servidor
Aunque SICOP no tiene términos explícitos de rate limiting:
• Implementar delay de 2-3 segundos entre requests si hay paginación
• Usar User-Agent identificable con contacto: "SICOPHealthBot/1.0
(contact@tudominio.com)"
• Cachear catálogo de productos (solo actualizar semanalmente)
• No hacer más de 1 request por minuto en horario pico (8am-5pm)
Seguridad y Privacidad
• Row Level Security (RLS) en Supabase: usuarios solo ven sus alertas
• API keys en Supabase Vault (no en código)
• Sanitización de inputs en búsquedas (prevenir SQL injection)
• Rate limiting en API routes de Next.js (prevenir abuse)
• Logs de acceso a datos sensibles (compliance)
Riesgos y Mitigaciones
Riesgo 1: SICOP cambia estructura de datos
Probabilidad: Media — están en proceso "Reimagine Apply"
Impacto: Alto — rompe el ETL completamente
Mitigación:
• Monitoring automático: si parsing falla >3 veces, alerta a devs
• Versionado del schema esperado de SICOP en código
• Contract testing: validar estructura de CSV en cada ejecución
• Relación con equipo técnico de SICOP (solicitar aviso de cambios)
Riesgo 2: Competidor aparece primero
Probabilidad: Baja — no existe actualmente
Impacto: Medio — reduce market share potencial
Mitigación:
• Speed to market: MVP en 4 semanas, no 6 meses
• Especialización vertical (solo salud) vs genérico
• Network effects: mientras más usuarios, mejores datos de precios
• Integración con sistemas internos de clientes (APIs custom)
Riesgo 3: Volumen de datos crece
exponencialmente
Probabilidad: Media — CCSS hace 10,000+ licitaciones/año
Impacto: Medio — costos de DB y procesamiento suben
Mitigación:
• Archivado de licitaciones >5 años a cold storage
• Agregación pre-computada de métricas (no calcular en runtime)
• Paginación eficiente con cursor-based en vez de offset
• Upgrade a Supabase Pro o Enterprise según crecimiento
Riesgo 4: Cambios legales en publicación de datos
Probabilidad: Muy baja — tendencia global es hacia más transparencia
Impacto: Crítico — elimina la fuente de datos
Mitigación:
• Diversificar fuentes: Observatorio UCR, CompraNet (si expanden a México)
• Pivote a herramienta de gestión interna de licitaciones (sin scraping)
• Relaciones institucionales con Ministerio de Hacienda
Roadmap Post-MVP
Features Avanzados
1. AI-Powered Insights
• LLM resume carteles de 50 páginas en bullet points
• Detección de requisitos técnicos clave con NLP
• Predicción de probabilidad de ganar según histórico
2. Colaboración en Equipo
• Múltiples usuarios por cuenta (tier Enterprise)
• Asignación de licitaciones a responsables
• Comentarios internos y notas privadas
• Workflow de aprobación de ofertas
3. Mobile App (React Native)
• Push notifications nativas
• Vista rápida de licitaciones en camino
• Compartir licitación a WhatsApp/email directamente
4. Integración con ERPs
• Sincronización bidireccional con SAP, Oracle, Dynamics
• Auto-población de formularios de oferta desde inventario
• Cálculo de costeo basado en precios históricos de SICOP
5. Expansión Regional
• Guatemala: Guatecompras (guatecompras.gt)
• Panamá: PanamaCompra (panamacompra.gob.pa)
• Misma arquitectura, diferentes scrapers por país
Métricas de Éxito
KPIs Técnicos
• Uptime del ETL: >99% (máximo 7 horas downtime/mes)
• Latencia de detección: <2 horas desde publicación en SICOP
• Precisión de matching: >95% (alertas relevantes vs false positives)
• Page load time: <2 segundos (dashboard principal)
Conclusión
SICOP Health Intelligence capitaliza una oportunidad clara en el mercado costarricense: la
necesidad de proveedores del sector salud de monitorear eficientemente las licitaciones
públicas. La combinación de especialización vertical, alertas configurables, y análisis de
precios históricos crea una propuesta de valor diferenciada frente a herramientas genéricas.
La arquitectura técnica basada en datos públicos garantiza sostenibilidad legal, mientras que
el stack moderno permite desarrollo rápido y escalabilidad. El plan para MVP es agresivo
pero factible, priorizando core features que generan valor inmediato.
El proyecto es estratégicamente valioso, con potencial de expansión regional y múltiples
vectores de monetización. La clave del éxito estará en velocidad de ejecución y calidad de la
experiencia de usuario en configuración de alertas.