import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Trophy, Store } from 'lucide-react';

const Home = () => {
  return (
    <div className="space-y-12">
      <section className="text-center py-16 bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-3xl text-white">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">Welcome to Turnup Spot</h1>
        <p className="text-xl md:text-2xl mb-8">Your ultimate platform for events, sports, and vendor management</p>
        <div className="flex justify-center space-x-4">
          <Link to="/events/create" className="bg-white text-indigo-600 px-8 py-3 rounded-lg font-bold hover:bg-indigo-100">
            Create Event
          </Link>
          <Link to="/sports/select" className="bg-indigo-500 text-white px-8 py-3 rounded-lg font-bold hover:bg-indigo-400">
            Join Sports Group
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-8 rounded-xl shadow-lg">
          <Calendar className="w-12 h-12 text-indigo-600 mb-4" />
          <h2 className="text-2xl font-bold mb-4">Event Services</h2>
          <p className="text-gray-600 mb-4">Create and manage events, generate invitation cards, and connect with vendors.</p>
          <Link to="/events" className="text-indigo-600 font-medium hover:text-indigo-800">Learn More →</Link>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg">
          <Trophy className="w-12 h-12 text-indigo-600 mb-4" />
          <h2 className="text-2xl font-bold mb-4">Sports Groups</h2>
          <p className="text-gray-600 mb-4">Organize sports activities, manage teams, and track statistics.</p>
          <Link to="/sports" className="text-indigo-600 font-medium hover:text-indigo-800">Learn More →</Link>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg">
          <Store className="w-12 h-12 text-indigo-600 mb-4" />
          <h2 className="text-2xl font-bold mb-4">Vendor Directory</h2>
          <p className="text-gray-600 mb-4">Find and connect with trusted vendors for your events.</p>
          <Link to="/vendors" className="text-indigo-600 font-medium hover:text-indigo-800">Learn More →</Link>
        </div>
      </section>

      <section className="bg-white p-8 rounded-xl shadow-lg">
        <h2 className="text-3xl font-bold mb-6 text-center">Featured Events</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-gray-50 rounded-lg overflow-hidden">
              <img 
                src={`https://images.pexels.com/photos/787961/pexels-photo-787961.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2`} 
                alt="Event" 
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h3 className="text-xl font-bold mb-2">Summer Music Festival</h3>
                <p className="text-gray-600 mb-4">Join us for an amazing day of music and fun!</p>
                <Link to={`/events/${i}`} className="text-indigo-600 font-medium hover:text-indigo-800">View Details →</Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;