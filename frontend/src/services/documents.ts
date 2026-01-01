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

  async getDocumentsByUnit(unitId: string, ownerIds: string[]): Promise<Document[]> {
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
}

export const documentsService = new DocumentsService();

