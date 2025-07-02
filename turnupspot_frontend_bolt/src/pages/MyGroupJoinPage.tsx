import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { post } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";

const MyGroupJoinPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [joining, setJoining] = useState(false);

  const handleJoin = async () => {
    if (!id || !token) return;
    setJoining(true);
    try {
      await post(
        `/sport-groups/${id}/join`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Join request submitted!");
      navigate(`/my-sports-groups/${id}`);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Failed to join group");
    } finally {
      setJoining(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-md mx-auto px-4 py-12 text-center">
        <h1 className="text-2xl font-bold mb-4">Join Group</h1>
        <p className="mb-6">
          You need a TurnUpSpot account to join this group.
        </p>
        <div className="flex justify-center space-x-4">
          <Link
            to="/signup"
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Sign Up
          </Link>
          <Link
            to="/signin"
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Log In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 py-12 text-center">
      <h1 className="text-2xl font-bold mb-4">Join Group</h1>
      <p className="mb-6">Click below to join this sports group.</p>
      <button
        onClick={handleJoin}
        disabled={joining}
        className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
      >
        {joining ? "Joining..." : "Join Group"}
      </button>
    </div>
  );
};

export default MyGroupJoinPage;
