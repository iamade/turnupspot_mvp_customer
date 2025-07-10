import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { get, post } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";
import {
  Users,
  Calendar,
  Trophy,
  MessageSquare,
  ArrowLeft,
} from "lucide-react";

interface SportGroup {
  id: string;
  name: string;
  description?: string;
  venue_name: string;
  venue_address: string;
  venue_image_url?: string;
  playing_days: string;
  game_start_time: string;
  game_end_time: string;
  max_teams: number;
  max_players_per_team: number;
  rules?: string;
  referee_required: boolean;
  sports_type: string;
  member_count?: number;
  current_user_membership?: {
    is_member: boolean;
    is_pending: boolean;
    role: string | null;
    is_creator: boolean;
  } | null;
}

const SportGroupDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [group, setGroup] = useState<SportGroup | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [joining, setJoining] = useState(false);
  const [leaving, setLeaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    get(
      `/sport-groups/${id}`,
      token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
    )
      .then((res) => setGroup(res.data as SportGroup))
      .catch(() => setError("Group not found"))
      .finally(() => setLoading(false));
  }, [id, token]);

  const handleJoinGroup = async () => {
    if (!id || !user || !token) return;
    setJoining(true);
    try {
      await post(
        `/sport-groups/${id}/join`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Join request submitted successfully!");
      // Refresh group data to update membership status
      const res = await get(`/sport-groups/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGroup(res.data as SportGroup);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to join group";
      toast.error(errorMessage);
    } finally {
      setJoining(false);
    }
  };

  const handleLeaveGroup = async () => {
    if (!id || !user || !token) return;
    setLeaving(true);
    try {
      await post(
        `/sport-groups/${id}/leave`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Left group successfully!");
      // Refresh group data to update membership status
      const res = await get(`/sport-groups/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGroup(res.data as SportGroup);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to leave group";
      toast.error(errorMessage);
    } finally {
      setLeaving(false);
    }
  };

  const handleDeleteGroup = async () => {
    if (!id) return;
    if (
      !window.confirm(
        "Are you sure you want to delete this group? This action cannot be undone."
      )
    )
      return;
    try {
      await post(`/sport-groups/${id}`, {}, { method: "DELETE" });
      toast.success("Group deleted successfully!");
      navigate("/sports/groups");
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to delete group";
      toast.error(errorMessage);
    }
  };

  if (loading) return <div className="text-center py-12">Loading...</div>;

  if (error || !group) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Group not found</h2>
        <Link
          to="/sports/groups"
          className="text-indigo-600 hover:text-indigo-800 mt-4 inline-block"
        >
          Return to Sports Groups
        </Link>
      </div>
    );
  }

  // Mock previous games data (optional, or fetch from backend if available)
  const previousGames = [
    {
      id: 1,
      date: "2024-03-10",
      teams: {
        team1: { name: "Team 1", score: 3 },
        team2: { name: "Team 2", score: 2 },
      },
    },
    {
      id: 2,
      date: "2024-03-03",
      teams: {
        team1: { name: "Team 3", score: 1 },
        team2: { name: "Team 4", score: 1 },
      },
    },
  ];

  const isGameDay = true;
  const isAdmin =
    group?.current_user_membership?.role === "admin" ||
    group?.current_user_membership?.is_creator;

  return (
    <div className="space-y-8 max-w-2xl mx-auto px-4">
      <Link
        to="/sports/groups"
        className="inline-flex items-center text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Sports Groups
      </Link>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="h-48 relative">
          <img
            src={
              group.venue_image_url ||
              "https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
            }
            alt={group.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        </div>

        <div className="p-6 relative">
          <div className="flex justify-between items-center mb-2">
            <div>
              <h1 className="text-3xl font-bold inline-block">{group.name}</h1>
              {isAdmin && (
                <button
                  className="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 inline-block"
                  onClick={() => navigate(`/sports/groups/${group.id}/edit`)}
                >
                  Update Group
                </button>
              )}
            </div>
            <div className="space-x-4">
              {group?.current_user_membership?.is_member ? (
                <>
                  {group.current_user_membership.role !== "admin" && (
                    <button
                      onClick={handleLeaveGroup}
                      disabled={
                        leaving || group.current_user_membership.is_creator
                      }
                      className="px-4 py-2 border border-red-500 text-red-500 rounded-lg hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {leaving ? "Leaving..." : "Leave Group"}
                    </button>
                  )}
                  {group.current_user_membership.role !== "admin" &&
                    group.current_user_membership.is_creator && (
                      <button
                        onClick={handleDeleteGroup}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 ml-2"
                      >
                        Delete Group
                      </button>
                    )}
                </>
              ) : group?.current_user_membership?.is_pending ? (
                <button
                  disabled
                  className="px-4 py-2 bg-gray-400 text-white rounded-lg cursor-not-allowed"
                >
                  Request Pending
                </button>
              ) : (
                <button
                  onClick={() => {
                    if (!user) {
                      navigate("/signin");
                    } else {
                      handleJoinGroup();
                    }
                  }}
                  disabled={joining}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {joining ? "Joining..." : "Join Group"}
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <Link
              to={`/sports/groups/${id}/members`}
              className="bg-purple-50 p-4 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <Users className="text-purple-600 mb-2" />
              <h3 className="font-semibold">Members</h3>
              <p className="text-purple-600">
                {group.member_count || 0} players
              </p>
            </Link>

            {/* Disabled Game Day Card */}
            <div
              className="bg-gray-100 p-4 rounded-lg cursor-not-allowed opacity-60"
              title="Game Day is disabled"
            >
              <Calendar className="text-gray-400 mb-2" />
              <h3 className="font-semibold text-gray-500">
                Game Day (Disabled)
              </h3>
              <p className="text-gray-500">Not available</p>
            </div>

            {/* Disabled Tournament Card */}
            <div
              className="bg-gray-100 p-4 rounded-lg cursor-not-allowed opacity-60"
              title="Tournament is disabled"
            >
              <Trophy className="text-gray-400 mb-2" />
              <h3 className="font-semibold text-gray-500">
                Tournament (Disabled)
              </h3>
              <p className="text-gray-500">Not available</p>
            </div>

            {/* Disabled Group Chat Card */}
            <div
              className="bg-gray-100 p-4 rounded-lg cursor-not-allowed opacity-60"
              title="Group Chat is disabled"
            >
              <MessageSquare className="text-gray-400 mb-2" />
              <h3 className="font-semibold text-gray-500">
                Group Chat (Disabled)
              </h3>
              <p className="text-gray-500">Not available</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Upcoming Games</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((game) => (
              <div key={game} className="border-b pb-4 last:border-b-0">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">Regular 5-a-side</h3>
                    <p className="text-gray-600">Saturday, 2PM</p>
                  </div>
                  <button className="px-3 py-1 border border-purple-600 text-purple-600 rounded hover:bg-purple-50">
                    RSVP
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Previous Games</h2>
          <div className="space-y-4">
            {previousGames.map((game) => (
              <div key={game.id} className="border-b pb-4 last:border-b-0">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-600">{game.date}</span>
                  <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                    Final Score
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">{game.teams.team1.name}</h3>
                    <p className="text-2xl font-bold text-purple-600">
                      {game.teams.team1.score}
                    </p>
                  </div>
                  <div className="text-gray-400 text-xl font-bold">vs</div>
                  <div className="text-right">
                    <h3 className="font-semibold">{game.teams.team2.name}</h3>
                    <p className="text-2xl font-bold text-purple-600">
                      {game.teams.team2.score}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SportGroupDetailsPage;
