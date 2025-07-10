import React from "react";
import { Link } from "react-router-dom";
import { Plus, Users, MapPin, Calendar } from "lucide-react";
import { SportGroup } from "../types";

const mockSportGroups: SportGroup[] = [
  {
    id: "1",
    name: "Weekend Warriors FC",
    sport: "Football",
    description: "5-a-side football group for casual players",
    location: "Central Park",
    venueImage:
      "https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    adminIds: ["1"],
    members: Array(24).fill({}), // 24 members
    playingDates: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "2",
    name: "Livingston Hub Guys",
    sport: "Football",
    description: "Join us for weekly games",
    location: "1248 Livingston Way NE, Calgary, AB T3P 0V9",
    venueImage:
      "https://images.pexels.com/photos/114296/pexels-photo-114296.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    adminIds: ["2"],
    members: Array(60).fill({}), // 60 members
    playingDates: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "3",
    name: "Ontario field group",
    sport: "Football",
    description: "Weekly football matches at Ontario Field",
    location: "Ontario Field Sports Complex",
    venueImage:
      "https://images.pexels.com/photos/47730/the-ball-stadion-football-the-pitch-47730.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    adminIds: ["3"],
    members: Array(32).fill({}), // 32 members
    playingDates: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "4",
    name: "Downtown street soccer",
    sport: "Football",
    description: "Casual soccer matches, all skill levels welcome",
    location: "Downtown Community Field",
    venueImage:
      "https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    adminIds: ["4"],
    members: Array(45).fill({}), // 45 members
    playingDates: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "5",
    name: "East Side football gang",
    sport: "Football",
    description: "Playtime Weekend rides",
    location: "East Side Park",
    venueImage:
      "https://images.pexels.com/photos/3448250/pexels-photo-3448250.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    adminIds: ["5"],
    members: Array(121).fill({}), // 121 members
    playingDates: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

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
    ? days
        .split(",")
        .map((d) => dayNames[parseInt(d, 10)] || "")
        .filter(Boolean)
        .join(", ")
    : "";
};

const formatTime = (dateTime: string): string => {
  if (!dateTime) return "";
  const timePart = dateTime.includes("T")
    ? dateTime.split("T")[1]
    : dateTime.split(" ")[1] || dateTime;
  return timePart ? timePart.slice(0, 5) : "";
};

const SportsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Sports Groups</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockSportGroups.map((group) => (
          <Link
            key={group.id}
            to={`/sports/groups/${group.id}`}
            className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden"
          >
            <div className="relative h-48">
              <img
                src={group.venueImage}
                alt={`${group.location} venue`}
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                <h3 className="text-xl font-semibold text-white">
                  {group.name}
                </h3>
                <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm mt-2">
                  {group.sport}
                </span>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-gray-600">{group.description}</p>
              <div className="space-y-2">
                <div className="flex items-center text-gray-500">
                  <MapPin size={18} className="mr-2" />
                  <span>{group.location}</span>
                </div>
                <div className="flex items-center text-gray-500">
                  <Users size={18} className="mr-2" />
                  <span>{group.members.length} members</span>
                </div>
                <div className="flex items-center text-gray-500">
                  <Calendar size={18} className="mr-2" />
                  <span>
                    Next game: {dayNumberToName(group.playing_days)},{" "}
                    {formatTime(group.game_start_time)}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default SportsPage;
