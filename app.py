
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import ast
from datetime import datetime
from air_quality_dashboard.api      import AirQualityAPI
from air_quality_dashboard.utils import obtener_pais, obtener_estaciones
# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Dashboard de Calidad del Aire"),
    html.Div([
        # Mapa en el lado izquierdo
        dl.Map(
            [dl.TileLayer(), dl.LayerGroup(id="marker-layer")],
            id="map",
            center=[4.637735, -74.09486],  # Coordenadas centrales (Colombia)
            zoom=12,
            style={'width': '50%', 'height': '50vh', 'display': 'inline-block'}
        ),
        # Información de latitud, longitud, país y ciudad en el lado derecho
        html.Div([
            html.Div([
                html.H3("País", style={'display': 'inline-block', 'marginRight': '10px'}),
                html.H3(id="country", style={'display': 'inline-block'})
            ], style={'paddingLeft': '20px'}),
            html.Div([
                html.H3("Ciudad", style={'display': 'inline-block', 'marginRight': '10px'}),
                html.H3(id="city", style={'display': 'inline-block'})
            ], style={'paddingLeft': '20px'}),
            html.H3("Coordenadas Seleccionadas"),
            html.P("Latitud:"),
            html.P(id="lat-output"),
            html.P("Longitud:"),
            html.P(id="lon-output")
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '20px'})
    ]),
    # Gráfico de calidad del aire en la parte inferior
    dcc.Graph(id="air-quality-graph")
])


# Callback para manejar clics en el mapa y en los marcadores
@app.callback(
    [Output("country", "children"),
     Output("city", "children"),
     Output("lat-output", "children"),
     Output("lon-output", "children"),
     Output("marker-layer", "children"),
     Output("air-quality-graph", "figure")],
    [Input("map", "clickData"),
     Input({"type": "marker", "index": ALL}, "n_clicks")],
    [State("marker-layer", "children")]
)
def handle_clicks(map_click, marker_clicks, existing_markers):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", "", "", "", [], {}

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "map":
        # El mapa fue clicado
        lat, lon = map_click['latlng'].values()
        country, city = obtener_pais(lat, lon)
        markers = obtener_estaciones(lat, lon)

        if not markers:
            print("No se encontraron estaciones cercanas.")
            return country, city, f"{lat:.4f}", f"{lon:.4f}", [], {}

        

        return country, city, f"{lat:.4f}", f"{lon:.4f}", markers, {}

    else:
        # Un marcador fue clicado
        marker_id = ast.literal_eval(triggered_id)
        location_id = marker_id["index"]
        print(f"Estación seleccionada: {location_id}")

        station = AirQualityAPI.get_station_details(location_id)
        if not station:
            print("No se encontraron detalles de la estación.")
            return "", "", "", "", [], {}

        lat = station[0]["coordinates"]["latitude"]
        lon = station[0]["coordinates"]["longitude"]
        country, city = obtener_pais(lat, lon)
        markers = obtener_estaciones(lat, lon)
        # Buscar mediciones de PM2.5
        pm25_measurements = None
        for sensor in station[0]["sensors"]:
            if sensor["parameter"]["displayName"] == "PM2.5":
                pm25_measurements = AirQualityAPI.get_latest_measurements(sensor["id"])
                break

        if not pm25_measurements:
            print("No se encontraron mediciones de PM2.5 para la estación seleccionada.")
            return country, city, f"{lat:.4f}", f"{lon:.4f}", markers, {}

        # Procesar las mediciones
        fechas = [datetime.fromisoformat(entry["coverage"]["datetimeTo"]["local"]) for entry in pm25_measurements]
        valores_promedio = [entry["summary"]["avg"] for entry in pm25_measurements]

        df = pd.DataFrame({"Fecha": fechas, "Promedio": valores_promedio})
        fig = px.line(df, x="Fecha", y="Promedio", title="Niveles de PM2.5 en la Estación Seleccionada")

        return country, city, f"{lat:.4f}", f"{lon:.4f}", markers, fig




# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)