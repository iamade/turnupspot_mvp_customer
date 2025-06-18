import React from 'react';
import { Link } from 'react-router-dom';
import { UserPlus, Store } from 'lucide-react';

const SignupPage = () => {
  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50">
      <div className="max-w-4xl w-full mx-4">
        <h1 className="text-4xl font-bold text-center mb-12">Join Turnup Spot</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <Link 
            to="/signup/user"
            className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow group"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center mb-6 group-hover:bg-indigo-200 transition-colors">
                <UserPlus className="w-10 h-10 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-semibold mb-4">Join as a User</h2>
              <p className="text-gray-600 mb-6">
                Discover and create events, join sports groups, and connect with amazing vendors.
              </p>
              <span className="text-indigo-600 font-medium group-hover:text-indigo-700">
                Create Account →
              </span>
            </div>
          </Link>

          <Link 
            to="/signup/vendor"
            className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow group"
          >
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mb-6 group-hover:bg-purple-200 transition-colors">
                <Store className="w-10 h-10 text-purple-600" />
              </div>
              <h2 className="text-2xl font-semibold mb-4">Join as a Vendor</h2>
              <p className="text-gray-600 mb-6">
                Showcase your services, connect with customers, and grow your business.
              </p>
              <span className="text-purple-600 font-medium group-hover:text-purple-700">
                Create Account →
              </span>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;