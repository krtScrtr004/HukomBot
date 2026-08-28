import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { getCurrentUser, logout } from '@/services/authService';
import type { UserResponse } from '@/types/user';

interface AuthContextValue {
  user: UserResponse | null;
  loading: boolean;
  login: (user: UserResponse) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const login = (u: UserResponse) => {
    setUser(u);
  };

  const performLogout = async () => {
    await logout();
    setUser(null);
  };

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const u = await getCurrentUser();
        setUser(u);
      } catch (e) {
        // ignore if not auth
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout: performLogout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
};

