import { useEffect, useState } from "react";

interface Doctor {
  username: string;
  name: string;
}

export default function Doctors() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const res = await fetch("/api/doctors");
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data: Doctor[] = await res.json();
        setDoctors(data);
      } catch (err) {
        console.error("Error fetching doctors:", err);
        setError("Failed to fetch doctors");
      } finally {
        setLoading(false);
      }
    };

    fetchDoctors();
  }, []);

  if (loading) return <p>Loading doctors…</p>;
  if (error) return <p>{error}</p>;
  if (doctors.length === 0) return <p>No doctors available</p>;

  return (
    <div>
      <h2>Doctors</h2>
      <ul>
        {doctors.map((doc) => (
          <li key={doc.username}>
            {doc.name} ({doc.username})
          </li>
        ))}
      </ul>
    </div>
  );
}
