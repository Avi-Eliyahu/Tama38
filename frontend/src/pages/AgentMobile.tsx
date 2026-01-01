import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { agentsService, Lead, AgentDashboard } from '../services/agents';
import { interactionsService, CreateInteractionDto } from '../services/interactions';
import { tasksService, Task } from '../services/tasks';
import { authService } from '../services/auth';

type View = 'dashboard' | 'leads' | 'tasks' | 'quick-log' | 'scanner';

export default function AgentMobile() {
  const [view, setView] = useState<View>('dashboard');
  const [dashboard, setDashboard] = useState<AgentDashboard | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [showQuickLog, setShowQuickLog] = useState(false);
  const [quickLogData, setQuickLogData] = useState<Partial<CreateInteractionDto>>({
    interaction_type: 'PHONE_CALL',
    interaction_date: new Date().toISOString().split('T')[0],
    call_summary: '',
    sentiment: 'NEUTRAL',
  });

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    if (view === 'leads') {
      loadLeads();
    } else if (view === 'tasks') {
      loadTasks();
    }
  }, [view]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await agentsService.getAgentDashboard();
      setDashboard(data);
    } catch (err: any) {
      console.error('[AGENT] Error loading dashboard', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadLeads = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await agentsService.getMyLeads();
      setLeads(data);
    } catch (err: any) {
      console.error('[AGENT] Error loading leads', err);
      setError(err.response?.data?.detail || 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await tasksService.getMyTasks();
      setTasks(data);
    } catch (err: any) {
      console.error('[AGENT] Error loading tasks', err);
      setError(err.response?.data?.detail || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLead || !quickLogData.call_summary?.trim()) {
      setError('Please select a lead and provide a call summary');
      return;
    }

    try {
      setError(null);
      await interactionsService.createInteraction({
        ...quickLogData,
        owner_id: selectedLead.owner_id,
      } as CreateInteractionDto);
      
      setShowQuickLog(false);
      setSelectedLead(null);
      setQuickLogData({
        interaction_type: 'PHONE_CALL',
        interaction_date: new Date().toISOString().split('T')[0],
        call_summary: '',
        sentiment: 'NEUTRAL',
      });
      
      // Refresh data
      loadDashboard();
      if (view === 'leads') {
        loadLeads();
      }
    } catch (err: any) {
      console.error('[AGENT] Error logging interaction', err);
      setError(err.response?.data?.detail || 'Failed to log interaction');
    }
  };

  const handleCall = (phone?: string) => {
    if (phone) {
      window.location.href = `tel:${phone}`;
    }
  };

  const handleWhatsApp = (phone?: string) => {
    if (phone) {
      // Remove + and spaces for WhatsApp
      const cleanPhone = phone.replace(/[\s+]/g, '');
      window.open(`https://wa.me/${cleanPhone}`, '_blank');
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      HIGH: 'bg-red-100 text-red-800 border-red-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      LOW: 'bg-green-100 text-green-800 border-green-300',
    };
    return colors[priority] || colors.MEDIUM;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      NOT_CONTACTED: 'bg-gray-100 text-gray-800',
      NEGOTIATING: 'bg-blue-100 text-blue-800',
      WAIT_FOR_SIGN: 'bg-purple-100 text-purple-800',
      SIGNED: 'bg-green-100 text-green-800',
      REFUSED: 'bg-red-100 text-red-800',
    };
    return colors[status] || colors.NOT_CONTACTED;
  };

  if (loading && !dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const user = authService.getCurrentUser();

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Mobile Header */}
      <div className="bg-teal-600 text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Agent Mobile</h1>
          <Link
            to="/dashboard"
            className="text-sm bg-teal-700 px-3 py-1 rounded"
          >
            Desktop
          </Link>
        </div>
        {user && (
          <p className="text-sm text-teal-100 mt-1">{user.full_name}</p>
        )}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around items-center h-16 z-10">
        <button
          onClick={() => setView('dashboard')}
          className={`flex flex-col items-center justify-center flex-1 h-full ${
            view === 'dashboard' ? 'text-teal-600' : 'text-gray-500'
          }`}
        >
          <span className="text-2xl mb-1">📊</span>
          <span className="text-xs">Dashboard</span>
        </button>
        <button
          onClick={() => setView('leads')}
          className={`flex flex-col items-center justify-center flex-1 h-full ${
            view === 'leads' ? 'text-teal-600' : 'text-gray-500'
          }`}
        >
          <span className="text-2xl mb-1">👥</span>
          <span className="text-xs">Leads</span>
        </button>
        <button
          onClick={() => setView('tasks')}
          className={`flex flex-col items-center justify-center flex-1 h-full ${
            view === 'tasks' ? 'text-teal-600' : 'text-gray-500'
          }`}
        >
          <span className="text-2xl mb-1">✅</span>
          <span className="text-xs">Tasks</span>
        </button>
        <button
          onClick={() => setView('scanner')}
          className={`flex flex-col items-center justify-center flex-1 h-full ${
            view === 'scanner' ? 'text-teal-600' : 'text-gray-500'
          }`}
        >
          <span className="text-2xl mb-1">📷</span>
          <span className="text-xs">Scanner</span>
        </button>
      </div>

      {/* Content Area */}
      <div className="p-4 pb-24">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {view === 'dashboard' && dashboard && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">My Dashboard</h2>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <p className="text-sm text-gray-600">Total Leads</p>
                <p className="text-2xl font-bold text-gray-900">{dashboard.total_leads}</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <p className="text-sm text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-red-600">{dashboard.high_priority_leads}</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <p className="text-sm text-gray-600">Pending Tasks</p>
                <p className="text-2xl font-bold text-yellow-600">{dashboard.pending_tasks}</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <p className="text-sm text-gray-600">Overdue</p>
                <p className="text-2xl font-bold text-red-600">{dashboard.overdue_tasks}</p>
              </div>
            </div>

            {/* Leads by Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Leads by Status</h3>
              <div className="space-y-2">
                {Object.entries(dashboard.leads_by_status).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">
                      {status.toLowerCase().replace('_', ' ')}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Today's Interactions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-2">Today's Activity</h3>
              <p className="text-2xl font-bold text-teal-600">
                {dashboard.recent_interactions_today} interactions
              </p>
            </div>
          </div>
        )}

        {view === 'leads' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">My Leads</h2>
              <button
                onClick={() => loadLeads()}
                className="text-teal-600 text-sm font-medium"
              >
                Refresh
              </button>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mx-auto"></div>
              </div>
            ) : leads.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <div className="text-4xl mb-2">👥</div>
                <p className="text-gray-600">No leads assigned</p>
              </div>
            ) : (
              leads.map((lead) => (
                <div
                  key={lead.owner_id}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{lead.owner_name}</h3>
                      <p className="text-sm text-gray-600">
                        {lead.building_name} - Unit {lead.unit_number}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(lead.priority)}`}
                    >
                      {lead.priority}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(lead.owner_status)}`}
                    >
                      {lead.owner_status.replace('_', ' ')}
                    </span>
                    {lead.days_since_contact !== null && lead.days_since_contact !== undefined && (
                      <span className="text-xs text-gray-500">
                        {lead.days_since_contact} days ago
                      </span>
                    )}
                    {lead.pending_tasks_count > 0 && (
                      <span className="text-xs text-yellow-600">
                        {lead.pending_tasks_count} tasks
                      </span>
                    )}
                  </div>

                  {/* Action Buttons - Thumb-friendly (≥44px) */}
                  <div className="grid grid-cols-3 gap-2">
                    {lead.phone_for_contact && (
                      <>
                        <button
                          onClick={() => handleCall(lead.phone_for_contact)}
                          className="bg-green-600 text-white py-3 px-2 rounded-lg font-medium text-sm flex items-center justify-center gap-1 min-h-[44px]"
                        >
                          <span>📞</span>
                          <span>Call</span>
                        </button>
                        <button
                          onClick={() => handleWhatsApp(lead.phone_for_contact)}
                          className="bg-green-500 text-white py-3 px-2 rounded-lg font-medium text-sm flex items-center justify-center gap-1 min-h-[44px]"
                        >
                          <span>💬</span>
                          <span>WhatsApp</span>
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => {
                        setSelectedLead(lead);
                        setShowQuickLog(true);
                      }}
                      className="bg-teal-600 text-white py-3 px-2 rounded-lg font-medium text-sm flex items-center justify-center gap-1 min-h-[44px]"
                    >
                      <span>📝</span>
                      <span>Log</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {view === 'tasks' && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">My Tasks</h2>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mx-auto"></div>
              </div>
            ) : tasks.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <div className="text-4xl mb-2">✅</div>
                <p className="text-gray-600">No tasks assigned</p>
              </div>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.task_id}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{task.title}</h3>
                      <p className="text-sm text-gray-600">{task.task_type}</p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        task.status === 'COMPLETED'
                          ? 'bg-green-100 text-green-800'
                          : task.status === 'OVERDUE'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {task.status}
                    </span>
                  </div>
                  {task.due_date && (
                    <p className="text-xs text-gray-500 mb-3">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </p>
                  )}
                  {task.status !== 'COMPLETED' && (
                    <button
                      onClick={async () => {
                        try {
                          await tasksService.completeTask(task.task_id);
                          loadTasks();
                        } catch (err: any) {
                          setError(err.response?.data?.detail || 'Failed to complete task');
                        }
                      }}
                      className="w-full bg-green-600 text-white py-3 rounded-lg font-medium min-h-[44px]"
                    >
                      Mark Complete
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {view === 'scanner' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Scanner</h2>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <p className="text-sm text-gray-600 mb-4">
                Upload documents (ID cards, signed contracts, etc.) for manual processing.
                In Phase 2, this will include camera integration for direct scanning.
              </p>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <div className="text-4xl mb-4">📷</div>
                <p className="text-gray-600 mb-2">Document Scanner</p>
                <p className="text-xs text-gray-500 mb-4">
                  Camera integration coming in Phase 2
                </p>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  className="hidden"
                  id="document-upload"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      // TODO: Implement document upload
                      alert(`Document upload will be implemented. Selected: ${file.name}`);
                    }
                  }}
                />
                <label
                  htmlFor="document-upload"
                  className="inline-flex bg-teal-600 text-white px-6 py-3 rounded-lg font-medium cursor-pointer min-h-[44px] items-center justify-center"
                >
                  Choose File
                </label>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Uploaded documents will be queued for manager approval.
                  Use the desktop interface for full document management features.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Log Modal */}
      {showQuickLog && selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end">
          <div className="bg-white w-full rounded-t-lg p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Quick Log Interaction</h2>
              <button
                onClick={() => {
                  setShowQuickLog(false);
                  setSelectedLead(null);
                }}
                className="text-gray-500 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-900">{selectedLead.owner_name}</p>
              <p className="text-xs text-gray-600">
                {selectedLead.building_name} - Unit {selectedLead.unit_number}
              </p>
            </div>

            <form onSubmit={handleQuickLog} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Interaction Type
                </label>
                <select
                  value={quickLogData.interaction_type}
                  onChange={(e) =>
                    setQuickLogData({ ...quickLogData, interaction_type: e.target.value })
                  }
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg text-base"
                  required
                >
                  <option value="PHONE_CALL">Phone Call</option>
                  <option value="IN_PERSON_MEETING">In-Person Meeting</option>
                  <option value="VIDEO_CALL">Video Call</option>
                  <option value="EMAIL">Email</option>
                  <option value="WHATSAPP">WhatsApp</option>
                  <option value="SMS">SMS</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  value={quickLogData.interaction_date}
                  onChange={(e) =>
                    setQuickLogData({ ...quickLogData, interaction_date: e.target.value })
                  }
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg text-base"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sentiment
                </label>
                <select
                  value={quickLogData.sentiment}
                  onChange={(e) =>
                    setQuickLogData({ ...quickLogData, sentiment: e.target.value })
                  }
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg text-base"
                >
                  <option value="POSITIVE">Positive</option>
                  <option value="NEUTRAL">Neutral</option>
                  <option value="NEGATIVE">Negative</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Call Summary * (Mandatory)
                </label>
                <textarea
                  value={quickLogData.call_summary}
                  onChange={(e) =>
                    setQuickLogData({ ...quickLogData, call_summary: e.target.value })
                  }
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg text-base"
                  rows={4}
                  placeholder="Enter summary of the interaction..."
                  required
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowQuickLog(false);
                    setSelectedLead(null);
                  }}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-medium min-h-[44px]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-teal-600 text-white py-3 rounded-lg font-medium min-h-[44px]"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

