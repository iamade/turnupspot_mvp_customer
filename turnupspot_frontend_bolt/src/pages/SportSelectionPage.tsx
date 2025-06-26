import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Search, Loader2 } from "lucide-react";
import { get } from "../api";
import { Sport } from "../types";

// Sport images mapping
const sportImages: Record<string, string> = {
  Football:
    "https://images.pexels.com/photos/46798/the-ball-stadion-football-the-pitch-46798.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  Basketball:
    "https://images.pexels.com/photos/358042/pexels-photo-358042.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  Tennis:
    "https://images.pexels.com/photos/8224691/pexels-photo-8224691.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  "Table Tennis":
    "https://images.pexels.com/photos/3660204/pexels-photo-3660204.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  Volleyball:
    "https://images.pexels.com/photos/1263426/pexels-photo-1263426.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  Badminton:
    "https://images.pexels.com/photos/3660204/pexels-photo-3660204.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  Cricket:
    "https://images.pexels.com/photos/3659097/pexels-photo-3659097.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
};

const SportSelectionPage = () => {
  const [sports, setSports] = useState<Sport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchSports();
  }, []);

  const fetchSports = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await get<Sport[]>("/sports/");
      setSports(response.data);
    } catch (err) {
      console.error("Error fetching sports:", err);
      setError("Failed to load sports. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const filteredSports = sports.filter((sport) =>
    sport.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getSportDescription = (sport: Sport) => {
    if (sport.type === "Team") {
      return `${sport.max_players_per_team || "Multiple"} players per team`;
    } else {
      return `${sport.players_per_match || 2} players per match`;
    }
  };

  const getSportSubtext = (sport: Sport) => {
    if (sport.type === "Team") {
      return `Minimum ${sport.min_teams || 2} teams`;
    } else {
      return sport.requires_referee ? "Referee required" : "No referee needed";
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <span className="ml-2 text-gray-600">Loading sports...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchSports}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Select Your Sport</h1>
        <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
      </div>

      <div className="relative mb-8">
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
          size={20}
        />
        <input
          type="text"
          placeholder="Search for a sport..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-gray-50 rounded-xl border-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {filteredSports.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">
            {searchTerm
              ? "No sports found matching your search."
              : "No sports available."}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredSports.map((sport) => (
            <Link
              key={sport.id}
              to={`/sports/create?type=${sport.name
                .toLowerCase()
                .replace(/\s+/g, "-")}`}
              className="flex items-center justify-between bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-1">{sport.name}</h3>
                <p className="text-sm text-gray-500">
                  {getSportDescription(sport)}
                </p>
                <p className="text-sm text-gray-400">
                  {getSportSubtext(sport)}
                </p>
                <button className="mt-2 px-4 py-1 text-sm text-indigo-600 bg-indigo-50 rounded-full hover:bg-indigo-100 transition-colors">
                  Create Group
                </button>
              </div>
              <div className="w-24 h-24 ml-4">
                <img
                  src={
                    sportImages[sport.name] ||
                    "https://images.pexels.com/photos/46798/the-ball-stadion-football-the-pitch-46798.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
                  }
                  alt={sport.name}
                  className="w-full h-full object-cover rounded-lg"
                />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default SportSelectionPage;
