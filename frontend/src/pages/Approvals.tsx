import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { approvalsService, Signature } from '../services/approvals';
import { ownersService, Owner } from '../services/owners';
import { documentsService } from '../services/documents';

export default function Approvals() {
  const { t } = useTranslation();
  const [signatures, setSignatures] = useState<Signature[]>([]);
  const [owners, setOwners] = useState<Record<string, Owner>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [approvalReason, setApprovalReason] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await approvalsService.getApprovalQueue();
      setSignatures(data);

      // Load owner details
      const ownerIds = [...new Set(data.map((s) => s.owner_id))];
      const ownerPromises = ownerIds.map((id) => ownersService.getOwner(id));
      const ownerData = await Promise.all(ownerPromises);
      const ownerMap: Record<string, Owner> = {};
      ownerData.forEach((owner) => {
        ownerMap[owner.owner_id] = owner;
      });
      setOwners(ownerMap);
    } catch (err: any) {
      console.error('[APPROVALS] Error loading approvals', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (signatureId: string) => {
    // Reason is optional for approval
    try {
      setLoading(true);
      setError(null);
      await approvalsService.approveSignature(signatureId, approvalReason || '');
      setApprovingId(null);
      setApprovalReason('');
      loadApprovals();
    } catch (err: any) {
      console.error('[APPROVALS] Error approving signature', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (signatureId: string) => {
    if (!rejectionReason.trim()) {
      setError(t('approvals.reasonRequired'));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await approvalsService.rejectSignature(signatureId, rejectionReason);
      setRejectingId(null);
      setRejectionReason('');
      loadApprovals();
    } catch (err: any) {
      console.error('[APPROVALS] Error rejecting signature', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      WAIT_FOR_SIGN: 'bg-yellow-100 text-yellow-800',
      SIGNED_PENDING_APPROVAL: 'bg-blue-100 text-blue-800',
      FINALIZED: 'bg-green-100 text-green-800',
      REJECTED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading && signatures.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('approvals.loadingApprovals')}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{t('approvals.title')}</h1>
        <p className="mt-1 text-sm text-gray-500">{t('approvals.subtitle')}</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Approvals Queue */}
      {signatures.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('approvals.noPendingApprovals')}</h3>
          <p className="text-gray-500">{t('approvals.allProcessed')}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {signatures.map((signature) => {
            const owner = owners[signature.owner_id];
            const isPendingApproval = signature.signature_status === 'SIGNED_PENDING_APPROVAL';
            const isApproving = approvingId === signature.signature_id;
            const isRejecting = rejectingId === signature.signature_id;

            return (
              <div
                key={signature.signature_id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {owner?.full_name || t('approvals.unknownOwner')}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                          signature.signature_status
                        )}`}
                      >
                        {signature.signature_status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>{t('approvals.documentId')}: {signature.document_id}</div>
                      {signature.signed_at && (
                        <div>{t('approvals.signedDate')}: {new Date(signature.signed_at).toLocaleString()}</div>
                      )}
                      {signature.task_id && (
                        <div>
                          {t('approvals.linkedTask')}:{' '}
                          <Link to={`/tasks`} className="text-teal-600 hover:underline">
                            {signature.task_id.substring(0, 8)}...
                          </Link>
                        </div>
                      )}
                      {signature.signed_document_id && signature.signed_document_name && (
                        <div className="mt-2">
                          <button
                            onClick={async () => {
                              try {
                                await documentsService.downloadDocument(signature.signed_document_id!);
                              } catch (err) {
                                console.error('Error downloading document:', err);
                                alert('Failed to download document');
                              }
                            }}
                            className="text-teal-600 hover:text-teal-700 hover:underline flex items-center gap-1"
                          >
                            📄 {t('approvals.viewSignedDocument')}: {signature.signed_document_name}
                          </button>
                        </div>
                      )}
                      {owner?.phone_for_contact && (
                        <div>{t('owners.phone')}: {owner.phone_for_contact}</div>
                      )}
                      {owner?.email && <div>{t('owners.email')}: {owner.email}</div>}
                    </div>
                  </div>
                </div>

                {isPendingApproval && (
                  <div className="border-t border-gray-200 pt-4 mt-4">
                    {isApproving ? (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {t('approvals.approvalReason')} ({t('common.optional')})
                          </label>
                          <textarea
                            value={approvalReason}
                            onChange={(e) => setApprovalReason(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                            rows={3}
                            placeholder={t('approvals.reasonPlaceholder')}
                          />
                        </div>
                        <div className="flex justify-end gap-3">
                          <button
                            onClick={() => {
                              setApprovingId(null);
                              setApprovalReason('');
                            }}
                            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                          >
                            {t('common.cancel')}
                          </button>
                          <button
                            onClick={() => handleApprove(signature.signature_id)}
                            disabled={loading}
                            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                          >
                            {loading ? t('approvals.approving') : t('approvals.approve')}
                          </button>
                        </div>
                      </div>
                    ) : isRejecting ? (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {t('approvals.rejectionReason')} *
                          </label>
                          <textarea
                            value={rejectionReason}
                            onChange={(e) => setRejectionReason(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                            rows={3}
                            placeholder={t('approvals.rejectionReasonPlaceholder')}
                            required
                          />
                        </div>
                        <div className="flex justify-end gap-3">
                          <button
                            onClick={() => {
                              setRejectingId(null);
                              setRejectionReason('');
                            }}
                            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                          >
                            {t('common.cancel')}
                          </button>
                          <button
                            onClick={() => handleReject(signature.signature_id)}
                            disabled={loading || !rejectionReason.trim()}
                            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                          >
                            {loading ? t('approvals.rejecting') : t('approvals.reject')}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-end gap-3">
                        <button
                          onClick={() => {
                            setRejectingId(signature.signature_id);
                            setApprovingId(null);
                            setRejectionReason('');
                          }}
                          className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50"
                        >
                          {t('approvals.reject')}
                        </button>
                        <button
                          onClick={() => {
                            setApprovingId(signature.signature_id);
                            setRejectingId(null);
                            setApprovalReason('');
                          }}
                          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          {t('approvals.approve')}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
