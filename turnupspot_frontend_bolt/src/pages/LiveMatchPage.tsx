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
  AlertTriangle,
} from "lucide-react";
import { Howl } from "howler";
import { useAuth } from "../contexts/AuthContext";
import { gameAPI } from "../api";
import { toast } from "react-toastify";

interface SuggestedTeamsResponse {
  suggested_teams: AvailableTeam[];
  team_a: AvailableTeam;
  team_b: AvailableTeam;
  reason: string;
  is_knockout_stage: boolean;
}

interface Team {
  id: string;
  name: string;
  team_number: number;
  captain_id?: number;
  score: number;
}

interface AvailableTeam {
  id: string;
  name: string;
  team_number: number;
  captain_id?: number;
  player_count?: number; // Add player count
}

interface GameState {
  current_match: Match | null;
  upcoming_match: {
    team_a_id: string;
    team_b_id: string;
    team_a_name: string;
    team_b_name: string;
    requires_coin_toss?: boolean;
    is_knockout_stage?: boolean; // Add knockout stage indicator
  } | null;
  completed_matches: Match[];
  referee: number | null;
  coin_toss_state: {
    pending?: boolean;
    team_a_id?: string;
    team_b_id?: string;
    result?: string;
    winner?: string;
    loser?: string;
  } | null;
  teams: string[];
  team_details: {
    [key: string]: {
      id: string;
      name: string;
      team_number: number;
      captain_id?: number;
      player_count?: number; // Add player count
    };
  };
  available_teams: AvailableTeam[];
  players: number[];
  can_control_match: boolean;
  referee_info: {
    name: string;
    team: string;
    user_id?: number;
  };
  match_timer?: {
    remaining_seconds: number;
    is_running: boolean;
    started_at?: string;
  };
  is_knockout_stage?: boolean; // Add knockout stage indicator
  total_teams_with_players?: number;
}

interface Match {
  team_a_id: string;
  team_b_id: string;
  team_a_name?: string;
  team_b_name?: string;
  team_a_score?: number;
  team_b_score?: number;
  winner_id?: string;
  is_draw?: boolean;
  referee_id?: number;
  completed_at?: string;
  started_at?: string;
}

interface AvailableTeam {
  id: string;
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

// interface GameResponse {
//   teams: any[]; // or define a proper Team interface
//   // add other properties as needed
// }

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
  const [gameId, setGameId] = useState<string | null>(null);

  const [timeRemaining, setTimeRemaining] = useState<number>(420); // 7 minutes in seconds
  const [isTimerRunning, setIsTimerRunning] = useState<boolean>(false);
  const [isTimerPaused, setIsTimerPaused] = useState<boolean>(false);
  const [matchEnded, setMatchEnded] = useState<boolean>(false);
  const [gameDayInfo, setGameDayInfo] = useState<GameDayInfo | null>(null);

  // Add this function to fetch game day info:
  const fetchGameDayInfo = async () => {
    console.log("fetchGameDayInfo called");
    if (!id) return;

    try {
      const response = await gameAPI.getGameDayInfo(id);
      setGameDayInfo(response.data as GameDayInfo);
    } catch (error) {
      console.error("Error fetching game day info:", error);
    }
  };

  // Update the useEffect to also fetch game day info:
  useEffect(() => {
    console.log("Polling fetchGameState and fetchGameDayInfo");
    fetchGameState();
    fetchGameDayInfo();
    // Poll for updates every 5 seconds
    const interval = setInterval(() => {
      fetchGameState();
      fetchGameDayInfo();
    }, 5000);
    return () => clearInterval(interval);
  }, [id, token]);

  // Fetch timer status from server
  const fetchTimerStatus = async () => {
    console.log("fetchTimerStatus called");
    if (!gameId) return;

    try {
      const response = await gameAPI.getTimerStatus(gameId);

      const { is_running, remaining_seconds, timer_expired, started_at } =
        response.data as {
          is_running: boolean;
          remaining_seconds: number;
          timer_expired: boolean;
          started_at?: string;
        };

      setTimeRemaining(remaining_seconds);
      setIsTimerRunning(is_running && !timer_expired);
      // If timer has been started before but is not currently running, it's paused
      setIsTimerPaused(!!started_at && !is_running && !timer_expired);

      if (timer_expired && is_running) {
        handleTimerExpired();
      }
    } catch (error) {
      console.error("Error fetching timer status:", error);
    }
  };

  const [suggestedTeams, setSuggestedTeams] = useState<{
    team_a: AvailableTeam | null;
    team_b: AvailableTeam | null;
    reason: string;
    is_knockout_stage: boolean;
  } | null>(null);

  // Update useEffect to fetch timer status on mount and periodically
  useEffect(() => {
    console.log("Polling fetchTimerStatus");
    if (gameId) {
      fetchTimerStatus();
      const timerStatusInterval = setInterval(fetchTimerStatus, 2000); // Sync every 2 seconds

      return () => clearInterval(timerStatusInterval);
    }
  }, [gameId, token]);

  // Add function to fetch suggested teams:
  const fetchSuggestedTeams = async () => {
    if (!gameId) return;

    try {
      const response = await gameAPI.getSuggestedTeams(gameId);

      const data = response.data as SuggestedTeamsResponse;
      setSuggestedTeams({
        team_a: data.team_a,
        team_b: data.team_b,
        reason: data.reason,
        is_knockout_stage: data.is_knockout_stage,
      });
    } catch (error) {
      console.error("Error fetching suggested teams:", error);
      // Fallback to first two available teams that haven't played
      const playedTeamIds = new Set(
        gameState?.completed_matches.flatMap(match => [match.team_a_id, match.team_b_id]) || []
      );
      const availableUnplayedTeams = availableTeams.filter(team => !playedTeamIds.has(team.id));
      if (availableUnplayedTeams.length >= 2) {
        setSuggestedTeams({
          team_a: availableUnplayedTeams[0],
          team_b: availableUnplayedTeams[1],
          reason: "Default selection",
          is_knockout_stage: false,
        });
      }
    }
  };

  // Update useEffect to fetch suggested teams:
  useEffect(() => {
    if (gameId && !gameState?.current_match && availableTeams.length >= 2) {
      fetchSuggestedTeams();
    }
  }, [gameId, gameState?.current_match, availableTeams]);

  // Start match timer
  const handleStartTimer = async () => {
    if (!gameId || !canControlMatch) return;

    try {
      await gameAPI.startTimer(gameId);

      // Play whistle sound
      whistleSound.play();
      toast.success("Match started!");

      // Start frontend timer
      setIsTimerRunning(true);
      setIsTimerPaused(false);
    } catch (error) {
      console.error("Error starting timer:", error);
      toast.error("Failed to start match timer");
    }
  };

  // Pause match timer
  const handlePauseTimer = async () => {
    if (!gameId || !canControlMatch) return;

    try {
      await gameAPI.updateTimer(gameId, { action: "pause" });
      toast.info("Match paused");
      setIsTimerRunning(false);
      setIsTimerPaused(true);
    } catch (error) {
      console.error("Error pausing timer:", error);
      toast.error("Failed to pause match timer");
    }
  };

  // Resume match timer
  const handleResumeTimer = async () => {
    if (!gameId || !canControlMatch) return;

    try {
      await gameAPI.updateTimer(gameId, { action: "resume" });
      toast.success("Match resumed!");
      setIsTimerRunning(true);
      setIsTimerPaused(false);
    } catch (error) {
      console.error("Error resuming timer:", error);
      toast.error("Failed to resume match timer");
    }
  };

  // Timer countdown effect
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isTimerRunning && !isTimerPaused && timeRemaining > 0 && !matchEnded) {
      interval = setInterval(() => {
        setTimeRemaining((prev) => {
          const newTime = prev - 1;
          if (newTime <= 0) {
            setIsTimerRunning(false);
            handleTimerExpired();
            return 0;
          }
          return newTime;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, isTimerPaused, timeRemaining, matchEnded]);

  // Add function to handle match ending
  const handleEndMatch = async () => {
    if (!gameId) return;

    try {
      const response = await gameAPI.endMatch(gameId);

      const { match_result } = response.data as {
        match_result: {
          is_draw?: boolean;
          team_a_score?: number;
          team_b_score?: number;
          winner_id?: string;
        };
        next_match?: unknown;
      };

      if (
        match_result.is_draw &&
        match_result.team_a_score === 0 &&
        match_result.team_b_score === 0
      ) {
        toast.info("Match ended 0-0 - Both teams are out!");
      } else if (match_result.winner_id) {
        const winnerName = getTeamName(match_result.winner_id);
        toast.success(`${winnerName} wins and advances!`);
      }

      // Reset timer state
      setTimeRemaining(420);
      setIsTimerRunning(false);
      setMatchEnded(false);

      // Refresh game state
      await fetchGameState();
    } catch (error) {
      console.error("Error ending match:", error);
      toast.error("Failed to end match");
    }
  };

  // Update handleTimerExpired
  const handleTimerExpired = async () => {
    if (!gameState?.current_match) return;

    const teamAScore = gameState.current_match.team_a_score || 0;
    const teamBScore = gameState.current_match.team_b_score || 0;

    if (teamAScore === 0 && teamBScore === 0) {
      // Both teams out - both teams leave
      toast.info("Time's up! No goals scored - both teams are out!");
    } else if (teamAScore === teamBScore) {
      // Draw with goals - coin toss needed
      toast.info("Time's up! Match ended in a draw - coin toss required!");
    } else if (teamAScore > teamBScore) {
      // Team A wins
      toast.info(
        `Time's up! ${getTeamName(gameState.current_match.team_a_id)} wins!`
      );
    } else if (teamBScore > teamAScore) {
      // Team B wins
      toast.info(
        `Time's up! ${getTeamName(gameState.current_match.team_b_id)} wins!`
      );
    }

    setMatchEnded(true);
    await handleEndMatch();
  };

  // Add function to check for 2-goal lead
  const checkForTwoGoalLead = () => {
    if (!gameState?.current_match) return;

    const teamAScore = gameState.current_match.team_a_score || 0;
    const teamBScore = gameState.current_match.team_b_score || 0;

    if (Math.abs(teamAScore - teamBScore) >= 2) {
      const winner =
        teamAScore > teamBScore
          ? getTeamName(gameState.current_match.team_a_id)
          : getTeamName(gameState.current_match.team_b_id);

      toast.info(`${winner} wins with a 2-goal lead!`);
      setIsTimerRunning(false);
      setMatchEnded(true);
      handleEndMatch();
    }
  };

  // Call checkForTwoGoalLead whenever game state updates
  useEffect(() => {
    if (gameState?.current_match) {
      checkForTwoGoalLead();
    }
  }, [
    gameState?.current_match?.team_a_score,
    gameState?.current_match?.team_b_score,
  ]);

  const whistleSound = new Howl({
    src: ["/sounds/whistle.mp3", "/sounds/whistle.wav", "/sounds/whistle.ogg"],
    html5: true,
    volume: 0.8,
    onloaderror: () => {
      console.warn("Could not load whistle sound file");
    },
  });

  useEffect(() => {
    if (gameState?.coin_toss_state?.pending && !coinTossMode) {
      setCoinTossMode(false);
      setCoinTossChoices({ team_a_choice: "", team_b_choice: "" });
    }
  }, [gameState?.coin_toss_state?.pending, coinTossMode]);

  // Format timer display
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  const fetchGameState = async () => {
    console.log("fetchGameState called");
    if (!id) return;

    try {
      // Get the game day info to get the actual game ID
      const gameDayResponse = await gameAPI.getGameDayInfo(id);
      const actualGameId = (gameDayResponse.data as GameDayInfo)
        .current_game_id;

      if (!actualGameId) {
        throw new Error("No active game found for today");
      }

      // Store the actual game ID
      setGameId(actualGameId);

      // Get the game state with team details
      const response = await gameAPI.getGameState(actualGameId);
      setGameState(response.data as GameState);

      // Check if coin toss is required immediately after fetching state
      if (
        (response.data as GameState).coin_toss_state?.pending &&
        !coinTossMode
      ) {
        // Force UI update to show coin toss section
        setCoinTossMode(false);
        toast.info("Coin toss required to determine next match!");
      }

      // Filter available teams to only show teams with players
      const teamsWithPlayers = (
        (response.data as GameState).available_teams || []
      ).filter((team: AvailableTeam) => {
        return team.player_count && team.player_count > 0;
      });

      // Set available teams from the game state
      setAvailableTeams(teamsWithPlayers);

      // Try to fetch teams data
      try {
        const teamsResponse = await gameAPI.getGameTeams(actualGameId);
        setTeams((teamsResponse.data as { teams: Team[] }).teams || []);
      } catch (teamError) {
        console.warn("Could not fetch teams data:", teamError);
        // Use team details from game state as fallback
        const gameStateData = response.data as GameState;
        if (gameStateData.team_details) {
          const teamArray = Object.values(gameStateData.team_details).map(
            (team: any) => ({
              id: team.id,
              name: team.name,
              team_number: team.team_number,
              captain_id: team.captain_id,
              score: 0, // Default score
            })
          );
          setTeams(teamArray as Team[]);
        }
      }
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
  const isAdmin =
    user?.role === "admin" ||
    gameDayInfo?.current_user_membership?.role === "admin" ||
    gameDayInfo?.current_user_membership?.is_creator ||
    gameState?.can_control_match;

  const canControlMatch = gameState?.can_control_match || isAdmin;

  // Simplified referee info function
  const getCurrentRefereeInfo = () => {
    return gameState?.referee_info || { name: "No referee assigned", team: "" };
  };

  // Get team name by ID
  const getTeamName = (teamId: number | string | undefined) => {
    if (!teamId) return "Unknown Team";
    // First check if we have team details from the game state
    if (gameState?.team_details && gameState.team_details[teamId]) {
      return gameState.team_details[teamId].name;
    }

    // Fallback to checking the teams array
    const team = teams.find((team) => team.id === teamId);
    if (team) {
      return team.name;
    }

    // Final fallback
    return `Team ${teamId}`;
  };

  // Start match
  const handleStartMatch = async (teamAId: string, teamBId: string) => {
    if (!gameId || !canControlMatch) return;

    setSubmitting(true);
    try {
      whistleSound.play();

      // Start the timer first as required by backend
      await gameAPI.startTimer(gameId);

      // Then start the match
      await gameAPI.startMatch(gameId, {
        team_a_id: teamAId,
        team_b_id: teamBId,
      });

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
    teamId: string,
    action: "increment" | "decrement" | "set",
    value?: number
  ) => {
    if (!gameId || !canControlMatch) return;

    setSubmitting(true);
    try {
      const response = await gameAPI.updateScore(gameId, {
        team_id: teamId,
        action,
        value,
      });

      const data = response.data as {
        match_ended?: boolean;
        next_match?: { requires_coin_toss?: boolean };
        winner_id?: string;
      };

      if (data.match_ended) {
        if (data.next_match?.requires_coin_toss) {
          toast.info("Match ended in a draw - coin toss required!");
        } else if (data.winner_id) {
          const winnerName = getTeamName(data.winner_id);
          toast.success(`${winnerName} wins and advances!`);
        }

        // Reset timer state
        setTimeRemaining(420);
        setIsTimerRunning(false);
        setMatchEnded(false);

        // Wait a moment then refresh state to show next match or coin toss
        setTimeout(() => {
          fetchGameState();
        }, 1000);
      } else {
        toast.success("Score updated!");
        await fetchGameState();
      }
    } catch (error) {
      console.error("Error updating score:", error);
      toast.error("Failed to update score");
    } finally {
      setSubmitting(false);
    }
  };

  // Add new function to start a scheduled match
  const handleStartScheduledMatch = async () => {
    if (!gameId || !canControlMatch) return;

    try {
      await gameAPI.startScheduledMatch(gameId);

      toast.success("New match started!");
      await fetchGameState();
    } catch (error) {
      console.error("Error starting scheduled match:", error);
      toast.error("Failed to start match");
    }
  };

  // Coin toss
  const handleCoinToss = async () => {
    if (!gameId || !canControlMatch) return;

    if (!coinTossChoices.team_a_choice || !coinTossChoices.team_b_choice) {
      toast.error("Both teams must choose a side");
      return;
    }
    if (coinTossChoices.team_a_choice === coinTossChoices.team_b_choice) {
      toast.error("Teams cannot choose the same side!");
      return;
    }

    setSubmitting(true);
    try {
      const coinTossData = {
        team_a_id: gameState?.coin_toss_state?.team_a_id || "",
        team_b_id: gameState?.coin_toss_state?.team_b_id || "",
        team_a_choice: coinTossChoices.team_a_choice,
        team_b_choice: coinTossChoices.team_b_choice,
        coin_toss_type: (gameState?.coin_toss_state as any)?.coin_toss_type,
      };

      const result = await gameAPI.performCoinToss(gameId, coinTossData);

      const data = result.data as {
        result: string;
        winner_name: string;
        message: string;
        next_match?: { team_a_name: string; team_b_name: string };
      };

      // Show detailed coin toss result
      const message = data.message;

      toast.success(`🪙 ${message}`, { autoClose: 5000 });

      // Show additional info about next match
      if (data.next_match) {
        setTimeout(() => {
          toast.info(
            `Next Match: ${data.next_match!.team_a_name} vs ${
              data.next_match!.team_b_name
            }`,
            { autoClose: 3000 }
          );
        }, 1000);
      }

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

  // Update the grid layout and move available teams to left side
  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <Link
        to={`/my-sports-groups/${id}/game-day`}
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Game Day
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Left Sidebar - Available Teams */}
        <div className="md:col-span-1 space-y-8">
          {/* Available Teams */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Users className="w-5 h-5 text-blue-600 mr-2" />
              Available Teams ({availableTeams.length})
            </h2>
            <div className="space-y-2">
              {availableTeams.length > 0 ? (
                availableTeams.map((team) => (
                  <div
                    key={team.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{team.name}</p>
                      <p className="text-sm text-gray-600">
                        Team {team.team_number} • {team.player_count || 0}{" "}
                        players
                      </p>
                    </div>
                    {team.captain_id && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Captain
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">
                  No teams with players available
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="md:col-span-2 space-y-8">
          {/* Current Match */}
          {gameState.current_match ? (
            <>
              {/* Match Timer */}
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <div className="flex items-center justify-center space-x-4 mb-4">
                  <Timer className="w-6 h-6 text-gray-600" />
                  <span
                    className={`text-4xl font-bold ${
                      timeRemaining <= 60 ? "text-red-500" : ""
                    }`}
                  >
                    {formatTime(timeRemaining)}
                  </span>
                </div>
                {canControlMatch && (
                  <div className="flex space-x-2">
                    {!isTimerRunning && !isTimerPaused && (
                      <button
                        onClick={handleStartTimer}
                        disabled={submitting}
                        className="flex items-center justify-center space-x-2 px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white flex-1"
                      >
                        <Whistle className="w-5 h-5" />
                        <span>Start</span>
                      </button>
                    )}
                    {isTimerRunning && (
                      <button
                        onClick={handlePauseTimer}
                        disabled={submitting}
                        className="flex items-center justify-center space-x-2 px-6 py-3 rounded-lg bg-yellow-600 hover:bg-yellow-700 text-white flex-1"
                      >
                        <span>Pause</span>
                      </button>
                    )}
                    {isTimerPaused && (
                      <button
                        onClick={handleResumeTimer}
                        disabled={submitting}
                        className="flex items-center justify-center space-x-2 px-6 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white flex-1"
                      >
                        <span>Resume</span>
                      </button>
                    )}
                  </div>
                )}
                {!canControlMatch && isTimerRunning && (
                  <div className="text-sm text-gray-600">Match in progress</div>
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
                            disabled={submitting || !!isTimerRunning}
                          >
                            -
                          </button>
                          <span className="text-4xl font-bold">
                            {gameState.current_match.team_a_score || 0}
                          </span>
                          <button
                            onClick={() =>
                              handleScoreChange(
                                gameState.current_match!.team_a_id,
                                "increment"
                              )
                            }
                            className="text-2xl bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            disabled={submitting || !isTimerRunning}
                          >
                            +
                          </button>
                        </>
                      )}
                      {!canControlMatch && (
                        <span className="text-4xl font-bold">
                          {gameState.current_match.team_a_score || 0}
                        </span>
                      )}
                    </div>
                    {/* Add message when buttons are disabled */}
                    {canControlMatch && !isTimerRunning && (
                      <p className="text-xs text-gray-500 mt-2">
                        Start the match to enable scoring
                      </p>
                    )}
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
                            disabled={submitting || !isTimerRunning}
                          >
                            -
                          </button>
                          <span className="text-4xl font-bold">
                            {gameState.current_match.team_b_score || 0}
                          </span>
                          <button
                            onClick={() =>
                              handleScoreChange(
                                gameState.current_match!.team_b_id,
                                "increment"
                              )
                            }
                            className="text-2xl bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            disabled={submitting || !isTimerRunning}
                          >
                            +
                          </button>
                        </>
                      )}
                      {!canControlMatch && (
                        <span className="text-4xl font-bold">
                          {gameState.current_match.team_b_score || 0}
                        </span>
                      )}
                    </div>
                    {/* Add message when buttons are disabled */}
                    {canControlMatch && !isTimerRunning && (
                      <p className="text-xs text-gray-500 mt-2">
                        Start the match to enable scoring
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Match Officials */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="grid grid-cols-1 gap-6">
                  <div className="text-center">
                    <h3 className="font-semibold text-lg mb-2">Referee</h3>
                    <div className="bg-gray-100 rounded-lg p-4">
                      {(() => {
                        const refereeInfo = getCurrentRefereeInfo();
                        return (
                          <>
                            <p className="text-gray-800">{refereeInfo.name}</p>
                            {refereeInfo.team && (
                              <p className="text-sm text-gray-600">
                                {refereeInfo.team}
                              </p>
                            )}
                          </>
                        );
                      })()}
                    </div>
                    {/* Show if current user can control match */}
                    {canControlMatch && (
                      <p className="text-xs text-green-600 mt-2">
                        You can control this match
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* No Current Match - Show Suggested Teams */
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Users className="w-5 h-5 text-blue-600 mr-2" />
                Start New Match
                {suggestedTeams?.is_knockout_stage && (
                  <span className="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                    KNOCKOUT
                  </span>
                )}
              </h2>
              {suggestedTeams?.team_a && suggestedTeams?.team_b ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-sm text-blue-600 font-medium">
                      {suggestedTeams.reason}
                    </p>
                    {suggestedTeams.is_knockout_stage && (
                      <p className="text-xs text-red-600 mt-1">
                        First to 1 goal wins
                      </p>
                    )}
                    {!suggestedTeams.is_knockout_stage && (
                      <p className="text-xs text-green-600 mt-1">
                        2-goal lead wins (minimum 2 goals)
                      </p>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded-lg text-center">
                      <h3 className="font-semibold">
                        {suggestedTeams.team_a.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Team {suggestedTeams.team_a.team_number} •{" "}
                        {suggestedTeams.team_a.player_count || 0} players
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg text-center">
                      <h3 className="font-semibold">
                        {suggestedTeams.team_b.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Team {suggestedTeams.team_b.team_number} •{" "}
                        {suggestedTeams.team_b.player_count || 0} players
                      </p>
                    </div>
                  </div>
                  {canControlMatch && (
                    <button
                      onClick={() =>
                        handleStartMatch(
                          suggestedTeams.team_a!.id,
                          suggestedTeams.team_b!.id
                        )
                      }
                      className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      disabled={submitting}
                    >
                      {submitting ? "Starting..." : "Start Match"}
                    </button>
                  )}
                  {!canControlMatch && (
                    <p className="text-center text-gray-500 text-sm">
                      Only admins can start matches
                    </p>
                  )}

                  {/* Keep the End Match button for admins */}
                  {canControlMatch && !matchEnded && (
                    <button
                      onClick={handleEndMatch}
                      className="w-full mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      End Match
                    </button>
                  )}
                </div>
              ) : availableTeams.length >= 2 ? (
                <div className="space-y-4">
                  <p className="text-gray-600">Loading suggested teams...</p>
                  <div className="grid grid-cols-2 gap-4">
                    {availableTeams.slice(0, 2).map((team) => (
                      <div
                        key={team.id}
                        className="bg-gray-50 p-4 rounded-lg text-center animate-pulse"
                      >
                        <div className="h-4 bg-gray-200 rounded mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-3/4 mx-auto"></div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">
                    Not enough teams with players available to start a match.
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Teams need at least one player to participate.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Coin Toss UI */}
          {gameState.coin_toss_state?.pending && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Crown className="w-5 h-5 text-yellow-600 mr-2" />
                Coin Toss Required
                {(gameState.coin_toss_state as any)?.coin_toss_type ===
                  "draw_decider" && (
                  <span className="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                    DRAW DECIDER
                  </span>
                )}
                {(gameState.coin_toss_state as any)?.coin_toss_type ===
                  "starting_team" && (
                  <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    STARTING TEAM
                  </span>
                )}
              </h2>
              <div className="space-y-4">
                {(gameState.coin_toss_state as any)?.coin_toss_type ===
                "draw_decider" ? (
                  <div className="bg-red-50 p-3 rounded-lg border border-red-200">
                    <p className="text-red-800 font-medium">Draw Scenario</p>
                    <p className="text-red-600 text-sm">
                      These teams drew previously and are meeting again. The
                      coin toss will determine which team gets to choose their
                      starting position or has first possession.
                    </p>
                  </div>
                ) : (gameState.coin_toss_state as any)?.coin_toss_type ===
                  "starting_team" ? (
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                    <p className="text-blue-800 font-medium">
                      Starting Team Selection
                    </p>
                    <p className="text-blue-600 text-sm">
                      The coin toss will determine which team starts the match
                      or has first possession.
                    </p>
                  </div>
                ) : (
                  <p className="text-gray-600">
                    The previous match ended in a draw. A coin toss is required
                    to determine who plays next.
                  </p>
                )}

                {!coinTossMode ? (
                  <button
                    onClick={() => setCoinTossMode(true)}
                    className="w-full bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700"
                    disabled={!canControlMatch}
                  >
                    {canControlMatch ? "Start Coin Toss" : "Admin/Referee Only"}
                  </button>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                      <p className="text-sm text-yellow-800">
                        ⚠️ Teams must choose different sides (one heads, one
                        tails)
                      </p>
                    </div>
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
                            } ${
                              coinTossChoices.team_b_choice === "heads"
                                ? "opacity-50 cursor-not-allowed"
                                : ""
                            }`}
                            disabled={coinTossChoices.team_b_choice === "heads"}
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
                            } ${
                              coinTossChoices.team_b_choice === "tails"
                                ? "opacity-50 cursor-not-allowed"
                                : ""
                            }`}
                            disabled={coinTossChoices.team_b_choice === "tails"}
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
                            } ${
                              coinTossChoices.team_a_choice === "heads"
                                ? "opacity-50 cursor-not-allowed"
                                : ""
                            }`}
                            disabled={coinTossChoices.team_a_choice === "heads"}
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
                            } ${
                              coinTossChoices.team_a_choice === "tails"
                                ? "opacity-50 cursor-not-allowed"
                                : ""
                            }`}
                            disabled={coinTossChoices.team_a_choice === "tails"}
                          >
                            Tails
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-4">
                      <button
                        onClick={handleCoinToss}
                        className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={
                          submitting ||
                          !coinTossChoices.team_a_choice ||
                          !coinTossChoices.team_b_choice ||
                          coinTossChoices.team_a_choice ===
                            coinTossChoices.team_b_choice
                        }
                      >
                        {submitting ? "Tossing..." : "🪙 Toss Coin"}
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

        {/* Right Sidebar - Next Match & Completed Matches */}
        <div className="md:col-span-1 space-y-8">
          {/* Upcoming Match Card */}
          {gameState?.upcoming_match && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <Clock className="w-5 h-5 text-purple-600 mr-2" />
                Next Match
                {gameState.is_knockout_stage && (
                  <span className="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                    KNOCKOUT
                  </span>
                )}
                {(gameState.upcoming_match as any)?.requires_coin_toss && (
                  <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded flex items-center">
                    <Crown className="w-3 h-3 mr-1" />
                    COIN TOSS
                  </span>
                )}
              </h2>
              <div className="space-y-4">
                <div
                  className={`text-center p-4 rounded-lg ${
                    (gameState.upcoming_match as any)?.requires_coin_toss
                      ? "bg-yellow-50 border border-yellow-200"
                      : "bg-purple-50"
                  }`}
                >
                  <p
                    className={`text-sm mb-2 ${
                      (gameState.upcoming_match as any)?.requires_coin_toss
                        ? "text-yellow-600"
                        : "text-purple-600"
                    }`}
                  >
                    Up Next
                  </p>
                  <p className="text-xl font-bold">
                    {getTeamName(gameState.upcoming_match.team_a_id)} vs{" "}
                    {getTeamName(gameState.upcoming_match.team_b_id)}
                  </p>
                  {(gameState.upcoming_match as any)?.requires_coin_toss && (
                    <div className="mt-2 p-2 bg-yellow-100 rounded border border-yellow-300">
                      <p className="text-xs text-yellow-800 flex items-center justify-center">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        Coin toss required - these teams drew previously
                      </p>
                    </div>
                  )}
                  {gameState.is_knockout_stage && (
                    <p className="text-xs text-red-600 mt-2">
                      First to 1 goal wins
                    </p>
                  )}
                  {!gameState.is_knockout_stage &&
                    !(gameState.upcoming_match as any)?.requires_coin_toss && (
                      <p className="text-xs text-blue-600 mt-2">
                        2-goal lead wins
                      </p>
                    )}
                </div>
                <p className="text-xs text-gray-500 text-center">
                  {(gameState.upcoming_match as any)?.requires_coin_toss
                    ? "Coin toss will be performed after current match ends"
                    : "Will start automatically when current match ends"}
                </p>
              </div>
            </div>
          )}

          {/* Completed Matches Card - Updated with winner tag under score */}
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
                    className={`border-b last:border-b-0 pb-4 last:pb-0 ${
                      (match as any).requires_coin_toss
                        ? "bg-yellow-50 p-3 rounded-lg border-yellow-200"
                        : ""
                    }`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-500">
                        {new Date(
                          match.completed_at || ""
                        ).toLocaleTimeString()}
                      </span>
                      {(match as any).requires_coin_toss && (
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded flex items-center">
                          <Crown className="w-3 h-3 mr-1" />
                          Coin Toss
                        </span>
                      )}
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="text-center flex-1">
                        <p className="font-medium">
                          {getTeamName(match.team_a_id)}
                        </p>
                        <p className="text-2xl font-bold text-purple-600">
                          {match.team_a_score || 0}
                        </p>
                        {/* Winner tag moved under score */}
                        {match.winner_id === match.team_a_id && (
                          <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full mt-1 inline-block">
                            WINNER
                          </div>
                        )}
                        {(match as any).coin_toss_winner_id ===
                          match.team_a_id && (
                          <div className="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full mt-1 inline-block ml-1">
                            🪙 WON TOSS
                          </div>
                        )}
                      </div>
                      <div className="text-gray-400 px-2">vs</div>
                      <div className="text-center flex-1">
                        <p className="font-medium">
                          {getTeamName(match.team_b_id)}
                        </p>
                        <p className="text-2xl font-bold text-purple-600">
                          {match.team_b_score || 0}
                        </p>
                        {/* Winner tag moved under score */}
                        {match.winner_id === match.team_b_id && (
                          <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full mt-1 inline-block">
                            WINNER
                          </div>
                        )}
                        {(match as any).coin_toss_winner_id ===
                          match.team_b_id && (
                          <div className="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full mt-1 inline-block ml-1">
                            🪙 WON TOSS
                          </div>
                        )}
                      </div>
                    </div>
                    {match.is_draw && (
                      <p className="text-sm text-yellow-600 text-center mt-2">
                        Draw - Teams return to rotation
                      </p>
                    )}
                    {(match as any).coin_toss_performed_at && (
                      <p className="text-sm text-blue-600 text-center mt-1">
                        Coin toss performed at{" "}
                        {new Date(
                          (match as any).coin_toss_performed_at
                        ).toLocaleTimeString()}
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
        </div>
      </div>
    </div>
  );
};

export default LiveMatchPage;
