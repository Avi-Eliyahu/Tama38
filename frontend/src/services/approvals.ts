import { apiClient } from './api';

export interface Signature {
  signature_id: string;
  document_id: string;
  owner_id: string;
  signature_status: string;
  signing_token?: string;
  signed_at?: string;
  approved_at?: string;
  created_at: string;
  task_id?: string;
  signed_document_id?: string;
  signed_document_name?: string;
}

export interface InitiateSignatureDto {
  owner_id: string;
  document_id: string;
}

export interface ApprovalRequestDto {
  reason: string;
}

class ApprovalsService {
  async getWaitingSignatures(): Promise<Signature[]> {
    // Use the correct /approvals/queue endpoint instead of non-existent /approvals/waiting
    return this.getApprovalQueue();
  }

  async getApprovalQueue(): Promise<Signature[]> {
    const response = await apiClient.get<Signature[]>('/approvals/queue');
    return response.data;
  }

  async initiateSignature(data: InitiateSignatureDto): Promise<Signature> {
    const response = await apiClient.post<Signature>('/approvals/signatures/initiate', data);
    return response.data;
  }

  async approveSignature(signatureId: string, reason: string): Promise<Signature> {
    const response = await apiClient.post<Signature>(`/approvals/${signatureId}/approve`, {
      reason,
    });
    return response.data;
  }

  async rejectSignature(signatureId: string, reason: string): Promise<Signature> {
    const response = await apiClient.post<Signature>(`/approvals/${signatureId}/reject`, {
      reason,
    });
    return response.data;
  }

  async getApprovalsByOwner(ownerId: string): Promise<Signature[]> {
    // Get approvals (signatures pending manager approval) for a specific owner
    const response = await apiClient.get<Signature[]>('/approvals/queue', {
      params: { owner_id: ownerId },
    });
    return response.data;
  }

  async getApprovalQueueByOwner(ownerId: string): Promise<Signature[]> {
    // Get all signatures and filter by owner_id in frontend
    const allSignatures = await this.getApprovalQueue();
    return allSignatures.filter(sig => sig.owner_id === ownerId);
  }
}

export const approvalsService = new ApprovalsService();

