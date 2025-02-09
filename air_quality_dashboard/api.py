import requests
import pandas as pd


# Clase para interactuar con la API de OpenAQ
class AirQualityAPI:
    BASE_URL = "https://api.openaq.org/v3"
    TU_API_KEY = "19bf755399d667822b7060216f064f913a6b4894a9de42102cd42e370762060b"  # Reemplaza con tu clave de API de OpenAQ

    @staticmethod
    def get_nearby_stations(lat, lon, radius=25000):
        """Obtiene las estaciones cercanas a las coordenadas proporcionadas."""
        url = f"{AirQualityAPI.BASE_URL}/locations"
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": radius,
            "limit": 1000
        }
        headers = {
            "X-API-Key": AirQualityAPI.TU_API_KEY
        }
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API: {e}")
            return []

    @staticmethod
    def get_station_details(location_id):
        """Obtiene los detalles de una estación específica."""
        url = f"{AirQualityAPI.BASE_URL}/locations/{location_id}"
        headers = {
            "X-API-Key": AirQualityAPI.TU_API_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener detalles de la estación: {e}")
            return []

    @staticmethod
    def get_latest_measurements(sensor_id):
        """Obtiene las últimas mediciones de un sensor específico."""
        url = f"{AirQualityAPI.BASE_URL}/sensors/{sensor_id}/days"
        headers = {
            "X-API-Key": AirQualityAPI.TU_API_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener las mediciones: {e}")
            return []

    @staticmethod
    def get_hourly_pm25_averages(sensor_id, start_date, end_date):
        """Obtiene los promedios horarios de PM2.5 para un sensor y rango de fechas."""
        url = f"{AirQualityAPI.BASE_URL}/measurements"
        params = {
            "sensor_id": sensor_id,
            "parameter": "pm25",
            "date_from": start_date,
            "date_to": end_date,
            "limit": 1000
        }
        headers = {
            "X-API-Key": AirQualityAPI.TU_API_KEY
        }
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            measurements = data.get("results", [])
            if not measurements:
                print("No se encontraron mediciones para el sensor y rango de fechas proporcionados.")
                return pd.DataFrame()

            df = pd.DataFrame(measurements)
            df['date'] = pd.to_datetime(df['date']['utc'])
            df.set_index('date', inplace=True)
            hourly_avg = df['value'].resample('H').mean()

            return hourly_avg
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener las mediciones: {e}")
            return pd.DataFrame()


