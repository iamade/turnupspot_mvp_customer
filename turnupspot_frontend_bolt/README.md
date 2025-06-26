# TurnUp Spot Frontend

## Setup

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Google Maps API Key for Places autocomplete and geocoding
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Backend API URL
VITE_API_URL=http://localhost:8000/api/v1
```

### Google Maps API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Geocoding API
   - Maps JavaScript API
4. Create credentials (API Key)
5. Add the API key to your `.env` file as `VITE_GOOGLE_MAPS_API_KEY`

### Installation

```bash
npm install
npm run dev
```

## Features

- **Sports Selection**: Browse and select from available sports
- **Sport Group Creation**: Create new sport groups with Google Places integration
- **Address Autocomplete**: Automatic address suggestions and geocoding
- **File Upload**: Venue image upload support
- **Real-time Search**: Search through sports and groups
