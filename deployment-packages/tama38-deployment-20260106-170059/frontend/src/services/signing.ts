import { apiClient } from './api';

export interface SigningTokenInfo {
  signature_id: string;
  document_id: string;
  owner_id: string;
  owner_name: string;
  document_name: string;
  document_type: string;
  signature_status: string;
  is_valid: boolean;
}

export interface SignDocumentRequest {
  signing_token: string;
  signature_data: string; // Base64 encoded signature image
}

class SigningService {
  async validateToken(token: string): Promise<SigningTokenInfo> {
    const response = await apiClient.get<SigningTokenInfo>(`/approvals/sign/validate/${token}`);
    return response.data;
  }

  async signDocument(token: string, signatureData: string): Promise<void> {
    await apiClient.post(`/approvals/sign/${token}`, {
      signing_token: token,
      signature_data: signatureData,
    });
  }
}

export const signingService = new SigningService();

