import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { approvalsService } from '../services/approvals';
import { Document } from '../services/documents';

interface InitiateSignatureFormProps {
  ownerId: string;
  documents: Document[];
  onSuccess: () => void;
}

export default function InitiateSignatureForm({ ownerId, documents, onSuccess }: InitiateSignatureFormProps) {
  const { t } = useTranslation();
  const [selectedDocumentId, setSelectedDocumentId] = useState<string>('');
  const [signedDocumentFile, setSignedDocumentFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Filter documents that can be signed (CONTRACT type)
  const signableDocuments = documents.filter(doc => 
    doc.document_type === 'CONTRACT' || doc.document_type === 'SIGNATURE'
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
      if (!allowedTypes.includes(file.type)) {
        setError('File type not allowed. Please upload PDF or image file.');
        return;
      }
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit.');
        return;
      }
      setSignedDocumentFile(file);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDocumentId) {
      setError('Please select a document to sign');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      await approvalsService.initiateSignature({
        owner_id: ownerId,
        document_id: selectedDocumentId,
      });

      setSuccess('Signature request initiated successfully!');
      setSelectedDocumentId('');
      setSignedDocumentFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('signed-document-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      // Call success callback
      setTimeout(() => {
        onSuccess();
        setSuccess(null);
      }, 2000);
    } catch (err: any) {
      console.error('[INITIATE_SIGNATURE] Error initiating signature', err);
      setError(err.response?.data?.detail || 'Failed to initiate signature');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('approvals.selectDocument')} *
        </label>
        <select
          value={selectedDocumentId}
          onChange={(e) => setSelectedDocumentId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          disabled={loading}
          required
        >
          <option value="">{t('approvals.selectDocumentPlaceholder')}</option>
          {signableDocuments.map((doc) => (
            <option key={doc.document_id} value={doc.document_id}>
              {doc.file_name} ({doc.document_type})
            </option>
          ))}
        </select>
        {signableDocuments.length === 0 && (
          <p className="text-sm text-gray-500 mt-1">
            {t('approvals.noSignableDocuments')}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('approvals.uploadSignedDocument')} ({t('common.optional')})
        </label>
        <input
          id="signed-document-input"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          disabled={loading}
        />
        <p className="text-xs text-gray-500 mt-1">
          {t('approvals.uploadSignedDocumentHint')}
        </p>
        {signedDocumentFile && (
          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
            <p className="text-sm text-green-800">
              ✓ {signedDocumentFile.name} ({(signedDocumentFile.size / 1024).toFixed(2)} KB)
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
          {success}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !selectedDocumentId || signableDocuments.length === 0}
        className="w-full bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? t('common.submitting') : t('approvals.initiateSignature')}
      </button>
    </form>
  );
}

