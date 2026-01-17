import { apiClient } from './api';

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: 'SUPER_ADMIN' | 'PROJECT_MANAGER' | 'AGENT' | 'TENANT';
  is_active: boolean;
  phone?: string;
}

export interface CreateUserData {
  email: string;
  password: string;
  full_name: string;
  role: 'PROJECT_MANAGER' | 'AGENT';
  phone?: string;
}

class UsersService {
  async getUsers(role?: string): Promise<User[]> {
    const params = role ? { role } : {};
    const response = await apiClient.get<User[]>('/users', { params });
    return response.data;
  }

  async getAgents(): Promise<User[]> {
    return this.getUsers('AGENT');
  }

  async getUser(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  }

  async createUser(userData: CreateUserData): Promise<User> {
    const response = await apiClient.post<User>('/users', userData);
    return response.data;
  }

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/users/${userId}`);
  }
}

export const usersService = new UsersService();

