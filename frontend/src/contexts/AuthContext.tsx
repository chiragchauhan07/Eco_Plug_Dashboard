import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { AuthService, type UserProfile } from '../services/auth.service';
import { TokenService } from '../services/token.service';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (TokenService.hasTokens()) {
        try {
          const profile = await AuthService.getProfile();
          setUser(profile);
        } catch {
          TokenService.clearTokens();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    await AuthService.login(email, password);
    const profile = await AuthService.getProfile();
    setUser(profile);
  };

  const logout = () => {
    setUser(null);
    AuthService.logout();
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
