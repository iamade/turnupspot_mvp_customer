import React from 'react';
import { Link } from 'react-router-dom';
import { Package, Calendar, PenTool } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section 
        className="relative h-[600px] bg-cover bg-center"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(https://images.pexels.com/photos/2263436/pexels-photo-2263436.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2)`
        }}
      >
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white text-center px-4">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">Your Next Unforgettable Event Starts Here</h1>
          <p className="text-xl mb-8">Discover amazing events and connect with top-tier vendors on Turnup Spot.</p>
          <div className="flex gap-4">
            <Link to="/events" className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition">
              Create Your Next Event
            </Link>
            <Link to="/vendor-signup" className="bg-white text-gray-900 px-8 py-3 rounded-lg hover:bg-gray-100 transition">
              Are You a Vendor?
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4">
        <h2 className="text-3xl font-bold text-center mb-16">How Turnup Spot Works</h2>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12">
          <div className="text-center">
            <Package className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Discover Events</h3>
            <p className="text-gray-600">Explore a wide variety of events happening near you, from concerts to sports.</p>
          </div>
          <div className="text-center">
            <Calendar className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Find Vendors</h3>
            <p className="text-gray-600">Connect with top-rated vendors like planners, photographers, and caterers.</p>
          </div>
          <div className="text-center">
            <PenTool className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Create Your Turnup</h3>
            <p className="text-gray-600">Plan and organize your own unforgettable events with ease.</p>
          </div>
        </div>
      </section>

      {/* Featured Events Section */}
      <section className="py-20 px-4 bg-gray-50">
        <h2 className="text-3xl font-bold text-center mb-12">Featured Events</h2>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredEvents.map((event) => (
            <div key={event.id} className="bg-white rounded-lg overflow-hidden shadow-md">
              <img src={event.image} alt={event.title} className="w-full h-48 object-cover" />
              <div className="p-4">
                <h3 className="font-semibold mb-1">{event.title}</h3>
                <p className="text-sm text-gray-500 mb-2">{event.date} | {event.location}</p>
                <p className="text-sm text-gray-600 mb-4">{event.description}</p>
                <Link to={`/events/${event.id}`} className="text-indigo-600 text-sm hover:text-indigo-800">
                  Learn more →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Vendor Spotlight Section */}
      <section className="py-20 px-4">
        <h2 className="text-3xl font-bold text-center mb-12">Vendor Spotlight</h2>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {vendors.map((vendor) => (
            <div key={vendor.id} className="group cursor-pointer">
              <div className="aspect-square rounded-lg overflow-hidden mb-3">
                <img 
                  src={vendor.image} 
                  alt={vendor.name} 
                  className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                />
              </div>
              <h3 className="font-semibold text-sm">{vendor.name}</h3>
              <p className="text-sm text-gray-600">{vendor.category}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to Turnup?</h2>
          <div className="flex justify-center gap-4">
            <Link to="/signup" className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition">
              Join as a User
            </Link>
            <Link to="/vendor-signup" className="bg-white text-gray-900 px-8 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition">
              Join as a Vendor
            </Link>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-20 px-4">
        <div className="max-w-xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Stay Up-to-Date</h2>
          <form className="flex gap-2">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition">
              Subscribe
            </button>
          </form>
        </div>
      </section>
    </div>
  );
};

const featuredEvents = [
  {
    id: '1',
    title: 'Groove Nation Fest',
    date: 'July 15, 2024',
    location: 'Central Park, NYC',
    description: 'An outdoor music festival featuring diverse genres and local artists.',
    image: 'https://images.pexels.com/photos/1190297/pexels-photo-1190297.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '2',
    title: 'City Basketball Championship',
    date: 'August 2, 2024',
    location: 'Community Arena',
    description: 'Watch the best local teams compete for the championship title.',
    image: 'https://images.pexels.com/photos/2277981/pexels-photo-2277981.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '3',
    title: 'Taste of the City Food Fair',
    date: 'September 10, 2024',
    location: 'Downtown Square',
    description: 'Sample delicious cuisines from local restaurants and food vendors.',
    image: 'https://images.pexels.com/photos/2983101/pexels-photo-2983101.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '4',
    title: 'Contemporary Art Show',
    date: 'October 5, 2024',
    location: 'Gallery One',
    description: 'An exhibition featuring works from emerging and established artists.',
    image: 'https://images.pexels.com/photos/1647121/pexels-photo-1647121.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  }
];

const vendors = [
  {
    id: '1',
    name: 'Elite Event Planners',
    category: 'Full-Service Event Planning',
    image: 'https://images.pexels.com/photos/587741/pexels-photo-587741.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '2',
    name: 'Capture Moments Photography',
    category: 'Event Photography & Videography',
    image: 'https://images.pexels.com/photos/1787235/pexels-photo-1787235.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '3',
    name: 'Gourmet Bites Catering',
    category: 'Catering Services for All Events',
    image: 'https://images.pexels.com/photos/5638268/pexels-photo-5638268.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '4',
    name: 'Rhythm Masters DJs',
    category: 'Professional DJ Services',
    image: 'https://images.pexels.com/photos/2526105/pexels-photo-2526105.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  },
  {
    id: '5',
    name: 'Grand Venues',
    category: 'Premium Event Spaces',
    image: 'https://images.pexels.com/photos/169190/pexels-photo-169190.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
  }
];

export default LandingPage;