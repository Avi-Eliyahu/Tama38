import { apiClient } from './api';

export interface Owner {
  owner_id: string;
  unit_id: string;
  full_name: string;
  phone_for_contact?: string;
  email?: string;
  ownership_share_percent: number;
  owner_status: string;
  preferred_contact_method?: string;
  preferred_language?: string;
  created_at: string;
}

export interface CreateOwnerDto {
  unit_id: string;
  full_name: string;
  id_number?: string;
  phone?: string;
  email?: string;
  ownership_share_percent: number;
  preferred_contact_method?: string;
  preferred_language?: string;
  link_to_existing?: boolean;
  existing_owner_id?: string;
}

export interface OwnerWithUnits extends Owner {
  units: Array<{
    unit_id: string;
    unit_number: string;
    building_name: string;
    ownership_share_percent: number;
  }>;
}

class OwnersService {
  async getOwners(unitId?: string): Promise<Owner[]> {
    const params = unitId ? { unit_id: unitId } : {};
    const response = await apiClient.get<Owner[]>('/owners', { params });
    return response.data;
  }

  async getOwner(ownerId: string): Promise<Owner> {
    const response = await apiClient.get<Owner>(`/owners/${ownerId}`);
    return response.data;
  }

  async getOwnerUnits(ownerId: string): Promise<Array<{
    unit_id: string;
    unit_number: string;
    floor_number?: number;
    building_id: string;
    ownership_share_percent: number;
  }>> {
    const response = await apiClient.get<Array<{
      unit_id: string;
      unit_number: string;
      floor_number?: number;
      building_id: string;
      ownership_share_percent: number;
    }>>(`/owners/${ownerId}/units`);
    return response.data;
  }

  async searchOwners(query: string): Promise<Owner[]> {
    const response = await apiClient.get<Owner[]>('/owners/search', {
      params: { q: query },
    });
    return response.data;
  }

  async createOwner(data: CreateOwnerDto): Promise<Owner> {
    const response = await apiClient.post<Owner>('/owners', data);
    return response.data;
  }

  async updateOwner(ownerId: string, data: Partial<CreateOwnerDto>): Promise<Owner> {
    const response = await apiClient.put<Owner>(`/owners/${ownerId}`, data);
    return response.data;
  }

  async deleteOwner(ownerId: string): Promise<void> {
    await apiClient.delete(`/owners/${ownerId}`);
  }

  async updateOwnerStatus(
    ownerId: string,
    ownerStatus: string,
    notes?: string,
    signedContractFile?: File
  ): Promise<{
    owner_id: string;
    owner_status: string;
    approval_task_id?: string;
    message: string;
  }> {
    // API endpoint always expects FormData (Form(...) parameters)
    const formData = new FormData();
    formData.append('owner_status', ownerStatus);
    if (notes) {
      formData.append('notes', notes);
    }
    if (signedContractFile) {
      formData.append('signed_contract_file', signedContractFile);
    }

    const response = await apiClient.put<{
      owner_id: string;
      owner_status: string;
      approval_task_id?: string;
      message: string;
    }>(`/owners/${ownerId}/status`, formData);
    return response.data;
  }
}

export const ownersService = new OwnersService();

