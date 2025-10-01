import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { get, del } from "../api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-toastify";
import ConfirmDialog from "../components/ui/ConfirmDialog";

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

interface SportGroup {
  id: string;
  name: string;
  current_user_membership?: {
    is_member: boolean;
    is_pending: boolean;
    role: string | null;
    is_creator: boolean;
  } | null;
}

const GroupMembersPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [group, setGroup] = useState<SportGroup | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!id || !token) return;
    setLoading(true);

    // Fetch both group details and members
    Promise.all([
      get(`/sport-groups/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
      get<Member[]>(`/sport-groups/${id}/members`, {
        headers: { Authorization: `Bearer ${token}` },
      })
    ])
      .then(([groupRes, membersRes]) => {
        setGroup(groupRes.data as SportGroup);
        setMembers(membersRes.data);
      })
      .finally(() => setLoading(false));
  }, [id, token]);

  const handleDeleteGroup = async () => {
    if (!id) return;
    setDeleting(true);
    try {
      await del(`/sport-groups/${id}`);
      toast.success("Group deleted successfully!");
      navigate("/my-sports-groups");
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to delete group";
      toast.error(errorMessage);
    } finally {
      setDeleting(false);
      setIsDeleteDialogOpen(false);
    }
  };

  const isCreator = group?.current_user_membership?.is_creator;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <Link
          to={`/sports/groups/${id}`}
          className="inline-flex items-center text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Group Details
        </Link>
        {isCreator && (
          <button
            onClick={() => setIsDeleteDialogOpen(true)}
            disabled={deleting}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {deleting ? "Deleting..." : "Delete Group"}
          </button>
        )}
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
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        title="Delete Group"
        message="Are you sure you want to delete this group? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteGroup}
        onCancel={() => setIsDeleteDialogOpen(false)}
      />
    </div>
  );
};

export default GroupMembersPage;
