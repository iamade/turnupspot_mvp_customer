import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { PartyPopper, Menu, X, Music, Star } from 'lucide-react';

const Header = () => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="bg-white shadow-sm relative">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute -top-2 -right-1 transform rotate-12">
                <Star size={12} className="text-yellow-400 animate-pulse" />
              </div>
              <div className="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-2 rounded-lg transform group-hover:rotate-12 transition-transform duration-300">
                <PartyPopper size={32} className="text-white" />
              </div>
              <div className="absolute -bottom-1 -left-1">
                <Music size={12} className="text-indigo-600 animate-bounce" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-transparent bg-clip-text transform group-hover:-translate-y-0.5 transition-transform duration-300">
                TurnUp Spot
              </span>
              <span className="text-xs text-gray-500 font-medium">Let's Party!</span>
            </div>
          </Link>
          
          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/home" className="text-gray-600 hover:text-gray-900">Home</Link>
            <Link to="/events" className="text-gray-600 hover:text-gray-900">Events</Link>
            <Link to="/sports" className="text-gray-600 hover:text-gray-900">Sports</Link>
            <Link to="/vendors" className="text-gray-600 hover:text-gray-900">Vendors</Link>
          </nav>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <input
              type="search"
              placeholder="Search Events..."
              className="px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <Link 
              to="/signin"
              className="bg-white text-gray-900 px-4 py-2 rounded-lg font-medium border border-gray-300 hover:bg-gray-50"
            >
              Sign In
            </Link>
            <button 
              onClick={() => navigate('/signup')}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700"
            >
              Sign Up
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
            <nav className="flex flex-col py-4">
              <Link 
                to="/home" 
                className="px-4 py-2 text-gray-600 hover:bg-gray-50"
                onClick={() => setIsMenuOpen(false)}
              >
                Home
              </Link>
              <Link 
                to="/events" 
                className="px-4 py-2 text-gray-600 hover:bg-gray-50"
                onClick={() => setIsMenuOpen(false)}
              >
                Events
              </Link>
              <Link 
                to="/sports" 
                className="px-4 py-2 text-gray-600 hover:bg-gray-50"
                onClick={() => setIsMenuOpen(false)}
              >
                Sports
              </Link>
              <Link 
                to="/vendors" 
                className="px-4 py-2 text-gray-600 hover:bg-gray-50"
                onClick={() => setIsMenuOpen(false)}
              >
                Vendors
              </Link>
              <div className="px-4 py-2 border-t border-gray-200">
                <input
                  type="search"
                  placeholder="Search Events..."
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-2"
                />
                <div className="flex flex-col space-y-2">
                  <Link 
                    to="/signin"
                    className="bg-white text-gray-900 px-4 py-2 rounded-lg font-medium border border-gray-300 hover:bg-gray-50 text-center"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/signup"
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 text-center"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Sign Up
                  </Link>
                </div>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;