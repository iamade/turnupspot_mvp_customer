import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ChevronLeft, ChevronRight, MapPin } from "lucide-react";
import { get, post } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";

interface Player {
  id: string;
  name: string;
  status: "arrived" | "expected" | "delayed" | "absent";
  arrivalTime?: string;
  isCaptain?: boolean;
  team?: number;
  user_id?: number; // user_id is a number from backend
  isSelected?: boolean; // For drafting selection
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
  user_id?: number; // user_id is a number from backend
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
  const [loading, setLoading] = useState(true);
  const [checkInLoading, setCheckInLoading] = useState(false);
  const [venueLocation, setVenueLocation] = useState<{
    lat: number;
    lng: number;
    radius: number;
  } | null>(null);
  const { token, user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [myMembershipId, setMyMembershipId] = useState<string | null>(null);
  const [draftingMode, setDraftingMode] = useState(false);
  const [selectedPlayers, setSelectedPlayers] = useState<string[]>([]);
  const [draftingTurn, setDraftingTurn] = useState<number>(1); // 1 = Team 1, 2 = Team 2, etc.

  useEffect(() => {
    fetchGameDayData();
  }, [id]);

  const fetchGameDayData = async () => {
    try {
      setLoading(true);

      // Always include the token in headers
      const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

      // Fetch game day info
      const gameDayResponse = await get<GameDayInfo>(`/games/game-day/${id}`, {
        headers,
      });
      setGameDayInfo(gameDayResponse.data);

      // Set venue location from API response
      setVenueLocation({
        lat: gameDayResponse.data.venue_latitude,
        lng: gameDayResponse.data.venue_longitude,
        radius: gameDayResponse.data.venue_radius,
      });

      // Fetch players
      const playersResponse = await get<BackendPlayer[]>(
        `/games/game-day/${id}/players`,
        { headers }
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
          user_id: player.user_id, // Map user_id
        })
      );

      setPlayers(mappedPlayers);

      // Find the current user's membership ID and set it in state
      if (user) {
        const myPlayer = mappedPlayers.find((p) => p.user_id === user.id);
        if (myPlayer) {
          setMyMembershipId(myPlayer.id);
        } else {
          setMyMembershipId(null);
        }
      }

      // Set isAtVenue if current user is arrived
      if (user && myMembershipId !== null) {
        const currentPlayer = mappedPlayers.find(
          (p) => p.id === myMembershipId
        );
        if (currentPlayer && currentPlayer.status === "arrived") {
          setIsAtVenue(true);
        } else {
          setIsAtVenue(false);
        }
      }

      // Teams are now generated dynamically in the UI
    } catch (error) {
      console.error("Error fetching game day data:", error);
    } finally {
      setLoading(false);
    }
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

  const handleBeCaptain = async (playerId: string, teamNumber: number) => {
    if (!id) return;
    try {
      await post(
        `/games/game-day/${id}/teams/assign-captains`,
        { [playerId]: teamNumber },
        token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
      );
      await fetchGameDayData();
    } catch (error: unknown) {
      let message = "Failed to assign captain. Please try again.";
      if (error && typeof error === "object" && "response" in error) {
        const errorResponse = error as {
          response?: { data?: { detail?: string } };
        };
        if (errorResponse.response?.data?.detail) {
          message = errorResponse.response.data.detail;
        }
      } else if (error && typeof error === "object" && "message" in error) {
        const errorWithMessage = error as { message: string };
        message = errorWithMessage.message;
      } else if (typeof error === "string") {
        message = error;
      }
      toast.error(message);
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

  // Team drafting functions
  const startDrafting = () => {
    setDraftingMode(true);
    setDraftingTurn(1);
    setSelectedPlayers([]);
  };

  const canCurrentUserDraft = () => {
    if (!myMembershipId) return false;
    const player = players.find((p) => p.id === myMembershipId);
    if (!player?.isCaptain) return false;

    // Check if it's this captain's turn
    // draftingTurn represents which team number should be drafting (1 = Team 1, 2 = Team 2, etc.)
    const canDraft = player.team === draftingTurn;
    console.log("Drafting Debug:", {
      myMembershipId,
      playerTeam: player.team,
      draftingTurn,
      isCaptain: player.isCaptain,
      canDraft,
    });
    return canDraft;
  };

  const handlePlayerSelection = (playerId: string) => {
    if (selectedPlayers.includes(playerId)) {
      setSelectedPlayers(selectedPlayers.filter((id) => id !== playerId));
    } else {
      setSelectedPlayers([...selectedPlayers, playerId]);
    }
  };

  const handleDraftPlayers = async () => {
    if (!id || selectedPlayers.length === 0) return;

    try {
      const currentTeam = players.find((p) => p.id === myMembershipId)?.team;
      if (!currentTeam) return;

      await post(
        `/games/game-day/${id}/teams/select-players`,
        { [currentTeam]: selectedPlayers },
        token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
      );

      // Move to next team's turn
      const captainTeams = players
        .filter((p) => p.isCaptain)
        .sort((a, b) => (a.team || 0) - (b.team || 0));

      if (draftingTurn < Math.max(...captainTeams.map((p) => p.team || 0))) {
        setDraftingTurn(draftingTurn + 1);
      } else {
        // All teams have drafted, end drafting mode
        setDraftingMode(false);
        setDraftingTurn(1);
      }

      setSelectedPlayers([]);
      await fetchGameDayData();
      toast.success("Players drafted successfully!");
    } catch (error: unknown) {
      let message = "Failed to draft players. Please try again.";
      if (error && typeof error === "object" && "response" in error) {
        const errorResponse = error as {
          response?: { data?: { detail?: string } };
        };
        if (errorResponse.response?.data?.detail) {
          message = errorResponse.response.data.detail;
        }
      } else if (error && typeof error === "object" && "message" in error) {
        const errorWithMessage = error as { message: string };
        message = errorWithMessage.message;
      } else if (typeof error === "string") {
        message = error;
      }
      toast.error(message);
    }
  };

  const canShowPlayBallButton = () => {
    if (!gameDayInfo?.is_playing_day) return false;

    // Check if there are at least 2 teams with players
    const teamsWithPlayers = new Set(
      players.filter((p) => p.team).map((p) => p.team)
    );
    if (teamsWithPlayers.size < 2) return false;

    // Check if current user is admin or captain
    if (isAdmin) return true;

    if (!myMembershipId) return false;
    const currentPlayer = players.find((p) => p.id === myMembershipId);
    return currentPlayer?.isCaptain || false;
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

                {/* Drafting Controls */}
                {!draftingMode &&
                  (isAdmin || players.some((p) => p.isCaptain)) && (
                    <div className="mt-4">
                      <button
                        onClick={startDrafting}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        Start Team Drafting
                      </button>
                    </div>
                  )}

                {draftingMode && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-semibold text-blue-800 mb-2">
                      Team Drafting in Progress
                    </h3>
                    <p className="text-blue-600 text-sm">
                      {canCurrentUserDraft()
                        ? `Your turn to draft players for your team!`
                        : `Waiting for Team ${draftingTurn} captain to draft...`}
                    </p>
                    {canCurrentUserDraft() && selectedPlayers.length > 0 && (
                      <button
                        onClick={handleDraftPlayers}
                        className="mt-2 px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                      >
                        Draft Selected Players ({selectedPlayers.length})
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Array.from({ length: gameDayInfo?.max_teams || 2 }, (_, i) => {
                  const teamNumber = i + 1;
                  const teamPlayers = players.filter(
                    (p) => p.team === teamNumber
                  );
                  const captain = teamPlayers.find((p) => p.isCaptain === true);
                  return (
                    <div key={teamNumber} className="border rounded-lg p-4">
                      <h3 className="font-semibold mb-2">Team {teamNumber}</h3>
                      <div className="text-sm font-medium text-purple-600">
                        Captain: {captain ? captain.name : "Not assigned"}
                      </div>
                      <div className="space-y-1">
                        {teamPlayers.map((member, idx) => (
                          <div key={idx} className="text-sm text-gray-600">
                            {member.name}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Player Arrival */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">Player Arrival</h2>
          <div className="space-y-4">
            {(() => {
              // Sort by arrival time, then by status (arrived first)
              const sortedPlayers = [...players].sort((a, b) => {
                if (a.arrivalTime && b.arrivalTime) {
                  return a.arrivalTime.localeCompare(b.arrivalTime);
                }
                return a.status === "arrived" ? -1 : 1;
              });
              // Get first 10 arrived players
              const firstTenArrived = sortedPlayers
                .filter((p) => p.status === "arrived")
                .slice(0, 10);
              // Find captains
              const team1Captain = firstTenArrived.find(
                (p) => p.isCaptain && p.team === 1
              );
              const team2Captain = firstTenArrived.find(
                (p) => p.isCaptain && p.team === 2
              );
              return currentPlayers.map((player) => {
                const isFirstTen = firstTenArrived.some(
                  (p) => p.id === player.id
                );
                const isPlayerTeam1Captain =
                  player.isCaptain && player.team === 1;
                const isPlayerTeam2Captain =
                  player.isCaptain && player.team === 2;
                let showCaptainButton = false;
                let captainButtonText = "";
                if (
                  isFirstTen &&
                  !isPlayerTeam1Captain &&
                  !isPlayerTeam2Captain
                ) {
                  if (!team1Captain) {
                    showCaptainButton = true;
                    captainButtonText = "Be captain of Team 1";
                  } else if (!team2Captain) {
                    showCaptainButton = true;
                    captainButtonText = "Be captain of Team 2";
                  }
                }
                return (
                  <div
                    key={player.id}
                    className="flex items-center justify-between border-b pb-4 last:border-b-0"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-gray-200 rounded-full overflow-hidden">
                        {/* Player avatar would go here */}
                      </div>
                      <div>
                        <h3 className="font-medium flex items-center gap-2">
                          {player.name}
                          {player.isCaptain && player.team && (
                            <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                              Captain (Team {player.team})
                            </span>
                          )}
                          {isFirstTen && (
                            <span className="ml-2 px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded-full">
                              1st ten
                            </span>
                          )}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-sm ${getStatusColor(
                              player.status
                            )}`}
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
                    <div className="flex items-center space-x-2">
                      {/* Drafting Selection */}
                      {draftingMode &&
                        canCurrentUserDraft() &&
                        player.status === "arrived" &&
                        !player.team && (
                          <button
                            onClick={() => handlePlayerSelection(player.id)}
                            className={`px-3 py-1 rounded text-xs ${
                              selectedPlayers.includes(player.id)
                                ? "bg-green-600 text-white"
                                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                            }`}
                          >
                            {selectedPlayers.includes(player.id)
                              ? "Selected"
                              : "Select"}
                          </button>
                        )}
                      {/* Debug info for drafting */}
                      {draftingMode && (
                        <div className="text-xs text-gray-500">
                          Draft: {draftingMode ? "ON" : "OFF"} | CanDraft:{" "}
                          {canCurrentUserDraft() ? "YES" : "NO"} | Status:{" "}
                          {player.status} | Team: {player.team || "None"}
                        </div>
                      )}

                      {/* Captain Assignment Button */}
                      {showCaptainButton &&
                        (isAdmin || player.id === myMembershipId) && (
                          <button
                            className="ml-auto px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs"
                            onClick={() =>
                              handleBeCaptain(player.id, !team1Captain ? 1 : 2)
                            }
                          >
                            {captainButtonText}
                          </button>
                        )}
                    </div>
                  </div>
                );
              });
            })()}
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
        {canShowPlayBallButton() && (
          <button
            onClick={handlePlayBall}
            className="w-full py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white"
          >
            Play Ball
          </button>
        )}
      </div>
    </div>
  );
};

export default GameDayPage;
