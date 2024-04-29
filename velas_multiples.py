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
    "Méx.": "Edo. de México",
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


def main(titulo, lado, *presas):
    """
    Inicia el reporte de la presa especificada.

    Se crean dos gráficas de vela con los datos
    mensuales de los últimos 15 años.

    Parameters
    ----------
    titulo : str
        El título que utilizaremos para las gráficas.

    lado : str (left|right)
        El lado donde se posicionará la anotación.

    presas : str
        Los identificadores de las presas que queremos graficar.

    """

    # Cargamos y filtramos el catálogo de presas.
    catalogo = pd.read_csv("./catalogo.csv")
    catalogo = catalogo[catalogo["clavesih"].isin(presas)]

    # calculamos el NAMO de todas las presas.
    namo = catalogo["namoalmac"].sum()

    # Obtenemos la lista de nombres comunes de las presas.
    nombres = list()

    for nombre in catalogo["nombrecomun"]:
        nombre, estado = nombre.split(", ")
        nombres.append(f"• {nombre}, {ENTIDADES[estado.strip()]}")

    nombres = "<br>".join(nombres)

    # Vamos a juntar todos los DataFrames en uno solo.
    dfs = list()
    cols = ["fechamonitoreo", "clavesih", "almacenaactual", "namoalmac"]

    # Iteramos sobre los archivos anuales.
    for file in os.listdir("./data")[-15:]:
        # Cargamos el dataset con las columnas especificadas.
        df = pd.read_csv(f"./data/{file}", parse_dates=["fechamonitoreo"], usecols=cols)

        # Seleccionamos las presas de nuestro interés.
        df = df[df["clavesih"].isin(presas)]

        # Agregamos el DataFrame a la lista de DataFrames.
        dfs.append(df)

    # Consolidamos todos los DataFrames.
    completo = pd.concat(dfs, axis=0)

    # Llamamos las siguientes funciones para crear las gráficas.
    plot_candle(completo, nombres, namo, titulo, lado)
    plot_candle_perc(completo, nombres, namo, titulo, lado)
    combinar_imagenes()


def main_estatal(titulo, entidad, lado):
    """
    Inicia el reporte de la presa especificada.

    Se crean dos gráficas de vela con los datos
    mensuales de los últimos 15 años.

    Parameters
    ----------
    titulo : str
        El título que utilizaremos para las gráficas.

    entidad : str
        El nombre de la entidad federativa que queremos graficar.

    lado : str (left|right)
        El lado donde se posicionará la anotación.

    """

    # Cargamos y filtramos el catálogo de presas.
    catalogo = pd.read_csv("./catalogo.csv")
    catalogo = catalogo[catalogo["estado"] == entidad]

    claves = catalogo["clavesih"].unique()

    # calculamos el NAMO de todas las presas.
    namo = catalogo["namoalmac"].sum()

    # Vamos a juntar todos los DataFrames en uno solo.
    dfs = list()
    cols = ["fechamonitoreo", "clavesih", "almacenaactual", "namoalmac"]

    # Iteramos sobre los archivos anuales.
    for file in os.listdir("./data")[-15:]:
        # Cargamos el dataset con las columnas especificadas.
        df = pd.read_csv(f"./data/{file}", parse_dates=["fechamonitoreo"], usecols=cols)

        # Seleccionamos las presas de nuestro interés.
        df = df[df["clavesih"].isin(claves)]

        # Agregamos el DataFrame a la lista de DataFrames.
        dfs.append(df)

    # Consolidamos todos los DataFrames.
    completo = pd.concat(dfs, axis=0)

    # Llamamos las siguientes funciones para crear las gráficas.
    plot_candle(completo, None, namo, titulo, lado)
    plot_candle_perc(completo, None, namo, titulo, lado)
    combinar_imagenes()


def plot_candle(df, nombres, namo, titulo, lado):
    """
    Crea una gráfica de velas con el nivel de almacenamiento
    de las presas especificadas.

    Parameters
    ----------
    df : pandas.DataFrame
        El DataFrame con los datos de las presas.

    nombres : str
        Los nombres comunes de las presas.

    namo : float
        el nivel de almacenamiento máximo ordinario de todas las presas.

    titulo : str
        El título de la gráfica.

    lado : str (left|right)
        El lado donde se posicionará la anotación.

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

    # Ajustamos el texto de la anotación.
    if nombres is None:
        nota = "<b>Nota:</b><br>Cada vela representa las cifras mensuales<br>de las principales presas del estado."
    else:
        nota = f"<b>Nota:</b><br>Cada vela representa las cifras<br>mensuales de las presas:<br>{nombres}"

    if lado == "left":
        xanchor = "left"
        x_pos = 0.02
    else:
        xanchor = "right"
        x_pos = 1.0

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
        title_text=f"Evolución del volumen de almacenamiento de {titulo} (NAMO: <b>{namo:,.1f} hm<sup>3</sup></b>)",
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
                x=x_pos,
                y=0.93,
                xref="paper",
                yref="paper",
                xanchor=xanchor,
                yanchor="top",
                borderpad=7,
                bordercolor="#FFFFFF",
                borderwidth=1,
                bgcolor="#000000",
                align="left",
                text=nota,
            ),
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


def plot_candle_perc(df, nombres, namo, titulo, lado):
    """
    Crea una gráfica de velas con el nivel de almacenamiento
    de las presas especificadas.

    A diferencia de la otra función, esta muestra los valores
    en porcentaje respecto al NAMO total.

    Parameters
    ----------
    df : pandas.DataFrame
        El DataFrame con los datos de las presas.

    nombres : str
        Los nombres comunes de las presas.

    namo : float
        el nivel de almacenamiento máximo ordinario de todas las presas.

    titulo : str
        El título de la gráfica.

    lado : str (left|right)
        El lado donde se posicionará la anotación.

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

    # Ajustamos el texto de la anotación.
    if nombres is None:
        nota = "<b>Nota:</b><br>Cada vela representa las cifras mensuales<br>de las principales presas del estado."
    else:
        nota = f"<b>Nota:</b><br>Cada vela representa las cifras<br>mensuales de las presas:<br>{nombres}"

    if lado == "left":
        xanchor = "left"
        x_pos = 0.02
    else:
        xanchor = "right"
        x_pos = 1.0

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
        title_text=f"Evolución del volumen de almacenamiento de {titulo} (NAMO: <b>{namo:,.1f} hm<sup>3</sup></b>)",
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
                x=x_pos,
                y=0.93,
                xref="paper",
                yref="paper",
                xanchor=xanchor,
                yanchor="top",
                borderpad=7,
                bordercolor="#FFFFFF",
                borderwidth=1,
                bgcolor="#000000",
                align="left",
                text=nota,
            ),
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


def combinar_imagenes():
    """
    Esta función une las dos imágenes generadas por
    las otras funciones.
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
    resultado.save("./final.png")


if __name__ == "__main__":
    # Seleccionado
    # main(
    #    "las principales presas de Nuevo León",
    #    "right",
    #    "CCHNL",
    #    "CPRNL",
    #    "LBCNL",
    #    "PSANL",
    # )
    main(
        "las principales presas del Sistema Cutzamala",
        "right",
        "VBRMX",
        "DBOMC",
        "VVCMX",
    )

    # Estatal
    # main_estatal("las principales presas de Querétaro", "Querétaro", "left")
