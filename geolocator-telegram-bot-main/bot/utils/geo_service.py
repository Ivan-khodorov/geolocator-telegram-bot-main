import requests
from bot.Config import YANDEX_GEOCODER_API_KEY


class GeoService:
    def __init__(self):
        self.yandex_url = "https://geocode-maps.yandex.ru/1.x"
        self.overpass_url = "http://overpass-api.de/api/interpreter"

    def get_address_from_coords(self, lat: float, lon: float) -> str:
        """
        Получение адреса по координатам через Яндекс Geocoder API
        """
        params = {
            "apikey": YANDEX_GEOCODER_API_KEY,
            "format": "json",
            "geocode": f"{lon},{lat}"
        }
        try:
            response = requests.get(self.yandex_url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
        except Exception:
            return "Адрес не найден"

    def get_nearby_buildings(self, lat: float, lon: float, radius: int = 200, count: int = 12) -> list[dict]:
        """
        Поиск ближайших зданий через Overpass API (OpenStreetMap)
        """
        query = f"""
        [out:json][timeout:25];
        (
          node["building"](around:{radius},{lat},{lon});
          way["building"](around:{radius},{lat},{lon});
        );
        out center {count};
        """

        try:
            response = requests.post(
                self.overpass_url,
                data=query.encode("utf-8"),
                headers={"User-Agent": "leaflet-bot"},
                timeout=25
            )
            response.raise_for_status()
            data = response.json()

            buildings = []
            for element in data["elements"]:
                # Центр может быть в "center" или "lat/lon"
                coords = element.get("center")
                if not coords and "lat" in element and "lon" in element:
                    coords = {"lat": element["lat"], "lon": element["lon"]}
                if not coords:
                    continue

                buildings.append({
                    "address": element["tags"].get("addr:full")
                               or element["tags"].get("name")
                               or element["tags"].get("addr:housenumber", "Жилой дом"),
                    "lat": coords["lat"],
                    "lon": coords["lon"]
                })

            return buildings[:count]
        except Exception:
            return []
