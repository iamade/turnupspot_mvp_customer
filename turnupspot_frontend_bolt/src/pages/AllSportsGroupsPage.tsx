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
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
            onClick={() => navigate(`/sports/groups/${group.id}`)}
          >
            <img
              src={
                group.venue_image_url ||
                "https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
              }
              alt={group.name}
              className="w-full h-40 object-cover"
            />
            <div className="p-6">
              <h2 className="text-xl font-bold mb-2">{group.name}</h2>
              <p className="text-gray-600 mb-2">{group.description}</p>
              <div className="text-sm text-gray-500 mb-1">
                <span className="font-medium">Venue:</span> {group.venue_name}
              </div>
              <div className="text-xs text-gray-400">{group.venue_address}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AllSportsGroupsPage;
