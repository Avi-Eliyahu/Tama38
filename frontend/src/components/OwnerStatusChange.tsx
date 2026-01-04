import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Owner } from '../services/owners';
import { ownersService } from '../services/owners';
import { tasksService, Task } from '../services/tasks';
import { authService } from '../services/auth';

interface OwnerStatusChangeProps {
  owner: Owner;
  onStatusChange: (newStatus: string) => void;
}

const WORKFLOW_STATUSES = ['NOT_CONTACTED', 'NEGOTIATING', 'AGREED_TO_SIGN', 'WAIT_FOR_SIGN'];
const RESTRICTED_STATUSES = ['SIGNED', 'REFUSED'];

export default function OwnerStatusChange({ owner, onStatusChange }: OwnerStatusChangeProps) {
  const { t } = useTranslation();
  const [selectedStatus, setSelectedStatus] = useState(owner.owner_status);
  const [notes, setNotes] = useState('');
  const [signedContractFile, setSignedContractFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [pendingTask, setPendingTask] = useState<Task | null>(null);
  const currentUser = authService.getCurrentUserSync();
  const isAgent = currentUser?.role === 'AGENT';

  useEffect(() => {
    loadPendingApprovalTask();
  }, [owner.owner_id]);

  const loadPendingApprovalTask = async () => {
    try {
      const tasks = await tasksService.getTasksByOwner(owner.owner_id);
      const approvalTask = tasks.find(
        t => t.task_type === 'MANAGER_REVIEW' && 
        t.status !== 'COMPLETED' && 
        t.status !== 'CANCELLED'
      );
      setPendingTask(approvalTask || null);
    } catch (err) {
      console.error('[OWNER_STATUS] Error loading pending task', err);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type (PDF only)
      if (file.type !== 'application/pdf') {
        setError('Only PDF files are allowed for signed contracts');
        setSignedContractFile(null);
        // Reset file input
        e.target.value = '';
        return;
      }
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit');
        setSignedContractFile(null);
        // Reset file input
        e.target.value = '';
        return;
      }
      setSignedContractFile(file);
      setError(null);
    }
  };

  const handleStatusChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStatus || selectedStatus === owner.owner_status) {
      return;
    }

    // Validate agent can only set workflow statuses
    if (isAgent && !WORKFLOW_STATUSES.includes(selectedStatus)) {
      setError(t('owners.invalidStatusForAgent'));
      return;
    }

    // Require file upload when status is WAIT_FOR_SIGN
    if (selectedStatus === 'WAIT_FOR_SIGN' && !signedContractFile) {
      setError('Signed contract PDF file is required when setting status to WAIT_FOR_SIGN');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const result = await ownersService.updateOwnerStatus(
        owner.owner_id,
        selectedStatus,
        notes || undefined,
        selectedStatus === 'WAIT_FOR_SIGN' ? signedContractFile : undefined
      );
      
      setSuccess(result.message);
      onStatusChange(selectedStatus);
      
      // Reload pending task if status is WAIT_FOR_SIGN
      if (selectedStatus === 'WAIT_FOR_SIGN') {
        await loadPendingApprovalTask();
      }

      // Clear form after delay
      setTimeout(() => {
        setSuccess(null);
        if (notes) setNotes('');
        setSignedContractFile(null);
        // Reset file input
        const fileInput = document.getElementById('signed-contract-input') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      }, 3000);
    } catch (err: any) {
      console.error('[OWNER_STATUS] Error updating status', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SIGNED': return 'bg-green-100 text-green-800';
      case 'WAIT_FOR_SIGN': return 'bg-purple-100 text-purple-800';
      case 'AGREED_TO_SIGN': return 'bg-blue-100 text-blue-800';
      case 'NEGOTIATING': return 'bg-yellow-100 text-yellow-800';
      case 'NOT_CONTACTED': return 'bg-gray-100 text-gray-800';
      case 'REFUSED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Only show for agents or managers/admins
  if (!isAgent && currentUser?.role !== 'PROJECT_MANAGER' && currentUser?.role !== 'SUPER_ADMIN') {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {t('owners.changeStatus')}
      </h3>

      {/* Current Status */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('owners.currentStatus')}
        </label>
        <span className={`px-3 py-1 text-sm font-medium rounded ${getStatusColor(owner.owner_status)}`}>
          {t(`owners.statusLabels.${owner.owner_status}`)}
        </span>
      </div>

      {/* Pending Approval Task */}
      {pendingTask && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            <strong>{t('owners.pendingApproval')}:</strong> {pendingTask.title}
          </p>
          <p className="text-xs text-yellow-600 mt-1">
            {t('owners.waitingForManagerApproval')}
          </p>
        </div>
      )}

      {/* Status Change Form */}
      <form onSubmit={handleStatusChange} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('owners.newStatus')}
          </label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          >
            {isAgent ? (
              // Agents can only select workflow statuses
              WORKFLOW_STATUSES.map(status => (
                <option key={status} value={status}>
                  {t(`owners.statusLabels.${status}`)}
                </option>
              ))
            ) : (
              // Managers/admins can select all statuses except restricted ones
              ['NOT_CONTACTED', 'NEGOTIATING', 'AGREED_TO_SIGN', 'WAIT_FOR_SIGN', 'SIGNED', 'REFUSED'].map(status => (
                <option key={status} value={status}>
                  {t(`owners.statusLabels.${status}`)}
                </option>
              ))
            )}
          </select>
        </div>

        {selectedStatus === 'WAIT_FOR_SIGN' && (
          <>
            <div className="p-3 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-800">
                {t('owners.approvalTaskWillBeCreated')}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('owners.uploadSignedContract')} *
              </label>
              <input
                id="signed-contract-input"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
                required={selectedStatus === 'WAIT_FOR_SIGN'}
              />
              <p className="text-xs text-gray-500 mt-1">
                {t('owners.signedContractHint')}
              </p>
              {signedContractFile && (
                <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-800">
                    ✓ {signedContractFile.name} ({(signedContractFile.size / 1024).toFixed(2)} KB)
                  </p>
                </div>
              )}
            </div>
          </>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('owners.notes')} ({t('common.optional')})
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder={t('owners.statusChangeNotes')}
            disabled={loading}
          />
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
          disabled={loading || selectedStatus === owner.owner_status || (selectedStatus === 'WAIT_FOR_SIGN' && !signedContractFile)}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? t('common.updating') : t('owners.updateStatus')}
        </button>
      </form>
    </div>
  );
}

