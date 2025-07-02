import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { get } from "../api";

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

const AllSportsGroupsPage: React.FC = () => {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<SportGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    get<SportGroup[]>("/sport-groups/")
      .then((res) => setGroups(res.data))
      .catch(() => setError("Failed to load sports groups."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-center flex-1">
          All Sports Groups
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
          No sports groups have been created yet. Be the first to create one!
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {groups.map((group) => (
          <div
            key={group.id}
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer relative"
            onClick={() => navigate(`/sports/groups/${group.id}`)}
          >
            <div className="relative">
              <img
                src={
                  group.venue_image_url ||
                  "https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
                }
                alt={group.name}
                className="w-full h-40 object-cover"
              />
              <span className="absolute top-3 left-3 bg-purple-600 text-white text-xs font-semibold px-3 py-1 rounded-full shadow flex items-center gap-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="w-4 h-4 mr-1"
                >
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6l2 4h4l-3 3 1 4-4-2-4 2 1-4-3-3h4z" />
                </svg>
                {group.sports_type}
              </span>
            </div>
            <div className="p-6">
              <h2 className="text-xl font-bold mb-2">{group.name}</h2>
              <p className="text-gray-600 mb-2">{group.description}</p>
              <div className="flex items-center text-sm text-gray-500 mb-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-4 h-4 mr-1"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-3A2.25 2.25 0 008.25 5.25V9m10.5 0v10.5a2.25 2.25 0 01-2.25 2.25H7.5a2.25 2.25 0 01-2.25-2.25V9m13.5 0h-15"
                  />
                </svg>
                {group.venue_address}
              </div>
              <div className="flex items-center text-sm text-gray-500 mb-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-4 h-4 mr-1"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0A5.978 5.978 0 0112 15c1.306 0 2.518.418 3.644 1.143M7.356 16.143A5.978 5.978 0 0112 15m0 0c1.306 0 2.518.418 3.644 1.143"
                  />
                </svg>
                {group.member_count || 0} members
              </div>
              <div className="flex items-center text-sm text-gray-500">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-4 h-4 mr-1"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 6v6l4 2"
                  />
                </svg>
                Next game: {group.playing_days},{" "}
                {typeof group.game_start_time === "string"
                  ? group.game_start_time.slice(0, 5)
                  : ""}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AllSportsGroupsPage;
