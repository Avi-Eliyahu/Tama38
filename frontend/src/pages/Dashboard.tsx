import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { dashboardService, DashboardData } from '../services/dashboard';
import { authService } from '../services/auth';

export default function Dashboard() {
  const { t } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const dashboardData = await dashboardService.getDashboardData();
      setData(dashboardData);
    } catch (err: any) {
      console.error('[DASHBOARD] Error loading data', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('common.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const kpiCards = [
    {
      title: t('dashboard.totalProjects'),
      value: data.total_projects,
      change: `${data.active_projects} ${t('dashboard.activeProjects').toLowerCase()}`,
      icon: '🏗️',
      color: 'bg-blue-500',
      link: '/projects',
    },
    {
      title: t('dashboard.totalBuildings'),
      value: data.total_buildings,
      change: '',
      icon: '🏢',
      color: 'bg-green-500',
      link: '/buildings',
    },
    {
      title: t('dashboard.totalUnits'),
      value: data.total_units,
      change: '',
      icon: '🏠',
      color: 'bg-purple-500',
      link: '/buildings',
    },
    {
      title: t('dashboard.totalOwners'),
      value: data.total_owners,
      change: `${data.signed_percentage.toFixed(1)}% ${t('dashboard.signedPercentage').toLowerCase()}`,
      icon: '👥',
      color: 'bg-orange-500',
      link: '/owners',
    },
    {
      title: t('dashboard.pendingApprovals'),
      value: data.pending_approvals,
      change: t('dashboard.requiresAttention'),
      icon: '✍️',
      color: 'bg-yellow-500',
      link: '/approvals',
    },
    {
      title: t('dashboard.overdueTasks'),
      value: data.overdue_tasks,
      change: t('dashboard.needsAction'),
      icon: '⚠️',
      color: 'bg-red-500',
      link: '/tasks',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('dashboard.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('dashboard.subtitle')}
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kpiCards.map((card) => (
          <Link
            key={card.title}
            to={card.link}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{card.value}</p>
                {card.change && (
                  <p className="mt-1 text-sm text-gray-500">{card.change}</p>
                )}
              </div>
              <div className={`${card.color} w-12 h-12 rounded-lg flex items-center justify-center text-2xl`}>
                {card.icon}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Projects by Stage */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('dashboard.projectsByStage')}</h2>
          <div className="space-y-3">
            {Object.entries(data.projects_by_stage).map(([stage, count]) => (
              <div key={stage} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">{stage.toLowerCase()}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-teal-600 h-2 rounded-full"
                      style={{
                        width: `${data.total_projects > 0 ? (count / data.total_projects) * 100 : 0}%`,
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Buildings by Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('dashboard.buildingsByStatus')}</h2>
          <div className="space-y-3">
            {Object.entries(data.buildings_by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">
                  {status.toLowerCase().replace('_', ' ')}
                </span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${data.total_buildings > 0 ? (count / data.total_buildings) * 100 : 0}%`,
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-8 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
