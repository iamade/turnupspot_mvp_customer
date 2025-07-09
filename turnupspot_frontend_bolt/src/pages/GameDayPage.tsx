import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ChevronLeft, ChevronRight, MapPin } from "lucide-react";
import { get, post } from "../api";

interface Player {
  id: string;
  name: string;
  status: "arrived" | "expected" | "delayed" | "absent";
  arrivalTime?: string;
  isCaptain?: boolean;
  team?: number;
}

interface Team {
  id: number;
  name: string;
  captain: string;
  members: string[];
}

interface GameDayInfo {
  is_playing_day: boolean;
  day: string;
  date: string;
  game_start_time: string;
  game_end_time: string;
  max_teams: number;
  max_players_per_team: number;
  check_in_enabled: boolean;
  current_game_id?: number;
  game_status?: string;
  venue_latitude: number;
  venue_longitude: number;
  venue_radius: number;
}

interface BackendPlayer {
  id: string;
  name: string;
  status: "arrived" | "expected" | "delayed" | "absent";
  arrival_time?: string;
  is_captain?: boolean;
  team?: number;
}

const GameDayPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const playersPerPage = 8;
  const [isAtVenue, setIsAtVenue] = useState(false);
  const [checkinError, setCheckinError] = useState<string>("");
  const [gameDayInfo, setGameDayInfo] = useState<GameDayInfo | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkInLoading, setCheckInLoading] = useState(false);
  const [venueLocation, setVenueLocation] = useState<{
    lat: number;
    lng: number;
    radius: number;
  } | null>(null);

  useEffect(() => {
    fetchGameDayData();
  }, [id]);

  const fetchGameDayData = async () => {
    try {
      setLoading(true);

      // Fetch game day info
      const gameDayResponse = await get<GameDayInfo>(`/games/game-day/${id}`);
      setGameDayInfo(gameDayResponse.data);

      // Set venue location from API response
      setVenueLocation({
        lat: gameDayResponse.data.venue_latitude,
        lng: gameDayResponse.data.venue_longitude,
        radius: gameDayResponse.data.venue_radius,
      });

      // Fetch players
      const playersResponse = await get<BackendPlayer[]>(
        `/games/game-day/${id}/players`
      );

      // Map backend response to frontend interface
      const mappedPlayers: Player[] = playersResponse.data.map(
        (player: BackendPlayer) => ({
          id: player.id,
          name: player.name,
          status: player.status,
          arrivalTime: player.arrival_time, // Map snake_case to camelCase
          isCaptain: player.is_captain,
          team: player.team,
        })
      );

      setPlayers(mappedPlayers);

      // Generate teams based on player data
      generateTeamsFromPlayers(playersResponse.data);
    } catch (error) {
      console.error("Error fetching game day data:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateTeamsFromPlayers = (playerData: Player[]) => {
    const teamMap = new Map<number, Team>();

    playerData.forEach((player) => {
      if (player.team) {
        if (!teamMap.has(player.team)) {
          teamMap.set(player.team, {
            id: player.team,
            name: `Team ${player.team}`,
            captain: "",
            members: [],
          });
        }

        const team = teamMap.get(player.team)!;
        if (player.isCaptain) {
          team.captain = player.name;
        }
        team.members.push(player.name);
      }
    });

    setTeams(Array.from(teamMap.values()));
  };

  useEffect(() => {
    // Check if it's after 6 PM and venue location is available
    const now = new Date();
    if (now.getHours() >= 18 && venueLocation) {
      checkLocation();
    }
  }, [venueLocation]);

  const calculateDistance = (
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ) => {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = (lat1 * Math.PI) / 180;
    const φ2 = (lat2 * Math.PI) / 180;
    const Δφ = ((lat2 - lat1) * Math.PI) / 180;
    const Δλ = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  };

  const checkLocation = () => {
    if (!navigator.geolocation) {
      setCheckinError("Geolocation is not supported by your browser");
      return;
    }

    if (!venueLocation) {
      setCheckinError("Venue location not available");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;

        // Calculate distance between user and venue
        const distance = calculateDistance(
          userLat,
          userLng,
          venueLocation.lat,
          venueLocation.lng
        );

        // Check if user is within venue radius
        if (distance <= venueLocation.radius) {
          setIsAtVenue(true);
          setCheckinError("");
        } else {
          setIsAtVenue(false);
          setCheckinError("You must be at the venue to check in");
        }
      },
      (error) => {
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setCheckinError(
              "Location access was denied. Please enable location access in your browser settings to check in."
            );
            break;
          case error.POSITION_UNAVAILABLE:
            setCheckinError(
              "Location information is unavailable. Please try again."
            );
            break;
          case error.TIMEOUT:
            setCheckinError("Location request timed out. Please try again.");
            break;
          default:
            setCheckinError(
              "An unexpected error occurred while getting your location."
            );
        }
        console.error("Geolocation error:", error);
      }
    );
  };

  const handleManualCheckin = async () => {
    if (!gameDayInfo?.check_in_enabled) {
      setCheckinError(
        "Check-in is not enabled yet. It opens 1 hour before game start."
      );
      return;
    }

    // If not at venue, try to check location first
    if (!isAtVenue) {
      checkLocation();
      // Don't return here - let the user proceed with manual check-in
    }

    try {
      setCheckInLoading(true);
      await post(`/games/game-day/${id}/check-in`);

      // Refresh data after successful check-in
      await fetchGameDayData();

      setIsAtVenue(true);
      setCheckinError("");
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to check in";
      setCheckinError(errorMessage);
    } finally {
      setCheckInLoading(false);
    }
  };

  const getStatusColor = (status: Player["status"]) => {
    switch (status) {
      case "arrived":
        return "text-green-600";
      case "expected":
        return "text-yellow-600";
      case "delayed":
        return "text-orange-600";
      case "absent":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getTeamFormationMessage = () => {
    if (!gameDayInfo) return "";

    if (!gameDayInfo.is_playing_day) {
      return "Today is not a playing day";
    }

    if (!gameDayInfo.check_in_enabled) {
      return "Check-in opens 1 hour before game start";
    }

    const arrivedPlayers = players.filter((p) => p.status === "arrived");
    if (arrivedPlayers.length === 0) {
      return "It's game day! Waiting for arrivals";
    }

    return `Players arrived: ${arrivedPlayers.length}`;
  };

  // Pagination
  const indexOfLastPlayer = currentPage * playersPerPage;
  const indexOfFirstPlayer = indexOfLastPlayer - playersPerPage;
  const currentPlayers = players.slice(indexOfFirstPlayer, indexOfLastPlayer);
  const totalPages = Math.ceil(players.length / playersPerPage);

  const handlePlayBall = () => {
    // Check if teams are ready and referee is present
    navigate(`/sports/groups/${id}/live-match`);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">Loading game day information...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        to={`/my-sports-groups/${id}`}
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Group Details
      </Link>

      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">Game Day</h1>
          {gameDayInfo && (
            <div className="flex items-center space-x-4 mt-4">
              <div className="bg-white rounded-lg shadow px-6 py-3">
                <p className="text-gray-600">
                  {gameDayInfo.day} {gameDayInfo.date}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow px-6 py-3">
                <p className="text-gray-600">
                  {gameDayInfo.game_start_time} - {gameDayInfo.game_end_time}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow px-6 py-3">
                <p className="text-gray-600">
                  Max Team: {gameDayInfo.max_teams}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Check-in Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <MapPin
                className={isAtVenue ? "text-green-600" : "text-gray-400"}
                size={24}
              />
              <div>
                <h3 className="font-semibold">Location Check-in</h3>
                <p
                  className={`text-sm ${
                    isAtVenue ? "text-green-600" : "text-gray-500"
                  }`}
                >
                  {isAtVenue ? "You are at the venue" : "Waiting for check-in"}
                </p>
              </div>
            </div>
            <button
              onClick={handleManualCheckin}
              disabled={
                isAtVenue || !gameDayInfo?.check_in_enabled || checkInLoading
              }
              className={`px-4 py-2 rounded-lg ${
                isAtVenue
                  ? "bg-green-100 text-green-700"
                  : !gameDayInfo?.check_in_enabled
                  ? "bg-gray-300 text-gray-500"
                  : "bg-purple-600 text-white hover:bg-purple-700"
              }`}
            >
              {checkInLoading
                ? "Checking In..."
                : isAtVenue
                ? "Checked In"
                : "Check In"}
            </button>
          </div>
          {checkinError && (
            <p className="mt-2 text-sm text-red-600">{checkinError}</p>
          )}
        </div>

        {/* Team Formation */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">Team Formation</h2>

          {!gameDayInfo?.is_playing_day ? (
            <div className="text-center py-8">
              <p className="text-gray-500 text-lg">
                {getTeamFormationMessage()}
              </p>
            </div>
          ) : (
            <>
              <div className="mb-4">
                <p className="text-gray-600">{getTeamFormationMessage()}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {teams.map((team) => (
                  <div key={team.id} className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2">{team.name}</h3>
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-purple-600">
                        Captain: {team.captain || "Not assigned"}
                      </div>
                      <div className="space-y-1">
                        {team.members.map((member, index) => (
                          <div key={index} className="text-sm text-gray-600">
                            {member}
                          </div>
                        ))}
                      </div>
                      <button className="mt-2 text-sm text-blue-600 hover:text-blue-800">
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Player Arrival */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">Player Arrival</h2>
          <div className="space-y-4">
            {currentPlayers
              .sort((a, b) => {
                if (a.arrivalTime && b.arrivalTime) {
                  return a.arrivalTime.localeCompare(b.arrivalTime);
                }
                return a.status === "arrived" ? -1 : 1;
              })
              .map((player) => (
                <div
                  key={player.id}
                  className="flex items-center justify-between border-b pb-4 last:border-b-0"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-200 rounded-full overflow-hidden">
                      {/* Player avatar would go here */}
                    </div>
                    <div>
                      <h3 className="font-medium">
                        {player.name}
                        {player.isCaptain && " (Captain)"}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span
                          className={`text-sm ${getStatusColor(player.status)}`}
                        >
                          {player.status}
                        </span>
                        {player.arrivalTime && (
                          <span className="text-sm text-gray-500">
                            • {player.arrivalTime}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-between items-center mt-6">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded-lg disabled:opacity-50"
            >
              <ChevronLeft size={20} />
            </button>
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() =>
                setCurrentPage((prev) => Math.min(prev + 1, totalPages))
              }
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded-lg disabled:opacity-50"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>

        {/* Play Ball Button */}
        <button
          onClick={handlePlayBall}
          className="w-full py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white"
        >
          Play Ball
        </button>
      </div>
    </div>
  );
};

export default GameDayPage;
