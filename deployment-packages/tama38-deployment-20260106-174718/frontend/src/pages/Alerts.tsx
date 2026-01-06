import { useEffect, useState } from 'react';
import { alertsService, Alert } from '../services/alerts';
import { authService } from '../services/auth';

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [, setAlertCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('ACTIVE');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  
  const currentUser = authService.getCurrentUserSync();
  const isManager = currentUser?.role && ['SUPER_ADMIN', 'PROJECT_MANAGER'].includes(currentUser.role);

  useEffect(() => {
    loadAlerts();
    loadAlertCount();
  }, [statusFilter, typeFilter, severityFilter]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { status: statusFilter };
      if (typeFilter) params.alert_type = typeFilter;
      if (severityFilter) params.severity = severityFilter;
      
      const data = await alertsService.getAlerts(params);
      setAlerts(data);
    } catch (err: any) {
      console.error('[ALERTS] Error loading alerts', err);
      setError(err.response?.data?.detail || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const loadAlertCount = async () => {
    try {
      const data = await alertsService.getAlertCount('ACTIVE');
      setAlertCount(data.count);
    } catch (err: any) {
      console.error('[ALERTS] Error loading alert count', err);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await alertsService.acknowledgeAlert(alertId);
      await loadAlerts();
      await loadAlertCount();
    } catch (err: any) {
      console.error('[ALERTS] Error acknowledging alert', err);
      setError(err.response?.data?.detail || 'Failed to acknowledge alert');
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await alertsService.resolveAlert(alertId);
      await loadAlerts();
      await loadAlertCount();
    } catch (err: any) {
      console.error('[ALERTS] Error resolving alert', err);
      setError(err.response?.data?.detail || 'Failed to resolve alert');
    }
  };

  const handleDismiss = async (alertId: string) => {
    try {
      await alertsService.dismissAlert(alertId);
      await loadAlerts();
      await loadAlertCount();
    } catch (err: any) {
      console.error('[ALERTS] Error dismissing alert', err);
      setError(err.response?.data?.detail || 'Failed to dismiss alert');
    }
  };

  const handleTriggerChecks = async () => {
    try {
      setLoading(true);
      await alertsService.triggerAlertChecks();
      await loadAlerts();
      await loadAlertCount();
    } catch (err: any) {
      console.error('[ALERTS] Error triggering checks', err);
      setError(err.response?.data?.detail || 'Failed to trigger alert checks');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      LOW: 'bg-gray-100 text-gray-800 border-gray-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      CRITICAL: 'bg-red-100 text-red-800 border-red-300',
    };
    return colors[severity] || colors.LOW;
  };

  const getAlertTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      THRESHOLD_VIOLATION: '⚠️',
      AGENT_INACTIVITY: '👤',
      OVERDUE_TASK: '⏰',
      PENDING_APPROVAL: '✍️',
      OWNERSHIP_TRANSFER: '🔄',
      SYSTEM_ERROR: '❌',
    };
    return icons[type] || '🔔';
  };

  if (loading && alerts.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading alerts...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts & Notifications</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and manage system alerts
          </p>
        </div>
        {isManager && (
          <button
            onClick={handleTriggerChecks}
            disabled={loading}
            className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Running...' : 'Run Alert Checks'}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            >
              <option value="ACTIVE">Active</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="RESOLVED">Resolved</option>
              <option value="DISMISSED">Dismissed</option>
              <option value="">All</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type
            </label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            >
              <option value="">All Types</option>
              <option value="THRESHOLD_VIOLATION">Threshold Violation</option>
              <option value="AGENT_INACTIVITY">Agent Inactivity</option>
              <option value="OVERDUE_TASK">Overdue Task</option>
              <option value="PENDING_APPROVAL">Pending Approval</option>
              <option value="OWNERSHIP_TRANSFER">Ownership Transfer</option>
              <option value="SYSTEM_ERROR">System Error</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Severity
            </label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            >
              <option value="">All Severities</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">🔔</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No alerts found</h3>
          <p className="text-gray-500">
            {statusFilter === 'ACTIVE'
              ? 'No active alerts at this time.'
              : `No ${statusFilter.toLowerCase()} alerts found.`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`bg-white rounded-lg shadow-sm border-2 ${
                alert.severity === 'CRITICAL'
                  ? 'border-red-300'
                  : alert.severity === 'HIGH'
                  ? 'border-orange-300'
                  : 'border-gray-200'
              } p-6`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getAlertTypeIcon(alert.alert_type)}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{alert.title}</h3>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded border ${getSeverityColor(
                        alert.severity
                      )}`}
                    >
                      {alert.severity}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        alert.status === 'ACTIVE'
                          ? 'bg-blue-100 text-blue-800'
                          : alert.status === 'ACKNOWLEDGED'
                          ? 'bg-yellow-100 text-yellow-800'
                          : alert.status === 'RESOLVED'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {alert.status}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3">{alert.message}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>
                      Type: <span className="font-medium">{alert.alert_type.replace('_', ' ')}</span>
                    </span>
                    <span>
                      Created: <span className="font-medium">{new Date(alert.created_at).toLocaleString()}</span>
                    </span>
                    {alert.acknowledged_at && (
                      <span>
                        Acknowledged: <span className="font-medium">{new Date(alert.acknowledged_at).toLocaleString()}</span>
                      </span>
                    )}
                    {alert.resolved_at && (
                      <span>
                        Resolved: <span className="font-medium">{new Date(alert.resolved_at).toLocaleString()}</span>
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  {alert.status === 'ACTIVE' && (
                    <>
                      <button
                        onClick={() => handleAcknowledge(alert.alert_id)}
                        className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200"
                      >
                        Acknowledge
                      </button>
                      {isManager && (
                        <button
                          onClick={() => handleResolve(alert.alert_id)}
                          className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                        >
                          Resolve
                        </button>
                      )}
                      <button
                        onClick={() => handleDismiss(alert.alert_id)}
                        className="px-3 py-1 text-sm bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
                      >
                        Dismiss
                      </button>
                    </>
                  )}
                  {alert.status === 'ACKNOWLEDGED' && isManager && (
                    <button
                      onClick={() => handleResolve(alert.alert_id)}
                      className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

