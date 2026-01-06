import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { tasksService, Task } from '../services/tasks';
import { authService } from '../services/auth';
import { documentsService } from '../services/documents';
import PDFViewer from '../components/PDFViewer';

export default function Tasks() {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'he';
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'my' | 'overdue'>('my');
  const [viewingDocument, setViewingDocument] = useState<{ documentId: string; filename: string } | null>(null);

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      let data: Task[];
      if (filter === 'my') {
        data = await tasksService.getMyTasks();
      } else if (filter === 'overdue') {
        data = await tasksService.getOverdueTasks();
      } else {
        data = await tasksService.getTasks();
      }
      setTasks(data);
    } catch (err: any) {
      console.error('[TASKS] Error loading tasks', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (taskId: string) => {
    try {
      await tasksService.completeTask(taskId);
      loadTasks();
    } catch (err: any) {
      console.error('[TASKS] Error completing task', err);
      setError(err.response?.data?.detail || t('common.error'));
    }
  };


  const currentUser = authService.getCurrentUserSync();
  const isManager = currentUser?.role === 'PROJECT_MANAGER' || currentUser?.role === 'SUPER_ADMIN';

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      HIGH: 'bg-red-100 text-red-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      LOW: 'bg-green-100 text-green-800',
    };
    return colors[priority] || colors.MEDIUM;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      IN_PROGRESS: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-gray-100 text-gray-800',
      NOT_STARTED: 'bg-gray-100 text-gray-800',
      BLOCKED: 'bg-red-100 text-red-800',
      OVERDUE: 'bg-red-100 text-red-800',
    };
    return colors[status] || colors.PENDING;
  };

  const getPriorityLabel = (priority: string) => {
    return t(`tasks.priorityLabels.${priority}`) || priority;
  };

  const getStatusLabel = (status: string) => {
    return t(`tasks.statusLabels.${status}`) || status;
  };

  const getTaskTypeLabel = (taskType: string) => {
    return t(`tasks.taskTypeLabels.${taskType}`) || taskType;
  };

  const isOverdue = (dueDate?: string) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date() && filter !== 'overdue';
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('common.loading')}</div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isRTL ? 'text-right' : 'text-left'}`}>
      {/* Header */}
      <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''} justify-between`}>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('tasks.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">{t('tasks.subtitle')}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''} gap-4`}>
          <button
            onClick={() => setFilter('my')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'my'
                ? 'bg-teal-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t('tasks.myTasks')}
          </button>
          <button
            onClick={() => setFilter('overdue')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'overdue'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t('tasks.overdue')}
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-teal-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t('tasks.allTasks')}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Tasks List */}
      {tasks.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {filter === 'overdue' ? t('tasks.noOverdueTasks') : t('tasks.noTasks')}
          </h3>
          <p className="text-gray-500">
            {filter === 'overdue'
              ? t('tasks.allUpToDate')
              : t('tasks.willAppear')}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div
              key={task.task_id}
              className={`bg-white rounded-lg shadow-sm border ${
                isOverdue(task.due_date) ? 'border-red-300' : 'border-gray-200'
              } p-6`}
            >
              <div className={`flex items-start ${isRTL ? 'flex-row-reverse' : ''} justify-between`}>
                <div className="flex-1">
                  <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''} gap-3 mb-2`}>
                    <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(task.priority)}`}
                    >
                      {getPriorityLabel(task.priority)}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(task.status)}`}
                    >
                      {getStatusLabel(task.status)}
                    </span>
                    {isOverdue(task.due_date) && (
                      <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800">
                        {t('tasks.overdue').toUpperCase()}
                      </span>
                    )}
                  </div>
                  {task.description && (
                    <p className="text-sm text-gray-600 mb-3">{task.description}</p>
                  )}
                  {task.task_type === 'MANAGER_REVIEW' && task.signature_id && (
                    <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className={`text-sm text-gray-700 space-y-1 ${isRTL ? 'text-right' : 'text-left'}`}>
                        <div>
                          {t('tasks.linkedApproval')}:{' '}
                          <Link to="/approvals" className="text-teal-600 hover:underline">
                            {t('tasks.viewApproval')}
                          </Link>
                        </div>
                        {task.signed_document_id && task.signed_document_name && (
                          <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''} gap-2`}>
                            <button
                              onClick={() => {
                                setViewingDocument({
                                  documentId: task.signed_document_id!,
                                  filename: task.signed_document_name!
                                });
                              }}
                              className={`px-3 py-1 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium flex items-center ${isRTL ? 'flex-row-reverse' : ''} gap-1`}
                            >
                              👁️ {t('documents.view')}
                            </button>
                            <button
                              onClick={async () => {
                                try {
                                  await documentsService.downloadDocument(
                                    task.signed_document_id!,
                                    task.signed_document_name!
                                  );
                                } catch (err) {
                                  console.error('Error downloading document:', err);
                                  alert(t('documents.downloadFailed'));
                                }
                              }}
                              className={`px-3 py-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium flex items-center ${isRTL ? 'flex-row-reverse' : ''} gap-1`}
                            >
                              ⬇️ {t('documents.download')}
                            </button>
                            <span className="text-sm text-gray-600">{task.signed_document_name}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''} gap-4 text-sm text-gray-500`}>
                    <span>{t('tasks.taskType')}: {getTaskTypeLabel(task.task_type)}</span>
                    {task.due_date && (
                      <span>
                        {t('tasks.dueDate')}: {new Date(task.due_date).toLocaleDateString(i18n.language === 'he' ? 'he-IL' : 'en-US')}
                      </span>
                    )}
                  </div>
                </div>
                <div className={`flex ${isRTL ? 'flex-row-reverse' : ''} gap-2`}>
                  {task.status !== 'COMPLETED' && task.task_type !== 'MANAGER_REVIEW' && (
                    <button
                      onClick={() => handleComplete(task.task_id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                    >
                      {t('tasks.markComplete')}
                    </button>
                  )}
                  {task.status === 'COMPLETED' && task.task_type === 'MANAGER_REVIEW' && (
                    <span className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium">
                      {t('tasks.completed')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* PDF Viewer Modal */}
      {viewingDocument && (
        <PDFViewer
          documentId={viewingDocument.documentId}
          filename={viewingDocument.filename}
          onClose={() => setViewingDocument(null)}
        />
      )}
    </div>
  );
}
