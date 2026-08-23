import axios from "axios";

const TOKEN_KEY = "scheduler.access_token";

const rawBase =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const baseURL = rawBase.endsWith("/")
  ? rawBase.slice(0, -1)
  : rawBase;



export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function clearAccessToken() {
  localStorage.removeItem(TOKEN_KEY);
}


export const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});


api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);


api.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    if (error?.response?.status === 401) {
      console.warn("Authentication failed. Clearing token.");

      clearAccessToken();

      if (
        typeof window !== "undefined" &&
        !window.location.pathname.startsWith("/login")
      ) {
        const next = encodeURIComponent(
          window.location.pathname + window.location.search
        );

        window.location.assign(`/login?next=${next}`);
      }
    }

    return Promise.reject(error);
  }
);