/// <reference types="@types/google.maps" />
import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, BarChart2, Upload, MapPin, X } from "lucide-react";
import { get, put } from "../../api"; // Changed post to put for updates
import { useAuth } from "../../contexts/AuthContext";
import { toast } from "react-toastify"; // Added toast for notifications

// Google Places API types
interface PlaceResult extends google.maps.places.AutocompletePrediction {
  place_id: string;
  description: string;
  structured_formatting: {
    main_text: string;
    secondary_text: string;
  };
}

// Interface for fetched SportGroup data
interface SportGroupData {
  id: string;
  name: string;
  description: string;
  venue_name: string;
  venue_address: string;
  venue_latitude: number;
  venue_longitude: number;
  venue_image_url?: string;
  playing_days: string[]; // Comma-separated string
  game_start_time: string; // ISO format string
  game_end_time: string; // ISO format string
  max_teams: number;
  max_players_per_team: number;
  rules?: string;
  referee_required: boolean;
  sports_type: string; // This field is not updated in the PUT request
}

const DAYS_OF_WEEK = [
  "MONDAY",
  "TUESDAY",
  "WEDNESDAY",
  "THURSDAY",
  "FRIDAY",
  "SATURDAY",
  "SUNDAY",
];

const EditSportGroupForm: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // Get group ID from URL
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  interface FormDataState {
    name: string;
    description: string;
    venue: string;
    address: string;
    latitude: string;
    longitude: string;
    maxTeams: string;
    maxPlayersPerTeam: string;
    playingDays: string[];
    gameStartTime: string;
    gameEndTime: string;
    rules: string;
    refereeRequired: boolean;
    venueImage: File | null;
    venueImagePreview: string;
  }

  const [formData, setFormData] = useState<FormDataState>({
    name: "",
    description: "",
    venue: "",
    address: "",
    latitude: "",
    longitude: "",
    maxTeams: "",
    maxPlayersPerTeam: "",
    playingDays: [],
    gameStartTime: "",
    gameEndTime: "",
    rules: "",
    refereeRequired: false,
    venueImage: null,
    venueImagePreview: "",
  });

  const [loadingGroupData, setLoadingGroupData] = useState(true);
  const [groupNotFound, setGroupNotFound] = useState(false);
  const dataLoaded = useRef(false);

  // Google Places API state
  const [addressSuggestions, setAddressSuggestions] = useState<PlaceResult[]>(
    []
  );
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
 

  // Load Google Places API
  useEffect(() => {
    const loadGooglePlacesAPI = () => {
      const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
      if (!apiKey || apiKey === "your_google_maps_api_key_here") {
        console.error(
          "Google Maps API key is not configured. Please add VITE_GOOGLE_MAPS_API_KEY to your .env file"
        );
        return Promise.reject(new Error("Google Maps API key not configured"));
      }

      return new Promise<void>((resolve, reject) => {
        // Check if API is already loaded
        if (window.google && window.google.maps && window.google.maps.places) {
          resolve();
          return;
        }

        // Check if script is already being loaded
        if (document.querySelector('script[src*="maps.googleapis.com"]')) {
          const checkLoaded = setInterval(() => {
            if (
              window.google &&
              window.google.maps &&
              window.google.maps.places
            ) {
              clearInterval(checkLoaded);
              resolve();
            }
          }, 100);
          return;
        }

        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
        script.async = true;
        script.defer = true;
        // script.nonce = "your-csp-nonce"; // Add if you're using CSP nonces

        script.onload = () => resolve();
        script.onerror = () => {
          console.error("Failed to load Google Maps API");
          reject(new Error("Failed to load Google Maps API"));
        };
        document.head.appendChild(script);
      });
    };

    loadGooglePlacesAPI()
      .then(() => {
        // Google Maps API is loaded and ready
        console.log("Google Maps API loaded successfully");
      })
      .catch((error) => {
        console.error("Error loading Google Maps API:", error);
      });
  }, []);

  // Fetch existing group data
  useEffect(() => {
    if (!id || !token || dataLoaded.current) {
      setLoadingGroupData(false);
      return;
    }

    const fetchGroupData = async () => {
      if(dataLoaded.current) return;

      setLoadingGroupData(true);
      try {
        const res = await get<SportGroupData>(`/sport-groups/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const groupData = res.data;

        // Format times to HH:MM
        const gameStartTime = new Date(
          groupData.game_start_time
        ).toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
        const gameEndTime = new Date(
          groupData.game_end_time
        ).toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });

        setFormData({
          name: groupData.name,
          description: groupData.description,
          venue: groupData.venue_name,
          address: groupData.venue_address,
          latitude: groupData.venue_latitude.toString(),
          longitude: groupData.venue_longitude.toString(),
          maxTeams: groupData.max_teams.toString(),
          maxPlayersPerTeam: groupData.max_players_per_team.toString(),
          playingDays: Array.isArray(groupData.playing_days)
            ? groupData.playing_days
            : [],
          gameStartTime: gameStartTime,
          gameEndTime: gameEndTime,
          rules: groupData.rules || "",
          refereeRequired: groupData.referee_required,
          venueImage: null, // No file object, only URL
          venueImagePreview: groupData.venue_image_url || "",
        });

        dataLoaded.current = true;
      } catch (error: any) {
        if (error.response && error.response.status === 404) {
          setGroupNotFound(true);
          toast.error("Sport group not found.");
        } else {
          toast.error("Failed to load sport group data.");
        }
        console.error("Error fetching sport group:", error);
      } finally {
        setLoadingGroupData(false);
      }
    };

    fetchGroupData();
  }, [id, token]);

  const handleAddressChange = async (value: string) => {
    setFormData({ ...formData, address: value });

    if (!window.google || !window.google.maps || !window.google.maps.places) {
      console.warn("Google Maps API is not loaded yet");
      return;
    }

    if (value.length > 3) {
      try {
        const service = new (window.google.maps.places
          .AutocompleteService as any)();
        const results = await new Promise<
          google.maps.places.AutocompletePrediction[]
        >((resolve, reject) => {
          service.getPlacePredictions(
            {
              input: value,
              types: ["establishment", "geocode"],
            },
            (predictions, status) => {
              if (status === window.google.maps.places.PlacesServiceStatus.OK) {
                resolve(predictions || []);
              } else {
                reject(new Error(`Places API error: ${status}`));
              }
            }
          );
        });

        setAddressSuggestions(results);
        setShowSuggestions(true);
      } catch (error) {
        console.error("Error fetching address suggestions:", error);
        setAddressSuggestions([]);
        setShowSuggestions(false);
      }
    } else {
      setAddressSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleAddressSelect = async (placeId: string) => {
    setIsLoadingLocation(true);
    setShowSuggestions(false);

    if (!window.google || !window.google.maps || !window.google.maps.places) {
      console.warn("Google Maps API is not loaded yet");
      setIsLoadingLocation(false);
      return;
    }

    try {
      const service = new window.google.maps.places.PlacesService(
        document.createElement("div")
      );

      const place = await new Promise<google.maps.places.PlaceResult>(
        (resolve, reject) => {
          service.getDetails(
            {
              placeId: placeId,
              fields: ["formatted_address", "geometry", "name"],
            },
            (result, status) => {
              if (
                status === window.google.maps.places.PlacesServiceStatus.OK &&
                result
              ) {
                resolve(result);
              } else {
                reject(new Error(`Places API error: ${status}`));
              }
            }
          );
        }
      );

      setFormData({
        ...formData,
        address: place.formatted_address || "",
        venue: place.name || "",
        latitude: place.geometry?.location?.lat().toString() || "",
        longitude: place.geometry?.location?.lng().toString() || "",
      });
    } catch (error) {
      console.error("Error getting place details:", error);
    } finally {
      setIsLoadingLocation(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData({
        ...formData,
        venueImage: file,
        venueImagePreview: URL.createObjectURL(file),
      });
    }
  };

  const daysOfWeek = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  const handleDayToggle = (day: string) => {
    setFormData((prev) => ({
      ...prev,
      playingDays: prev.playingDays.includes(day)
        ? prev.playingDays.filter((d) => d !== day)
        : [...prev.playingDays, day],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      console.error("User not authenticated");
      navigate("/signin");
      return;
    }

    try {
    // Create object instead of FormData for regular fields
    const updateData = {
      name: formData.name.trim(),
      description: formData.description.trim(),
      venue_name: formData.venue.trim(),
      venue_address: formData.address.trim(),
      venue_latitude: parseFloat(formData.latitude),
      venue_longitude: parseFloat(formData.longitude),
      playing_days: formData.playingDays,
      game_start_time: formData.gameStartTime.trim(),
      game_end_time: formData.gameEndTime.trim(),
      max_teams: parseInt(formData.maxTeams),
      max_players_per_team: parseInt(formData.maxPlayersPerTeam),
      rules: formData.rules ? formData.rules.trim() : "",
      referee_required: formData.refereeRequired
    };

    // If there's a new image, use FormData
    if (formData.venueImage) {
      const submitData = new FormData();
            // For FormData, we need to handle each field individually
      Object.entries(updateData).forEach(([key, value]) => {
        if (key === 'playing_days') {
          // For playing_days, keep it as an array
          submitData.append(key, JSON.stringify(value));
        } else {
          submitData.append(key, String(value));
        }
      });
      // Add the file
      submitData.append("venue_image", formData.venueImage);
      // Add other fields as stringified JSON
      // submitData.append("data", JSON.stringify(updateData));

      await put(`/sport-groups/${id}`, submitData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });
    } else {
      // If no new image, send JSON directly
      await put(`/sport-groups/${id}`, updateData, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
    }

    // try {
    //   const submitData = new FormData();
    //   submitData.append("name", formData.name.trim());
    //   submitData.append("description", formData.description.trim());
    //   submitData.append("venue_name", formData.venue.trim());
    //   submitData.append("venue_address", formData.address.trim());
    //   submitData.append("venue_latitude", formData.latitude.toString());
    //   submitData.append("venue_longitude", formData.longitude.toString());
    //   submitData.append(
    //     "playing_days",
    //     JSON.stringify(formData.playingDays.map((day) => day.toUpperCase()))
    //   );
    //   submitData.append("game_start_time", formData.gameStartTime.trim());
    //   submitData.append("game_end_time", formData.gameEndTime.trim());
    //   submitData.append("max_teams", formData.maxTeams.toString());
    //   submitData.append(
    //     "max_players_per_team",
    //     formData.maxPlayersPerTeam.toString()
    //   );
    //   submitData.append("rules", formData.rules ? formData.rules.trim() : "");
    //   submitData.append(
    //     "referee_required",
    //     formData.refereeRequired.toString()
    //   );

    //   if (formData.venueImage) {
    //     submitData.append("venue_image", formData.venueImage);
    //   }

    //   await put(`/sport-groups/${id}`, submitData, {
    //     // Changed to PUT request
    //     headers: {
    //       "Content-Type": "multipart/form-data",
    //       Authorization: `Bearer ${token}`,
    //     },
    //   });

      toast.success("Sport group updated successfully!");
      navigate(`/my-sports-groups/${id}`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Error updating sport group.";
      toast.error(errorMessage);
      console.error("Error updating sport group:", error);
    }
  };

  if (loadingGroupData) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 text-center">
        Loading group data...
      </div>
    );
  }

  if (groupNotFound) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 text-center text-red-600">
        Sport group not found.
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate(-1)}
          className="text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-xl font-semibold">Edit Group</h1>
        <button className="text-gray-600 hover:text-gray-900">
          <BarChart2 size={24} />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Group Name*
            </label>
            <input
              type="text"
              id="name"
              placeholder="Enter group name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Description*
            </label>
            <textarea
              id="description"
              placeholder="Describe your group"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={4}
              required
            />
          </div>
        </div>

        {/* Venue Information */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Venue Information</h2>

          <div>
            <label
              htmlFor="venue"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Venue Name*
            </label>
            <input
              type="text"
              id="venue"
              placeholder="Enter venue name"
              value={formData.venue}
              onChange={(e) =>
                setFormData({ ...formData, venue: e.target.value })
              }
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div className="relative">
            <label
              htmlFor="address"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Address* (with Google Places autocomplete)
            </label>
            <div className="relative">
              <MapPin
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                size={20}
              />
              <input
                type="text"
                id="address"
                placeholder="Start typing address for suggestions..."
                value={formData.address}
                onChange={(e) => handleAddressChange(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
              {isLoadingLocation && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                </div>
              )}
            </div>

            {/* Address Suggestions Dropdown */}
            {showSuggestions && addressSuggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
                {addressSuggestions.map((suggestion) => (
                  <button
                    key={suggestion.place_id}
                    type="button"
                    onClick={() => handleAddressSelect(suggestion.place_id)}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                  >
                    <div className="font-medium">
                      {suggestion.structured_formatting.main_text}
                    </div>
                    <div className="text-sm text-gray-500">
                      {suggestion.structured_formatting.secondary_text}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="latitude"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Latitude*
              </label>
              <input
                type="text"
                id="latitude"
                placeholder="Auto-filled from address"
                value={formData.latitude}
                onChange={(e) =>
                  setFormData({ ...formData, latitude: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-gray-50"
                required
                readOnly
              />
            </div>
            <div>
              <label
                htmlFor="longitude"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Longitude*
              </label>
              <input
                type="text"
                id="longitude"
                placeholder="Auto-filled from address"
                value={formData.longitude}
                onChange={(e) =>
                  setFormData({ ...formData, longitude: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-gray-50"
                required
                readOnly
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Venue Image (Optional)
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-xl">
              <div className="space-y-1 text-center">
                {formData.venueImagePreview ? (
                  <div className="relative">
                    <img
                      src={formData.venueImagePreview}
                      alt="Venue preview"
                      className="mx-auto h-32 w-auto rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          venueImage: null,
                          venueImagePreview: "",
                        })
                      }
                      className="absolute top-0 right-0 -mt-2 -mr-2 bg-red-500 text-white rounded-full p-1"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="venue-image"
                        className="relative cursor-pointer rounded-md font-medium text-indigo-600 hover:text-indigo-500"
                      >
                        <span>Upload a file</span>
                        <input
                          id="venue-image"
                          name="venue-image"
                          type="file"
                          accept="image/*"
                          className="sr-only"
                          onChange={handleImageChange}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">
                      PNG, JPG, GIF up to 10MB
                    </p>
                  </>
                )}
                {/* {formData.venueImagePreview ? (
                  <div className="relative">
                    <img
                      src={formData.venueImagePreview}
                      alt="Venue preview"
                      className="mx-auto h-32 w-auto rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setFormData({
                          ...formData,
                          venueImage: null,
                          venueImagePreview: "",
                        })
                      }
                      className="absolute top-0 right-0 bg-red-500 text-white p-1 rounded-full"
                    >
                      ×
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="venue-image"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                      >
                        <span>Upload a file</span>
                        <input
                          id="venue-image"
                          name="venue-image"
                          type="file"
                          accept="image/*"
                          className="sr-only"
                          onChange={handleImageChange}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">
                      PNG, JPG, GIF up to 10MB
                    </p>
                  </>
                )} */}
              </div>
            </div>
          </div>
        </div>

        {/* Game Schedule */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Game Schedule</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Playing Days*
            </label>
            <div className="grid grid-cols-4 gap-2">
              {daysOfWeek.map((day) => (
                <button
                  key={day}
                  type="button"
                  onClick={() => handleDayToggle(day.toUpperCase())}
                  className={`p-2 text-sm rounded-lg ${
                    formData.playingDays.includes(day.toUpperCase())
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {day}
                </button>
              ))}
            </div>
            {/* <div className="grid grid-cols-4 gap-2">
              {daysOfWeek.map((day) => (
                <label
                  key={day}
                  className={`flex items-center justify-center px-4 py-2 rounded-lg border cursor-pointer ${
                    formData.playingDays.includes(day)
                      ? "bg-indigo-50 border-indigo-500 text-indigo-700"
                      : "border-gray-300 text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={formData.playingDays.includes(day)}
                    onChange={() => handleDayToggle(day)}
                  />
                  <span className="text-sm">{day.slice(0, 3)}</span>
                </label>
              ))}
            </div> */}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="gameStartTime"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Start Time*
              </label>
              <input
                type="time"
                id="gameStartTime"
                value={formData.gameStartTime}
                onChange={(e) =>
                  setFormData({ ...formData, gameStartTime: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label
                htmlFor="gameEndTime"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                End Time*
              </label>
              <input
                type="time"
                id="gameEndTime"
                value={formData.gameEndTime}
                onChange={(e) =>
                  setFormData({ ...formData, gameEndTime: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="gameStartTime"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Game Start Time*
              </label>
              <input
                type="time"
                id="gameStartTime"
                value={formData.gameStartTime}
                onChange={(e) =>
                  setFormData({ ...formData, gameStartTime: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label
                htmlFor="gameEndTime"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Game End Time*
              </label>
              <input
                type="time"
                id="gameEndTime"
                value={formData.gameEndTime}
                onChange={(e) =>
                  setFormData({ ...formData, gameEndTime: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
          </div> */}
        </div>

        {/* Team Configuration */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Team Configuration</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="maxTeams"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Maximum Teams*
              </label>
              <input
                type="number"
                id="maxTeams"
                min="2"
                placeholder="Enter max teams"
                value={formData.maxTeams}
                onChange={(e) =>
                  setFormData({ ...formData, maxTeams: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label
                htmlFor="maxPlayersPerTeam"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Players per Team*
              </label>
              <input
                type="number"
                id="maxPlayersPerTeam"
                min="1"
                placeholder="Max players per team"
                value={formData.maxPlayersPerTeam}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    maxPlayersPerTeam: e.target.value,
                  })
                }
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
          </div>
        </div>

        {/* Additional Information */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Additional Information</h2>

          <div>
            <label
              htmlFor="rules"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Group Rules
            </label>
            <textarea
              id="rules"
              placeholder="Enter group rules and guidelines"
              value={formData.rules}
              onChange={(e) =>
                setFormData({ ...formData, rules: e.target.value })
              }
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={4}
            />
          </div>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="refereeRequired"
            checked={formData.refereeRequired}
            onChange={(e) =>
              setFormData({ ...formData, refereeRequired: e.target.checked })
            }
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <label
            htmlFor="refereeRequired"
            className="ml-2 block text-sm text-gray-700"
          >
            Referee Required
          </label>
        </div>

        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-3 rounded-xl font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          Save Changes
        </button>
      </form>
    </div>
  );
};

export default EditSportGroupForm;
