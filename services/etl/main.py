# services/etl/main.py
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from fetcher import fetch_sicop
from parser import parse_batch
from classifier import clasificar
from uploader import upsert_licitaciones, insert_modificaciones


async def run():
    print("=== SICOP ETL — Iniciando ===")

    data = await fetch_sicop(dias_atras=3)

    for tipo, type_key in [("publicadas", "RPT_PUB"), ("adjudicadas", "RPT_ADJ")]:
        parsed  = parse_batch(data[tipo], type_key)

        # Enriquecer cada item — clasificar() retorna el item + es_medica + categoria
        clasificados = []
        for p in parsed:
            resultado = clasificar(p)
            if resultado:
                # Es médica — usar el item enriquecido
                clasificados.append(resultado)
            else:
                # No médica — insertar con flags vacíos
                clasificados.append({**p, "es_medica": False, "categoria": None})

        upsert_licitaciones(clasificados)
        medicas = [r for r in clasificados if r["es_medica"]]
        print(f"[main] {tipo}: {len(medicas)} médicas de {len(parsed)} totales")

    # Modificadas — solo insertar las médicas enriquecidas
    mod_parsed  = parse_batch(data["modificadas"], "RPT_MOD")
    mod_medicas = [r for r in [clasificar(p) for p in mod_parsed] if r is not None]
    insert_modificaciones(mod_medicas)

    print("=== ETL Completado ===")


if __name__ == "__main__":
    asyncio.run(run())
