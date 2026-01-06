import { apiClient } from './api';

export interface Alert {
  alert_id: string;
  rule_id?: string;
  alert_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  message: string;
  project_id?: string;
  building_id?: string;
  owner_id?: string;
  task_id?: string;
  agent_id?: string;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED';
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
}

export interface AlertCountResponse {
  count: number;
  status: string;
}

class AlertsService {
  async getAlerts(params?: {
    status?: string;
    alert_type?: string;
    severity?: string;
    project_id?: string;
    building_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<Alert[]> {
    const response = await apiClient.get<Alert[]>('/alerts', { params });
    return response.data;
  }

  async getAlertCount(status: string = 'ACTIVE'): Promise<AlertCountResponse> {
    const response = await apiClient.get<AlertCountResponse>('/alerts/count', {
      params: { status },
    });
    return response.data;
  }

  async getAlertHistory(days: number = 30, skip?: number, limit?: number): Promise<Alert[]> {
    const response = await apiClient.get<Alert[]>('/alerts/history', {
      params: { days, skip, limit },
    });
    return response.data;
  }

  async acknowledgeAlert(alertId: string, notes?: string): Promise<void> {
    await apiClient.post(`/alerts/${alertId}/acknowledge`, { notes });
  }

  async resolveAlert(alertId: string, resolutionNotes?: string): Promise<void> {
    await apiClient.post(`/alerts/${alertId}/resolve`, { resolution_notes: resolutionNotes });
  }

  async dismissAlert(alertId: string): Promise<void> {
    await apiClient.post(`/alerts/${alertId}/dismiss`);
  }

  async triggerAlertChecks(): Promise<{ message: string; result: any }> {
    const response = await apiClient.post<{ message: string; result: any }>('/alerts/check');
    return response.data;
  }
}

export const alertsService = new AlertsService();

