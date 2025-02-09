import unittest
from air_quality_dashboard.api import AirQualityAPI

class TestAirQualityAPI(unittest.TestCase):
    def test_get_nearby_stations(self):
        # Prueba con coordenadas conocidas
        stations = AirQualityAPI.get_nearby_stations(4.637735, -74.09486)
        self.assertIsInstance(stations, list)
        self.assertGreater(len(stations), 0)

if __name__ == "__main__":
    unittest.main()