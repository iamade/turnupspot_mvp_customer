import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { UserPlus, Shield, Trash2, X, Check, ArrowLeft } from 'lucide-react';

interface Member {
  id: string;
  name: string;
  email: string;
  isAdmin: boolean;
}

interface PendingMember {
  id: string;
  name: string;
  email: string;
  requestDate: string;
}

const GroupMembersPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Mock data - replace with actual data from your backend
  const [members, setMembers] = useState<Member[]>([
    { id: '1', name: 'John Doe', email: 'john@example.com', isAdmin: false },
    { id: '2', name: 'Jane Smith', email: 'jane@example.com', isAdmin: true },
    { id: '3', name: 'Mike Johnson', email: 'mike@example.com', isAdmin: false },
  ]);

  const [pendingMembers, setPendingMembers] = useState<PendingMember[]>([
    { id: '4', name: 'Alice Brown', email: 'alice@example.com', requestDate: '2024-03-15' },
    { id: '5', name: 'Bob Wilson', email: 'bob@example.com', requestDate: '2024-03-14' },
  ]);

  const handleMakeAdmin = (memberId: string) => {
    setMembers(members.map(member => 
      member.id === memberId ? { ...member, isAdmin: true } : member
    ));
  };

  const handleRemoveMember = (memberId: string) => {
    setMembers(members.filter(member => member.id !== memberId));
  };

  const handleApproveRequest = (memberId: string) => {
    const approvedMember = pendingMembers.find(m => m.id === memberId);
    if (approvedMember) {
      setPendingMembers(pendingMembers.filter(m => m.id !== memberId));
      setMembers([...members, { 
        id: approvedMember.id, 
        name: approvedMember.name, 
        email: approvedMember.email, 
        isAdmin: false 
      }]);
    }
  };

  const handleRejectRequest = (memberId: string) => {
    setPendingMembers(pendingMembers.filter(m => m.id !== memberId));
  };

  const handleDeleteGroup = () => {
    // Handle group deletion
    if (window.confirm('Are you sure you want to delete this group? This action cannot be undone.')) {
      navigate('/sports');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to={`/sports/groups/${id}`} className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8">
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Group Details
      </Link>

      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Group Members</h1>
          <Link 
            to={`/sports/groups/${id}/invite`}
            className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
          >
            <UserPlus size={20} />
            <span>Add New Member</span>
          </Link>
        </div>

        {/* Pending Registrations */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Pending Registrations</h2>
          <div className="space-y-4">
            {pendingMembers.map(member => (
              <div key={member.id} className="flex items-center justify-between border-b pb-4 last:border-b-0">
                <div>
                  <h3 className="font-medium">{member.name}</h3>
                  <p className="text-sm text-gray-500">{member.email}</p>
                  <p className="text-sm text-gray-400">Requested: {member.requestDate}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleApproveRequest(member.id)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg"
                  >
                    <Check size={20} />
                  </button>
                  <button
                    onClick={() => handleRejectRequest(member.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>
            ))}
            {pendingMembers.length === 0 && (
              <p className="text-gray-500 text-center py-4">No pending requests</p>
            )}
          </div>
        </div>

        {/* Current Members */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Current Members</h2>
          <div className="space-y-4">
            {members.map(member => (
              <div key={member.id} className="flex items-center justify-between border-b pb-4 last:border-b-0">
                <div>
                  <h3 className="font-medium">{member.name}</h3>
                  <p className="text-sm text-gray-500">{member.email}</p>
                  {member.isAdmin && (
                    <span className="inline-block px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                      Admin
                    </span>
                  )}
                </div>
                <div className="flex space-x-2">
                  {!member.isAdmin && (
                    <button
                      onClick={() => handleMakeAdmin(member.id)}
                      className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                      title="Make Admin"
                    >
                      <Shield size={20} />
                    </button>
                  )}
                  <button
                    onClick={() => handleRemoveMember(member.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                    title="Remove Member"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Delete Group */}
        <div className="flex justify-center pt-8">
          <button
            onClick={handleDeleteGroup}
            className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700"
          >
            Delete Group
          </button>
        </div>
      </div>
    </div>
  );
};

export default GroupMembersPage;