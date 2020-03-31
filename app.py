# ===================================================================
# Importante tener el stylesheet.css dentro de el directorio assets
# ===================================================================

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
from dash.dependencies import Output, Input, State
import pandas as pd
import plotly.express as px
import io
import requests
from urllib.request import urlopen
import json
import numpy as np




def generar_cuenta_colombia():
    lista = ["Amazonas","Antioquia","Arauca","Atlántico","Bogotá","Bolívar",
    "Boyacá","Caldas","Caquetá","Casanare","Cauca","Cesar","Chocó",
    "Córdoba","Cundinamarca","Guainía","Guaviare","Huila","La Guajira","Magdalena",
    "Meta","Nariño","Norte de Santander","Putumayo","Quindío","Risaralda","San Andrés y Providencia",
    "Santander","Sucre","Tolima","Valle del Cauca","Vaupés","Vichada"]
    lista = [depto.upper() for depto in lista]
    ceros = [0]*len(lista)
    df_ceros = pd.DataFrame({"NOMBRE_DPT":lista, "cuenta_ceros":ceros})

    df_data = pd.read_csv("data/Casos1.csv")
    df_data = df_data.rename(columns={"Departamento": "NOMBRE_DPT"})
    df_data["NOMBRE_DPT"] = df_data["NOMBRE_DPT"].str.upper()
    df_cuenta = pd.DataFrame(df_data.groupby("NOMBRE_DPT")["ID de caso"].count()).reset_index().rename(columns={"ID de caso": "cuenta"})
    df_merge = df_ceros.merge(df_cuenta, on="NOMBRE_DPT", how="left")
    df_merge["total"] = df_merge["cuenta"] + df_merge["cuenta_ceros"]
    df_merge = df_merge.drop(["cuenta", "cuenta_ceros"], axis=1)
    nombres_dict = {"BOGOTÁ": "SANTAFE DE BOGOTA D.C",
                    "VALLE": "VALLE DEL CAUCA"}
    for dept in nombres_dict:
        df_merge = df_merge.replace(dept, nombres_dict[dept])
    df_merge = df_merge.fillna(0)
    df_merge['NOMBRE_DPT'] = df_merge['NOMBRE_DPT'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df_merge = df_merge.replace("NARINO", "NARIÑO")
    return df_merge

def generar_mapa_colombia_cuenta():
    df_merge = generar_cuenta_colombia()
    with urlopen('https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json') as response:
        counties = json.load(response)

    fig = px.choropleth(df_merge, geojson=counties, color="total",
                        locations="NOMBRE_DPT", featureidkey="properties.NOMBRE_DPT",
                        projection="mercator",scope="south america",color_continuous_scale=px.colors.sequential.Blues
                    )
    fig.update_geos(fitbounds="locations", visible=False, showcountries=True, countrycolor="Black",
        showsubunits=True)
    fig.update_layout(
        title_text = 'Confirmados en Colombia',
        font=dict(
            family="Courier New, monospace",
            size=25,
            color="#7f7f7f"
        )
    )
    return fig





    cod =row["codigos"]
    row_cod = df_lat_lon[df_lat_lon["code"] == cod]
    row["lat"] = row_cod["lat"].values[0]
    row["long"] = row_cod["lon"].values[0]
    return row



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


app.layout = dbc.Container([
    html.Div([
        html.H2("Coronavirus", className="pretty_container", style={'text-align': 'center'}),
        html.Div([html.H2("Confirmed: ", style = {"color": "#14378F "}),
                  html.H2(total_confirmed)], 
                className="pretty_container", style={'text-align': 'center'}),

        html.Div([html.H2("Deaths: ", style = {"color": "#AF1E3E "}),
                        html.H2(total_deaths)], 
                        className="pretty_container", style={'text-align': 'center'}),

        html.Div([html.H2("Recovered: ", style = {"color": "#07830D"}),
                  html.H2(total_recovered)], 
                className="pretty_container", style={'text-align': 'center'}),
        
        html.Div([html.H2("Confirmados en Colombia: ", style = {"color": "#89690E"}),
                  html.H2(total_colombia)], 
                className="pretty_container", style={'text-align': 'center'}),
        ],className="pretty_container"

    ),
    
    html.Div([  dbc.Row([
                    html.Div(
                        dcc.Graph(
                            id = "mapa_colombia",
                            figure = generar_mapa_colombia_cuenta()
                        ), className="pretty_container"
                    ),
                ]),
                
    ])


], fluid=True)



# @app.callback(Output("mapa1", "figure"),
#             [Input('radio_mapa', 'value')])

# def update_mapa1(input_value):
#     cuenta = df_data.groupby("Country")[input_value].max().reset_index()
#     cuenta = cuenta[cuenta[input_value]>0]
#     if input_value == "Confirmed":
#         maximo = 5000
#     elif input_value == "Deaths":
#         maximo = 50
#     else:
#         maximo = 500
#     fig = px.choropleth(cuenta, 
#                             locations="Country", 
#                             locationmode='country names', 
#                             color=input_value, 
#                             hover_name="Country", 
#                             range_color=[1,maximo], 
#                             color_continuous_scale="Sunsetdark")  

#     fig.update_layout(title=f'Countries with {input_value} Cases',
#                         font=dict(
#                                 family="Courier New, monospace",
#                                 size=15,
#                                 color="#7f7f7f"
#                             ),
#                  )
#     return fig


if __name__ == "__main__":
    app.run_server(port=4070)
