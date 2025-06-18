import React from 'react';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';

const sports = [
  {
    id: 'football',
    name: 'Football',
    description: 'Popular team sport',
    subtext: 'Played worldwide',
    image: 'https://images.pexels.com/photos/46798/the-ball-stadion-football-the-pitch-46798.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    action: 'Play'
  },
  {
    id: 'basketball',
    name: 'Basketball',
    description: 'Fast-paced game',
    subtext: 'Played indoors',
    image: 'https://images.pexels.com/photos/358042/pexels-photo-358042.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    action: 'View'
  },
  {
    id: 'tennis',
    name: 'Lawn Tennis',
    description: 'Elegant sport',
    subtext: 'Played on grass',
    image: 'https://images.pexels.com/photos/8224691/pexels-photo-8224691.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    action: 'View'
  },
  {
    id: 'volleyball',
    name: 'Volleyball',
    description: 'Beach or indoor',
    subtext: 'Team-oriented',
    image: 'https://images.pexels.com/photos/1263426/pexels-photo-1263426.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    action: 'View'
  },
  {
    id: 'badminton',
    name: 'Badminton',
    description: 'Fast racket game',
    subtext: 'Indoor or outdoor',
    image: 'https://images.pexels.com/photos/3660204/pexels-photo-3660204.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    action: 'View'
  },
  {
    id: 'cricket',
    name: 'Cricket',
    description: 'Team-based game',
    subtext: 'Played on pitch',
    image: 'https://images.pexels.com/photos/3659097/pexels-photo-3659097.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    action: 'View'
  }
];

const SportSelectionPage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Select Your Sport</h1>
        <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
      </div>

      <div className="relative mb-8">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search for a sport..."
          className="w-full pl-10 pr-4 py-3 bg-gray-50 rounded-xl border-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <div className="space-y-6">
        {sports.map((sport) => (
          <Link
            key={sport.id}
            to={`/sports/create?type=${sport.id}`}
            className="flex items-center justify-between bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-1">{sport.name}</h3>
              <p className="text-sm text-gray-500">{sport.description}</p>
              <p className="text-sm text-gray-400">{sport.subtext}</p>
              <button className="mt-2 px-4 py-1 text-sm text-indigo-600 bg-indigo-50 rounded-full hover:bg-indigo-100 transition-colors">
                {sport.action}
              </button>
            </div>
            <div className="w-24 h-24 ml-4">
              <img
                src={sport.image}
                alt={sport.name}
                className="w-full h-full object-cover rounded-lg"
              />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default SportSelectionPage;