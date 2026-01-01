import { apiClient } from './api';

export interface Task {
  task_id: string;
  building_id?: string;
  owner_id?: string;
  task_type: string;
  title: string;
  description?: string;
  assigned_to_agent_id: string;
  due_date?: string;
  status: string;
  priority: string;
  created_at: string;
}

export interface CreateTaskDto {
  building_id?: string;
  owner_id?: string;
  task_type: string;
  title: string;
  description?: string;
  assigned_to_agent_id: string;
  due_date?: string;
  priority?: string;
}

class TasksService {
  async getTasks(assignedTo?: string, statusFilter?: string): Promise<Task[]> {
    const params: any = {};
    if (assignedTo) params.assigned_to = assignedTo;
    if (statusFilter) params.status_filter = statusFilter;
    const response = await apiClient.get<Task[]>('/tasks', { params });
    return response.data;
  }

  async getTasksByOwner(ownerId: string): Promise<Task[]> {
    const params = { owner_id: ownerId };
    const response = await apiClient.get<Task[]>('/tasks', { params });
    return response.data;
  }

  async getTasksByUnit(unitId: string, ownerIds: string[]): Promise<Task[]> {
    // Get tasks for all owners of a unit
    const allTasks: Task[] = [];
    for (const ownerId of ownerIds) {
      const tasks = await this.getTasksByOwner(ownerId);
      allTasks.push(...tasks);
    }
    // Remove duplicates and sort by created_at descending
    const uniqueTasks = Array.from(
      new Map(allTasks.map(task => [task.task_id, task])).values()
    );
    return uniqueTasks.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }

  async getMyTasks(): Promise<Task[]> {
    const response = await apiClient.get<Task[]>('/tasks/my-tasks');
    return response.data;
  }

  async getOverdueTasks(): Promise<Task[]> {
    const response = await apiClient.get<Task[]>('/tasks/overdue');
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await apiClient.get<Task>(`/tasks/${taskId}`);
    return response.data;
  }

  async createTask(data: CreateTaskDto): Promise<Task> {
    const response = await apiClient.post<Task>('/tasks', data);
    return response.data;
  }

  async updateTask(taskId: string, data: Partial<CreateTaskDto>): Promise<Task> {
    const response = await apiClient.put<Task>(`/tasks/${taskId}`, data);
    return response.data;
  }

  async completeTask(taskId: string): Promise<Task> {
    const response = await apiClient.put<Task>(`/tasks/${taskId}/complete`);
    return response.data;
  }

  async approveSignature(taskId: string, notes?: string): Promise<{
    task_id: string;
    owner_id: string;
    owner_status: string;
    message: string;
  }> {
    const response = await apiClient.post<{
      task_id: string;
      owner_id: string;
      owner_status: string;
      message: string;
    }>(`/tasks/${taskId}/approve-signature`, {
      notes,
    });
    return response.data;
  }

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/tasks/${taskId}`);
  }
}

export const tasksService = new TasksService();

