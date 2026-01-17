import { apiClient } from './api';

export interface Unit {
  unit_id: string;
  building_id: string;
  floor_number?: number;
  unit_number: string;
  area_sqm?: number;
  unit_status: string;
  total_owners: number;
  owners_signed: number;
  signature_percentage: number;
  created_at: string;
}

export interface CreateUnitDto {
  building_id: string;
  floor_number?: number;
  unit_number: string;
  unit_code?: string;
  area_sqm?: number;
  room_count?: number;
  estimated_value_ils?: number;
}

export interface UpdateUnitDto {
  floor_number?: number;
  unit_number?: string;
  unit_code?: string;
  area_sqm?: number;
  room_count?: number;
  estimated_value_ils?: number;
}

class UnitsService {
  async getUnits(buildingId?: string): Promise<Unit[]> {
    const params = buildingId ? { building_id: buildingId } : {};
    const response = await apiClient.get<Unit[]>('/units', { params });
    return response.data;
  }

  async getUnit(unitId: string): Promise<Unit> {
    const response = await apiClient.get<Unit>(`/units/${unitId}`);
    return response.data;
  }

  async createUnit(data: CreateUnitDto): Promise<Unit> {
    const response = await apiClient.post<Unit>('/units', data);
    return response.data;
  }

  async updateUnit(unitId: string, data: UpdateUnitDto): Promise<Unit> {
    const response = await apiClient.put<Unit>(`/units/${unitId}`, data);
    return response.data;
  }

  async deleteUnit(unitId: string): Promise<void> {
    await apiClient.delete(`/units/${unitId}`);
  }
}

export const unitsService = new UnitsService();

