import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="bg-surface-container-low min-h-screen flex flex-col items-center justify-center p-md font-body-md text-on-surface select-none">
      {/* Login Container */}
      <main className="w-full max-w-[440px] animate-in fade-in duration-700">
        {/* Brand Identity */}
        <div className="flex flex-col items-center mb-xl">
          <div className="w-12 h-12 bg-primary-container rounded-xl flex items-center justify-center mb-md login-card-shadow">
            <span
              className="material-symbols-outlined text-on-primary-container !text-[28px]"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              bolt
            </span>
          </div>
          <h1 className="font-headline-md text-headline-md text-primary tracking-tight">Eco Plug</h1>
        </div>
        
        {/* Login Card */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-xl login-card-shadow">
          {/* Header Section */}
          <header className="mb-xl">
            <h2 className="font-headline-md text-headline-md text-on-surface mb-xs">Sign In</h2>
            <p className="font-body-sm text-body-sm text-secondary">Enter your credentials to access the workspace.</p>
          </header>
          
          {error && (
            <div className="mb-md p-3 bg-error-container text-on-error-container rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form className="space-y-lg" onSubmit={handleSubmit}>
            {/* Email Input */}
            <div className="space-y-xs">
              <label className="font-label-md text-label-md text-on-surface-variant block" htmlFor="email">
                Email address
              </label>
              <input
                className="w-full px-md py-[16px] bg-surface-container-lowest border border-outline rounded-lg font-body-md text-on-surface focus-ring transition-all placeholder:text-outline"
                id="email"
                name="email"
                placeholder="name@company.com"
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            
            {/* Password Input */}
            <div className="space-y-xs relative">
              <div className="flex justify-between items-center">
                <label className="font-label-md text-label-md text-on-surface-variant block" htmlFor="password">
                  Password
                </label>
                <a className="font-label-sm text-label-sm text-primary hover:underline transition-all" href="#">
                  Forgot Password?
                </a>
              </div>
              <div className="relative">
                <input
                  className="w-full px-md py-[16px] bg-surface-container-lowest border border-outline rounded-lg font-body-md text-on-surface focus-ring transition-all placeholder:text-outline pr-[48px]"
                  id="password"
                  name="password"
                  placeholder="••••••••"
                  required
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  aria-label="Toggle password visibility"
                  className="absolute right-md top-1/2 -translate-y-1/2 text-secondary hover:text-on-surface-variant transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                  type="button"
                >
                  <span className="material-symbols-outlined" id="password-toggle-icon">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>
            
            {/* Action Button */}
            <button
              className="w-full bg-primary-container text-on-primary-container font-headline-md py-md rounded-lg hover:brightness-95 active:scale-[0.98] transition-all login-card-shadow mt-md"
              type="submit"
            >
              Sign In
            </button>
          </form>
          
          {/* Social Login / Alternate (Optional Visual Polish) */}
          <div className="mt-xl pt-lg border-t border-outline-variant text-center">
            <p className="font-label-sm text-label-sm text-secondary">Secure SSO enabled for verified domains</p>
          </div>
        </div>
        
        {/* Footer Text */}
        <footer className="mt-xl text-center">
          <p className="font-label-sm text-label-sm text-outline tracking-wider uppercase">
            Eco Plug Intelligence Dashboard
          </p>
          <p className="mt-base font-body-sm text-body-sm text-outline/50">
            © 2024 Eco Plug Workspace. All rights reserved.
          </p>
        </footer>
      </main>
    </div>
  );
}
