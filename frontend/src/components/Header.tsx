import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { authService } from '../services/auth';
import { alertsService } from '../services/alerts';
import { useNavigate, Link } from 'react-router-dom';
import LanguageSwitcher from './LanguageSwitcher';

export default function Header() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [user, setUser] = useState(authService.getCurrentUserSync());
  const [alertCount, setAlertCount] = useState<number>(0);
  const isRTL = ['he', 'ar'].includes(i18n.language);

  useEffect(() => {
    // Load user if token exists but user is not loaded
    const loadUser = async () => {
      if (authService.isAuthenticated() && !user) {
        try {
          const loadedUser = await authService.getCurrentUser();
          setUser(loadedUser);
        } catch (error) {
          console.error('[HEADER] Failed to load user', error);
        }
      }
    };
    
    loadUser();
    loadAlertCount();
    // Refresh alert count every 30 seconds
    const interval = setInterval(loadAlertCount, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const loadAlertCount = async () => {
    try {
      const data = await alertsService.getAlertCount('ACTIVE');
      setAlertCount(data.count);
    } catch (err: any) {
      // Silently fail - alerts are not critical for header
      console.error('[HEADER] Error loading alert count', err);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      navigate('/login');
    } catch (error) {
      console.error('[HEADER] Logout error', error);
      // Force logout on error
      navigate('/login');
    }
  };

  return (
    <header className={`h-16 bg-white border-b border-gray-200 flex items-center px-6 ${isRTL ? 'flex-row-reverse justify-between' : 'justify-between'}`}>
      <div className={`flex items-center ${isRTL ? 'flex-row-reverse gap-4' : 'gap-4'}`}>
        <h1 className={`text-xl font-semibold text-gray-900 ${isRTL ? 'text-right' : ''}`}>{t('common.appName')}</h1>
      </div>

      <div className={`flex items-center ${isRTL ? 'flex-row-reverse gap-4' : 'gap-4'}`}>
        {/* Language Switcher - Always visible */}
        <LanguageSwitcher />
        
        {user && (
          <>
            {/* Alerts Badge */}
            <Link
              to="/alerts"
              className="relative px-3 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
              title="Alerts & Notifications"
            >
              <span className="text-xl">🔔</span>
              {alertCount > 0 && (
                <span className={`absolute -top-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center ${isRTL ? '-left-1' : '-right-1'}`}>
                  {alertCount > 99 ? '99+' : alertCount}
                </span>
              )}
            </Link>
            
            <div className="text-sm text-gray-600">
              <span className="font-medium">{user.full_name}</span>
              <span className="mx-2">•</span>
              <span className="text-gray-500">{user.role.replace('_', ' ')}</span>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
            >
              {t('auth.logout')}
            </button>
          </>
        )}
      </div>
    </header>
  );
}

