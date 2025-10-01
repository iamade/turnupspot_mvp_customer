import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { get } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";
import { MapPin, Users, Calendar, Plus } from "lucide-react";

interface PlayingDay {
  id: string;
  sport_group_id: string;
  day: string;
}

interface SportGroup {
  id: string;
  name: string;
  description?: string;
  venue_name: string;
  venue_address: string;
  venue_image_url?: string;
  playing_days: PlayingDay[];
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

const formatPlayingDays = (days: PlayingDay[]): string => {
  if (!days || !days.length) return 'No days set';
  
  return days
    .map(d => d.day)
    .sort((a, b) => {
      const daysOrder = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'];
      return daysOrder.indexOf(a) - daysOrder.indexOf(b);
    })
    .join(', ');
};

const formatTime = (dateTime: string): string => {
  if (!dateTime) return "";
  const timePart = dateTime.includes("T")
    ? dateTime.split("T")[1]
    : dateTime.split(" ")[1] || dateTime;
  return timePart ? timePart.slice(0, 5) : "";
};

const AllSportsGroupsPage: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [groups, setGroups] = useState<SportGroup[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAllGroups();
  }, [token]);

  const fetchAllGroups = async () => {
    try {
      const response = await get<SportGroup[]>(
        "/sport-groups",
        token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
      );
      setGroups(response.data);
    } catch (error) {
      console.error("Error fetching sport groups:", error);
      setError("Failed to load sport groups.");
      toast.error("Failed to load sport groups.");
    }
  };

  const handleJoinGroup = async (groupId: string, e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigation to group details
    e.stopPropagation();
    
    if (!token) {
      navigate("/signin");
      return;
    }

    try {
      await get(
        `/sport-groups/${groupId}/join`,
        { 
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` } 
        }
      );
      toast.success("Join request submitted successfully!");
      
      // Refresh the groups data to update membership status
      fetchAllGroups();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Failed to join group";
      toast.error(errorMessage);
    }
  };

  const getMembershipStatus = (group: SportGroup) => {
    if (!group.current_user_membership) return null;
    
    if (group.current_user_membership.is_member) {
      return "member";
    } else if (group.current_user_membership.is_pending) {
      return "pending";
    }
    return null;
  };

  const renderMembershipButton = (group: SportGroup) => {
    const status = getMembershipStatus(group);
    
    if (status === "member") {
      return (
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
          Member
        </span>
      );
    } else if (status === "pending") {
      return (
        <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
          Pending
        </span>
      );
    } else {
      return (
        <button
          onClick={(e) => handleJoinGroup(group.id, e)}
          className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm hover:bg-purple-700 transition-colors"
        >
          Join
        </button>
      );
    }
  };

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-500 text-lg">{error}</p>
          <button
            onClick={fetchAllGroups}
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">All Sports Groups</h1>
        <button
          className="flex items-center space-x-2 px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
          onClick={() => navigate("/sports/select")}
        >
          <Plus className="w-5 h-5" />
          <span>Create Group</span>
        </button>
      </div>

      {groups.length === 0 ? (
        <div className="text-center py-16">
          <div className="max-w-md mx-auto">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Sport Groups Yet</h3>
            <p className="text-gray-600 mb-6">
              Be the first to create a sport group and start building your community!
            </p>
            <button
              onClick={() => navigate("/sports/select")}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
            >
              Create First Group
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {groups.map((group) => (
            <Link
              key={group.id}
              to={`/sports/groups/${group.id}`}
              className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden group"
            >
              <div className="relative h-48">
                <img
                  src={
                    group.venue_image_url ||
                    "https://via.placeholder.com/400x200?text=No+Image"
                  }
                  alt={`${group.venue_name} venue`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = "https://via.placeholder.com/400x200?text=No+Image";
                  }}
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <h3 className="text-xl font-semibold text-white group-hover:text-purple-200 transition-colors">
                    {group.name}
                  </h3>
                  <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm mt-2">
                    {group.sports_type}
                  </span>
                </div>
                <div className="absolute top-3 right-3">
                  {renderMembershipButton(group)}
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <p className="text-gray-600 line-clamp-2">
                  {group.description || "No description available"}
                </p>
                
                <div className="space-y-2">
                  <div className="flex items-center text-gray-500">
                    <MapPin size={18} className="mr-2 flex-shrink-0" />
                    <span className="truncate">{group.venue_address}</span>
                  </div>
                  
                  <div className="flex items-center text-gray-500">
                    <Users size={18} className="mr-2 flex-shrink-0" />
                    <span>{group.member_count || 0} members</span>
                  </div>
                  
                  <div className="flex items-center text-gray-500">
                    <Calendar size={18} className="mr-2 flex-shrink-0" />
                    <span className="truncate">
                      {formatPlayingDays(group.playing_days)}, {formatTime(group.game_start_time)}
                    </span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center pt-2 border-t border-gray-100">
                  <div className="text-sm text-gray-500">
                    Max {group.max_teams} teams • {group.max_players_per_team} players/team
                  </div>
                  {group.referee_required && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Referee Required
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default AllSportsGroupsPage;