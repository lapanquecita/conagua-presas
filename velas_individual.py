import os

import pandas as pd
import plotly.graph_objects as go
from PIL import Image


ENTIDADES = {
    "Ags.": "Aguascalientes",
    "B.C.": "Baja California",
    "Chih.": "Chihuahua",
    "Chis.": "Chiapas",
    "Coah.": "Coahuila",
    "Col.": "Colima",
    "Dgo.": "Durango",
    "Gro.": "Guerrero",
    "Gto.": "Guanajuato",
    "Hgo.": "Hidalgo",
    "Jal.": "Jalisco",
    "Mich.": "Michoacán",
    "Mor.": "Morelos",
    "Méx.": "Estado de México",
    "N.L.": "Nuevo León",
    "Nay.": "Nayarit",
    "Oax.": "Oaxaca",
    "Pue.": "Puebla",
    "Qro.": "Querétaro",
    "S.L.P.": "San Luis Potosí",
    "Sin.": "Sinaloa",
    "Son.": "Sonora",
    "Tamps.": "Tamaulipas",
    "Tlax.": "Tlaxcala",
    "Ver.": "Veracruz",
    "Zac.": "Zacatecas",
}

# La fecha que se mostrará en la fuente.
FECHA_FUENTE = "abril 2024"


def main(presa_id):
    """
    Inicia el reporte de la presa especificada.

    Se crean dos gráficas de vela con los datos
    mensuales de los últimos 15 años.

    Parameters
    ----------
    presa_id : str
        El identificador de la presa que queremos graficar.

    """

    # Cargamos y filtramos el catálogo de presas.
    catalogo = pd.read_csv("./catalogo.csv")
    catalogo = catalogo[catalogo["clavesih"] == presa_id]

    # Obtenemos el NAMO.
    namo = catalogo["namoalmac"].iloc[0]

    # Obtenemos el nombre común de la presa y lo limpiamos.
    nombre, estado = catalogo["nombrecomun"].iloc[0].split(",")
    nombre = ", ".join([nombre, ENTIDADES[estado.strip()]])

    # Vamos a juntar todos los DataFrames en uno solo.
    dfs = list()
    cols = ["fechamonitoreo", "clavesih", "almacenaactual", "namoalmac"]

    # Iteramos sobre los archivos anuales.
    for file in os.listdir("./data")[-15:]:
        # Cargamos el dataset con las columnas especificadas.
        df = pd.read_csv(f"./data/{file}", parse_dates=["fechamonitoreo"], usecols=cols)

        # Seleccionamos la presa de nuestro interés.
        df = df[df["clavesih"] == presa_id]

        # Agregamos el DataFrame a la lista de DataFrames.
        dfs.append(df)

    # Consolidamos todos los DataFrames.
    completo = pd.concat(dfs, axis=0)

    # Llamamos las siguientes funciones para crear las gráficas.
    plot_candle(completo, nombre, namo)
    plot_candle_perc(completo, nombre, namo)
    combinar_imagenes(presa_id)


def plot_candle(df, nombre, namo):
    """
    Crea una gráfica de velas con el nivel de almacenamiento
    de las presas especificadas.

    Parameters
    ----------
    df : pandas.DataFrame
        El DataFrame con los datos de la presa.

    nomre : str
        El nomre común de la presa.

    namo : float
        el nivel de almacenamiento máximo ordinario.

    """

    # Transformamos el DataFrame para que las columnas sean las presas
    # y los valores el nivel actual de llenado.
    df = df.pivot_table(
        index="fechamonitoreo",
        columns="clavesih",
        values="almacenaactual",
        aggfunc="last",
    )

    # Calculamos el total de llenado de todas las presas.
    df["total"] = df.sum(axis=1)

    # Quitamos los picos en la serie de tiempo.
    df = df.rolling(7).median()

    # Transformamos los datos en valores OHLC mensuales.
    df = df["total"].resample("MS").ohlc()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color="#84ffff",
            decreasing_line_color="#ff9800",
        )
    )

    fig.update_xaxes(
        rangeslider_visible=False,
        ticks="outside",
        tickformat="%m<br>%Y",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Almacenamiento actual en hm<sup>3</sup>",
        ticks="outside",
        separatethousands=True,
        titlefont_size=18,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=1,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        zerolinewidth=1,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=False,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_font_size=20,
        legend_x=0.5,
        legend_y=0.05,
        legend_xanchor="center",
        legend_yanchor="bottom",
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Evolución del nivel de almacenamiento de la presa <b>{nombre}</b> (NAMO: <b>{namo:,.1f} hm<sup>3</sup></b>)",
        title_x=0.5,
        title_y=0.975,
        margin_t=50,
        margin_r=40,
        margin_b=100,
        margin_l=100,
        title_font_size=22,
        plot_bgcolor="#000000",
        paper_bgcolor="#282A3A",
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: CONAGUA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./1.png")


def plot_candle_perc(df, nombre, namo):
    """
    Crea una gráfica de velas con el nivel de almacenamiento
    de las presas especificadas.

    A diferencia de la otra función, esta muestra los valores
    en porcentaje respecto al NAMO total.

    Parameters
    ----------
    df : pandas.DataFrame
        El DataFrame con los datos de la presa.

    nomre : str
        El nomre común de la presa.

    namo : float
        el nivel de almacenamiento máximo ordinario.

    """

    # Extraemos el NAMO diario, que será usado para calcular el porcentaje de llenado.
    namo_diario = df.groupby(df["fechamonitoreo"]).sum(numeric_only=True)["namoalmac"]

    # Transformamos el DataFrame para que las columnas sean las presas
    # y los valores el nivel actual de llenado.
    df = df.pivot_table(
        index="fechamonitoreo",
        columns="clavesih",
        values="almacenaactual",
        aggfunc="last",
    )

    # Calculamos el porcentaje de llenado de todas las presas.
    df["total"] = df.sum(axis=1) / namo_diario * 100

    # Quitamos los picos en la serie de tiempo.
    df = df.rolling(7).median()

    # Transformamos los datos en valores OHLC mensuales.
    df = df["total"].resample("MS").ohlc()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color="#84ffff",
            decreasing_line_color="#ff9800",
        )
    )

    fig.update_xaxes(
        rangeslider_visible=False,
        ticks="outside",
        tickformat="%m<br>%Y",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Almacenamiento actual respecto al nivel máximo ordinario",
        ticksuffix="%",
        ticks="outside",
        separatethousands=True,
        titlefont_size=18,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=1,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        zerolinewidth=1,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=False,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_font_size=20,
        legend_x=0.5,
        legend_y=0.05,
        legend_xanchor="center",
        legend_yanchor="bottom",
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Evolución del nivel de almacenamiento de la presa <b>{nombre}</b> (NAMO: <b>{namo:,.1f} hm<sup>3</sup></b>)",
        title_x=0.5,
        title_y=0.975,
        margin_t=50,
        margin_r=40,
        margin_b=100,
        margin_l=100,
        title_font_size=22,
        plot_bgcolor="#000000",
        paper_bgcolor="#282A3A",
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: CONAGUA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./2.png")


def combinar_imagenes(presa_id):
    """
    Esta función une las dos imágenes generadas por
    las otras funciones.

    Parameters
    ----------
    presa_id : str
        El identificador de la presa. Usado para nombrar el archivo final.

    """

    # Cargamos las imágenes.
    imagen1 = Image.open("./1.png")
    imagen2 = Image.open("./2.png")

    # Definimos las dimensiones del lienzo.
    reusltado_ancho = 1280
    resultado_alto = imagen1.height + imagen2.height

    # Copiamos los pixeles al lienzo.
    resultado = Image.new("RGB", (reusltado_ancho, resultado_alto))
    resultado.paste(im=imagen1, box=(0, 0))
    resultado.paste(im=imagen2, box=(0, imagen1.height * 1))

    # Gaurdamos la imagen final.
    resultado.save(f"./{presa_id}.png")


if __name__ == "__main__":
    main("ARCSO")
    # main("VBRMX")
