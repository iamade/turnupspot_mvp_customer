import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { get, del } from "../api";
import { useAuth } from "../contexts/AuthContext";

interface SportGroup {
  id: string;
  name: string;
  description?: string;
  venue_name: string;
  venue_address: string;
  venue_image_url?: string;
  playing_days: string;
  game_start_time: string;
  game_end_time: string;
  max_teams: number;
  max_players_per_team: number;
  rules?: string;
  referee_required: boolean;
  sports_type: string;
}

const MySportsGroupsPage: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [groups, setGroups] = useState<SportGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      navigate("/signin");
      return;
    }
    setLoading(true);
    get<SportGroup[]>("/sport-groups/my", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => setGroups(res.data))
      .catch(() => setError("Failed to load your sport groups."))
      .finally(() => setLoading(false));
  }, [token, navigate]);

  const openDeleteModal = (id: string) => {
    setPendingDeleteId(id);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setPendingDeleteId(null);
  };

  const handleDelete = async () => {
    if (!pendingDeleteId) return;
    setDeletingId(pendingDeleteId);
    try {
      await del(`/sport-groups/${pendingDeleteId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setGroups((prev) => prev.filter((g) => g.id !== pendingDeleteId));
      closeModal();
    } catch (e) {
      alert("Failed to delete group.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-center flex-1">
          Your Sports Groups
        </h1>
        <button
          className="ml-4 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700"
          onClick={() => navigate("/sports/select")}
        >
          Create Group
        </button>
      </div>
      {loading && <div className="text-center">Loading...</div>}
      {error && <div className="text-center text-red-500">{error}</div>}
      {!loading && !error && groups.length === 0 && (
        <div className="text-center text-gray-500 text-lg mt-16">
          You have not joined or created any sport groups yet.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {groups.map((group) => (
          <div
            key={group.id}
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer relative"
          >
            <img
              src={
                group.venue_image_url ||
                "https://images.pexels.com/photos/399187/pexels-photo-399187.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
              }
              alt={group.name}
              className="w-full h-40 object-cover"
              onClick={() => navigate(`/sports/groups/${group.id}`)}
            />
            <div
              className="p-6"
              onClick={() => navigate(`/sports/groups/${group.id}`)}
            >
              <h2 className="text-xl font-bold mb-2">{group.name}</h2>
              <p className="text-gray-600 mb-2">{group.description}</p>
              <div className="text-sm text-gray-500 mb-1">
                <span className="font-medium">Venue:</span> {group.venue_name}
              </div>
              <div className="text-xs text-gray-400">{group.venue_address}</div>
            </div>
            <button
              className="absolute top-2 right-2 bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-xs z-10"
              onClick={(e) => {
                e.stopPropagation();
                openDeleteModal(group.id);
              }}
              disabled={deletingId === group.id}
            >
              {deletingId === group.id ? "Deleting..." : "Delete"}
            </button>
          </div>
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-sm w-full">
            <h2 className="text-xl font-bold mb-4 text-center">Delete Group</h2>
            <p className="mb-6 text-center">
              Are you sure you want to delete this group? This action cannot be
              undone.
            </p>
            <div className="flex justify-end space-x-4">
              <button
                className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
                onClick={closeModal}
                disabled={deletingId !== null}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700"
                onClick={handleDelete}
                disabled={deletingId !== null}
              >
                {deletingId !== null ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MySportsGroupsPage;
