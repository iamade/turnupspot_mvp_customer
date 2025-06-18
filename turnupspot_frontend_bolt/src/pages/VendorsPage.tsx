import React from 'react';
import { Store, ShoppingBag, Truck, CreditCard } from 'lucide-react';

const VendorsPage = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center space-y-6 max-w-2xl mx-auto px-4">
        <div className="bg-gradient-to-r from-purple-500 via-indigo-500 to-blue-500 text-white rounded-xl p-8 shadow-xl">
          <Store className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-4">Vendor Directory Coming Soon!</h1>
          <p className="text-xl opacity-90">
            We're building the ultimate marketplace for event vendors. Connect with trusted professionals for your next event!
          </p>
        </div>
        
        <div className="bg-white rounded-xl p-8 shadow-lg">
          <h2 className="text-2xl font-semibold mb-6">Featured Services</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="text-left p-4 rounded-lg bg-purple-50">
              <ShoppingBag className="w-8 h-8 text-purple-600 mb-3" />
              <h3 className="font-semibold text-lg mb-2">Event Supplies</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Decorations and props</li>
                <li>• Furniture rentals</li>
                <li>• Audio/visual equipment</li>
                <li>• Custom installations</li>
              </ul>
            </div>
            <div className="text-left p-4 rounded-lg bg-blue-50">
              <Truck className="w-8 h-8 text-blue-600 mb-3" />
              <h3 className="font-semibold text-lg mb-2">Service Providers</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Event planners</li>
                <li>• Catering services</li>
                <li>• Photography/videography</li>
                <li>• Entertainment</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
            <CreditCard className="w-8 h-8 text-indigo-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Secure Payments</h3>
            <p className="text-gray-600">
              All transactions will be protected with industry-standard security measures and buyer protection policies.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorsPage;