import { apiClient } from './api';

export interface ReportType {
  id: string;
  name: string;
  description: string;
  formats: string[];
}

export interface ReportTypesResponse {
  report_types: ReportType[];
}

export interface ReportRequest {
  report_type: 'building_progress' | 'agent_performance' | 'interaction_history' | 'compliance_audit';
  format: 'pdf' | 'excel';
  project_id?: string;
  building_id?: string;
  agent_id?: string;
  start_date?: string;
  end_date?: string;
}

class ReportsService {
  async getReportTypes(): Promise<ReportTypesResponse> {
    const response = await apiClient.get<ReportTypesResponse>('/reports/types');
    return response.data;
  }

  async generateReport(request: ReportRequest): Promise<Blob> {
    const response = await apiClient.post<Blob>('/reports/generate', request, {
      responseType: 'blob',
    });
    return response.data;
  }

  async downloadReport(request: ReportRequest): Promise<void> {
    const blob = await this.generateReport(request);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Determine filename based on report type and format
    const extension = request.format === 'pdf' ? 'pdf' : 'xlsx';
    const filename = `${request.report_type}_${new Date().toISOString().split('T')[0]}.${extension}`;
    link.download = filename;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

export const reportsService = new ReportsService();

