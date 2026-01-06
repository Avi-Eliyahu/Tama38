import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { ownersService, Owner } from '../services/owners';
import Breadcrumbs, { BreadcrumbItem } from '../components/Breadcrumbs';

export default function Owners() {
  const { t, i18n } = useTranslation();
  const isRTL = ['he', 'ar'].includes(i18n.language);
  const navigate = useNavigate();
  const [owners, setOwners] = useState<Owner[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const breadcrumbs: BreadcrumbItem[] = [
    { label: t('owners.title'), path: '/owners' },
  ];

  useEffect(() => {
    loadOwners();
  }, []);

  const loadOwners = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ownersService.getOwners();
      setOwners(data);
    } catch (err: any) {
      console.error('[OWNERS] Error loading owners', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadOwners();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const results = await ownersService.searchOwners(searchQuery);
      setOwners(results);
    } catch (err: any) {
      console.error('[OWNERS] Error searching owners', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      SIGNED: 'bg-green-100 text-green-800',
      PENDING: 'bg-yellow-100 text-yellow-800',
      NEGOTIATING: 'bg-blue-100 text-blue-800',
      AGREED_TO_SIGN: 'bg-blue-100 text-blue-800',
      WAIT_FOR_SIGN: 'bg-yellow-100 text-yellow-800',
      REFUSED: 'bg-red-100 text-red-800',
      NOT_CONTACTED: 'bg-gray-100 text-gray-800',
      ACTIVE: 'bg-blue-100 text-blue-800',
      INACTIVE: 'bg-gray-100 text-gray-800',
      COMPLETED: 'bg-green-100 text-green-800',
      ON_HOLD: 'bg-yellow-100 text-yellow-800',
      CANCELLED: 'bg-red-100 text-red-800',
      DECEASED: 'bg-gray-100 text-gray-800',
      INCAPACITATED: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

    const getOwnerStatusLabel = (status: string) => {
      const labels: Record<string, string> = {
        NOT_CONTACTED: t('owners.statusLabels.NOT_CONTACTED'),
        PENDING_SIGNATURE: t('owners.statusLabels.PENDING_SIGNATURE'),
        NEGOTIATING: t('owners.statusLabels.NEGOTIATING'),
        AGREED_TO_SIGN: t('owners.statusLabels.AGREED_TO_SIGN'),
        WAIT_FOR_SIGN: t('owners.statusLabels.WAIT_FOR_SIGN'),
        SIGNED: t('owners.statusLabels.SIGNED'),
        REFUSED: t('owners.statusLabels.REFUSED'),
        DECEASED: t('owners.statusLabels.DECEASED'),
        INCAPACITATED: t('owners.statusLabels.INCAPACITATED'),
      };
      return labels[status] || status;
    };

  if (loading && owners.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('owners.loadingOwners')}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <Breadcrumbs items={breadcrumbs} />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('owners.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">{t('owners.subtitle')}</p>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder={t('owners.searchPlaceholder')}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
          >
            {t('common.search')}
          </button>
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                loadOwners();
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              {t('common.clear')}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Owners List */}
      {owners.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">👥</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {searchQuery ? t('owners.noOwners') : t('owners.noOwnersYet')}
          </h3>
          <p className="text-gray-500">
            {searchQuery
              ? t('owners.tryDifferentSearch')
              : t('owners.willAppear')}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {t('owners.ownerName')}
                </th>
                <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {t('owners.contact')}
                </th>
                <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {t('owners.ownershipShare')}
                </th>
                <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {t('owners.status')}
                </th>
                <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                  {t('owners.preferredContact')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {owners.map((owner) => (
                    <tr
                      key={owner.owner_id}
                      onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromOwnersList: true } })}
                      className="hover:bg-gray-50 cursor-pointer"
                    >
                      <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                        <div className="text-sm font-medium text-teal-600 hover:text-teal-700">{owner.full_name}</div>
                      </td>
                  <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                    <div className={`text-sm text-gray-900 ${isRTL ? 'text-right' : ''}`}>
                      {owner.phone_for_contact && (
                        <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <span className={isRTL ? 'ml-2' : 'mr-2'}>📞</span>
                          <span>{owner.phone_for_contact}</span>
                        </div>
                      )}
                      {owner.email && (
                        <div className={`flex items-center mt-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                          <span className={isRTL ? 'ml-2' : 'mr-2'}>✉️</span>
                          <span>{owner.email}</span>
                        </div>
                      )}
                      {!owner.phone_for_contact && !owner.email && (
                        <span className="text-gray-400">{t('owners.noContactInfo')}</span>
                      )}
                    </div>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                    <div className="text-sm text-gray-900">{owner.ownership_share_percent}%</div>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(owner.owner_status)}`}
                    >
                      {getOwnerStatusLabel(owner.owner_status)}
                    </span>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                    <div className="text-sm text-gray-500">
                      {owner.preferred_contact_method || t('owners.notSpecified')}
                    </div>
                    {owner.preferred_language && (
                      <div className="text-xs text-gray-400 mt-1">
                        {t('owners.language')}: {owner.preferred_language}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
