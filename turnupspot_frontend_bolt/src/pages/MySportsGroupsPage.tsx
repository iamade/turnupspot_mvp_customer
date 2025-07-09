import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { get, post } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";
import { MapPin, Users, Calendar } from "lucide-react";

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
}

const dayNumberToName = (days: string): string => {
  const dayNames = [
    "Monday", // 0
    "Tuesday", // 1
    "Wednesday", // 2
    "Thursday", // 3
    "Friday", // 4
    "Saturday", // 5
    "Sunday", // 6
  ];
  return days
    .split(",")
    .map((d) => dayNames[parseInt(d, 10)] || "")
    .filter(Boolean)
    .join(", ");
};

const formatTime = (dateTime: string): string => {
  if (!dateTime) return "";
  const timePart = dateTime.includes("T")
    ? dateTime.split("T")[1]
    : dateTime.split(" ")[1] || dateTime;
  return timePart ? timePart.slice(0, 5) : "";
};

const MySportsGroupsPage: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [groups, setGroups] = useState<SportGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      navigate("/signin");
      return;
    }
    setLoading(true);
    get<SportGroup[]>("/sport-groups/my", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => setGroups(res.data))
      .catch(() => setError("Failed to load your sport groups."))
      .finally(() => setLoading(false));
  }, [token, navigate]);

  const handleLeave = async (id: string) => {
    setDeletingId(id);
    try {
      await post(
        `/sport-groups/${id}/leave`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setGroups((prev) => prev.filter((g) => g.id !== id));
      toast.success("Left group successfully!");
    } catch (e) {
      toast.error("Failed to leave group.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-center flex-1">
          Your Sports Groups
        </h1>
        <button
          className="ml-4 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700"
          onClick={() => navigate("/sports/select")}
        >
          Create Group
        </button>
      </div>
      {loading && <div className="text-center">Loading...</div>}
      {error && <div className="text-center text-red-500">{error}</div>}
      {!loading && !error && groups.length === 0 && (
        <div className="text-center text-gray-500 text-lg mt-16">
          You have not joined or created any sport groups yet.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {groups.map((group) => (
          <div
            key={group.id}
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer relative"
          >
            <div className="relative">
              <img
                src={
                  group.venue_image_url ||
                  "https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
                }
                alt={group.name}
                className="w-full h-40 object-cover"
                onClick={() => navigate(`/my-sports-groups/${group.id}`)}
              />
              <span className="absolute top-3 left-3 bg-purple-600 text-white text-xs font-semibold px-3 py-1 rounded-full shadow">
                {group.sports_type}
              </span>
            </div>
            <div
              className="p-6"
              onClick={() => navigate(`/my-sports-groups/${group.id}`)}
            >
              <h2 className="text-xl font-bold mb-2">{group.name}</h2>
              <p className="text-gray-600 mb-2">{group.description}</p>
              <div className="flex items-center text-sm text-gray-500 mb-1">
                <MapPin className="w-4 h-4 mr-1" />
                {group.venue_address}
              </div>
              <div className="flex items-center text-sm text-gray-500 mb-1">
                <Users className="w-4 h-4 mr-1" />
                {group.member_count || 0} members
              </div>
              <div className="flex items-center text-sm text-gray-500">
                <Calendar className="w-4 h-4 mr-1" />
                Next game: {dayNumberToName(group.playing_days)},{" "}
                {formatTime(group.game_start_time)}
              </div>
            </div>
            <button
              className="absolute top-2 right-2 bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-xs z-10"
              onClick={() => handleLeave(group.id)}
              disabled={deletingId === group.id}
            >
              {deletingId === group.id ? "Leaving..." : "Leave Group"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MySportsGroupsPage;
