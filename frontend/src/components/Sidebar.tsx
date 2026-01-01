import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { authService } from '../services/auth';

const navigationKeys = [
  { key: 'dashboard', href: '/dashboard', icon: '📊' },
  { key: 'projects', href: '/projects', icon: '🏗️' },
  { key: 'buildings', href: '/buildings', icon: '🏢' },
  { key: 'owners', href: '/owners', icon: '👥' },
  { key: 'interactions', href: '/interactions', icon: '💬' },
  { key: 'tasks', href: '/tasks', icon: '✅' },
  { key: 'approvals', href: '/approvals', icon: '✍️' },
  { key: 'alerts', href: '/alerts', icon: '🔔' },
  { key: 'documents', href: '/documents', icon: '📄' },
  { key: 'reports', href: '/reports', icon: '📊' },
  { key: 'agentMobile', href: '/agent', icon: '📱', roles: ['AGENT'] },
];

export default function Sidebar() {
  const { t, i18n } = useTranslation();
  const user = authService.getCurrentUserSync();
  const userRole = user?.role || '';
  const isRTL = ['he', 'ar'].includes(i18n.language);

  // Translate navigation items
  const navigation = navigationKeys.map((item) => ({
    ...item,
    name: t(`navigation.${item.key}`),
  }));

  // Filter navigation based on role
  const filteredNav = navigation.filter((item) => {
    if (item.href === '/approvals' && !['SUPER_ADMIN', 'PROJECT_MANAGER'].includes(userRole)) {
      return false;
    }
    // Show Agent Mobile only for AGENT role
    if ((item as any).roles && !(item as any).roles.includes(userRole)) {
      return false;
    }
    return true;
  });

  return (
    <div className={`w-64 bg-white flex flex-col ${isRTL ? 'border-l border-gray-200' : 'border-r border-gray-200'}`}>
      {/* Logo */}
      <div className={`h-16 flex items-center border-b border-gray-200 ${isRTL ? 'px-6' : 'px-6'}`}>
        <div className={`flex items-center ${isRTL ? 'flex-row-reverse gap-3' : 'gap-3'}`}>
          <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-lg flex items-center justify-center text-white font-bold text-lg">
            T38
          </div>
          <div>
            <div className="font-semibold text-gray-900 text-sm">TAMA38</div>
            <div className="text-xs text-gray-500">Urban Renewal</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className={`flex-1 py-4 space-y-1 ${isRTL ? 'px-4' : 'px-4'}`}>
        {filteredNav.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isRTL ? 'flex-row-reverse gap-3' : 'gap-3'
              } ${
                isActive
                  ? 'bg-teal-50 text-teal-700 border border-teal-200'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span className={isRTL ? 'text-right' : ''}>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* User Info */}
      {user && (
        <div className="border-t border-gray-200 p-4">
          <div className={`flex items-center ${isRTL ? 'flex-row-reverse gap-3' : 'gap-3'}`}>
            <div className="w-8 h-8 bg-teal-500 rounded-full flex items-center justify-center text-white text-xs font-semibold">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                {user.full_name}
              </div>
              <div className="text-xs text-gray-500 truncate">
                {user.role.replace('_', ' ')}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

