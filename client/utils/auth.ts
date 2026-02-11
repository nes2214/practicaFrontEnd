// src/utils/auth.ts

// Guardar/recuperar token
export const getToken = () => localStorage.getItem("access_token");
export const setToken = (token: string) => localStorage.setItem("access_token", token);
export const removeToken = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_role"); // limpiar rol también
};

// Guardar/recuperar rol
export const setUserRole = (role: string) => localStorage.setItem("user_role", role);
export const getUserRole = () => localStorage.getItem("user_role");
export const removeUserRole = () => localStorage.removeItem("user_role");

// Fetcher per SWR o fetch simple amb JWT
export const authFetcher = <T>(url: string): Promise<T> => {
  const token = getToken();
  if (!token) throw new Error("Not authenticated");
  return fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => {
    if (!res.ok) throw new Error("Error fetching data");
    return res.json() as Promise<T>;
  });
};
