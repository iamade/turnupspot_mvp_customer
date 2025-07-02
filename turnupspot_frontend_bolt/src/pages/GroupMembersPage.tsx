import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { get } from "../api";
import { useAuth } from "../contexts/AuthContext";

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

const GroupMembersPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id || !token) return;
    setLoading(true);
    get<Member[]>(`/sport-groups/${id}/members`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => setMembers(res.data))
      .finally(() => setLoading(false));
  }, [id, token]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        to={`/sports/groups/${id}`}
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Group Details
      </Link>
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
                    <span className="inline-block px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                      Admin
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupMembersPage;
