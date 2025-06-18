import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, UserCheck, ChevronLeft, ChevronRight, MapPin } from 'lucide-react';

interface Player {
  id: string;
  name: string;
  status: 'arrived' | 'expected' | 'delayed' | 'absent';
  arrivalTime?: string;
  isCaptain?: boolean;
  team?: number;
}

interface Team {
  id: number;
  name: string;
  captain: string;
  members: string[];
}

const GameDayPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const playersPerPage = 8;
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [isAtVenue, setIsAtVenue] = useState(false);
  const [checkinError, setCheckinError] = useState<string>('');

  // Mock venue location (this would come from your database)
  const venueLocation = {
    lat: 40.7128,
    lng: -74.0060,
    radius: 100 // meters
  };

  const [teams] = useState<Team[]>([
    { id: 1, name: 'Team 1', captain: 'Bright', members: ['Kevin De Bruyne', 'Mohamed Salah', 'Virgil van Dijk', 'Jude Bellingham'] },
    { id: 2, name: 'Team 2', captain: 'Gbolahan', members: ['Erling Haaland', 'Kylian Mbappé', 'Joshua Kimmich', 'Vinicius Jr'] },
    { id: 3, name: 'Team 3', captain: 'Deji', members: ['Bruno Fernandes', 'Rodri', 'Bernardo Silva', 'Phil Foden'] },
    { id: 4, name: 'Team 4', captain: 'Kojay', members: ['Toni Kroos', 'Casemiro', 'Federico Valverde', 'Eduardo Camavinga'] },
    { id: 5, name: 'Team 5', captain: 'Lacazet', members: ['Mason Mount', 'Jack Grealish', 'Declan Rice', 'Bukayo Saka'] },
    { id: 6, name: 'Team 6', captain: 'Lola', members: ['Takehiro Tomiyasu', 'Kim Min-jae', 'Kaoru Mitoma', 'Wataru Endo'] },
    { id: 7, name: 'Team 7', captain: 'Femi', members: ['Thomas Müller', 'Leroy Sané', 'Leon Goretzka', 'Jamal Musiala'] },
    { id: 8, name: 'Team 8', captain: 'Lekan', members: ['Casemiro', 'Marquinhos', 'Thiago Silva', 'Lucas Paquetá'] },
  ]);

  const [players] = useState<Player[]>([
    { id: '1', name: 'Bright', status: 'arrived', arrivalTime: '19:15', isCaptain: true },
    { id: '2', name: 'Gbolahan', status: 'arrived', arrivalTime: '19:16', isCaptain: true },
    { id: '3', name: 'Kevin De Bruyne', status: 'arrived', arrivalTime: '19:20' },
    { id: '4', name: 'Erling Haaland', status: 'arrived', arrivalTime: '19:22' },
    { id: '5', name: 'Mohamed Salah', status: 'arrived', arrivalTime: '19:25' },
    { id: '6', name: 'Kylian Mbappé', status: 'arrived', arrivalTime: '19:28' },
    { id: '7', name: 'Virgil van Dijk', status: 'arrived', arrivalTime: '19:30' },
    { id: '8', name: 'Joshua Kimmich', status: 'arrived', arrivalTime: '19:32' },
    { id: '9', name: 'Jude Bellingham', status: 'arrived', arrivalTime: '19:35' },
    { id: '10', name: 'Vinicius Jr', status: 'arrived', arrivalTime: '19:38' },
    { id: '11', name: 'Deji', status: 'arrived', arrivalTime: '19:40' },
    { id: '12', name: 'Bruno Fernandes', status: 'arrived', arrivalTime: '19:42' },
    { id: '13', name: 'Rodri', status: 'arrived', arrivalTime: '19:45' },
    { id: '14', name: 'Bernardo Silva', status: 'arrived', arrivalTime: '19:47' },
    { id: '15', name: 'Phil Foden', status: 'arrived', arrivalTime: '19:50' },
    { id: '16', name: 'Kojay', status: 'expected' },
    { id: '17', name: 'Lacazet', status: 'delayed' },
    { id: '18', name: 'Lola', status: 'absent' },
    { id: '19', name: 'Femi', status: 'arrived', arrivalTime: '19:52' },
    { id: '20', name: 'Lekan', status: 'arrived', arrivalTime: '19:55' },
  ]);

  useEffect(() => {
    // Check if it's after 6 PM
    const now = new Date();
    if (now.getHours() >= 18) {
      checkLocation();
    }
  }, []);

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c;
  };

  const checkLocation = () => {
    if (!navigator.geolocation) {
      setCheckinError('Geolocation is not supported by your browser');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;
        
        setUserLocation({ lat: userLat, lng: userLng });

        // Calculate distance between user and venue
        const distance = calculateDistance(
          userLat,
          userLng,
          venueLocation.lat,
          venueLocation.lng
        );

        // Check if user is within venue radius
        if (distance <= venueLocation.radius) {
          setIsAtVenue(true);
          setCheckinError('');
        } else {
          setIsAtVenue(false);
          setCheckinError('You must be at the venue to check in');
        }
      },
      (error) => {
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setCheckinError(
              'Location access was denied. Please enable location access in your browser settings to check in.'
            );
            break;
          case error.POSITION_UNAVAILABLE:
            setCheckinError('Location information is unavailable. Please try again.');
            break;
          case error.TIMEOUT:
            setCheckinError('Location request timed out. Please try again.');
            break;
          default:
            setCheckinError('An unexpected error occurred while getting your location.');
        }
        console.error('Geolocation error:', error);
      }
    );
  };

  const handleManualCheckin = () => {
    checkLocation();
  };

  const getStatusColor = (status: Player['status']) => {
    switch (status) {
      case 'arrived': return 'text-green-600';
      case 'expected': return 'text-yellow-600';
      case 'delayed': return 'text-orange-600';
      case 'absent': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // Pagination
  const indexOfLastPlayer = currentPage * playersPerPage;
  const indexOfFirstPlayer = indexOfLastPlayer - playersPerPage;
  const currentPlayers = players.slice(indexOfFirstPlayer, indexOfLastPlayer);
  const totalPages = Math.ceil(players.length / playersPerPage);

  const handlePlayBall = () => {
    // Check if teams are ready and referee is present
    navigate(`/sports/groups/${id}/live-match`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to={`/sports/groups/${id}`} className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8">
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Group Details
      </Link>

      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold">Game Day</h1>
          <div className="flex items-center space-x-4 mt-4">
            <div className="bg-white rounded-lg shadow px-6 py-3">
              <p className="text-gray-600">Wednesday October 10, 2023</p>
            </div>
            <div className="bg-white rounded-lg shadow px-6 py-3">
              <p className="text-gray-600">6:00 PM - 9:00 PM</p>
            </div>
            <div className="bg-white rounded-lg shadow px-6 py-3">
              <p className="text-gray-600">Max Team: 8</p>
            </div>
          </div>
        </div>

        {/* Check-in Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <MapPin className={isAtVenue ? 'text-green-600' : 'text-gray-400'} size={24} />
              <div>
                <h3 className="font-semibold">Location Check-in</h3>
                <p className={`text-sm ${isAtVenue ? 'text-green-600' : 'text-gray-500'}`}>
                  {isAtVenue ? 'You are at the venue' : 'Waiting for check-in'}
                </p>
              </div>
            </div>
            <button
              onClick={handleManualCheckin}
              className={`px-4 py-2 rounded-lg ${
                isAtVenue 
                  ? 'bg-green-100 text-green-700'
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
              disabled={isAtVenue}
            >
              {isAtVenue ? 'Checked In' : 'Check In'}
            </button>
          </div>
          {checkinError && (
            <p className="mt-2 text-sm text-red-600">{checkinError}</p>
          )}
        </div>

        {/* Team Formation */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">Team Formation</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {teams.map((team) => (
              <div key={team.id} className="border rounded-lg p-4">
                <h3 className="font-semibold mb-2">{team.name}</h3>
                <div className="space-y-2">
                  <div className="text-sm font-medium text-purple-600">
                    Captain: {team.captain}
                  </div>
                  <div className="space-y-1">
                    {team.members.map((member, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        {member}
                      </div>
                    ))}
                  </div>
                  <button className="mt-2 text-sm text-blue-600 hover:text-blue-800">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Player Arrival */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">Player Arrival</h2>
          <div className="space-y-4">
            {currentPlayers
              .sort((a, b) => {
                if (a.arrivalTime && b.arrivalTime) {
                  return a.arrivalTime.localeCompare(b.arrivalTime);
                }
                return a.status === 'arrived' ? -1 : 1;
              })
              .map((player) => (
                <div key={player.id} className="flex items-center justify-between border-b pb-4 last:border-b-0">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-200 rounded-full overflow-hidden">
                      {/* Player avatar would go here */}
                    </div>
                    <div>
                      <h3 className="font-medium">
                        {player.name}
                        {player.isCaptain && ' (Captain)'}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm ${getStatusColor(player.status)}`}>
                          {player.status}
                        </span>
                        {player.arrivalTime && (
                          <span className="text-sm text-gray-500">• {player.arrivalTime}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-between items-center mt-6">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded-lg disabled:opacity-50"
            >
              <ChevronLeft size={20} />
            </button>
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded-lg disabled:opacity-50"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>

        {/* Play Ball Button */}
        <button 
          onClick={handlePlayBall}
          className="w-full py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white"
        >
          Play Ball
        </button>
      </div>
    </div>
  );
};

export default GameDayPage;