import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login, token } = useAuth();
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    if (token) {
      navigate('/dashboard', { replace: true });
    }
  }, [token, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ email, password });
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      console.error('Login failed:', err);
      const errorMessage =
        (err as { response?: { data?: { message?: string } } })?.response?.data?.message ||
        'Invalid email or password. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ backgroundColor: 'var(--page-bg)' }}
    >
      <div className="w-full max-w-md">
        {/* Login Card */}
        <div
          className="rounded-xl shadow-lg p-8"
          style={{ backgroundColor: 'var(--white)' }}
        >
          {/* Logo */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="text-[#7aecb4] text-3xl">⬡</span>
            <span className="text-[#1e2d3b] font-bold text-2xl tracking-wide">LUMBER</span>
          </div>

          {/* Subtitle */}
          <p className="text-center text-[#6b7280] mb-8">Sign in to your account</p>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-[#374151] mb-2"
              >
                Email address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                className="w-full px-4 py-3 rounded-lg border border-[#d0d5dd] text-[#111827] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-[#7aecb4] focus:border-transparent transition-all disabled:bg-gray-50 disabled:cursor-not-allowed"
                placeholder="you@example.com"
              />
            </div>

            {/* Password Field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-[#374151] mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                className="w-full px-4 py-3 rounded-lg border border-[#d0d5dd] text-[#111827] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-[#7aecb4] focus:border-transparent transition-all disabled:bg-gray-50 disabled:cursor-not-allowed"
                placeholder="Enter your password"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full py-3 px-4 rounded-lg font-semibold text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                backgroundColor: loading ? '#9ca3af' : '#7aecb4',
              }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-[#6b7280]">
              Having trouble?{' '}
              <a
                href="mailto:support@lumberfi.com"
                className="text-[#2563eb] hover:underline font-medium"
              >
                Contact support
              </a>
            </p>
          </div>
        </div>

        {/* Brand Footer */}
        <p className="text-center text-xs text-[#9ca3af] mt-6">
          © {new Date().getFullYear()} Lumber. All rights reserved.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
