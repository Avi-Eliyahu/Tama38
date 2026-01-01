import { apiClient } from './api';

export interface Interaction {
  log_id: string;
  owner_id: string;
  agent_id: string;
  interaction_type: string;
  interaction_date: string;
  interaction_timestamp: string;
  duration_minutes?: number;
  outcome?: string;
  call_summary: string;
  sentiment?: string;
  created_at: string;
}

export interface CreateInteractionDto {
  owner_id: string;
  interaction_type: string;
  interaction_date: string;
  duration_minutes?: number;
  outcome?: string;
  call_summary: string;
  key_objection?: string;
  next_action?: string;
  next_follow_up_date?: string;
  follow_up_type?: string;
  sentiment?: string;
  is_escalated?: boolean;
  escalation_reason?: string;
  attempted?: boolean;
  contact_method_used?: string;
}

class InteractionsService {
  async getInteractions(ownerId?: string): Promise<Interaction[]> {
    const params = ownerId ? { owner_id: ownerId } : {};
    const response = await apiClient.get<Interaction[]>('/interactions', { params });
    return response.data;
  }

  async getInteractionsByOwner(ownerId: string): Promise<Interaction[]> {
    return this.getInteractions(ownerId);
  }

  async getInteractionsByUnit(unitId: string, ownerIds: string[]): Promise<Interaction[]> {
    // Get interactions for all owners of a unit
    const allInteractions: Interaction[] = [];
    for (const ownerId of ownerIds) {
      const interactions = await this.getInteractions(ownerId);
      allInteractions.push(...interactions);
    }
    // Sort by timestamp descending
    return allInteractions.sort((a, b) => 
      new Date(b.interaction_timestamp).getTime() - new Date(a.interaction_timestamp).getTime()
    );
  }

  async getRecentInteractions(): Promise<Interaction[]> {
    const response = await apiClient.get<Interaction[]>('/interactions/recent');
    return response.data;
  }

  async createInteraction(data: CreateInteractionDto): Promise<Interaction> {
    const response = await apiClient.post<Interaction>('/interactions', data);
    return response.data;
  }
}

export const interactionsService = new InteractionsService();

