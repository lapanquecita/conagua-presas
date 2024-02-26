"""
Este script se encarga de descargar y consolidar
los datos del nivel de llenado de presas en México.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import requests


# Esta es la URL de la API.
URL_BASE = "https://sinav30.conagua.gob.mx:8080/PresasPG/presas/reporte/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
}


def descargar(año):
    """
    Esta función descarga los datos para
    el año especificado.

    Parameters
    ----------
    año : int
        El año que deseamos descargar.

    """

    # Creamos la carpeta para guardar los archivos JSON.
    os.makedirs("./archivos", exist_ok=True)

    # Cargamos la lista de los archivos previamente descargados.
    archivos_guardados = os.listdir("./archivos")

    # Definimos la fecha de inicio y de fin, las cuales son
    # el primero de enero del año especificado y del año siguiente.
    # El primero de enero del siguiente año será ignorado.
    fecha_inicio = datetime(año, 1, 1)
    fecha_fin = datetime(año + 1, 1, 1)

    # Alternativamente podemos limitar la búqueda hasta el día actual.
    fecha_fin = datetime.today()

    # Calculamos la diferencia de días entre ambas fechas.
    dias = (fecha_fin - fecha_inicio).days

    for i in range(dias):
        # Calculamos la fecha a descargar.
        nueva_fecha = fecha_inicio + timedelta(days=i)
        nueva_fecha_str = f"{nueva_fecha.year}-{str(nueva_fecha.month).zfill(2)}-{str(nueva_fecha.day).zfill(2)}"

        # Definimos el nombre del archivo a guardar.
        nombre_archivo = f"{nueva_fecha_str}.json"
        url_nueva = URL_BASE.format(nueva_fecha_str)

        # Si el archivo ya existe, nos lo saltamos.
        # De lo contrario, lo descargamos.
        if nombre_archivo not in archivos_guardados:
            with requests.get(url_nueva, headers=HEADERS) as respuesta:
                open(f"./archivos/{nombre_archivo}", "w", encoding="utf-8").write(
                    respuesta.text
                )
                print("Descargado:", nombre_archivo)


def combinar(año):
    """
    Esta función une todos los archivos JSON del año
    especificado.

    Parameters
    ----------
    año : int
        El año que deseamos consolidar.

    """

    # Creamos la carpeta para guardar los archivos CSV consolidados.
    os.makedirs("./data", exist_ok=True)

    # Esta lista almacenará los DataFrames de cada archivo JSON.
    dfs = list()

    # Iteramos sobre la lista de archivos descargados y
    # solo tomamos los del año especificado.
    for archivo in os.listdir("./archivos"):
        if str(año) in archivo:
            # Cargamos el archivo JSOn y agregamos el DataFrame a la lista.
            df = pd.read_json(f"./archivos/{archivo}")
            dfs.append(df)

    # Unimos todos los DataFrames.
    final = pd.concat(dfs, axis=0)

    # Las columnas de texto suelen tener espacios en blanco.
    # Con este ciclo las limpiamos.
    for col in final.columns:
        if final[col].dtype == "object":
            final[col] = final[col].str.strip()

    # Guardamos el DataFrame consolidado.
    final.to_csv(f"./data/{año}.csv", index=False, encoding="utf-8")


def generar_catalogo():
    """
    GEnera un catálogo con los datos de cada presa.
    """

    # Definioms la fecha del catálogo.
    fecha = datetime(2024, 1, 1)
    fecha_str = f"{fecha.year}-{str(fecha.month).zfill(2)}-{str(fecha.day).zfill(2)}"

    # Preparamos la URL y hacemos la petición.
    url = URL_BASE.format(fecha_str)

    with requests.get(url, headers=HEADERS) as respuesta:
        # Convertimos la respuesta a DataFrame.
        df = pd.DataFrame.from_records(respuesta.json())

        # Quitamos las columnas que no necesitamos.
        df = df.iloc[:, 2:-3]

        # Limpiamos el nombre com;un.
        df["nombrecomun"] = df["nombrecomun"].apply(
            lambda x: ", ".join([item.strip() for item in x.split(",")])
            if x is not None
            else x
        )

        # Guardamos el DataFrame a CSV.
        df.to_csv("./catalogo.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    descargar(2024)
    combinar(2024)
    generar_catalogo()
