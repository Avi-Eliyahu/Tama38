import { useEffect, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { documentsService } from '../services/documents';

interface PDFViewerProps {
  documentId: string;
  filename: string;
  onClose: () => void;
}

export default function PDFViewer({ documentId, filename, onClose }: PDFViewerProps) {
  const { t } = useTranslation();
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const blobUrlRef = useRef<string | null>(null);

  useEffect(() => {
    loadPDF();
    
    // Cleanup blob URL on unmount or when documentId changes
    return () => {
      if (blobUrlRef.current) {
        window.URL.revokeObjectURL(blobUrlRef.current);
        blobUrlRef.current = null;
      }
    };
  }, [documentId]);

  const loadPDF = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Cleanup previous blob URL if exists
      if (blobUrlRef.current) {
        window.URL.revokeObjectURL(blobUrlRef.current);
        blobUrlRef.current = null;
      }
      
      // Get PDF blob URL for viewing
      const url = await documentsService.getDocumentViewUrl(documentId);
      blobUrlRef.current = url;
      setPdfUrl(url);
    } catch (err: any) {
      console.error('[PDF_VIEWER] Error loading PDF', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      await documentsService.downloadDocument(documentId, filename);
    } catch (err: any) {
      console.error('[PDF_VIEWER] Error downloading document', err);
      alert(t('documents.downloadFailed') || 'Failed to download document');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75">
      <div className="bg-white rounded-lg shadow-xl w-full h-full max-w-7xl max-h-[95vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 truncate flex-1 mr-4">
            {filename}
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
            >
              {t('documents.download')}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium"
            >
              {t('common.close')}
            </button>
          </div>
        </div>

        {/* PDF Content */}
        <div className="flex-1 overflow-hidden relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-gray-500">{t('common.loading')}</div>
            </div>
          )}
          
          {error && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-red-600 text-center p-4">
                <p className="font-semibold mb-2">{t('documents.viewFailed')}</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}
          
          {pdfUrl && !loading && !error && (
            <iframe
              src={pdfUrl}
              className="w-full h-full border-0"
              title={filename}
            />
          )}
        </div>
      </div>
    </div>
  );
}

