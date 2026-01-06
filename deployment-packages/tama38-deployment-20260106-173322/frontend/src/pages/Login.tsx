import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { authService, LoginCredentials } from '../services/auth';

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Login.tsx:12',message:'handleSubmit called',data:{email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion

    try {
      const credentials: LoginCredentials = { email, password };
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Login.tsx:19',message:'Calling authService.login',data:{email},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      
      await authService.login(credentials);
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Login.tsx:22',message:'authService.login completed',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      // Redirect agents to agent mobile view, others to dashboard
      const user = authService.getCurrentUserSync();
      const redirectPath = user?.role === 'AGENT' ? '/agent' : '/dashboard';
      navigate(redirectPath);
    } catch (err: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Login.tsx:25',message:'Login error caught',data:{error:err?.message,status:err?.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      
      setError(err.response?.data?.detail || t('auth.loginError'));
      console.error('[LOGIN] Error', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            {t('common.appName')}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {t('auth.loginSubtitle')}
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                {t('auth.email')}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                placeholder={t('auth.email')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                {t('auth.password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                placeholder={t('auth.password')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
            >
              {loading ? t('common.loading') : t('auth.login')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

