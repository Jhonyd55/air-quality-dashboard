from air_quality_dashboard.api import AirQualityAPI
import dash_leaflet as dl
import requests

def obtener_estaciones(lat, lon):    
    stations = AirQualityAPI.get_nearby_stations(lat, lon)
    if not stations:
            print("No se encontraron estaciones cercanas.")
            return []

    markers = [
            dl.Marker(
                position=[station["coordinates"]["latitude"], station["coordinates"]["longitude"]],
                children=[dl.Tooltip(station["name"])],
                id={"type": "marker", "index": station["id"]}
            )
            for station in stations
        ]
    return markers

def obtener_pais(lat, lon):
    """Obtiene el país y la ciudad basado en las coordenadas."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 10,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "NombreDeTuAplicacion/1.0 (https://tusitio.com; [email protected])"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        pais = data.get("address", {}).get("country", "")
        city = data.get("address", {}).get("city", "")
        return pais, city
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return "Error al obtener el país", ""