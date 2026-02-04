import { useState, useEffect } from "react";
import { getToken, authFetcher } from "../../utils/auth";

interface UserToken {
  username: string;
  role: string;
}

export default function UserInfo() {
  const [token] = useState<string | null>(getToken());
  const [user, setUser] = useState<UserToken | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      authFetcher<UserToken>("/api/users/me")
        .then(setUser)
        .catch(err => setError(err.message));
    }
  }, [token]);

  if (!token) return <p className="text-red-600">No estàs autenticat</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!user) return <p>Loading...</p>;

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border rounded shadow">
      <h2 className="text-xl mb-2 text-center">Token de prova </h2>

      <div className="bg-gray-100 p-2 rounded mb-4 break-all">
        <strong>Token:</strong>
        <p>{token}</p>
      </div>

      <div className="bg-gray-50 p-2 rounded">
        <p><strong>Usuari:</strong> {user.username}</p>
        <p><strong>Rol:</strong> {user.role}</p>
      </div>
    </div>
  );
}
