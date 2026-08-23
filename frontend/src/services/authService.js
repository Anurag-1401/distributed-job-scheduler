import { api, setAccessToken } from "./api";

export async function register(payload) {
  console.log("Payload:", payload);

  try {
    const response = await api.post("/api/v1/auth/register", payload);
    console.log("Data:", response);

    return response.data;
  } catch (error) {
    console.error("Full error:", error);

    throw error;
  }
}

export async function login(payload) {
  const { data } = await api.post("/api/v1/auth/login", payload);
  const token = data.access_token || data.token;
  if (!token) {
    throw new Error("Login succeeded but no access token was returned");
  }
  setAccessToken(token);
  return data;
}

export async function getMe() {
  const { data } = await api.get("/api/v1/auth/me");
  return data;
}

export function logout() {
  setAccessToken(null);
}
