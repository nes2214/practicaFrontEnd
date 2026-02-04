import { useState } from "react";
import { getToken } from "../utils/auth"; // ← AÑADE ESTE IMPORT

interface AddUserFormsProps {
  onDoctorAdded: () => void;
  onCancel: () => void;
}

export default function AddUserForms({
  onDoctorAdded,
  onCancel,
}: AddUserFormsProps) {
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = getToken(); // ← AÑADE ESTA LÍNEA
      
      const res = await fetch("/api/doctors", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`, // ← AÑADE ESTA LÍNEA
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          name,
          age: Number(age),
        }),
      });

      if (!res.ok) {
        throw new Error("Error creating doctor");
      }

      onDoctorAdded();
    } catch (err) {
      setError("No s'ha pogut crear el doctor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow p-6 border mt-6">
      <h3 className="text-xl font-bold mb-4">Afegir Doctor</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          className="w-full border rounded p-2"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          type="text"
          placeholder="Name"
          className="w-full border rounded p-2"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Age"
          className="w-full border rounded p-2"
          value={age}
          onChange={(e) => setAge(e.target.value === "" ? "" : Number(e.target.value))}
          required
        />

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            {loading ? "Guardant..." : "Guardar"}
          </button>

          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded"
          >
            Cancel·lar
          </button>
        </div>
      </form>
    </div>
  );
}