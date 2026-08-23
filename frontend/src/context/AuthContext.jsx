import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getMe,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from "../services/authService";

import {
  getAccessToken,
  clearAccessToken,
} from "../services/api";

import { getErrorMessage } from "../utils/errors";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadSession() {
      const token = getAccessToken();

      // No token = definitely logged out
      if (!token) {
        if (!cancelled) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        const me = await getMe();

        if (!cancelled) {
          setUser(me);
          setError(null);
        }
      } catch (err) {
        console.error("Session check failed:", err);

        if (!cancelled) {
          setUser(null);
          setError(getErrorMessage(err));

          // Very important:
          // remove expired/invalid token
          clearAccessToken();
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadSession();

    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      isAuthenticated: Boolean(user),

      async login(credentials) {
        const result = await loginRequest(credentials);

        const me = await getMe();

        setUser(me);
        setError(null);

        return me;
      },

      async register(payload) {
        return registerRequest(payload);
      },

      logout() {
        logoutRequest();
        clearAccessToken();
        setUser(null);
        setError(null);
      },
    }),
    [user, loading, error]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);

  if (!ctx) {
    throw new Error(
      "useAuth must be used within AuthProvider"
    );
  }

  return ctx;
}