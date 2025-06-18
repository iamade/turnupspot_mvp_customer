import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Users, Calendar, Trophy, MessageSquare, ArrowLeft } from 'lucide-react';

const groupData = {
  '1': {
    name: 'Weekend Warriors FC',
    description: '5-a-side football group for casual players',
    members: 24,
    nextGame: 'Saturday, 2PM',
    venue: 'Central Park',
    image: 'https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  '2': {
    name: 'Livingston Hub Guys',
    description: 'Join us for weekly games',
    members: 60,
    nextGame: 'Wednesday, 6:30PM',
    venue: '1248 Livingston Way NE, Calgary, AB T3P 0V9',
    image: 'https://images.pexels.com/photos/114296/pexels-photo-114296.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  '3': {
    name: 'Ontario field group',
    description: 'Weekly football matches at Ontario Field',
    members: 32,
    nextGame: 'Friday, 7PM',
    venue: 'Ontario Field Sports Complex',
    image: 'https://images.pexels.com/photos/47730/the-ball-stadion-football-the-pitch-47730.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  '4': {
    name: 'Downtown street soccer',
    description: 'Casual soccer matches, all skill levels welcome',
    members: 45,
    nextGame: 'Monday, 6PM',
    venue: 'Downtown Community Field',
    image: 'https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  '5': {
    name: 'East Side football gang',
    description: 'Playtime Weekend rides',
    members: 121,
    nextGame: 'Sunday, 4PM',
    venue: 'East Side Park',
    image: 'https://images.pexels.com/photos/3448250/pexels-photo-3448250.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  }
};

const SportGroupDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const group = id ? groupData[id as keyof typeof groupData] : null;

  const handleLeaveGroup = () => {
    console.log(`Leaving group ${id}`);
    navigate('/sports');
  };

  if (!group) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Group not found</h2>
        <Link to="/sports" className="text-indigo-600 hover:text-indigo-800 mt-4 inline-block">
          Return to Sports Groups
        </Link>
      </div>
    );
  }

  // Mock previous games data
  const previousGames = [
    {
      id: 1,
      date: '2024-03-10',
      teams: {
        team1: { name: 'Team 1', score: 3 },
        team2: { name: 'Team 2', score: 2 }
      }
    },
    {
      id: 2,
      date: '2024-03-03',
      teams: {
        team1: { name: 'Team 3', score: 1 },
        team2: { name: 'Team 4', score: 1 }
      }
    }
  ];

  const isGameDay = true;

  return (
    <div className="space-y-8">
      <Link to="/sports" className="inline-flex items-center text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Sports
      </Link>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="h-48 relative">
          <img 
            src={group.image} 
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
                <span className="font-medium">Venue:</span> {group.venue}
              </p>
            </div>
            <div className="space-x-4">
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                Join Group
              </button>
              <button 
                onClick={handleLeaveGroup}
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
              <p className="text-purple-600">{group.members} players</p>
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
                    <p className="text-gray-600">{group.nextGame}</p>
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
            {previousGames.map(game => (
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
                    <p className="text-2xl font-bold text-purple-600">{game.teams.team1.score}</p>
                  </div>
                  <div className="text-gray-400 text-xl font-bold">vs</div>
                  <div className="text-right">
                    <h3 className="font-semibold">{game.teams.team2.name}</h3>
                    <p className="text-2xl font-bold text-purple-600">{game.teams.team2.score}</p>
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