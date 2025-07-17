import React, { useState } from "react";
import Input from "../ui/Input";
import Button from "../ui/Button";

interface PlayerData {
  name: string;
  email: string;
  phone: string;
}

interface ManualCheckinFormProps {
  onSubmit: (players: PlayerData[]) => void;
  submitting?: boolean;
}

const ManualCheckinForm: React.FC<ManualCheckinFormProps> = ({
  onSubmit,
  submitting,
}) => {
  const [players, setPlayers] = useState<PlayerData[]>([
    { name: "", email: "", phone: "" },
  ]);

  const handleChange = (
    index: number,
    field: keyof PlayerData,
    value: string
  ) => {
    const updated = [...players];
    updated[index][field] = value;
    setPlayers(updated);
  };

  const handleAddPlayer = () => {
    setPlayers([...players, { name: "", email: "", phone: "" }]);
  };

  const handleRemovePlayer = (index: number) => {
    if (players.length === 1) return;
    setPlayers(players.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(players);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-lg font-bold mb-2">Manual Player Check-in</h2>
      {players.map((player, idx) => (
        <div
          key={idx}
          className="flex flex-col md:flex-row gap-2 items-center mb-2 border-b pb-2"
        >
          <Input
            type="text"
            placeholder="Player Name"
            value={player.name}
            onChange={(e) => handleChange(idx, "name", e.target.value)}
            required
            className="flex-1"
          />
          <Input
            type="email"
            placeholder="Email"
            value={player.email}
            onChange={(e) => handleChange(idx, "email", e.target.value)}
            className="flex-1"
          />
          <Input
            type="tel"
            placeholder="Phone Number"
            value={player.phone}
            onChange={(e) => handleChange(idx, "phone", e.target.value)}
            className="flex-1"
          />
          <Button
            type="button"
            onClick={() => handleRemovePlayer(idx)}
            className="bg-red-500 text-white px-2 py-1 rounded ml-2"
            disabled={players.length === 1}
          >
            Remove
          </Button>
        </div>
      ))}
      <Button
        type="button"
        onClick={handleAddPlayer}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Add Player
      </Button>
      <Button
        type="submit"
        className="bg-green-600 text-white px-4 py-2 rounded"
        disabled={submitting}
      >
        {submitting ? "Submitting..." : "Submit Check-in"}
      </Button>
    </form>
  );
};

export default ManualCheckinForm;
