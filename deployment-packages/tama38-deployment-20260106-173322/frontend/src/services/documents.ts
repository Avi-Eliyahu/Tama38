import { apiClient } from './api';

export interface Document {
  document_id: string;
  owner_id?: string;
  building_id?: string;
  project_id?: string;
  document_type: string;
  file_name: string;
  file_size_bytes: number;
  file_path: string;
  uploaded_by_user_id: string;
  created_at: string;
}

class DocumentsService {
  async getDocuments(params?: {
    owner_id?: string;
    building_id?: string;
    project_id?: string;
  }): Promise<Document[]> {
    const response = await apiClient.get<Document[]>('/documents', { params });
    return response.data;
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await apiClient.get<Document>(`/documents/${documentId}`);
    return response.data;
  }

  async getDocumentsByOwner(ownerId: string): Promise<Document[]> {
    return this.getDocuments({ owner_id: ownerId });
  }

  async getDocumentsByUnit(_unitId: string, ownerIds: string[]): Promise<Document[]> {
    // Get documents for all owners of a unit
    const allDocuments: Document[] = [];
    for (const ownerId of ownerIds) {
      const documents = await this.getDocumentsByOwner(ownerId);
      allDocuments.push(...documents);
    }
    // Remove duplicates and sort by created_at descending
    const uniqueDocuments = Array.from(
      new Map(allDocuments.map(doc => [doc.document_id, doc])).values()
    );
    return uniqueDocuments.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }

  async getDocumentDownloadUrl(documentId: string): Promise<string> {
    const response = await apiClient.get<{ download_url: string }>(`/documents/${documentId}/download`);
    return response.data.download_url;
  }

  async getDocumentViewUrl(documentId: string): Promise<string> {
    // Fetch the file using axios with authentication and blob response type
    // Use the files endpoint directly to get the file with proper auth headers
    const response = await apiClient.get(`/files/${documentId}`, {
      responseType: 'blob',
    });
    
    // When responseType is 'blob', axios already returns a Blob
    const blob = response.data as Blob;
    
    // Create a blob URL for viewing (caller is responsible for revoking it)
    return window.URL.createObjectURL(blob);
  }

  async downloadDocument(documentId: string, filename?: string): Promise<void> {
    // Get the document to get the filename if not provided
    const doc = filename ? { file_name: filename } : await this.getDocument(documentId);
    
    // Get blob URL for the file
    const url = await this.getDocumentViewUrl(documentId);
    
    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = doc.file_name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Revoke the blob URL to free up memory (after a small delay to ensure download starts)
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 100);
  }
}

export const documentsService = new DocumentsService();

