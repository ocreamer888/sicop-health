# services/etl/classifier.py
"""
Clasificador de licitaciones médicas SICOP v3.8
ULTRAFIX — Root causes forenses resueltos:

1. _normalizar: \u00a0 (non-breaking space) era eliminado por encode('ascii','ignore')
   en lugar de convertido a espacio — fusionaba palabras y rompía TODOS los matches.
   Fix: reemplazar familia completa de Unicode spaces ANTES del encode.

2. Curly quotes y caracteres ornamentales de sistemas legacy CR eliminados pre-normalización.

3. r"activos?\s+(de\s+)?uso\s+medic" movido a PATRONES_REGEX — ahora usa \s+ que
   matchea cualquier Unicode space sobreviviente.

4. Upsert bug documentado — ver uploader.py (DO UPDATE SET requerido).
"""

import re
import unicodedata

# Mapa completo de Unicode spaces y caracteres problemáticos de sistemas legacy
_UNICODE_SANITIZE = str.maketrans({
    '\u00a0': ' ',   # non-breaking space — ROOT CAUSE #1
    '\u200b': '',    # zero-width space
    '\u200c': '',    # zero-width non-joiner
    '\u200d': '',    # zero-width joiner
    '\u2060': '',    # word joiner
    '\ufeff': '',    # BOM
    '\u00ad': '',    # soft hyphen
    '\u2019': "'",   # right single quotation mark
    '\u2018': "'",   # left single quotation mark
    '\u201c': '"',   # left double quotation mark
    '\u201d': '"',   # right double quotation mark
    '\u2013': '-',   # en dash
    '\u2014': '-',   # em dash
    '\u2026': '...',  # ellipsis
})


def _normalizar(texto: str) -> str:
    # 1. Sanitizar Unicode problemático ANTES de cualquier transformación
    texto = texto.translate(_UNICODE_SANITIZE)
    # 2. NFD + strip diacríticos
    sin_tildes = (
        unicodedata.normalize("NFD", texto.lower())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    # 3. Colapsar whitespace múltiple (tabs, newlines, dobles espacios)
    return re.sub(r'\s+', ' ', sin_tildes).strip()


# ─────────────────────────────────────────────
# INSTITUCIONES DE SALUD CONOCIDAS
# ─────────────────────────────────────────────

INSTITUCIONES_SALUD = [
    "caja costarricense", "ccss", "ministerio de salud",
    "hospital", "clinica", "ebais", "cendeiss",
    "inciensa",
    "instituto costarricense de investigacion",
    "farmacia nacional", "ins ",
]

INSTITUCIONES_SALUD_NORM = [_normalizar(i) for i in INSTITUCIONES_SALUD]


def _es_institucion_salud(inst_nm: str) -> bool:
    inst_norm = _normalizar(inst_nm or "")
    return any(kw in inst_norm for kw in INSTITUCIONES_SALUD_NORM)


# ─────────────────────────────────────────────
# KEYWORDS DIRECTOS
# ─────────────────────────────────────────────

KEYWORDS_DIRECTOS_RAW = [
    # Formas farmacéuticas
    "solucion inyectable", "suspension oral", "comprimido recubierto",
    "tableta recubierta", "supositorio", "frasco ampolla",
    "parche transdermico", "polvo para reconstituir",
    "colirio", "unguento", "crema dermatologica",
    # Unidades de medida
    "mg/ml", "mcg/ml", "mg/kg", "ui/ml", "meq/ml",
    # Equipamiento mayor
    "tomografo", "resonancia magnetica", "ecografo",
    "ventilador mecanico", "desfibrilador", "oximetro",
    "endoscopio", "laparoscopio", "broncoscopio",
    "facoemulsificador", "electrocardiografo",
    "electroencefalografo", "electroencefalograf",
    "ecmo", "autoclave", "esterilizador", "incubadora neonatal",
    "bomba de infusion", "monitor de signos vitales",
    "camara de flujo laminar", "equipo de oxigenacion",
    "escaner intraoral",
    # Servicios clínicos
    "laboratorio clinico", "analisis clinico", "imagen medica",
    "terapia fisica", "radioterapia", "hemodialisis",
    # Medicamentos
    "medicamento", "farmaco", "vacuna", "insulina",
    "antibiotico", "antifungico", "hemoderivado",
    "reactivo para deteccion",
    "anestesico", "analgesico", "solucion salina", "suero fisiologico",
    "solifenacina",
    # Insumos
    "insumos medicos", "insumo medico",
    "insumos quirurgicos", "insumo quirurgico",
    "insumo hospitalario", "insumos hospitalarios",
    "jeringa", "cateter", "sutura",
    "guante quirurgico", "silla de ruedas",
    "ortesis", "protesis", "aposito", "gasas esteriles",
    "aguja hipodermica", "tubo endotraqueal", "papel crepe",
    "malla quirurgica", "cinta quirurgica",
    "quirurgic",
    # Farmacia específica
    "servicio de farmacia", "insumos farmacia",
    # Tecnología salud
    "expediente electronico", "historia clinica electronica",
    "telemedicina", "telesalud", "hl7", "fhir", "dicom",
    "sistema de informacion de salud",
    "sistema de informacion hospitalario",
    # Servicios médicos
    "servicios medicos", "servicio medico", "atencion medica",
    "materia prima para la confeccion de protesis",
    "repuestos para equipo de oxigenacion",
    # v3.3
    "protrombina", "clavo telescopico",
    "pesario", "camilla",
    "equipo de laboratorio", "equipos de laboratorio",
    "oftalmologia", "instrumental oftalmologico",
    # v3.4
    "oftalmologico", "agente oftalmologico",
    # v3.5
    "ileostomia", "colostomia", "ostomia",
    "torniquete", "ferula", "estoquineta",
    "neurocirugia", "sindesmosis", "rectoscopia",
    "postoperatori", "povidone", "yodo",
    "camara de bioseguridad",
    # v3.6
    "ortoped", "electrocirugia", "electrocirugias",
    # v3.7
    "hiperbar",
    "reactivos inmunologicos",
    # v3.8: keywords que fallaban por \u00a0 — ahora redundantes pero explícitos
    "uso medico",
    "insumos medicos para cirugia",
    "activos de uso medico",
]

KEYWORDS_DIRECTOS = [_normalizar(kw) for kw in KEYWORDS_DIRECTOS_RAW]


# ─────────────────────────────────────────────
# PATRONES REGEX
# ─────────────────────────────────────────────
# Nota: los regex usan \s+ donde podría haber espacios — esto matchea
# tanto espacios normales como cualquier Unicode space que sobreviva
# a _normalizar (edge cases de encodings exóticos)

PATRONES_REGEX = [
    # Dosificaciones
    r'\d+[\.,]?\d*\s*mg/ml',
    r'\d+[\.,]?\d*\s*mg/kg',
    r'\d+[\.,]?\d*\s*mcg',
    r'\d+[\.,]?\d*\s*ui/ml',
    r'\d+[\.,]?\d*\s*meq',
    r'\d+\s*mg\b',
    r'\d+[,\.]\d+%',
    # Códigos institucionales
    r'codigo\s*1-1[0-9]-\d+',
    r'codigo\s*2-\d{2}-\d+',
    r'ley\s+6914',
    # Rutas farmacológicas
    r'subcutaneo|subcutanea|subcutane',
    # Oftalmología
    r'oftalmolog',
    r'instrumental\s+oftalmolog',
    # Equipamiento
    r'consumibles\s+autoclave',
    r'tubo\s+(de\s+)?rx|tubo\s+tomografo',
    r'escaner\s+intraoral',
    r'electrocirugía|electrocirugia',
    # v3.8: movido de KEYWORDS_CATEGORIA a PATRONES_REGEX — \s+ es defensivo
    r'activos?\s+(de\s+)?uso\s+medic',
    # Insumos
    r'bolsa\s+postoperatori',
    r'sistema\s+(de\s+)?irrigacion',
    r'fabricacion\s+.*silla\s+.*rueda',
    r'repuesto\s+.*silla\s+.*rueda',
    r'insumos?\s+medicos?\s+para',          # tilde-proof + \u00a0-proof via \s+
    r'ortoped',
    r'hiperbar',
    # Servicios
    r'mpc\s+para',
    r'mantenimiento\s+.*camara\s+(de\s+)?flujo',
    r'mantenimiento\s+.*farmacia',
    r'mantenimiento\s+.*bioseguridad',
    r'mantenimiento\s+.*laboratorio\s+clinic',
    r'mantenimiento\s+.*(ecmo|oxigenacion\s+por\s+membrana)',
    # Reactivos — tilde-proof
    r'reactivos?\s+inmunolog',
    r'licitacion\s+.*reactivo',
    r'reactivo\s+para\s+deteccion',
]


# ─────────────────────────────────────────────
# EXCLUSIONES
# ─────────────────────────────────────────────

EXCLUSIONES = [
    # Vehículos y transporte
    r'\bvehiculo\b', r'\bautomovil\b', r'\bcamion\b', r'\bcamioneta\b',
    r'\bcombustible\b', r'\bboleto\b', r'\bviaje\b',
    r'\btractor\b', r'\bretroexcavadora\b', r'\bexcavadora\b',
    r'\bniveladora\b', r'\bcompactadora\b', r'pick.?up',
    r'boletos?\s+aereo',
    # Alojamiento y alimentación
    r'\bhotel\b', r'\bhospedaje\b',
    r'\balimentacion\b', r'\balimento\b', r'\bpescado\b',
    r'\bcatering\b', r'\brancho\b', r'\bmariscos?\b',
    # Limpieza
    r'insumos?\s+(de\s+)?limpieza',
    r'insumos?\s+(de\s+)?aseo',
    r'lavanderia', r'lavado\s+de\s+ropa', r'higienizacion',
    # Marketing y eventos
    r'\bpublicidad\b', r'campana\s+publicitaria', r'\bmercadeo\b',
    r'\bpatrocinio\b', r'\bevento\b', r'inscripcion\s+.*actividad',
    # Oficina e IT no médico
    r'\btoner\b', r'fotocopiadora', r'servicio\s+de\s+impresion',
    r'utiles\s+.*oficina', r'materiales\s+.*oficina',
    r'licencia\s+.*sonicwall', r'licencia\s+.*seguridad',
    r'network\s+.*storage', r'\bservidor\b', r'respaldo\s+.*informacion',
    r'sonicwall', r'\bnas\b',
    r'power\s+apps', r'power\s+automate',
    r'arquitectura\s+.*revit', r'\bbim\b', r'twinmotion',
    # Capacitación
    r'\bcapacitacion\b', r'\bcurso\b', r'\bseminario\b',
    # Infraestructura y construcción
    r'\btuberia\b', r'\bdrenaje\b', r'\balcantarillado\b',
    r'\bacera\b', r'\bpavimento\b', r'\bpuente\b',
    r'\bcamino\b', r'obra\s+vial', r'red\s+vial',
    r'aguas\s+pluviales', r'red\s+pluvial',
    r'\bmontacargas\b', r'\bascensor\b', r'\belevador\b',
    r'\bfinisher\b', r'material\s+petreo', r'\bquebrador\b',
    r'maquinaria\s+(pesada|ligera|de\s+construccion|vial|agricola)',
    r'\bmobiliario\b', r'\bedificio\b',
    r'fontaneria', r'\bcalzado\b',
    # Combustibles
    r'\bgasolina\b', r'\bdiesel\b', r'\bgasoil\b', r'\baceite\b',
    # Iluminación y espacios
    r'\bleds?\b', r'\bluminaria\b', r'\balumbrado\b',
    r'\btecho\b', r'\bpolideportivo\b',
    r'\bgimnasio\b', r'salon\s+de\s+eventos',
    # Proyectos urbanos
    r'proyecto\s+urbano', r'desarrollo\s+urbano', r'plan\s+urbano',
    r'renovacion\s+urbana', r'espacio\s+urbano', r'mobiliario\s+urbano',
    r'infraestructura\s+urbana', r'vialidad\s+urbana',
    r'concejo\s+municipal', r'\bcanton\b',
    # Misceláneos
    r'sets?\s+educativo', r'\brobotica\b',
    r'arbol(es)?\s+para\s+embellecimiento',
    r'informe\s+de\s+labores', r'cristaleria',
    r'bienes\s+tacticos',
    r'diario\s+oficial', r'publicacion\s+.*gaceta',
    r'banco\s+nacional', r'estrategia\s+corporativa',
    # v3.7+
    r'carretillas?\s+electric',
    r'planta\s+.*generacion\s+electric',
    r'aires?\s+acondicionado',
    r'sistema\s+.*bms',
    r'topografi',
    # v3.8: nuevos falsos positivos observados
    r'\barrendamiento\b',            # arrendamiento de inmuebles
    r'cubierta\s+conectora',         # construcción hospitalaria
    r'cerramiento\s+de\s+acceso',
    r'acometida\s+electric',
    r'pantallas?\s+led',             # TVs para salas — no médico
    r'smart\s+tv',
    r'suscripcion\s+autocad',
    r'cableado\s+estructurado',
    r'radio\s+comunicacion',         # radios portátiles
    r'equipos\s+de\s+radio',
]


# ─────────────────────────────────────────────
# KEYWORDS POR CATEGORÍA
# ─────────────────────────────────────────────

KEYWORDS_CATEGORIA = {
    "SERVICIO_SALUD": [
        "laboratorio clinico", "analisis clinico", "imagen medica",
        "terapia fisica", "radioterapia", "hemodialisis",
        "servicios medicos", "servicio medico", "atencion medica",
        "oftalmologia", "oftalmologico", "agente oftalmologico",
        "cardiologia", "odontologia",
        "hiperbar",
        "camara de bioseguridad",
        "farmacia",
        "insumos farmacia",
        r"mpc\s+para",
        r"mantenimiento\s+.*camara\s+(de\s+)?flujo",
        r"mantenimiento\s+.*farmacia",
        r"mantenimiento\s+.*bioseguridad",
        r"mantenimiento\s+.*(ecmo|oxigenacion\s+por\s+membrana)",
        r"servicios\s+.*quirurgicos\s+.*oftalmolog",
        r"sistema\s+(de\s+)?irrigacion",
        r"reactivos?\s+inmunolog",
        r"licitacion\s+.*reactivo",
        r"reactivo\s+para\s+deteccion",
    ],
    "EQUIPAMIENTO": [
        "tomografo", "resonancia", "ecografo", "ultrasonido",
        "ventilador", "desfibrilador", "oximetro", "endoscopio",
        "laparoscopio", "broncoscopio", "facoemulsificador", "ecmo",
        "electrocardiografo", "electroencefalografo", "electroencefalograf",
        "eeg", "autoclave", "esterilizador", "incubadora",
        "bomba de infusion", "monitor de signos vitales",
        "camara de flujo laminar", "equipo de oxigenacion",
        "equipo de laboratorio", "equipos de laboratorio",
        "rectoscopia", "electrocirugia", "electrocirugias",
        "escaner intraoral",
        r"tubo\s+(de\s+)?rx|tubo\s+tomografo",
        r"instrumental\s+oftalmolog",
        r"activos?\s+(de\s+)?uso\s+medic",  # v3.8: también aquí para categoría
        r"electrocirugía|electrocirugia",
        r"mantenimiento\s+.*laboratorio\s+clinic",
        r"escaner\s+intraoral",
    ],
    "INSUMO": [
        "insumos medicos", "insumo medico",
        "insumos quirurgicos", "insumo quirurgico",
        "insumo hospitalario", "insumos hospitalarios",
        "jeringa", "cateter", "sutura", "quirurgic",
        "silla de ruedas", "ortesis", "protesis",
        "aposito", "gasas", "vendaje", "aguja",
        "tubo endotraqueal", "papel crepe",
        "camilla", "clavo telescopico",
        "pesario", "malla", "cinta quirurgica",
        "ileostomia", "colostomia", "ostomia",
        "torniquete", "ferula", "estoquineta",
        "neurocirugia", "sindesmosis",
        "postoperatori", "ortoped",
        r"codigo\s*2-\d{2}-\d+",
        r"materia\s+prima\s+.*protesis",
        r"consumibles\s+.*autoclave",
        r"bolsa\s+postoperatori",
        r"fabricacion\s+.*silla\s+.*rueda",
        r"repuesto\s+.*silla\s+.*rueda",
        r"insumos?\s+medicos?\s+para",
        r"ortoped",
    ],
    "MEDICAMENTO": [
        "medicamento", "farmaco", "vacuna", "insulina",
        "antibiotico", "antifungico", "solucion inyectable", "frasco ampolla",
        "comprimido", "tableta", "supositorio", "jarabe",
        "anestesico", "analgesico", "oncologico", "quimioterapia",
        "hemoderivado", "plasma", "suero", "solucion salina",
        "reactivos inmunologicos",
        "protrombina", "povidone", "yodo", "solifenacina",
        r"codigo\s*1-1[0-9]",
        r"ley\s+6914",
        r"\d+\s*mg/ml", r"\d+\s*mcg", r"\d+\s*mg\b",
        r"subcutane",
        r"\d+[,\.]\d+%",
    ],
    "TECNOLOGIA": [
        "expediente electronico", "historia clinica electronica",
        "telemedicina", "telesalud", "hl7", "fhir", "dicom",
        "sistema de informacion de salud",
        "sistema de informacion hospitalario",
    ],
}

_REGEX_META = re.compile(r'[\\^$*+?.()|{}\[\]\d]')

KEYWORDS_CATEGORIA_NORM = {
    cat: [kw if _REGEX_META.search(kw) else _normalizar(kw)
          for kw in kws]
    for cat, kws in KEYWORDS_CATEGORIA.items()
}

_PATRONES_COMPILADOS    = [re.compile(p, re.IGNORECASE) for p in PATRONES_REGEX]
_EXCLUSIONES_COMPILADAS = [re.compile(p, re.IGNORECASE) for p in EXCLUSIONES]


# ─────────────────────────────────────────────
# FUNCIONES DE MATCHING
# ─────────────────────────────────────────────

def _tiene_exclusion(nombre_norm: str) -> bool:
    return any(p.search(nombre_norm) for p in _EXCLUSIONES_COMPILADAS)


def _tiene_keyword_directo(nombre_norm: str) -> bool:
    return any(kw in nombre_norm for kw in KEYWORDS_DIRECTOS)


def _tiene_patron_regex(nombre_norm: str) -> bool:
    return any(p.search(nombre_norm) for p in _PATRONES_COMPILADOS)


def _determinar_categoria(nombre_norm: str) -> str:
    ORDEN = ["SERVICIO_SALUD", "EQUIPAMIENTO", "INSUMO", "MEDICAMENTO", "TECNOLOGIA"]
    for cat in ORDEN:
        for kw in KEYWORDS_CATEGORIA_NORM[cat]:
            if re.search(kw, nombre_norm, re.IGNORECASE):
                return cat
    print(f"  SIN_CATEGORIA: '{nombre_norm[:80]}'")
    return "OTRO_MEDICO"


# ─────────────────────────────────────────────
# CLASIFICADOR PRINCIPAL
# ─────────────────────────────────────────────

def clasificar(item: dict) -> dict | None:
    nombre_raw = (item.get("cartel_nm") or "").strip()
    if not nombre_raw:
        return None

    nombre_norm = _normalizar(nombre_raw)

    if _tiene_exclusion(nombre_norm):
        return None

    es_medica = _tiene_keyword_directo(nombre_norm)

    if not es_medica:
        es_medica = _tiene_patron_regex(nombre_norm)

    if not es_medica:
        if _es_institucion_salud(item.get("inst_nm", "")):
            es_medica = _tiene_keyword_directo(nombre_norm) or _tiene_patron_regex(nombre_norm)

    if not es_medica:
        return None

    categoria = _determinar_categoria(nombre_norm)
    return {**item, "es_medica": True, "categoria": categoria}
