import { apiClient } from './api';

export interface Lead {
  owner_id: string;
  owner_name: string;
  unit_id: string;
  unit_number: string;
  building_id: string;
  building_name: string;
  phone_for_contact?: string;
  email?: string;
  owner_status: string;
  priority: string;
  last_contact_date?: string;
  days_since_contact?: number;
  pending_tasks_count: number;
  signature_percentage: number;
  preferred_contact_method?: string;
}

export interface AgentDashboard {
  total_leads: number;
  high_priority_leads: number;
  pending_tasks: number;
  overdue_tasks: number;
  recent_interactions_today: number;
  leads_by_status: Record<string, number>;
}

class AgentsService {
  async getMyLeads(priorityFilter?: string, statusFilter?: string): Promise<Lead[]> {
    const params: any = {};
    if (priorityFilter) params.priority_filter = priorityFilter;
    if (statusFilter) params.status_filter = statusFilter;
    const response = await apiClient.get<Lead[]>('/agents/my-leads', { params });
    return response.data;
  }

  async getAgentDashboard(): Promise<AgentDashboard> {
    const response = await apiClient.get<AgentDashboard>('/agents/dashboard');
    return response.data;
  }

  async getMyAssignedOwners(): Promise<any[]> {
    const response = await apiClient.get<any[]>('/agents/my-assigned-owners');
    return response.data;
  }
}

export const agentsService = new AgentsService();

