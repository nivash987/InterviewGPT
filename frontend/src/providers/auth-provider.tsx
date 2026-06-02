"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

import { ROUTES } from "@/constants/routes";
import {
  clearTokens,
  getRefreshToken,
  hasAccessToken,
  setTokens,
} from "@/lib/auth/tokens";
import { getErrorMessage } from "@/lib/errors";
import { authService, usersService } from "@/services";
import type {
  LoginCredentials,
  RegisterCredentials,
  UserProfile,
} from "@/types/auth";

interface AuthContextValue {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!hasAccessToken()) {
      setUser(null);
      return;
    }

    try {
      const profile = await usersService.getMe();
      setUser(profile);
    } catch {
      clearTokens();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      if (!hasAccessToken()) {
        if (!cancelled) {
          setUser(null);
          setIsLoading(false);
        }
        return;
      }

      try {
        const profile = await usersService.getMe();
        if (!cancelled) {
          setUser(profile);
        }
      } catch {
        clearTokens();
        if (!cancelled) {
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const tokens = await authService.login(credentials);
      setTokens(tokens);
      const profile = await usersService.getMe();
      setUser(profile);
      router.push(ROUTES.dashboard);
      router.refresh();
    },
    [router],
  );

  const register = useCallback(
    async (credentials: RegisterCredentials) => {
      const result = await authService.register(credentials);

      if (result.tokens) {
        setTokens(result.tokens);
        const profile = await usersService.getMe();
        setUser(profile);
        router.push(ROUTES.dashboard);
        router.refresh();
        return;
      }

      router.push(`${ROUTES.checkEmail}?email=${encodeURIComponent(credentials.email)}`);
      router.refresh();
    },
    [router],
  );

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();

    try {
      if (hasAccessToken()) {
        await authService.logout(refreshToken);
      }
    } catch (error) {
      console.warn("Logout request failed:", getErrorMessage(error));
    } finally {
      clearTokens();
      setUser(null);
      router.push(ROUTES.login);
      router.refresh();
    }
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
