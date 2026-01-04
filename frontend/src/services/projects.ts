import { apiClient } from './api';

export interface Project {
  project_id: string;
  project_name: string;
  project_code: string;
  project_type: 'TAMA38_1' | 'TAMA38_2' | 'PINUI_BINUI';
  location_city?: string;
  location_address?: string;
  project_stage: 'PLANNING' | 'ACTIVE' | 'APPROVAL' | 'COMPLETED' | 'ARCHIVED';
  required_majority_percent: number;
  majority_calc_type: 'HEADCOUNT' | 'AREA' | 'WEIGHTED' | 'CUSTOM';
  created_at: string;
  updated_at: string;
}

export interface CreateProjectDto {
  project_name: string;
  project_code: string;
  project_type: 'TAMA38_1' | 'TAMA38_2' | 'PINUI_BINUI';
  location_city?: string;
  location_address?: string;
  required_majority_percent: number;
  majority_calc_type: 'HEADCOUNT' | 'AREA' | 'WEIGHTED' | 'CUSTOM';
}

class ProjectsService {
  async getProjects(): Promise<Project[]> {
    const response = await apiClient.get<Project[]>('/projects');
    return response.data;
  }

  async getProject(projectId: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/projects/${projectId}`);
    return response.data;
  }

  async createProject(data: CreateProjectDto): Promise<Project> {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  }

  async updateProject(projectId: string, data: Partial<CreateProjectDto>): Promise<Project> {
    const response = await apiClient.put<Project>(`/projects/${projectId}`, data);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<void> {
    await apiClient.delete(`/projects/${projectId}`);
  }
}

export const projectsService = new ProjectsService();

