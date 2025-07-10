import React from "react";
import EditSportGroupForm from "../components/sports/EditSportGroupFrom";

const EditSportGroupPage: React.FC = () => {
  return (
    <div className="py-6">
      <EditSportGroupForm />
    </div>
  );
};

export default EditSportGroupPage;

// import React, { useEffect, useState } from "react";
// import { useParams, useNavigate } from "react-router-dom";
// import { get, put } from "../api";

// const EditSportGroupPage = () => {
//   const { id } = useParams<{ id: string }>();
//   const navigate = useNavigate();
//   const [form, setForm] = useState<any>({});
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     get(`/sport-groups/${id}`)
//       .then((res) => {
//         setForm(res.data);
//         setLoading(false);
//       })
//       .catch(() => {
//         setError("Failed to load group data");
//         setLoading(false);
//       });
//   }, [id]);

//   const handleChange = (
//     e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
//   ) => {
//     setForm({ ...form, [e.target.name]: e.target.value });
//   };

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     try {
//       await put(`/sport-groups/${id}`, form);
//       navigate(`/sports/groups/${id}`);
//     } catch (err) {
//       setError("Failed to update group");
//     }
//   };

//   if (loading) return <div>Loading...</div>;
//   if (error) return <div className="text-red-600">{error}</div>;

//   return (
//     <div className="max-w-xl mx-auto p-6 bg-white rounded shadow">
//       <h2 className="text-2xl font-bold mb-4">Edit Group</h2>
//       <form onSubmit={handleSubmit} className="space-y-4">
//         <input
//           name="name"
//           value={form.name || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Group Name"
//         />
//         <input
//           name="venue_name"
//           value={form.venue_name || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Venue Name"
//         />
//         <input
//           name="venue_address"
//           value={form.venue_address || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Venue Address"
//         />
//         <input
//           name="playing_days"
//           value={form.playing_days || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Playing Days (e.g. 0,2,4)"
//         />
//         <input
//           name="game_start_time"
//           value={form.game_start_time || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Game Start Time (HH:MM)"
//         />
//         <input
//           name="game_end_time"
//           value={form.game_end_time || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Game End Time (HH:MM)"
//         />
//         <input
//           name="max_teams"
//           type="number"
//           value={form.max_teams || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Max Teams"
//         />
//         <input
//           name="max_players_per_team"
//           type="number"
//           value={form.max_players_per_team || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Max Players Per Team"
//         />
//         <textarea
//           name="rules"
//           value={form.rules || ""}
//           onChange={handleChange}
//           className="input w-full"
//           placeholder="Rules"
//         />
//         <button type="submit" className="btn btn-primary w-full">
//           Save Changes
//         </button>
//       </form>
//     </div>
//   );
// };

// export default EditSportGroupPage;
