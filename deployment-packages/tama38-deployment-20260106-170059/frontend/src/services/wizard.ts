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
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:34',message:'startWizard service call',data:{url:'/projects/wizard/start'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    const response = await apiClient.post<WizardStartResponse>('/projects/wizard/start');
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:37',message:'startWizard service success',data:{draftId:response.data.draft_id,status:response.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    return response.data;
  }

  async saveStep1(draftId: string, data: any): Promise<WizardStepResponse> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:42',message:'saveStep1 service call',data:{url:'/projects/wizard/step/1',draftId,dataKeys:Object.keys(data)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/1', {
      draft_id: draftId,
      data,
    });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:48',message:'saveStep1 service success',data:{status:response.status,currentStep:response.data.current_step},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return response.data;
  }

  async saveStep2(draftId: string, data: any): Promise<WizardStepResponse> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:54',message:'saveStep2 service call',data:{url:'/projects/wizard/step/2',draftId,buildingsCount:data.buildings?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/2', {
      draft_id: draftId,
      data,
    });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:60',message:'saveStep2 service success',data:{status:response.status,currentStep:response.data.current_step},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return response.data;
  }

  async saveStep3(draftId: string, data: any): Promise<WizardStepResponse> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:66',message:'saveStep3 service call',data:{url:'/projects/wizard/step/3',draftId,unitsCount:data.units?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/3', {
      draft_id: draftId,
      data,
    });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:72',message:'saveStep3 service success',data:{status:response.status,currentStep:response.data.current_step},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return response.data;
  }

  async saveStep4(draftId: string, data: any): Promise<WizardStepResponse> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:78',message:'saveStep4 service call',data:{url:'/projects/wizard/step/4',draftId,ownersCount:data.owners?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const response = await apiClient.post<WizardStepResponse>('/projects/wizard/step/4', {
      draft_id: draftId,
      data,
    });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:84',message:'saveStep4 service success',data:{status:response.status,currentStep:response.data.current_step},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return response.data;
  }

  async getDraft(draftId: string): Promise<WizardDraft> {
    const response = await apiClient.get<WizardDraft>(`/projects/wizard/draft/${draftId}`);
    return response.data;
  }

  async completeWizard(draftId: string): Promise<WizardCompleteResponse> {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:76',message:'completeWizard service call',data:{url:'/projects/wizard/complete',draftId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const response = await apiClient.post<WizardCompleteResponse>('/projects/wizard/complete', {
      draft_id: draftId,
    });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'wizard.ts:80',message:'completeWizard service success',data:{status:response.status,projectId:response.data.project_id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return response.data;
  }
}

export const wizardService = new WizardService();

