import googlemaps
from app.core.config import settings
from typing import Tuple, Optional

class GeocodingService:
    def __init__(self):
        self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def get_coordinates(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Get latitude and longitude for a given address using Google Maps Geocoding API.
        Returns a tuple of (latitude, longitude) or (None, None) if geocoding fails.
        """
        try:
            # Geocode the address
            result = self.client.geocode(address)
            
            if not result:
                return None, None
            
            # Extract location from the first result
            location = result[0]['geometry']['location']
            return location['lat'], location['lng']
            
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            return None, None

geocoding_service = GeocodingService() 