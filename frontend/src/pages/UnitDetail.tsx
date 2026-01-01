import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { unitsService, Unit } from '../services/units';
import { buildingsService, Building } from '../services/buildings';
import { projectsService, Project } from '../services/projects';
import { ownersService, Owner } from '../services/owners';
import { interactionsService, Interaction } from '../services/interactions';
import { tasksService, Task } from '../services/tasks';
import { documentsService, Document } from '../services/documents';
import Breadcrumbs, { BreadcrumbItem } from '../components/Breadcrumbs';

export default function UnitDetail() {
  const { unitId } = useParams<{ unitId: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [unit, setUnit] = useState<Unit | null>(null);
  const [building, setBuilding] = useState<Building | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [owners, setOwners] = useState<Owner[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'owners' | 'interactions' | 'tasks' | 'documents'>('owners');
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);

  useEffect(() => {
    if (unitId) {
      loadUnitData();
    }
  }, [unitId]);

  const loadUnitData = async () => {
    if (!unitId) return;

    try {
      setLoading(true);
      setError(null);

      // Load unit details
      const unitData = await unitsService.getUnit(unitId);
      setUnit(unitData);

      // Load building details
      const buildingData = await buildingsService.getBuilding(unitData.building_id);
      setBuilding(buildingData);

      // Load project details
      if (buildingData.project_id) {
        try {
          const projectData = await projectsService.getProject(buildingData.project_id);
          setProject(projectData);
          // Set breadcrumbs
          setBreadcrumbs([
            { label: t('projects.title'), path: '/projects' },
            { label: projectData.project_name, path: `/projects/${projectData.project_id}` },
            { label: buildingData.building_name || buildingData.building_code || t('buildings.title'), path: `/buildings/${buildingData.building_id}` },
            { label: `${t('buildings.unit')} ${unitData.unit_number}`, path: `/units/${unitId}` },
          ]);
        } catch (err) {
          console.error('[UNIT_DETAIL] Error loading project', err);
        }
      }

      // Load owners for this unit
      const ownersData = await ownersService.getOwners(unitId);
      setOwners(ownersData);

      // Load related data for tabs
      const ownerIds = ownersData.map(o => o.owner_id);
      
      if (ownerIds.length > 0) {
        // Load interactions
        const interactionsData = await interactionsService.getInteractionsByUnit(unitId, ownerIds);
        setInteractions(interactionsData);

        // Load tasks
        const tasksData = await tasksService.getTasksByUnit(unitId, ownerIds);
        setTasks(tasksData);

        // Load documents
        const documentsData = await documentsService.getDocumentsByUnit(unitId, ownerIds);
        setDocuments(documentsData);
      }
    } catch (err: any) {
      console.error('[UNIT_DETAIL] Error loading unit data', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      SIGNED: 'bg-green-100 text-green-800',
      PENDING: 'bg-yellow-100 text-yellow-800',
      NEGOTIATING: 'bg-blue-100 text-blue-800',
      AGREED_TO_SIGN: 'bg-blue-100 text-blue-800',
      WAIT_FOR_SIGN: 'bg-yellow-100 text-yellow-800',
      REFUSED: 'bg-red-100 text-red-800',
      NOT_CONTACTED: 'bg-gray-100 text-gray-800',
      ACTIVE: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      ON_HOLD: 'bg-yellow-100 text-yellow-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getSentimentColor = (sentiment?: string) => {
    const colors: Record<string, string> = {
      POSITIVE: 'bg-green-100 text-green-800',
      VERY_POSITIVE: 'bg-green-100 text-green-800',
      NEGATIVE: 'bg-red-100 text-red-800',
      VERY_NEGATIVE: 'bg-red-100 text-red-800',
      NEUTRAL: 'bg-gray-100 text-gray-800',
    };
    return colors[sentiment || 'NEUTRAL'] || colors.NEUTRAL;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      HIGH: 'bg-red-100 text-red-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      LOW: 'bg-green-100 text-green-800',
    };
    return colors[priority] || colors.MEDIUM;
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      PHONE_CALL: t('interactions.phoneCall'),
      IN_PERSON_MEETING: t('interactions.inPersonMeeting'),
      VIDEO_CALL: t('interactions.videoCall'),
      SCHEDULED_MEETING: t('interactions.scheduledMeeting'),
      EMAIL: t('interactions.email'),
      WHATSAPP: t('interactions.whatsapp'),
      SMS: t('interactions.sms'),
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('common.loading')}</div>
      </div>
    );
  }

  if (error || !unit || !building) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error || t('buildings.unitNotFound')}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && <Breadcrumbs items={breadcrumbs} />}

      {/* Header */}
      <div>
        <button
          onClick={() => navigate(`/buildings/${building.building_id}`)}
          className="text-sm text-teal-600 hover:text-teal-700 mb-4 inline-block"
        >
          ← {t('common.back')} {t('buildings.title')}
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {t('buildings.unit')} {unit.unit_number}
              {unit.floor_number !== undefined && ` | ${t('buildings.floor')} ${unit.floor_number}`}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {building.building_name || building.building_code}
              {building.address && ` | ${building.address}`}
              {project && ` | ${project.project_name}`}
            </p>
          </div>
        </div>
      </div>

      {/* Unit Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.area')} (m²)
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {unit.area_sqm || '-'}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.owners')}
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {unit.total_owners || owners.length}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.signatureProgress')}
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {unit.signature_percentage.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {unit.owners_signed} {t('buildings.of')} {unit.total_owners} {t('buildings.signed')}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.status')}
          </div>
          <div className="text-lg font-semibold text-gray-900">
            <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(unit.unit_status)}`}>
              {unit.unit_status}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('owners')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'owners'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('owners.title')} ({owners.length})
            </button>
            <button
              onClick={() => setActiveTab('interactions')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'interactions'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('interactions.title')} ({interactions.length})
            </button>
            <button
              onClick={() => setActiveTab('tasks')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'tasks'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('tasks.title')} ({tasks.length})
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'documents'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('navigation.documents')} ({documents.length})
            </button>
          </nav>
        </div>

        {/* Owners Tab */}
        {activeTab === 'owners' && (
          <div className="p-6">
            {owners.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">👥</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t('buildings.noOwners')}
                </h3>
                <p className="text-gray-500">
                  {t('buildings.ownersWillAppear')}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('owners.ownerName')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('owners.contact')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('owners.ownershipShare')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('owners.status')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {owners.map((owner) => (
                      <tr
                        key={owner.owner_id}
                        onClick={() => navigate(`/owners/${owner.owner_id}`)}
                        className="hover:bg-gray-50 cursor-pointer"
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-teal-600 hover:text-teal-700">
                            {owner.full_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {owner.phone_for_contact && (
                              <div className="flex items-center">
                                <span className="mr-2">📞</span>
                                <span>{owner.phone_for_contact}</span>
                              </div>
                            )}
                            {owner.email && (
                              <div className="flex items-center mt-1">
                                <span className="mr-2">✉️</span>
                                <span>{owner.email}</span>
                              </div>
                            )}
                            {!owner.phone_for_contact && !owner.email && (
                              <span className="text-gray-400">{t('owners.noContactInfo')}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {owner.ownership_share_percent}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(owner.owner_status)}`}
                          >
                            {owner.owner_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Interactions Tab */}
        {activeTab === 'interactions' && (
          <div className="p-6">
            {interactions.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t('interactions.noInteractions')}
                </h3>
                <p className="text-gray-500">
                  {t('interactions.willAppear')}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {interactions.map((interaction) => (
                  <div
                    key={interaction.log_id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-sm font-medium text-gray-900">
                            {getTypeLabel(interaction.interaction_type)}
                          </span>
                          <span className="text-sm text-gray-500">
                            {new Date(interaction.interaction_date).toLocaleDateString()}
                          </span>
                          {interaction.sentiment && (
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded ${getSentimentColor(interaction.sentiment)}`}
                            >
                              {interaction.sentiment}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{interaction.call_summary}</p>
                        {interaction.duration_minutes && (
                          <span className="text-xs text-gray-500">
                            {t('interactions.duration')}: {interaction.duration_minutes} {t('interactions.minutes')}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tasks Tab */}
        {activeTab === 'tasks' && (
          <div className="p-6">
            {tasks.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">✅</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t('tasks.noTasks')}
                </h3>
                <p className="text-gray-500">
                  {t('tasks.willAppear')}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div
                    key={task.task_id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(task.priority)}`}
                          >
                            {task.priority}
                          </span>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(task.status)}`}
                          >
                            {task.status}
                          </span>
                        </div>
                        {task.description && (
                          <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                        )}
                        {task.due_date && (
                          <span className="text-xs text-gray-500">
                            {t('tasks.dueDate')}: {new Date(task.due_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="p-6">
            {documents.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t('buildings.noDocuments')}
                </h3>
                <p className="text-gray-500">
                  {t('buildings.documentsWillAppear')}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {documents.map((document) => (
                  <div
                    key={document.document_id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{document.file_name}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {document.document_type} • {(document.file_size_bytes / 1024).toFixed(2)} KB
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(document.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

