import { apiClient } from './api';

export interface DashboardData {
  total_projects: number;
  active_projects: number;
  total_buildings: number;
  total_units: number;
  total_owners: number;
  signed_percentage: number;
  pending_approvals: number;
  overdue_tasks: number;
  recent_interactions: number;
  projects_by_stage: {
    PLANNING: number;
    ACTIVE: number;
    APPROVAL: number;
    COMPLETED: number;
    ARCHIVED: number;
  };
  buildings_by_status: {
    INITIAL: number;
    NEGOTIATING: number;
    APPROVED: number;
    RENOVATION_PLANNING: number;
    RENOVATION_ONGOING: number;
    COMPLETED: number;
  };
}

class DashboardService {
  async getDashboardData(): Promise<DashboardData> {
    const response = await apiClient.get<DashboardData>('/dashboard/data');
    return response.data;
  }
}

export const dashboardService = new DashboardService();

