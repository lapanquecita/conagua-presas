from datetime import datetime
import plotly.graph_objects as go
import pandas as pd


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

# Este diccionario será usado para darle formato al título de la tabla.
MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def plot_table(año, mes, dia, color):
    """
    Crea una tabla con infomación a nivel estatal
    de las princiaples presas de México.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    mes : int
        El mes que se desea graficar.

    dia : int
        El día del mes que se desea graficar.

    color : str
        El color hexadecimal para la fila cabecera.

    """

    # Escogemos las columnas que vamos a necesitar.
    cols = ["fechamonitoreo", "nombreoficial", "namoalmac", "almacenaactual"]

    # Cargamos el dataset del año especificado.
    df = pd.read_csv(
        f"./data/{año}.csv",
        usecols=cols,
        parse_dates=["fechamonitoreo"],
        index_col="fechamonitoreo",
    )

    # Seleccionamos solo los registros del día de nuesto interés.
    df = df[df.index == datetime(año, mes, dia)]

    # Generamos la columna del nombre del estado de cada presa.
    df["estado"] = df["nombreoficial"].apply(
        lambda x: ENTIDADES[x.split(",")[-1].strip()]
    )

    # Obtenemos el total de presas por estado.
    counts = df["estado"].value_counts()

    # Agruapos el DataFrame por estado.
    df = df.groupby("estado").sum(numeric_only=True)

    # Agregamos el conteo de presas por estado a nuestro DataFrame.
    df["counts"] = counts

    # Agregamos la fila para el total nacional.
    df.loc["Nacional"] = df.sum(axis=0)

    # Calculamos el porcentaje de llenado.
    df["nivel"] = df["almacenaactual"] / df["namoalmac"] * 100

    # Para resaltar, los registros a nivel nacional serán de color amarillo.
    df["text_color"] = df.index.map(
        lambda x: "#ffff00" if x == "Nacional" else "#FFFFFF"
    )

    # Ordenamos nuestro DataFrame por nivel de llenado de mayor a menor.
    df.sort_values("nivel", ascending=False, inplace=True)

    # El texto de la anotación que irá abajo.
    nota = "*Nivel de aguas máximo ordinario"

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[100, 80, 130, 100],
            header=dict(
                values=[
                    "<b>Entidad</b><sup></sup>",
                    "<b>No. presas</b><sup></sup>",
                    "<b>Capacidad NAMO (hm<sup>3</sup>)*</b>",
                    "<b>% de llenado ↓</b>",
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color=color,
                align="center",
                height=32,
            ),
            cells=dict(
                values=[df.index, df["counts"], df["namoalmac"], df["nivel"]],
                line_width=0.75,
                fill_color="#000000",
                font_color=[
                    df["text_color"],
                    df["text_color"],
                    df["text_color"],
                    df["text_color"],
                ],
                height=32,
                format=["", "", ",.1f", ",.2f"],
                suffix=["", "", "", "%"],
                align=["left", "center"],
            ),
        )
    )

    fig.update_layout(
        showlegend=False,
        width=840,
        height=1050,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        margin_t=80,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.97,
        title_font_size=26,
        title_text=f"Volumen de almacenamiento de las presas de México por entidad<br>(corte al {dia:02} de {MESES[mes]} del <b>{año}</b>)",
        paper_bgcolor="#282A3A",
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                font_size=16,
                text="Fuente: CONAGUA",
            ),
            dict(
                x=0.5,
                y=0.015,
                xanchor="center",
                yanchor="top",
                font_size=16,
                text=nota,
            ),
            dict(
                x=1.01,
                y=0.015,
                xanchor="right",
                yanchor="top",
                font_size=16,
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Guardamos el archivo con el nombre del año especificado.
    fig.write_image(f"./tabla_presas_{año}.png")


if __name__ == "__main__":
    # plot_table(2009, 4, 28, "#d84315")
    # plot_table(2014, 4, 28, "#558b2f")
    # plot_table(2019, 4, 28, "#116D6E")
    plot_table(2024, 4, 28, "#DA0037")
