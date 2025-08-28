import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  Castle as Whistle,
  Timer,
  Trophy,
  Clock,
  CheckCircle,
  ArrowLeft,
  Users,
  Crown,
  AlertCircle,
} from "lucide-react";
import { Howl } from "howler";
import { useAuth } from "../contexts/AuthContext";
import { get, post } from "../api";
import { toast } from "react-toastify";

interface Team {
  id: number;
  name: string;
  team_number: number;
  captain_id?: number;
  score: number;
}

interface Match {
  team_a_id: number;
  team_b_id: number;
  team_a_score?: number;
  team_b_score?: number;
  winner_id?: number;
  is_draw?: boolean;
  referee_id?: number;
  completed_at?: string;
  started_at?: string;
}

interface GameState {
  current_match: Match | null;
  upcoming_match: Match | null;
  completed_matches: Match[];
  referee: number | null;
  coin_toss_state: any | null;
  teams: number[];
  players: number[];
}

interface AvailableTeam {
  id: number;
  name: string;
  team_number: number;
  captain_id?: number;
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
  current_game_id?: string;
  game_status?: string;
  venue_latitude: number;
  venue_longitude: number;
  venue_radius: number;
  current_user_membership?: {
    role: string;
    is_creator: boolean;
  };
}

interface GameResponse {
  teams: any[]; // or define a proper Team interface
  // add other properties as needed
}

const LiveMatchPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { token, user } = useAuth();

  // State
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [availableTeams, setAvailableTeams] = useState<AvailableTeam[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [coinTossMode, setCoinTossMode] = useState(false);
  const [coinTossChoices, setCoinTossChoices] = useState({
    team_a_choice: "",
    team_b_choice: "",
  });

  // Better whistle sound
  const whistleSound = new Howl({
    src: ["https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"],
    html5: true,
    volume: 0.7,
  });

  // Fetch game state
  const fetchGameState = async () => {
    if (!id || !token) return;

    try {
      // First get the game day info to get the actual game ID
      const gameDayResponse = await get<GameDayInfo>(`/games/game-day/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const gameId = gameDayResponse.data.current_game_id;

      if (!gameId) {
        throw new Error("No active game found for today");
      }

      // Then use the actual game ID to get the state
      const response = await get<GameState>(`/games/${gameId}/state`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGameState(response.data);

      // Fetch teams data using the game ID
      const teamsResponse = await get<GameResponse>(`/games/${gameId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTeams(teamsResponse.data.teams || []);

      // Fetch available teams
      const availableResponse = await get(`/games/${gameId}/available-teams`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAvailableTeams((availableResponse.data as any).available_teams || []);
    } catch (error) {
      console.error("Error fetching game state:", error);
      toast.error("Failed to load match data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGameState();
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchGameState, 5000);
    return () => clearInterval(interval);
  }, [id, token]);

  // Check if user is admin or referee
  const isAdmin = user?.role === "admin";
  const isReferee = gameState?.referee === user?.id;
  const canControlMatch = isAdmin || isReferee;

  // Get team by ID
  const getTeamById = (teamId: number) => {
    return teams.find((team) => team.id === teamId);
  };

  // Get team name by ID
  const getTeamName = (teamId: number) => {
    const team = getTeamById(teamId);
    return team?.name || `Team ${teamId}`;
  };

  // Start match
  const handleStartMatch = async (teamAId: number, teamBId: number) => {
    if (!id || !token || !canControlMatch) return;

    setSubmitting(true);
    try {
      await post(
        `/games/${id}/start-match`,
        { team_a_id: teamAId, team_b_id: teamBId },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      whistleSound.play();
      toast.success("Match started!");
      await fetchGameState();
    } catch (error) {
      console.error("Error starting match:", error);
      toast.error("Failed to start match");
    } finally {
      setSubmitting(false);
    }
  };

  // Update score
  const handleScoreChange = async (
    teamId: number,
    action: "increment" | "decrement" | "set",
    value?: number
  ) => {
    if (!id || !token || !canControlMatch) return;

    setSubmitting(true);
    try {
      await post(
        `/games/${id}/score`,
        { team_id: teamId, action, value },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      toast.success("Score updated!");
      await fetchGameState();
    } catch (error) {
      console.error("Error updating score:", error);
      toast.error("Failed to update score");
    } finally {
      setSubmitting(false);
    }
  };

  // Coin toss
  const handleCoinToss = async () => {
    if (!id || !token || !isAdmin) return;

    if (!coinTossChoices.team_a_choice || !coinTossChoices.team_b_choice) {
      toast.error("Both teams must choose a side");
      return;
    }

    setSubmitting(true);
    try {
      const coinTossData = {
        team_a_id: gameState?.coin_toss_state?.team_a_id,
        team_b_id: gameState?.coin_toss_state?.team_b_id,
        team_a_choice: coinTossChoices.team_a_choice,
        team_b_choice: coinTossChoices.team_b_choice,
      };

      const result = await post(`/games/${id}/coin-toss`, coinTossData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(`Coin toss result: ${(result as any).result.toUpperCase()}`);
      setCoinTossMode(false);
      setCoinTossChoices({ team_a_choice: "", team_b_choice: "" });
      await fetchGameState();
    } catch (error) {
      console.error("Error performing coin toss:", error);
      toast.error("Failed to perform coin toss");
    } finally {
      setSubmitting(false);
    }
  };

  // Assign referee
  const handleAssignReferee = async (refereeId: number) => {
    if (!id || !token || !isAdmin) return;

    setSubmitting(true);
    try {
      await post(`/games/${id}/referee`, { referee_id: refereeId }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success("Referee assigned!");
      await fetchGameState();
    } catch (error) {
      console.error("Error assigning referee:", error);
      toast.error("Failed to assign referee");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading match data...</p>
        </div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Match Not Found</h2>
          <p className="text-gray-600 mb-4">
            The requested match could not be loaded.
          </p>
          <Link
            to={`/my-sports-groups/${id}/game-day`}
            className="inline-flex items-center text-blue-600 hover:text-blue-700"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Game Day
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        to={`/my-sports-groups/${id}/game-day`}
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Game Day
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          {/* Current Match */}
          {gameState.current_match ? (
            <>
              {/* Match Timer */}
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <div className="flex items-center justify-center space-x-4">
                  <Timer className="w-6 h-6 text-gray-600" />
                  <span className="text-4xl font-bold">7:00</span>
                </div>
                {canControlMatch && (
                  <button
                    onClick={() => whistleSound.play()}
                    className="mt-4 flex items-center justify-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 w-full"
                    disabled={submitting}
                  >
                    <Whistle className="w-5 h-5" />
                    <span>Play Whistle</span>
                  </button>
                )}
              </div>

              {/* Scoreboard */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center">
                  <div className="text-center flex-1">
                    <h3 className="text-xl font-bold mb-2">
                      {getTeamName(gameState.current_match.team_a_id)}
                    </h3>
                    <div className="flex items-center justify-center space-x-4">
                      {canControlMatch && (
                        <>
                          <button
                            onClick={() =>
                              handleScoreChange(
                                gameState.current_match!.team_a_id,
                                "decrement"
                              )
                            }
                            className="text-2xl bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            disabled={submitting}
                          >
                            -
                          </button>
                          <span className="text-4xl font-bold">
                            {getTeamById(gameState.current_match!.team_a_id)
                              ?.score || 0}
                          </span>
                          <button
                            onClick={() =>
                              handleScoreChange(
                                gameState.current_match!.team_a_id,
                                "increment"
                              )
                            }
                            className="text-2xl bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            disabled={submitting}
                          >
                            +
                          </button>
                        </>
                      )}
                      {!canControlMatch && (
                        <span className="text-4xl font-bold">
                          {getTeamById(gameState.current_match!.team_a_id)
                            ?.score || 0}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-gray-400 px-4">
                    vs
                  </div>
                  <div className="text-center flex-1">
                    <h3 className="text-xl font-bold mb-2">
                      {getTeamName(gameState.current_match.team_b_id)}
                    </h3>
                    <div className="flex items-center justify-center space-x-4">
                      {canControlMatch && (
                        <>
                          <button
                            onClick={() =>
                              handleScoreChange(
                                gameState.current_match!.team_b_id,
                                "decrement"
                              )
                            }
                            className="text-2xl bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            disabled={submitting}
                          >
                            -
                          </button>
                          <span className="text-4xl font-bold">
                            {getTeamById(gameState.current_match!.team_b_id)
                              ?.score || 0}
                          </span>
                          <button
                            onClick={() =>
                              handleScoreChange(
                                gameState.current_match!.team_b_id,
                                "increment"
                              )
                            }
                            className="text-2xl bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            disabled={submitting}
                          >
                            +
                          </button>
                        </>
                      )}
                      {!canControlMatch && (
                        <span className="text-4xl font-bold">
                          {getTeamById(gameState.current_match!.team_b_id)
                            ?.score || 0}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Match Officials */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="grid grid-cols-1 gap-6">
                  <div className="text-center">
                    <h3 className="font-semibold text-lg mb-2">Referee</h3>
                    <div className="bg-gray-100 rounded-lg p-4">
                      {gameState.referee ? (
                        <p className="text-gray-800">
                          Referee ID: {gameState.referee}
                        </p>
                      ) : (
                        <p className="text-gray-500">No referee assigned</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* No Current Match - Show Available Teams */
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Users className="w-5 h-5 text-blue-600 mr-2" />
                Start New Match
              </h2>
              {availableTeams.length >= 2 ? (
                <div className="space-y-4">
                  <p className="text-gray-600">
                    Select two teams to start a match:
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    {availableTeams.slice(0, 2).map((team) => (
                      <div
                        key={team.id}
                        className="bg-gray-50 p-4 rounded-lg text-center"
                      >
                        <h3 className="font-semibold">{team.name}</h3>
                        <p className="text-sm text-gray-600">
                          Team {team.team_number}
                        </p>
                      </div>
                    ))}
                  </div>
                  {canControlMatch && (
                    <button
                      onClick={() =>
                        handleStartMatch(
                          availableTeams[0].id,
                          availableTeams[1].id
                        )
                      }
                      className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
                      disabled={submitting}
                    >
                      {submitting ? "Starting..." : "Start Match"}
                    </button>
                  )}
                </div>
              ) : (
                <p className="text-gray-600">
                  Not enough teams available to start a match.
                </p>
              )}
            </div>
          )}

          {/* Coin Toss UI */}
          {gameState.coin_toss_state?.pending && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Crown className="w-5 h-5 text-yellow-600 mr-2" />
                Coin Toss Required
              </h2>
              <div className="space-y-4">
                <p className="text-gray-600">
                  The previous match ended in a draw. A coin toss is required to
                  determine who plays next.
                </p>

                {!coinTossMode ? (
                  <button
                    onClick={() => setCoinTossMode(true)}
                    className="w-full bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700"
                    disabled={!isAdmin}
                  >
                    {isAdmin ? "Start Coin Toss" : "Admin Only"}
                  </button>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <h3 className="font-semibold mb-2">
                          {getTeamName(gameState.coin_toss_state.team_a_id)}
                        </h3>
                        <div className="space-y-2">
                          <button
                            onClick={() =>
                              setCoinTossChoices((prev) => ({
                                ...prev,
                                team_a_choice: "heads",
                              }))
                            }
                            className={`w-full p-2 rounded ${
                              coinTossChoices.team_a_choice === "heads"
                                ? "bg-blue-600 text-white"
                                : "bg-gray-200"
                            }`}
                          >
                            Heads
                          </button>
                          <button
                            onClick={() =>
                              setCoinTossChoices((prev) => ({
                                ...prev,
                                team_a_choice: "tails",
                              }))
                            }
                            className={`w-full p-2 rounded ${
                              coinTossChoices.team_a_choice === "tails"
                                ? "bg-blue-600 text-white"
                                : "bg-gray-200"
                            }`}
                          >
                            Tails
                          </button>
                        </div>
                      </div>
                      <div className="text-center">
                        <h3 className="font-semibold mb-2">
                          {getTeamName(gameState.coin_toss_state.team_b_id)}
                        </h3>
                        <div className="space-y-2">
                          <button
                            onClick={() =>
                              setCoinTossChoices((prev) => ({
                                ...prev,
                                team_b_choice: "heads",
                              }))
                            }
                            className={`w-full p-2 rounded ${
                              coinTossChoices.team_b_choice === "heads"
                                ? "bg-blue-600 text-white"
                                : "bg-gray-200"
                            }`}
                          >
                            Heads
                          </button>
                          <button
                            onClick={() =>
                              setCoinTossChoices((prev) => ({
                                ...prev,
                                team_b_choice: "tails",
                              }))
                            }
                            className={`w-full p-2 rounded ${
                              coinTossChoices.team_b_choice === "tails"
                                ? "bg-blue-600 text-white"
                                : "bg-gray-200"
                            }`}
                          >
                            Tails
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-4">
                      <button
                        onClick={handleCoinToss}
                        className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
                        disabled={
                          submitting ||
                          !coinTossChoices.team_a_choice ||
                          !coinTossChoices.team_b_choice
                        }
                      >
                        {submitting ? "Tossing..." : "Toss Coin"}
                      </button>
                      <button
                        onClick={() => setCoinTossMode(false)}
                        className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-8">
          {/* Upcoming Match Card */}
          {gameState.upcoming_match && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <Clock className="w-5 h-5 text-purple-600 mr-2" />
                Upcoming Match
              </h2>
              <div className="space-y-4">
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-purple-600 mb-2">Next Up</p>
                  <p className="text-xl font-bold">
                    {getTeamName(gameState.upcoming_match.team_a_id)} vs{" "}
                    {getTeamName(gameState.upcoming_match.team_b_id)}
                  </p>
                  {gameState.upcoming_match.coin_toss_winner && (
                    <p className="text-sm text-yellow-600 mt-2">
                      Coin toss winner
                    </p>
                  )}
                </div>
                {canControlMatch && (
                  <button
                    onClick={() =>
                      handleStartMatch(
                        gameState.upcoming_match!.team_a_id,
                        gameState.upcoming_match!.team_b_id
                      )
                    }
                    className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700"
                    disabled={submitting}
                  >
                    {submitting ? "Starting..." : "Start Match"}
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Completed Matches Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              Completed Matches
            </h2>
            <div className="space-y-4">
              {gameState.completed_matches.length > 0 ? (
                gameState.completed_matches.map((match, index) => (
                  <div
                    key={index}
                    className="border-b last:border-b-0 pb-4 last:pb-0"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-500">
                        {new Date(
                          match.completed_at || ""
                        ).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="text-center flex-1 relative">
                        <p className="font-medium">
                          {getTeamName(match.team_a_id)}
                        </p>
                        <p className="text-2xl font-bold text-purple-600">
                          {match.team_a_score || 0}
                        </p>
                        {match.winner_id === match.team_a_id && (
                          <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                            WINNER
                          </div>
                        )}
                      </div>
                      <div className="text-gray-400 px-2">vs</div>
                      <div className="text-center flex-1 relative">
                        <p className="font-medium">
                          {getTeamName(match.team_b_id)}
                        </p>
                        <p className="text-2xl font-bold text-purple-600">
                          {match.team_b_score || 0}
                        </p>
                        {match.winner_id === match.team_b_id && (
                          <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                            WINNER
                          </div>
                        )}
                      </div>
                    </div>
                    {match.is_draw && (
                      <p className="text-sm text-yellow-600 text-center mt-2">
                        Draw
                      </p>
                    )}
                    <p className="text-sm text-gray-500 text-center mt-2">
                      Referee: {match.referee_id || "Not assigned"}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center">
                  No completed matches yet.
                </p>
              )}
            </div>
          </div>

          {/* Available Teams */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Users className="w-5 h-5 text-blue-600 mr-2" />
              Available Teams ({availableTeams.length})
            </h2>
            <div className="space-y-2">
              {availableTeams.map((team) => (
                <div
                  key={team.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{team.name}</p>
                    <p className="text-sm text-gray-600">
                      Team {team.team_number}
                    </p>
                  </div>
                  {team.captain_id && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Captain
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveMatchPage;
