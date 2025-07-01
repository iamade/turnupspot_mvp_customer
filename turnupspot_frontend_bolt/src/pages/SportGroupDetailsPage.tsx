import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { get } from "../api";
import {
  Users,
  Calendar,
  Trophy,
  MessageSquare,
  ArrowLeft,
} from "lucide-react";

const SportGroupDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    get(`/sport-groups/${id}`)
      .then((res) => setGroup(res.data))
      .catch(() => setError("Group not found"))
      .finally(() => setLoading(false));
  }, [id]);

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
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold">{group.name}</h1>
              <p className="text-gray-600 mt-2">{group.description}</p>
              <p className="text-gray-500 mt-1">
                <span className="font-medium">Venue:</span> {group.venue_name}
              </p>
            </div>
            <div className="space-x-4">
              <button
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                onClick={() => navigate("/sports/groups")}
              >
                Join Group
              </button>
              <button
                onClick={() => navigate("/my-sports-groups")}
                className="px-4 py-2 border border-red-500 text-red-500 rounded-lg hover:bg-red-50"
              >
                Leave Group
              </button>
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

            {isGameDay ? (
              <Link
                to={`/sports/groups/${id}/game-day`}
                className="bg-green-50 p-4 rounded-lg hover:bg-green-100 transition-colors"
              >
                <Calendar className="text-green-600 mb-2" />
                <h3 className="font-semibold">Game Day!</h3>
                <p className="text-green-600">Click to manage</p>
              </Link>
            ) : (
              <div className="bg-purple-50 p-4 rounded-lg">
                <Calendar className="text-purple-600 mb-2" />
                <h3 className="font-semibold">Next Game</h3>
                <p className="text-purple-600">{group.nextGame}</p>
              </div>
            )}

            <div className="bg-purple-50 p-4 rounded-lg">
              <Trophy className="text-purple-600 mb-2" />
              <h3 className="font-semibold">Tournament</h3>
              <p className="text-purple-600">In Progress</p>
            </div>

            <Link
              to={`/sports/groups/${id}/chat`}
              className="bg-purple-50 p-4 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <MessageSquare className="text-purple-600 mb-2" />
              <h3 className="font-semibold">Group Chat</h3>
              <p className="text-purple-600">12 new messages</p>
            </Link>
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
