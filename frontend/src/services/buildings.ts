import { apiClient } from './api';

export interface Building {
  building_id: string;
  project_id: string;
  building_name: string;
  building_code?: string;
  address?: string;
  floor_count?: number;
  total_units?: number;
  current_status: string;
  signature_percentage: number;
  traffic_light_status: string;
  assigned_agent_id?: string;
  assigned_agent_name?: string;
  assigned_agent_email?: string;
  units_signed?: number;
  units_partially_signed?: number;
  units_not_signed?: number;
  created_at: string;
}

export interface CreateBuildingDto {
  project_id: string;
  building_name: string;
  building_code?: string;
  address?: string;
  floor_count?: number;
  total_units?: number;
  structure_type?: string;
  assigned_agent_id?: string;
}

class BuildingsService {
  async getBuildings(projectId?: string): Promise<Building[]> {
    const params = projectId ? { project_id: projectId } : {};
    const response = await apiClient.get<Building[]>('/buildings', { params });
    return response.data;
  }

  async getBuilding(buildingId: string): Promise<Building> {
    const response = await apiClient.get<Building>(`/buildings/${buildingId}`);
    return response.data;
  }

  async createBuilding(data: CreateBuildingDto): Promise<Building> {
    const response = await apiClient.post<Building>('/buildings', data);
    return response.data;
  }

  async updateBuilding(buildingId: string, data: Partial<CreateBuildingDto>): Promise<Building> {
    const response = await apiClient.put<Building>(`/buildings/${buildingId}`, data);
    return response.data;
  }

  async deleteBuilding(buildingId: string): Promise<void> {
    await apiClient.delete(`/buildings/${buildingId}`);
  }
}

export const buildingsService = new BuildingsService();

