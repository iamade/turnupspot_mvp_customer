import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, Store, Trophy } from 'lucide-react';

const Sidebar = () => {
  return (
    <aside className="w-64 bg-white shadow-lg hidden md:block">
      <nav className="p-4">
        <ul className="space-y-2">
          <li>
            <Link to="/events" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-purple-50">
              <Calendar className="text-purple-600" />
              <span>Events</span>
            </Link>
          </li>
          <li>
            <Link to="/sports" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-purple-50">
              <Trophy className="text-purple-600" />
              <span>Sports Groups</span>
            </Link>
          </li>
          <li>
            <Link to="/vendors" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-purple-50">
              <Store className="text-purple-600" />
              <span>Vendors</span>
            </Link>
          </li>
          <li>
            <Link to="/community" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-purple-50">
              <Users className="text-purple-600" />
              <span>Community</span>
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar