# services/etl/classifier.py
"""
Clasificador de licitaciones médicas SICOP v3.1
Fix: normalización unicode antes de matching.
"""

import re
import unicodedata


def _normalizar(texto: str) -> str:
    """Lowercase + strip tildes para matching robusto."""
    return unicodedata.normalize("NFD", texto.lower()).encode("ascii", "ignore").decode("ascii")


# Normalizar keywords al cargar el módulo
KEYWORDS_DIRECTOS_RAW = [
    "solucion inyectable", "suspension oral", "comprimido recubierto",
    "tableta recubierta", "supositorio", "frasco ampolla",
    "parche transdermico", "polvo para reconstituir",
    "colirio", "unguento", "crema dermatologica",
    "mg/ml", "mcg/ml", "mg/kg", "ui/ml", "meq/ml",
    "tomografo", "resonancia magnetica", "ecografo",
    "ventilador mecanico", "desfibrilador", "oximetro",
    "endoscopio", "laparoscopio", "broncoscopio",
    "facoemulsificador", "electrocardiografo",
    "electroencefalografo", "electroencefalograf",
    "ecmo", "autoclave", "esterilizador", "incubadora neonatal",
    "bomba de infusion", "monitor de signos vitales",
    "camara de flujo laminar", "equipo de oxigenacion",
    "laboratorio clinico", "analisis clinico", "imagen medica",
    "terapia fisica", "radioterapia", "hemodialisis",
    "medicamento", "farmaco", "vacuna", "insulina",
    "antibiotico", "antifungico", "hemoderivado",
    "reactivos inmunologicos", "reactivo para deteccion",
    "anestesico", "analgesico", "solucion salina", "suero fisiologico",
    "insumos medicos", "insumo medico",
    "insumos quirurgicos", "insumo quirurgico",
    "insumo hospitalario", "insumos hospitalarios",
    "jeringa", "cateter", "sutura",
    "guante quirurgico", "silla de ruedas",
    "ortesis", "protesis", "aposito", "gasas esteriles",
    "aguja hipodermica", "tubo endotraqueal", "papel crepe",
    "malla quirurgica", "cinta quirurgica",
    "quirurgic",
    "farmacia", "servicio de farmacia",
    "expediente electronico", "historia clinica electronica",
    "telemedicina", "telesalud", "hl7", "fhir", "dicom",
    "sistema de informacion de salud",
    "sistema de informacion hospitalario",
    "servicios medicos", "servicio medico", "atencion medica",
    "materia prima para la confeccion de protesis",
    "mantenimiento preventivo y correctivo para equipo",
    "repuestos para equipo de oxigenacion",
]

# Pre-normalizar todos los keywords
KEYWORDS_DIRECTOS = [_normalizar(kw) for kw in KEYWORDS_DIRECTOS_RAW]


PATRONES_REGEX = [
    r'\d+[\.,]?\d*\s*mg/ml',
    r'\d+[\.,]?\d*\s*mg/kg',
    r'\d+[\.,]?\d*\s*mcg',
    r'\d+[\.,]?\d*\s*ui/ml',
    r'\d+[\.,]?\d*\s*meq',
    r'codigo\s*1-1[0-9]-\d+',
    r'codigo\s*2-94-\d+',
    r'ley\s+6914',
    r'\d+\s*mg\b',
    r'\d+[\.,]?\d*\s*%',        # ← NUEVO: cubre "0,2%" de Brimonidina
    r'subcutaneo|subcutánea',   # ← NUEVO: vía de administración
    r'oftalmolog',              # ← NUEVO: Brimonidina es oftalmológico
    r'subcutane',
]


EXCLUSIONES = [
    r'\bvehiculo\b', r'\bautomovil\b', r'\bcamion\b',
    r'\bcombustible\b', r'\bboleto\b', r'\bviaje\b',
    r'\bhotel\b', r'\bhospedaje\b',
    r'\balimentacion\b', r'\balimento\b', r'\bpescado\b',
    r'\bcatering\b', r'\brancho\b', r'\bmariscos?\b',
    r'insumos? (de )?limpieza',
    r'insumos? (de )?aseo',
    r'lavanderia', r'lavado de ropa', r'higienizacion',
    r'\bpublicidad\b', r'campana publicitaria', r'\bmercadeo\b',
    r'\bpatrocinio\b', r'\bevento\b',
    r'\btoner\b', r'fotocopiadora', r'servicio de impresion',
    r'\bcapacitacion\b', r'\bcurso\b', r'\bseminario\b',
    r'\btuberia\b', r'\bdrenaje\b', r'\balcantarillado\b',
    r'\bacera\b', r'\bpavimento\b', r'\bpuente\b',
    r'\bcamino\b', r'obra vial', r'red vial',
    r'aguas pluviales', r'red pluvial',
    r'\bmontacargas\b', r'\bascensor\b', r'\belevador\b',
    r'\bfinisher\b', r'material petreo', r'\bquebrador\b',
    r'sets? educativo', r'robotica',
    r'arbol(es)? para embellecimiento',
    r'bolsas? (y arboles? )?para embellecimiento',
    r'informe de labores', r'cristaleria',
    r'utiles.*oficina', r'materiales.*oficina',
    r'licencia.*sonicwall', r'licencia.*seguridad',  # IT no médico
    r'network.*storage', r'servidor\b', r'respaldo.*informacion',
    r'sonicwall', r'nas\b',
    r'boletos? aereo', r'inscripcion.*actividad',
    r'bienes tacticos',
    r'diario oficial', r'publicacion.*gaceta',
    r'arquitectura.*revit', r'bim\b', r'twinmotion',
    r'power apps', r'power automate',
    r'concejo municipal', r'canton\b',
    r'banco nacional', r'estrategia corporativa',
]


KEYWORDS_CATEGORIA = {
    "MEDICAMENTO": [
        "medicamento", "farmaco", "farmacia", "vacuna", "insulina",
        "antibiotico", "antifungico", "solucion inyectable", "frasco ampolla",
        "comprimido", "tableta", "supositorio", "jarabe",
        "anestesico", "analgesico", "oncologico", "quimioterapia",
        "hemoderivado", "plasma", "suero", "solucion salina",
        "reactivos inmunologicos", "reactivo para deteccion",
        r"codigo\s*1-1[0-9]", r"ley\s+6914",
        r"\d+\s*mg/ml", r"\d+\s*mcg", r"\d+\s*mg\b",
        r"\d+[\.,]?\d*\s*%",         # ← cubre Brimonidina 0,2%
        r"subcutane", r"oftalmolog",  # ← vía/especialidad
    ],
    "EQUIPAMIENTO": [
        "tomografo", "resonancia", "ecografo", "ultrasonido",
        "ventilador", "desfibrilador", "oximetro", "endoscopio",
        "laparoscopio", "broncoscopio", "facoemulsificador", "ecmo",
        "electrocardiografo", "electroencefalografo", "electroencefalograf",
        "eeg", "autoclave", "esterilizador", "incubadora",
        "bomba de infusion", "monitor de signos vitales",
        "camara de flujo laminar", "equipo de oxigenacion",
        r"tubo.*rx", r"tubo.*tomografo",
    ],
    "INSUMO": [
        "insumos medicos", "insumo medico",
        "insumos quirurgicos", "insumo quirurgico",
        "insumo hospitalario", "insumos hospitalarios",
        "jeringa", "cateter", "sutura", "quirurgic",
        "silla de ruedas", "ortesis", "protesis",
        "aposito", "gasas", "vendaje", "aguja",
        "tubo endotraqueal", "papel crepe",
        r"codigo\s*2-94", "malla", "cinta quirurgica",
        "materia prima.*protesis",
    ],
    "SERVICIO_SALUD": [
        "laboratorio clinico", "analisis clinico", "imagen medica",
        "terapia fisica", "radioterapia", "hemodialisis",
        r"mpc para", r"mantenimiento.*equipo",
        "servicios medicos", "servicio medico", "atencion medica",
        "oftalmologia", "cardiologia", "odontologia",
    ],
    "TECNOLOGIA": [
        "expediente electronico", "historia clinica electronica",
        "telemedicina", "telesalud",
        "hl7", "fhir", "dicom",
        "sistema de informacion de salud",
        "sistema de informacion hospitalario",
    ],
}

# Normalizar KEYWORDS_CATEGORIA también
KEYWORDS_CATEGORIA_NORM = {
    cat: [_normalizar(kw) if not kw.startswith(r"\\") and "\\" not in kw else kw
          for kw in kws]
    for cat, kws in KEYWORDS_CATEGORIA.items()
}

_PATRONES_COMPILADOS    = [re.compile(p, re.IGNORECASE) for p in PATRONES_REGEX]
_EXCLUSIONES_COMPILADAS = [re.compile(p, re.IGNORECASE) for p in EXCLUSIONES]


def _tiene_exclusion(nombre_norm: str) -> bool:
    return any(p.search(nombre_norm) for p in _EXCLUSIONES_COMPILADAS)


def _tiene_keyword_directo(nombre_norm: str) -> bool:
    return any(kw in nombre_norm for kw in KEYWORDS_DIRECTOS)


def _tiene_patron_regex(nombre_norm: str) -> bool:
    return any(p.search(nombre_norm) for p in _PATRONES_COMPILADOS)


def _determinar_categoria(nombre_norm: str) -> str:
    ORDEN = ["MEDICAMENTO", "EQUIPAMIENTO", "INSUMO", "SERVICIO_SALUD", "TECNOLOGIA"]
    for cat in ORDEN:
        for kw in KEYWORDS_CATEGORIA_NORM[cat]:
            if re.search(kw, nombre_norm, re.IGNORECASE):
                return cat
    print(f"  SIN_CATEGORIA: '{nombre_norm[:80]}'")
    return "OTRO_MEDICO"


def clasificar(item: dict) -> dict | None:
    nombre_raw = (item.get("cartel_nm") or "").strip()
    if not nombre_raw:
        return None

    # Normalizar una sola vez — sin tildes, lowercase
    nombre_norm = _normalizar(nombre_raw)

    if _tiene_exclusion(nombre_norm):
        return None

    es_medica = _tiene_keyword_directo(nombre_norm)
    if not es_medica:
        es_medica = _tiene_patron_regex(nombre_norm)
    if not es_medica:
        return None

    categoria = _determinar_categoria(nombre_norm)
    return {**item, "es_medica": True, "categoria": categoria}
