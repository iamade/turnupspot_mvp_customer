declare global {
  interface Window {
    google: typeof google;
  }
}

declare namespace google.maps {
  class LatLng {
    constructor(lat: number, lng: number);
    lat(): number;
    lng(): number;
  }
}

declare namespace google.maps.places {
  interface AutocompletePrediction {
    place_id: string;
    description: string;
    structured_formatting: {
      main_text: string;
      secondary_text: string;
    };
  }

  interface AutocompletionRequest {
    input: string;
    types?: string[];
  }

  interface AutocompleteService {
    getPlacePredictions(
      request: AutocompletionRequest,
      callback: (
        predictions: AutocompletePrediction[],
        status: PlacesServiceStatus
      ) => void
    ): void;
  }

  interface PlaceResult {
    place_id?: string;
    formatted_address?: string;
    name?: string;
    geometry?: {
      location?: google.maps.LatLng;
    };
  }

  interface PlaceDetailsRequest {
    placeId: string;
    fields: string[];
  }

  interface PlacesService {
    getDetails(
      request: PlaceDetailsRequest,
      callback: (
        result: PlaceResult | null,
        status: PlacesServiceStatus
      ) => void
    ): void;
  }

  enum PlacesServiceStatus {
    OK = "OK",
    ZERO_RESULTS = "ZERO_RESULTS",
    OVER_QUERY_LIMIT = "OVER_QUERY_LIMIT",
    REQUEST_DENIED = "REQUEST_DENIED",
    INVALID_REQUEST = "INVALID_REQUEST",
    UNKNOWN_ERROR = "UNKNOWN_ERROR",
  }

  function AutocompleteService(): AutocompleteService;
  function PlacesService(attrContainer: HTMLDivElement): PlacesService;
}

export {};
