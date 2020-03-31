# ===================================================================
# Importante tener el stylesheet.css dentro de el directorio assets
# ===================================================================

import dash
import dash_table
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
import topojson
from topojson import geometry

with urlopen('https://raw.githubusercontent.com/davidbetancur8/Antioquia_dash/master/colombia-municipios.json') as response:
        topoJSON = json.load(response)


def top2geo(topoJSON):
    geometries = topoJSON["objects"]["mpios"]["geometries"]
    geometries_ant = []
    ciudades = []
    for mpio in geometries:
        if mpio["properties"]["dpt"] == "ANTIOQUIA":
            geometries_ant.append(mpio)
            ciudades.append(mpio["properties"]["name"])
    topoJSON["objects"]["mpios"]["geometries"] = geometries_ant
    topo_features = topoJSON['objects']["mpios"]['geometries']
    scale = topoJSON['transform']['scale']
    translation = topoJSON['transform']['translate']

    geoJSON=dict(type= 'FeatureCollection', 
                features = [])

    for k, tfeature in enumerate(topo_features):
        geo_feature = dict(id=k, type= "Feature")
        geo_feature['properties'] = tfeature['properties']
        geo_feature['geometry'] = geometry(tfeature, topoJSON['arcs'], scale, translation)    
        geoJSON['features'].append(geo_feature) 

    return geoJSON



def get_city_names(topoJSON):
    geometries = topoJSON["objects"]["mpios"]["geometries"]
    ciudades = []
    for mpio in geometries:
        if mpio["properties"]["dpt"] == "ANTIOQUIA":
            ciudades.append(mpio["properties"]["name"])
    return ciudades


def generar_mapa_antioquia_cuenta(df_ciudades_ant_cuenta):
    geoJSON = top2geo(topoJSON)

    fig = px.choropleth(df_ciudades_ant_cuenta, geojson=geoJSON, color="cuenta",
                        locations="ciudad", featureidkey="properties.name",
                        width=1000, height=1000,
                        projection="mercator",scope="south america",color_continuous_scale=px.colors.sequential.Blues)

    fig.update_geos(fitbounds="locations", visible=True, showcountries=True, countrycolor="Black", showsubunits=True)
    fig.update_layout(
        title_text = 'Confirmados Antioquia',
        font=dict(
            family="Courier New, monospace",
            size=25,
            color="#7f7f7f"
        )
    )
    return fig


def generate_initial_df():
    ciudades = get_city_names(topoJSON)
    df = pd.DataFrame({"ciudad": ciudades, "cuenta":[0]*len(ciudades)})
    return df

df = generate_initial_df()
geoJSON = top2geo(topoJSON)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server



app.layout = dbc.Container([
    html.Div([
        html.H2("Antioquia en datos", className="pretty_container", style={'text-align': 'center'})],className="pretty_container"),
    html.Div([
            html.H3("Titulo", className="pretty_container", style={'text-align': 'center'}),
            dcc.Input(
                id = "input_titulo",
                placeholder = "Ingresa el título",
                type="text",
                value = "",
                className = "pretty_container",
                style={'text-align': 'center'}
            )
    ],className="pretty_container", style={'text-align': 'center'}),
    html.Div([
            html.H3("Nombre de la variable", className="pretty_container", style={'text-align': 'center'}),
            dcc.Input(
                id = "input_var",
                placeholder = "Ingresa el nombre de la variable",
                type="text",
                value = "",
                className = "pretty_container"
                
            )
    ],className="pretty_container", style={'text-align': 'center'}),
    html.Div([  dbc.Row([
                    html.Div(
                        dcc.Graph(
                            id = "mapa_colombia",
                        ), className="pretty_container"
                    ),
                ]),
    html.Div([
        dash_table.DataTable(
            id='table-editing-simple',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            editable=True
        ),
    ],className="pretty_container"),
    
    
                
    ], className="pretty_container")


], fluid=True)





@app.callback(
    Output('mapa_colombia', 'figure'),
    [Input('table-editing-simple', 'data'),
     Input('table-editing-simple', 'columns'),
     Input('input_titulo', 'value'),
     Input('input_var', 'value')])

def display_output(rows, columns, titulo, varname):
    df_ciudades_ant_cuenta = pd.DataFrame(rows, columns=[c['name'] for c in columns])



    fig = go.Figure(data=go.Choropleth(
        locations=df_ciudades_ant_cuenta['ciudad'], # Spatial coordinates
        z = df_ciudades_ant_cuenta['cuenta'].astype(float), # Data to be color-coded
        geojson = geoJSON,
        featureidkey="properties.name",
        colorscale = 'Blues',
        colorbar_title = varname,
        locationmode = 'geojson-id'
    ))

    fig.update_geos(fitbounds="locations", visible=False, showcountries=False, countrycolor="Black", showsubunits=False)
    fig.update_layout(
        width=1000,
        height=1000,
        geo = dict(
            scope='south america',
            projection=go.layout.geo.Projection(type = 'mercator'),
            showlakes=True, # lakes
            lakecolor='rgb(255, 255, 255)'),

        title_text = titulo,
        font=dict(
            family="Courier New, monospace",
            size=25,
            color="#7f7f7f"
        )
    )

    return fig



if __name__ == "__main__":
    app.run_server(port=4060)

