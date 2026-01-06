import { apiClient } from './api';

export interface WizardDraft {
  draft_id: string;
  current_step: number;
  step_data: {
    step1?: any;
    step2?: any;
    step3?: any;
    step4?: any;
  };
  expires_at: string;
}

export interface WizardStartResponse {
  draft_id: string;
  expires_at: string;
}

export interface WizardStepResponse {
  message: string;
  current_step: number;
}

export interface WizardCompleteResponse {
  message: string;
  project_id: string;
  buildings_created: number;
  units_created: number;
  owners_created: number;
}

class WizardService {
  async startWizard(): Promise<WizardStartResponse> {
    const response = await apiClient.post<WizardStartResponse>('/projects/wizard/start');
    return response.data;
  }

  async saveStep1(draftId: string, data: any): Promise<WizardStepResponse> {
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/1', {
      draft_id: draftId,
      data,
    });
    return response.data;
  }

  async saveStep2(draftId: string, data: any): Promise<WizardStepResponse> {
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/2', {
      draft_id: draftId,
      data,
    });
    return response.data;
  }

  async saveStep3(draftId: string, data: any): Promise<WizardStepResponse> {
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/3', {
      draft_id: draftId,
      data,
    });
    return response.data;
  }

  async saveStep4(draftId: string, data: any): Promise<WizardStepResponse> {
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/4', {
      draft_id: draftId,
      data,
    });
    return response.data;
  }

  async getDraft(draftId: string): Promise<WizardDraft> {
    const response = await apiClient.get<WizardDraft>(`/projects/wizard/draft/${draftId}`);
    return response.data;
  }

  async completeWizard(draftId: string): Promise<WizardCompleteResponse> {
    const response = await apiClient.post<WizardCompleteResponse>('/projects/wizard/complete', {
      draft_id: draftId,
    });
    return response.data;
  }
}

export const wizardService = new WizardService();

