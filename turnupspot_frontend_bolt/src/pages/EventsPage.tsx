import React from 'react';
import { Construction } from 'lucide-react';

const EventsPage = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center space-y-6 max-w-2xl mx-auto px-4">
        <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white rounded-xl p-8 shadow-xl">
          <Construction className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-4">Events Coming Soon!</h1>
          <p className="text-xl opacity-90">
            We're working hard to bring you an amazing events platform. Stay tuned for updates!
          </p>
        </div>
        
        <div className="bg-white rounded-xl p-8 shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">What to Expect</h2>
          <div className="grid md:grid-cols-2 gap-6 text-left">
            <div>
              <h3 className="font-semibold text-lg mb-2">For Event Organizers</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Easy event creation and management</li>
                <li>• Ticket sales and registration</li>
                <li>• Attendee management tools</li>
                <li>• Real-time analytics</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">For Attendees</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Discover local events</li>
                <li>• Secure ticket purchasing</li>
                <li>• Event recommendations</li>
                <li>• Mobile tickets and check-in</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventsPage;