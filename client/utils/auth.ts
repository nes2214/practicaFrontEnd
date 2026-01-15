// src/utils/auth.ts

// Helper per guardar/recuperar token
export const getToken = () => localStorage.getItem("access_token");
export const setToken = (token: string) => localStorage.setItem("access_token", token);
export const removeToken = () => localStorage.removeItem("access_token");

// Fetcher per SWR amb JWT
export const authFetcher = (url: string) => {
  const token = getToken();
  if (!token) throw new Error("Not authenticated");
  return fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => {
    if (!res.ok) throw new Error("Error fetching data");
    return res.json();
  });
};
