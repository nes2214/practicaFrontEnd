import { getToken } from "../utils/auth";
import UserInfo from "../pages/UserInfo";
import Menu from "../pages/Menu";

export default function ProtectedPage() {
  const token = getToken();

  if (!token) {
    return (
      <p className="text-center mt-10 text-red-600">
        ⛔ Access denied. Please login.
      </p>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border rounded shadow">
      <h1 className="text-2xl mb-4 text-center">Welcome 🎉</h1>

      <Menu />

      <div className="mt-4 p-2 bg-gray-100 rounded text-xs break-all">
        <strong>Token (debug):</strong>
        <p>{token}</p>
      </div>

      <UserInfo />
    </div>
  );
}