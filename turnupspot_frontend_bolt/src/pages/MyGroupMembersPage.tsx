import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Trash2, ArrowLeft, UserPlus, Check, X } from "lucide-react";
import { get, del, post } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";

interface Member {
  id: number;
  user: {
    first_name: string;
    last_name: string;
    email: string;
  };
  role: string;
  is_approved: boolean;
}

interface PendingMember {
  id: number;
  user: {
    first_name: string;
    last_name: string;
    email: string;
  };
  joined_at: string;
}

const MyGroupMembersPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [members, setMembers] = useState<Member[]>([]);
  const [pendingMembers, setPendingMembers] = useState<PendingMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id || !token) return;
    setLoading(true);
    Promise.all([
      get<Member[]>(`/sport-groups/${id}/members`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
      get<PendingMember[]>(`/sport-groups/${id}/members?include_pending=true`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    ])
      .then(([membersRes, pendingRes]) => {
        setMembers(membersRes.data);
        setPendingMembers(pendingRes.data);
      })
      .catch(() => toast.error("Failed to load members"))
      .finally(() => setLoading(false));
  }, [id, token]);

  const handleRemoveMember = async (memberId: number) => {
    if (!id || !token) return;
    try {
      await del(`/sport-groups/${id}/members/${memberId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMembers((prev) => prev.filter((m) => m.id !== memberId));
      toast.success("Member removed successfully");
    } catch {
      toast.error("Failed to remove member");
    }
  };

  const handleDeleteGroup = async () => {
    if (!id || !token) return;
    if (
      !window.confirm(
        "Are you sure you want to delete this group? This action cannot be undone."
      )
    )
      return;
    try {
      await del(`/sport-groups/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success("Group deleted successfully");
      navigate("/my-sports-groups");
    } catch {
      toast.error("Failed to delete group");
    }
  };

  const handleApproveRequest = async (memberId: number) => {
    if (!id || !token) return;
    try {
      await post(
        `/sport-groups/${id}/members/${memberId}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPendingMembers((prev) => prev.filter((m) => m.id !== memberId));
      setMembers((prev) => {
        const approved = pendingMembers.find((m) => m.id === memberId);
        if (!approved) return prev;
        return [
          ...prev,
          {
            id: approved.id,
            user: approved.user,
            role: "member",
            is_approved: true,
          },
        ];
      });
      toast.success("Member approved");
    } catch {
      toast.error("Failed to approve member");
    }
  };

  const handleRejectRequest = async (memberId: number) => {
    if (!id || !token) return;
    try {
      await del(`/sport-groups/${id}/members/${memberId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPendingMembers((prev) => prev.filter((m) => m.id !== memberId));
      toast.success("Member rejected");
    } catch {
      toast.error("Failed to reject member");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <Link
          to={`/my-sports-groups/${id}`}
          className="inline-flex items-center text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Group Details
        </Link>
        <button
          className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
          onClick={() => navigate(`/my-sports-groups/${id}/invite`)}
        >
          <UserPlus size={20} />
          <span>Add New Member</span>
        </button>
      </div>
      <div className="space-y-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Pending Registrations</h2>
          <div className="space-y-4">
            {pendingMembers.map((member) => (
              <div
                key={member.id}
                className="flex items-center justify-between border-b pb-4 last:border-b-0"
              >
                <div>
                  <h3 className="font-medium">
                    {member.user.first_name} {member.user.last_name}
                  </h3>
                  <p className="text-sm text-gray-500">{member.user.email}</p>
                  <p className="text-sm text-gray-400">
                    Requested: {member.joined_at.slice(0, 10)}
                  </p>
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
              <p className="text-gray-500 text-center py-4">
                No pending requests
              </p>
            )}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Current Members</h2>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="space-y-4">
              {members.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between border-b pb-4 last:border-b-0"
                >
                  <div>
                    <h3 className="font-medium">
                      {member.user.first_name} {member.user.last_name}
                    </h3>
                    <p className="text-sm text-gray-500">{member.user.email}</p>
                    {member.role === "admin" && (
                      <span className="inline-block px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full mt-2">
                        Admin
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
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
          )}
        </div>
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

export default MyGroupMembersPage;
