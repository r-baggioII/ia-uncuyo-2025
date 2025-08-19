import os
import json
import csv

# Carpeta donde están los JSONs
CARPETA_JSON = "resultados_experimentos_simple_agent"  # sin .json al final

# Carpeta donde vamos a guardar el CSV
CARPETA_SALIDA = "csv_exportados"
os.makedirs(CARPETA_SALIDA, exist_ok=True)

ARCHIVO_CSV = os.path.join(CARPETA_SALIDA, "metadata_simple_agent.csv")

def leer_jsons(carpeta):
    datos = []
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".json"):
            ruta = os.path.join(carpeta, archivo)
            with open(ruta, "r", encoding="utf-8") as f:
                try:
                    contenido = json.load(f)
                    # Extraer solo la sección "metadata" si existe
                    if "metadata" in contenido:
                        datos.append(contenido["metadata"])
                except json.JSONDecodeError:
                    print(f"⚠ Error leyendo {ruta}, archivo no es JSON válido.")
    return datos

def guardar_csv(datos, archivo_csv):
    if not datos:
        print("⚠ No se encontraron datos para exportar.")
        return
    # Usar las claves de metadata como encabezados
    encabezados = list(datos[0].keys())
    with open(archivo_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(datos)
    print(f"✅ CSV exportado a: {archivo_csv}")

if __name__ == "__main__":
    datos = leer_jsons(CARPETA_JSON)
    guardar_csv(datos, ARCHIVO_CSV)
