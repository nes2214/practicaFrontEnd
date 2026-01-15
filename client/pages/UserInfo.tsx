import useSWR from "swr";
import { authFetcher } from "../utils/auth";

export default function UserInfo() {
  const { data, error, isValidating } = useSWR("/users/me", authFetcher);

  if (error) return <p className="text-center text-red-600 mt-5">{error.message}</p>;
  if (isValidating) return <p className="text-center mt-5">Loading...</p>;

  return (
    <div className="text-center mt-5">
      <p>Username: {data.username}</p>
      <p>Role: {data.role}</p>
    </div>
  );
}
