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
}

export const unitsService = new UnitsService();

