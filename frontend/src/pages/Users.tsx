import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { usersService, User, CreateUserData } from '../services/users';
import Modal from '../components/Modal';

export default function Users() {
  const { t, i18n } = useTranslation();
  const isRTL = ['he', 'ar'].includes(i18n.language);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [formData, setFormData] = useState<CreateUserData>({
    email: '',
    password: '',
    full_name: '',
    role: 'AGENT',
    phone: '',
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      // Load both PROJECT_MANAGER and AGENT users
      const [managers, agents] = await Promise.all([
        usersService.getUsers('PROJECT_MANAGER'),
        usersService.getUsers('AGENT'),
      ]);
      setUsers([...managers, ...agents]);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email format';
    }

    if (!formData.password.trim()) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    if (!formData.full_name.trim()) {
      errors.full_name = 'Full name is required';
    }

    if (!formData.role || !['PROJECT_MANAGER', 'AGENT'].includes(formData.role)) {
      errors.role = 'Role must be PROJECT_MANAGER or AGENT';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const userData: CreateUserData = {
        email: formData.email.trim(),
        password: formData.password,
        full_name: formData.full_name.trim(),
        role: formData.role,
        phone: formData.phone?.trim() || undefined,
      };

      await usersService.createUser(userData);
      setSuccess(t('users.createSuccess', 'User {{email}} created successfully', { email: userData.email }));
      setIsAddModalOpen(false);
      resetForm();
      loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('users.createError', 'Failed to create user'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      full_name: '',
      role: 'AGENT',
      phone: '',
    });
    setFormErrors({});
  };

  const handleDeleteUser = async (user: User) => {
    const confirmMessage = t('users.confirmDelete', 'Are you sure you want to delete user "{{name}}" ({{email}})?', {
      name: user.full_name,
      email: user.email
    });
    if (window.confirm(confirmMessage)) {
      try {
        await usersService.deleteUser(user.user_id);
        setSuccess(t('users.deleteSuccess', 'User {{email}} deleted successfully', { email: user.email }));
        loadUsers();
      } catch (err: any) {
        setError(err.response?.data?.detail || t('users.deleteError', 'Failed to delete user'));
      }
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      PROJECT_MANAGER: 'bg-blue-100 text-blue-800',
      AGENT: 'bg-green-100 text-green-800',
      SUPER_ADMIN: 'bg-purple-100 text-purple-800',
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  const getRoleLabel = (role: string) => {
    return role.replace('_', ' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('common.loading')}</div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isRTL ? 'text-right' : ''}`}>
      {/* Header */}
      <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className={isRTL ? 'text-right' : ''}>
          <h1 className="text-3xl font-bold text-gray-900">{t('users.title', 'User Management')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('users.subtitle', 'Manage Project Managers and Agents')}
          </p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className={`inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium ${isRTL ? 'flex-row-reverse' : ''}`}
        >
          <span className={isRTL ? 'ml-2' : 'mr-2'}>+</span>
          {t('users.addUser', 'Add User')}
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {/* Users Table */}
      {users.length === 0 ? (
        <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center ${isRTL ? 'text-right' : ''}`}>
          <div className="text-6xl mb-4">👤</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('users.noUsers', 'No Users Found')}</h3>
          <p className="text-gray-500 mb-6">{t('users.getStarted', 'Get started by adding a new user')}</p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="inline-block px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
          >
            {t('users.addUser', 'Add User')}
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                    {t('users.name', 'Name')}
                  </th>
                  <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                    {t('users.email', 'Email')}
                  </th>
                  <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                    {t('users.role', 'Role')}
                  </th>
                  <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                    {t('users.phone', 'Phone')}
                  </th>
                  <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                    {t('users.status', 'Status')}
                  </th>
                  <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-left' : 'text-right'}`}>
                    {t('common.actions', 'Actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50">
                    <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                      <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                      <div className="text-sm text-gray-900">{user.email}</div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${getRoleBadgeColor(user.role)}`}
                      >
                        {getRoleLabel(user.role)}
                      </span>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                      <div className="text-sm text-gray-500">{user.phone || '-'}</div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? t('users.active', 'Active') : t('users.inactive', 'Inactive')}
                      </span>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${isRTL ? 'text-left' : 'text-right'}`}>
                      <button
                        onClick={() => handleDeleteUser(user)}
                        className="text-red-600 hover:text-red-900 transition-colors"
                      >
                        {t('common.delete', 'Delete')}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          resetForm();
          setError(null);
          setSuccess(null);
        }}
        title={t('users.addNewUser', 'Add New User')}
        size="md"
      >
        <form onSubmit={handleSubmit} className={`space-y-4 ${isRTL ? 'text-right' : ''}`}>
          <div>
            <label htmlFor="email" className={`block text-sm font-medium text-gray-700 mb-1 ${isRTL ? 'text-right' : ''}`}>
              {t('users.email', 'Email')} *
            </label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                isRTL ? 'text-right' : ''
              } ${
                formErrors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="user@example.com"
              dir="ltr"
            />
            {formErrors.email && (
              <p className={`mt-1 text-sm text-red-600 ${isRTL ? 'text-right' : ''}`}>{formErrors.email}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className={`block text-sm font-medium text-gray-700 mb-1 ${isRTL ? 'text-right' : ''}`}>
              {t('users.password', 'Password')} *
            </label>
            <input
              type="password"
              id="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                isRTL ? 'text-right' : ''
              } ${
                formErrors.password ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder={t('users.passwordPlaceholder', 'Minimum 6 characters')}
              dir="ltr"
            />
            {formErrors.password && (
              <p className={`mt-1 text-sm text-red-600 ${isRTL ? 'text-right' : ''}`}>{formErrors.password}</p>
            )}
          </div>

          <div>
            <label htmlFor="full_name" className={`block text-sm font-medium text-gray-700 mb-1 ${isRTL ? 'text-right' : ''}`}>
              {t('users.fullName', 'Full Name')} *
            </label>
            <input
              type="text"
              id="full_name"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                isRTL ? 'text-right' : ''
              } ${
                formErrors.full_name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder={t('users.fullNamePlaceholder', 'John Doe')}
            />
            {formErrors.full_name && (
              <p className={`mt-1 text-sm text-red-600 ${isRTL ? 'text-right' : ''}`}>{formErrors.full_name}</p>
            )}
          </div>

          <div>
            <label htmlFor="role" className={`block text-sm font-medium text-gray-700 mb-1 ${isRTL ? 'text-right' : ''}`}>
              {t('users.role', 'Role')} *
            </label>
            <select
              id="role"
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as 'PROJECT_MANAGER' | 'AGENT' })}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                isRTL ? 'text-right' : ''
              } ${
                formErrors.role ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="AGENT">{t('users.agent', 'Agent')}</option>
              <option value="PROJECT_MANAGER">{t('users.projectManager', 'Project Manager')}</option>
            </select>
            {formErrors.role && (
              <p className={`mt-1 text-sm text-red-600 ${isRTL ? 'text-right' : ''}`}>{formErrors.role}</p>
            )}
          </div>

          <div>
            <label htmlFor="phone" className={`block text-sm font-medium text-gray-700 mb-1 ${isRTL ? 'text-right' : ''}`}>
              {t('users.phone', 'Phone')} ({t('common.optional', 'Optional')})
            </label>
            <input
              type="tel"
              id="phone"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                isRTL ? 'text-right' : ''
              }`}
              placeholder="+1234567890"
              dir="ltr"
            />
          </div>

          <div className={`flex gap-3 pt-4 border-t ${isRTL ? 'flex-row-reverse justify-start' : 'justify-end'}`}>
            <button
              type="button"
              onClick={() => {
                setIsAddModalOpen(false);
                resetForm();
                setError(null);
                setSuccess(null);
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              {t('common.cancel', 'Cancel')}
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? t('users.creating', 'Creating...') : t('users.createUser', 'Create User')}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

