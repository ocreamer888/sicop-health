# services/etl/classifier.py
"""
Clasificador de licitaciones médicas SICOP v3.12
Cambios vs v3.11:
- KEYWORDS_DIRECTOS: "segun demanda" / "segundo demanda" movidos a PATRONES_REGEX
  con \\b para evitar match sobre "granelsegun" y similares
- PATRONES_REGEX: r'\\bsegun\\s+demanda\\b', r'\\bsegundo\\s+demanda\\b'
- EXCLUSIONES: r'frutas?.{0,3}vegetales?.{0,3}verduras?' reemplaza versión con comas fijas
  (fix para títulos sin separadores del parser)
- EXCLUSIONES: r'productos\\s+qu[ií]micos\\s+para\\s+(lav|limpieza|desinfeccion)'
- KEYWORDS_CATEGORIA["INSUMO"]: "helio segun demanda", "compra de helio",
  "insumos para cirugia" — estaban en KEYWORDS_DIRECTOS pero ausentes en categorías
"""

import re
import unicodedata


# ─────────────────────────────────────────────
# SANITIZADOR UNICODE
# ─────────────────────────────────────────────
_UNICODE_SANITIZE = str.maketrans({
    '\u00a0': ' ', '\u200b': '', '\u200c': '', '\u200d': '',
    '\u2060': '', '\ufeff': '', '\u00ad': '',
    '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
    '\u2013': '-', '\u2014': '-', '\u2026': '...',
})


def _normalizar(texto: str) -> str:
    texto = texto.translate(_UNICODE_SANITIZE)
    sin_tildes = (
        unicodedata.normalize("NFD", texto.lower())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return re.sub(r'\s+', ' ', sin_tildes).strip()


# ─────────────────────────────────────────────
# INSTITUCIONES DE SALUD
# ─────────────────────────────────────────────
INSTITUCIONES_SALUD = [
    "caja costarricense", "ccss", "ministerio de salud",
    "hospital", "clinica", "ebais", "cendeiss",
    "inciensa", "instituto costarricense de investigacion",
    "farmacia nacional",
    "ins ",
    "instituto nacional de seguros",
    "junta de proteccion social",
    "conapam", "iafa", "conis",
    "consejo de salud ocupacional",
]

INSTITUCIONES_SALUD_NORM = [_normalizar(i) for i in INSTITUCIONES_SALUD]
_INST_CODE_CCSS_RE = re.compile(r'^00011\d{5}$')


def _es_institucion_salud(inst_nm: str, inst_code: str = "") -> bool:
    inst_norm = _normalizar(inst_nm or "")
    if any(kw in inst_norm for kw in INSTITUCIONES_SALUD_NORM):
        return True
    if inst_code and _INST_CODE_CCSS_RE.match(inst_code):
        return True
    return False


# ─────────────────────────────────────────────
# KEYWORDS DIRECTOS
# ─────────────────────────────────────────────
KEYWORDS_DIRECTOS_RAW = [
    # Formas farmacéuticas
    "solucion inyectable", "suspension oral", "comprimido recubierto",
    "tableta recubierta", "supositorio", "frasco ampolla",
    "parche transdermico", "polvo para reconstituir",
    "colirio", "unguento", "crema dermatologica",
    # Unidades farmacológicas
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
    "solifenacina", "protrombina",
    "quimioterapia", "oncologico",
    # Insumos
    "insumos medicos", "insumo medico",
    "insumos quirurgicos", "insumo quirurgico",
    "insumo hospitalario", "insumos hospitalarios",
    "jeringa", "cateter", "sutura",
    "guante quirurgico", "silla de ruedas",
    "ortesis", "protesis", "aposito", "gasas esteriles",
    "aguja hipodermica", "tubo endotraqueal", "papel crepe",
    "malla quirurgica", "cinta quirurgica", "quirurgic",
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
    # v3.3–v3.5
    "clavo telescopico", "pesario", "camilla",
    "equipo de laboratorio", "equipos de laboratorio",
    "oftalmologia", "instrumental oftalmologico",
    "oftalmologico", "agente oftalmologico",
    "ileostomia", "colostomia", "ostomia",
    "torniquete", "ferula", "estoquineta",
    "neurocirugia", "sindesmosis", "rectoscopia",
    "postoperatori", "povidone", "yodo",
    "camara de bioseguridad",
    # v3.6–v3.7
    "ortoped", "electrocirugia",
    "hiperbar", "reactivos inmunologicos",
    # v3.8
    "uso medico", "activos de uso medico",
    # v3.9
    "drenaje quirurgico", "aposito hemostatico", "hemostatico",
    "material de osteosintesis", "osteosintesis",
    "implante", "implantes ortopedicos",
    "equipo de cirugia", "set quirurgico",
    "linea arterial", "linea venosa",
    "carro de paro", "desfibrilador externo automatico", "dea",
    "saturometro", "capnografo",
    "negatoscopio", "iluminador de radiografias",
    "centrifuga", "micropipeta", "pipeta",
    "medio de contraste", "contraste radiologico",
    "plasma fresco congelado",
    "hemofiltro", "cartucho de dialisis",
    "bolsa de colostomia", "dispositivo de ostomia",
    # v3.9.1
    "equipo medico", "equipos medicos",
    "equipo de enfermeria",
    "insumos de enfermeria", "insumos de enfemeria",
    "insumos laparascopicos", "insumos para cirugia",
    "terapia renal", "unidad de terapia renal",
    "alto flujo de oxigeno",
    "insumos de laboratorio",
    "banco de sangre",
    "craneotomo", "arco en c",
    "neonatologia", "pediatria",
    "invalidez", "antihemorroidal",
    "laparascopico", "laparoscopico",
    # v3.10
    "betametasona",
    "gases medicinales",
    "instrumental laparoscopico",
    "insumos odontologicos",
    "suplementos y modulos nutricionales",
    "modulos nutricionales",
    "formulas nutricionales",
    "ropa y colchones hospitalarios",
    "colchones hospitalarios",
    "ropa hospitalaria",
    "cirugia de torax",
    "servicios de medicina general",
    "medicina general paquete",
    "laboratorio de marcha",
    "servicio de laboratorio de marcha",
    "sillas de ruedas a la medida",
    "por prescripcion medica",
    "colchones y posicionadores de gel",
    "posicionadores de gel",
    "traslado de pacientes",
    "traslado pacientes",
    "ambulancia",
    "oxigeno hiperbarico",
    "planta de tratamiento del centro de salud",
    "compra de helio",
    "helio segun demanda",
    # v3.11
    "equipos medico", "equipo medicos",
    # v3.12 — "segun demanda" movido a PATRONES_REGEX con \b (ver abajo)
    # eliminados: "segun demanda", "segundo demanda"
]

KEYWORDS_DIRECTOS = [_normalizar(kw) for kw in KEYWORDS_DIRECTOS_RAW]


# ─────────────────────────────────────────────
# PATRONES REGEX
# ─────────────────────────────────────────────
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
    r'cod[:\s]+insti[:\s]+\d+-\d+-\d+-\d+',
    r'cod[:\s]+insti[:\s]+\d',
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
    r'activos?\s+(de\s+)?uso\s+medic',
    # Insumos
    r'bolsa\s+postoperatori',
    r'sistema\s+(de\s+)?irrigacion',
    r'fabricacion\s+.*silla\s+.*rueda',
    r'repuesto\s+.*silla\s+.*rueda',
    r'insumos?\s+medicos?\s+para',
    r'ortoped',
    r'hiperbar',
    r'material\s+(de\s+)?osteosintesis',
    r'implantes?\s+ortoped',
    r'linea\s+(arterial|venosa|central)',
    # Servicios
    r'mpc\s+para',
    r'mantenimiento\s+.*camara\s+(de\s+)?flujo',
    r'mantenimiento\s+.*farmacia',
    r'mantenimiento\s+.*bioseguridad',
    r'mantenimiento\s+.*laboratorio\s+clinic',
    r'mantenimiento\s+.*(ecmo|oxigenacion\s+por\s+membrana)',
    # Reactivos
    r'reactivos?\s+inmunolog',
    r'licitacion\s+.*reactivo',
    r'reactivo\s+para\s+deteccion',
    # Servicios médicos compuestos
    r'servicios?\s+de\s+(salud|cirugia|enfermeria|laboratorio)',
    r'adquisicion\s+de\s+(medicamento|insumo|equipo\s+medico)',
    r'suministro\s+de\s+(medicamento|insumo|reactivo)',
    r'compra\s+(urgente\s+)?de\s+(medicamento|insumo|reactivo|equipo\s+medico)',
    # v3.9.1
    r'compra\s+de\s+equipo\s+medico',
    r'compra\s+de\s+equipos?\s+medicos?',
    r'adquisicion\s+de\s+equipo\s+medico',
    r'compra\s+de\s+insumos?\s+(de\s+)?(enfermeria|enfemeria)',
    r'adquisicion\s+de\s+insumos?\s+(lapar|para\s+cirug)',
    r'insumos?\s+(lapar|para\s+terapia\s+renal|alto\s+flujo)',
    r'compra\s+de\s+insumos?\s+de\s+laboratorio',
    r'servicios?\s+de\s+laboratorio\s+(y\s+)?banco\s+de\s+sangre',
    r'compra\s+de\s+equipo\s+craneotomo',
    r'equipo\s+medico\s+arco\s+en\s+c',
    r'solicitud\s+de\s+contratacion\s+.*insumos?\s+lapar',
    r'insumos?\s+(de\s+)?atap',
    r'compra\s+de\s+insumos?\s+.*resguardo',
    r'convenio\s+marco\s+.*equipo\s+(medico|tecnologico\s+medico)',
    r'procedimiento\s+de\s+compra\s+de\s+equipo\s+de\s+enfermeria',
    r'licitacion\s+reducida.*insumos?\s+(de\s+)?(enfermeria|enfemeria)',
    # v3.10
    r'compra\s+fuera\s+de\s+sicop\s*[-–]\s*insumo',
    r'gases?\s+medicinal',
    r'cirug[ií]a\s+de\s+t[oó]rax',
    r'sillas?\s+de\s+ruedas?\s+(a\s+la\s+medida|por\s+prescripci[oó]n)',
    r'residencias?\s+m[eé]dicas?',
    r'analisis\s+(quimico|bacteriologico).*agua.*(salud|siquirres|matina|cariari)',
    r'fractura\s+de\s+f[eé]mur',
    r'suministro\s+de\s+gases?\s+medicinal',
    r'traslado\s+(de\s+)?pacientes?',
    r'servicio\s+de\s+traslado\s+(de\s+)?pacientes?',
    r'planta\s+de\s+tratamiento\s+del\s+centro\s+de\s+salud',
    r'posicionadores?\s+de\s+gel',
    r'colchones?\s+(y\s+)?posicionadores?',
    r'ropa\s+(y\s+)?colchones?\s+hospitalarios?',
    # v3.11
    r'adquisicion\s+de\s+equipos?\s+medico[s]?',
    r'compra\s+de\s+equipos?\s+medico[s]?',
    # v3.12 — "segun demanda" con word boundary para evitar "granelsegun"
    r'\bsegun\s+demanda\b',
    r'\bsegundo\s+demanda\b',
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
    # Proyectos urbanos / municipales
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
    # v3.8
    r'\barrendamiento\b',
    r'cubierta\s+conectora',
    r'cerramiento\s+de\s+acceso',
    r'acometida\s+electric',
    r'pantallas?\s+led',
    r'smart\s+tv',
    r'suscripcion\s+autocad',
    r'cableado\s+estructurado',
    r'radio\s+comunicacion',
    r'equipos\s+de\s+radio',
    # v3.9
    r'cerca\s+perimetral',
    r'caseta\s+de\s+control',
    r'sistema\s+.*cctv',
    r'camara\s+de\s+seguridad',
    r'vigilancia\s+.*perimetral',
    r'portones?\s+electric',
    r'sistema\s+.*control\s+acceso',
    r'pintura\s+(de\s+)?(exterior|interior|edificio|muro)',
    r'impermeabilizacion',
    r'sistema\s+fotovoltaic',
    r'paneles?\s+solares?',
    r'generador\s+electric',
    r'ups\s+electric',
    r'planta\s+electric',
    r'sistema\s+.*alarma\s+incendi',
    r'extintor',
    r'sistema\s+.*rociador',
    # v3.9.1
    r'compra\s+de\s+equipo\s+de\s+computo',
    r'compra\s+de\s+equipo\s+de\s+seguridad',
    r'compra\s+de\s+equipos?\s+de\s+(audio|video|iluminacion)',
    r'insumos?\s+descartables\s+para\s+cocina',
    r'compra\s+de\s+equipos?\s+de\s+pesaje',
    r'convenio\s+marco\s+.*equipo\s+tecnologico(?!\s+medico)',
    r'actividades?\s+deportivas?\s+(y\s+)?recreativa',
    # v3.10
    r'alineado\s+(y\s+)?tramado\s+.*veh[ií]culo',
    r'mesas?\s+y\s+sillas?\s+plegables',
    r'mini\s+racks?\s+(tipo\s+)?picking',
    r'manteles?\s*,?\s*cubremanteles?',
    r'utensilios\s+de\s+cocina',
    r'sacos?\s+de\s+sal\s+.*ablandador',
    r'ablandador\s+de\s+agua',
    r'bater[ií]as?\s+y\s+papel\s+bond',
    r'adquisici[oó]n\s+de\s+bater[ií]as?\s+segun\s+demanda',
    r'pruebas?\s+psicol[oó]gicas?\s+(y\s+)?competenciales?',
    r'reclutamiento\s+(y\s+)?selecci[oó]n\s+de\s+personal\s+ejecutivo',
    r'registro\s+de\s+datos\s+de\s+p[oó]lizas',
    r'procesamiento\s+de\s+pagos\s+de\s+primas',
    r'acompa[nñ]amiento\s+en\s+temas\s+asg',
    r'temas\s+asg\s+(y\s+)?sostenibilidad',
    r'localizaci[oó]n\s+de\s+personas\s+f[ií]sicas',
    r'control\s+de\s+filas\s+(y\s+)?despliegue',
    r'adquisici[oó]n\s+de\s+equipos?\s+de\s+seguridad\s+segun\s+demanda',
    r'aviones?\s+no\s+tripulados?|drones?',
    r'calibraci[oó]n\s+(y\s+)?reparaci[oó]n\s+de\s+equipo\s+de\s+medici[oó]n\s+para\s+mantenimiento',
    r'calibraci[oó]n\s+.*equipos?\s+.*higiene\s+ocupacional',
    r'limpieza\s+de\s+tanques',
    r'fumigaci[oó]n\s+.*eliminaci[oó]n\s+de\s+plagas',
    r'cable\s+el[eé]ctrico',
    r'suministro\s+(e\s+)?instalaci[oó]n\s+de\s+llantas?',
    r'auditor[ií]a\s+externa\s+.*(seguro|sem|ivm|rncp)',
    r'unidades?\s+de\s+potencia\s+ininterrumpida.*eaton',
    r'mantenimiento\s+.*ups.*eaton',
    r'suministros?\s+(y\s+)?materiales?\s+de\s+limpieza',
    # v3.12 — fixes del run 2026-03-05
    r'frutas?.{0,3}vegetales?.{0,3}verduras?',              # reemplaza versión con comas fijas
    r'productos\s+qu[ií]micos\s+para\s+(lav|limpieza|desinfeccion)',
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
        "cardiologia", "odontologia", "hiperbar",
        "camara de bioseguridad", "farmacia", "insumos farmacia",
        "banco de sangre",
        "terapia renal", "alto flujo de oxigeno",
        "traslado de pacientes", "traslado pacientes",
        "ambulancia",
        "medicina general paquete",
        "servicios de medicina general",
        "laboratorio de marcha",
        r"mpc\s+para",
        r"mantenimiento\s+.*camara\s+(de\s+)?flujo",
        r"mantenimiento\s+.*farmacia",
        r"mantenimiento\s+.*bioseguridad",
        r"mantenimiento\s+.*(ecmo|oxigenacion\s+por\s+membrana)",
        r"servicios?\s+.*quirurgicos\s+.*oftalmolog",
        r"sistema\s+(de\s+)?irrigacion",
        r"reactivos?\s+inmunolog",
        r"licitacion\s+.*reactivo",
        r"reactivo\s+para\s+deteccion",
        r"servicios?\s+de\s+(salud|cirugia|enfermeria)",
        r"mantenimiento\s+.*laboratorio\s+clinic",
        r"servicios?\s+de\s+laboratorio\s+(y\s+)?banco\s+de\s+sangre",
        r"cirug[ií]a\s+de\s+t[oó]rax",
        r"traslado\s+(de\s+)?pacientes?",
        r"residencias?\s+m[eé]dicas?",
        r"analisis\s+(quimico|bacteriologico).*agua",
        r"planta\s+de\s+tratamiento\s+del\s+centro\s+de\s+salud",
    ],
    "EQUIPAMIENTO": [
        "tomografo", "resonancia", "ecografo", "ultrasonido",
        "ventilador", "desfibrilador", "oximetro", "endoscopio",
        "laparoscopio", "broncoscopio", "facoemulsificador", "ecmo",
        "electrocardiografo", "electroencefalografo", "electroencefalograf",
        "autoclave", "esterilizador", "incubadora",
        "bomba de infusion", "monitor de signos vitales",
        "camara de flujo laminar", "equipo de oxigenacion",
        "equipo de laboratorio", "equipos de laboratorio",
        "rectoscopia", "electrocirugia", "escaner intraoral",
        "saturometro", "capnografo", "negatoscopio",
        "centrifuga", "micropipeta", "pipeta",
        "carro de paro", "dea",
        "equipo medico", "equipos medicos",
        "equipos medico", "equipo medicos",
        "equipo de enfermeria",
        "craneotomo", "arco en c",
        "neonatologia", "pediatria",
        r"tubo\s+(de\s+)?rx|tubo\s+tomografo",
        r"instrumental\s+oftalmolog",
        r"activos?\s+(de\s+)?uso\s+medic",
        r"electrocirugía|electrocirugia",
        r"desfibrilador\s+externo\s+automatico",
        r"equipo\s+de\s+cirugia",
        r"compra\s+de\s+equipo\s+medico",
        r"compra\s+de\s+equipos?\s+medicos?",
        r"equipo\s+medico\s+arco\s+en\s+c",
        r"procedimiento\s+de\s+compra\s+de\s+equipo\s+de\s+enfermeria",
        r"adquisicion\s+de\s+equipos?\s+medico[s]?",
        r"compra\s+de\s+equipos?\s+medico[s]?",
    ],
    "INSUMO": [
        "insumos medicos", "insumo medico",
        "insumos quirurgicos", "insumo quirurgico",
        "insumo hospitalario", "insumos hospitalarios",
        "jeringa", "cateter", "sutura", "quirurgic",
        "silla de ruedas", "ortesis", "protesis",
        "aposito", "gasas", "vendaje", "aguja",
        "tubo endotraqueal", "papel crepe", "camilla",
        "clavo telescopico", "pesario", "malla", "cinta quirurgica",
        "ileostomia", "colostomia", "ostomia",
        "torniquete", "ferula", "estoquineta",
        "neurocirugia", "sindesmosis", "postoperatori",
        "ortoped", "osteosintesis", "implante",
        "drenaje quirurgico", "hemostatico",
        "set quirurgico", "hemofiltro", "linea arterial",
        "insumos de enfermeria", "insumos de enfemeria",
        "insumos laparascopicos", "laparascopico",
        "insumos de laboratorio",
        "instrumental laparoscopico",
        "insumos odontologicos",
        "ropa y colchones hospitalarios",
        "colchones hospitalarios",
        "posicionadores de gel",
        "gases medicinales",
        "insumos para cirugia",                              # v3.12: faltaba en categorías
        "compra de helio", "helio segun demanda",            # v3.12: faltaba en categorías
        r"codigo\s*2-\d{2}-\d+",
        r"materia\s+prima\s+.*protesis",
        r"consumibles\s+.*autoclave",
        r"bolsa\s+postoperatori",
        r"fabricacion\s+.*silla\s+.*rueda",
        r"repuesto\s+.*silla\s+.*rueda",
        r"insumos?\s+medicos?\s+para",
        r"material\s+(de\s+)?osteosintesis",
        r"implantes?\s+ortoped",
        r"linea\s+(arterial|venosa|central)",
        r"set\s+quirurgico",
        r"compra\s+de\s+insumos?\s+(de\s+)?(enfermeria|enfemeria)",
        r"adquisicion\s+de\s+insumos?\s+(lapar|para\s+cirug)",
        r"insumos?\s+(lapar|para\s+terapia\s+renal|alto\s+flujo)",
        r"compra\s+de\s+insumos?\s+de\s+laboratorio",
        r"licitacion\s+reducida.*insumos?\s+(de\s+)?(enfermeria|enfemeria)",
        r"insumos?\s+(de\s+)?atap",
        r"sillas?\s+de\s+ruedas?\s+(a\s+la\s+medida|por\s+prescripci[oó]n)",
        r"suministro\s+de\s+gases?\s+medicinal",
        r"colchones?\s+(y\s+)?posicionadores?",
        r"compra\s+fuera\s+de\s+sicop\s*[-–]\s*insumo",
        r"fractura\s+de\s+f[eé]mur",
    ],
    "MEDICAMENTO": [
        "medicamento", "farmaco", "vacuna", "insulina",
        "antibiotico", "antifungico", "solucion inyectable", "frasco ampolla",
        "comprimido", "tableta", "supositorio", "jarabe",
        "anestesico", "analgesico", "oncologico", "quimioterapia",
        "hemoderivado", "plasma", "suero", "solucion salina",
        "reactivos inmunologicos", "protrombina",
        "povidone", "yodo", "solifenacina",
        "antihemorroidal",
        "contraste radiologico", "plasma fresco congelado",
        "betametasona",
        "suplementos y modulos nutricionales",
        "modulos nutricionales",
        "formulas nutricionales",
        r"codigo\s*1-1[0-9]",
        r"cod[:\s]+insti[:\s]+\d",
        r"ley\s+6914",
        r"\d+\s*mg/ml", r"\d+\s*mcg", r"\d+\s*mg\b",
        r"subcutane",
        r"\d+[,\.]\d+%",
        r"suministro\s+de\s+(medicamento|reactivo)",
        r"adquisicion\s+de\s+medicamento",
        r"compra\s+(urgente\s+)?de\s+(medicamento|reactivo)",
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
    ORDEN = ["SERVICIO_SALUD", "EQUIPAMIENTO", "MEDICAMENTO", "INSUMO", "TECNOLOGIA"]
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
    nombre_raw = (
        item.get("cartelnm") or
        item.get("cartel_nm") or
        item.get("cartelNm") or
        ""
    ).strip()

    if not nombre_raw:
        return None

    nombre_norm = _normalizar(nombre_raw)

    if _tiene_exclusion(nombre_norm):
        return None

    es_medica = _tiene_keyword_directo(nombre_norm)

    if not es_medica:
        es_medica = _tiene_patron_regex(nombre_norm)

    if not es_medica:
        inst_nm   = item.get("instnm") or item.get("inst_nm") or item.get("instNm") or ""
        inst_code = item.get("inst_code") or ""
        if _es_institucion_salud(inst_nm, inst_code):
            es_medica = _tiene_keyword_directo(nombre_norm) or _tiene_patron_regex(nombre_norm)
            if es_medica and _tiene_exclusion(nombre_norm):
                return None

    if not es_medica:
        return None

    categoria = _determinar_categoria(nombre_norm)
    return {**item, "es_medica": True, "categoria": categoria}
