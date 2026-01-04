import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ownersService, Owner } from '../services/owners';
import { unitsService, Unit } from '../services/units';
import { buildingsService, Building } from '../services/buildings';
import { projectsService, Project } from '../services/projects';
import { interactionsService, Interaction } from '../services/interactions';
import { tasksService, Task } from '../services/tasks';
import { documentsService, Document } from '../services/documents';
import { approvalsService, Signature } from '../services/approvals';
import { authService } from '../services/auth';
import Breadcrumbs, { BreadcrumbItem } from '../components/Breadcrumbs';
import OwnerStatusChange from '../components/OwnerStatusChange';
import InitiateSignatureForm from '../components/InitiateSignatureForm';
import PDFViewer from '../components/PDFViewer';

interface OwnerUnit {
  unit_id: string;
  unit_number: string;
  floor_number?: number;
  building_id: string;
  ownership_share_percent: number;
}

export default function OwnerDetail() {
  const { ownerId } = useParams<{ ownerId: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [owner, setOwner] = useState<Owner | null>(null);
  const [primaryUnit, setPrimaryUnit] = useState<Unit | null>(null);
  const [building, setBuilding] = useState<Building | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [ownerUnits, setOwnerUnits] = useState<OwnerUnit[]>([]);
  const [unitsData, setUnitsData] = useState<Map<string, { unit: Unit; building: Building }>>(new Map());
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [approvals, setApprovals] = useState<Signature[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'units' | 'correspondence' | 'tasks' | 'documents'>('units');
  const [correspondenceSubTab, setCorrespondenceSubTab] = useState<'interactions' | 'documents' | 'tasks' | 'approvals'>('interactions');
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);
  const [viewingDocument, setViewingDocument] = useState<{ documentId: string; filename: string } | null>(null);

  useEffect(() => {
    if (ownerId) {
      loadOwnerData();
    }
  }, [ownerId]);

  const loadOwnerData = async () => {
    if (!ownerId) return;

    try {
      setLoading(true);
      setError(null);

      // Load owner details
      const ownerData = await ownersService.getOwner(ownerId);
      setOwner(ownerData);

      // Load primary unit details
      const unitData = await unitsService.getUnit(ownerData.unit_id);
      setPrimaryUnit(unitData);

      // Load building details
      const buildingData = await buildingsService.getBuilding(unitData.building_id);
      setBuilding(buildingData);

      // Load project details
      if (buildingData.project_id) {
        try {
          const projectData = await projectsService.getProject(buildingData.project_id);
          setProject(projectData);
        } catch (err) {
          console.error('[OWNER_DETAIL] Error loading project', err);
        }
      }

      // Load all units owned by this owner (multi-unit support)
      const unitsList = await ownersService.getOwnerUnits(ownerId);
      setOwnerUnits(unitsList);

      // Load building and unit details for all units
      const unitsDataMap = new Map<string, { unit: Unit; building: Building }>();
      for (const ownerUnit of unitsList) {
        try {
          const unit = await unitsService.getUnit(ownerUnit.unit_id);
          const building = await buildingsService.getBuilding(ownerUnit.building_id);
          unitsDataMap.set(ownerUnit.unit_id, { unit, building });
        } catch (err) {
          console.error(`[OWNER_DETAIL] Error loading unit ${ownerUnit.unit_id}`, err);
        }
      }
      setUnitsData(unitsDataMap);

      // Build breadcrumbs
      if (project && building && unitData) {
        setBreadcrumbs([
          { label: t('projects.title'), path: '/projects' },
          { label: project.project_name, path: `/projects/${project.project_id}` },
          { label: building.building_name || building.building_code || t('buildings.title'), path: `/buildings/${building.building_id}` },
          { label: `${t('buildings.unit')} ${unitData.unit_number}`, path: `/units/${unitData.unit_id}` },
          { label: ownerData.full_name, path: `/owners/${ownerId}` },
        ]);
      }

      // Load related data
      const interactionsData = await interactionsService.getInteractionsByOwner(ownerId);
      setInteractions(interactionsData);

      const tasksData = await tasksService.getTasksByOwner(ownerId);
      setTasks(tasksData);

      const documentsData = await documentsService.getDocumentsByOwner(ownerId);
      setDocuments(documentsData);

      try {
        const approvalsData = await approvalsService.getApprovalsByOwner(ownerId);
        setApprovals(approvalsData);
      } catch (err) {
        console.error('[OWNER_DETAIL] Error loading approvals', err);
      }
    } catch (err: any) {
      console.error('[OWNER_DETAIL] Error loading owner data', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getBackPath = () => {
    // If came from unit detail, go back to unit
    if (location.state?.fromUnit && primaryUnit) {
      return `/units/${primaryUnit.unit_id}`;
    }
    // If came from building detail, go back to building
    if (location.state?.fromBuilding && building) {
      return `/buildings/${building.building_id}`;
    }
    // Default: go to owners list
    return '/owners';
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

  if (error || !owner || !primaryUnit || !building) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error || t('owners.ownerNotFound')}
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
          onClick={() => navigate(getBackPath())}
          className="text-sm text-teal-600 hover:text-teal-700 mb-4 inline-block"
        >
          ← {t('common.back')}
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{owner.full_name}</h1>
            <p className="mt-1 text-sm text-gray-500">
              {primaryUnit && `${t('buildings.unit')} ${primaryUnit.unit_number}`}
              {building && ` | ${building.building_name || building.building_code}`}
              {project && ` | ${project.project_name}`}
            </p>
          </div>
        </div>
      </div>

      {/* Owner Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('owners.contact')}
          </div>
          <div className="text-sm text-gray-900">
            {owner.phone_for_contact && (
              <div className="flex items-center mb-1">
                <span className="mr-2">📞</span>
                <span>{owner.phone_for_contact}</span>
              </div>
            )}
            {owner.email && (
              <div className="flex items-center">
                <span className="mr-2">✉️</span>
                <span>{owner.email}</span>
              </div>
            )}
            {!owner.phone_for_contact && !owner.email && (
              <span className="text-gray-400">{t('owners.noContactInfo')}</span>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('owners.ownershipShare')}
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {owner.ownership_share_percent}%
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {ownerUnits.length} {ownerUnits.length === 1 ? t('buildings.unit') : t('buildings.units')}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('owners.status')}
          </div>
          <div className="text-lg font-semibold text-gray-900">
            <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(owner.owner_status)}`}>
              {owner.owner_status}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('owners.preferredContact')}
          </div>
          <div className="text-sm text-gray-900">
            {owner.preferred_contact_method || t('owners.notSpecified')}
          </div>
          {owner.preferred_language && (
            <div className="text-xs text-gray-500 mt-1">
              {t('owners.language')}: {owner.preferred_language}
            </div>
          )}
        </div>
      </div>

      {/* Status Change Section */}
      <OwnerStatusChange 
        owner={owner} 
        onStatusChange={(newStatus) => {
          setOwner({ ...owner, owner_status: newStatus });
          loadOwnerData();
        }} 
      />

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('units')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'units'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('buildings.units')} ({ownerUnits.length})
            </button>
            <button
              onClick={() => setActiveTab('correspondence')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'correspondence'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('owners.correspondence')} ({interactions.length + documents.length + tasks.length + approvals.length})
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

        {/* Units Tab */}
        {activeTab === 'units' && (
          <div className="p-6">
            {ownerUnits.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🏠</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t('buildings.noUnits')}
                </h3>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('buildings.unit')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('buildings.buildingName')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('buildings.area')} (m²)
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('owners.ownershipShare')}
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {t('buildings.status')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {ownerUnits.map((ownerUnit) => {
                      const unitData = unitsData.get(ownerUnit.unit_id);
                      return (
                        <tr
                          key={ownerUnit.unit_id}
                          onClick={() => navigate(`/units/${ownerUnit.unit_id}`)}
                          className="hover:bg-gray-50 cursor-pointer"
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-teal-600 hover:text-teal-700">
                              {t('buildings.unit')} {ownerUnit.unit_number}
                              {ownerUnit.floor_number !== undefined && ` | ${t('buildings.floor')} ${ownerUnit.floor_number}`}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {unitData?.building.building_name || unitData?.building.building_code || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {unitData?.unit.area_sqm || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {ownerUnit.ownership_share_percent}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {unitData && (
                              <span
                                className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(unitData.unit.unit_status)}`}
                              >
                                {unitData.unit.unit_status}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Correspondence Tab */}
        {activeTab === 'correspondence' && (
          <div className="p-6">
            {/* Sub-tabs for correspondence */}
            <div className="border-b border-gray-200 mb-4">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setCorrespondenceSubTab('interactions')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    correspondenceSubTab === 'interactions'
                      ? 'border-teal-500 text-teal-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {t('interactions.title')} ({interactions.length})
                </button>
                <button
                  onClick={() => setCorrespondenceSubTab('documents')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    correspondenceSubTab === 'documents'
                      ? 'border-teal-500 text-teal-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {t('navigation.documents')} ({documents.length})
                </button>
                <button
                  onClick={() => setCorrespondenceSubTab('tasks')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    correspondenceSubTab === 'tasks'
                      ? 'border-teal-500 text-teal-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {t('tasks.title')} ({tasks.length})
                </button>
                <button
                  onClick={() => setCorrespondenceSubTab('approvals')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    correspondenceSubTab === 'approvals'
                      ? 'border-teal-500 text-teal-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {t('approvals.title')} ({approvals.length})
                </button>
              </nav>
            </div>

            {/* Interactions Sub-tab */}
            {correspondenceSubTab === 'interactions' && (
              <div>
                {interactions.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">💬</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {t('interactions.noInteractions')}
                    </h3>
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

            {/* Documents Sub-tab */}
            {correspondenceSubTab === 'documents' && (
              <div className="space-y-6">
                {/* Initiate Signature Section (for agents) */}
                {authService.getCurrentUserSync()?.role === 'AGENT' && owner && owner.owner_status !== 'SIGNED' && owner.owner_status !== 'REFUSED' && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      {t('approvals.initiateSignature')}
                    </h3>
                    <InitiateSignatureForm ownerId={owner.owner_id} documents={documents} onSuccess={() => loadOwnerData()} />
                  </div>
                )}
                
                {/* Documents List */}
                {documents.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">📄</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {t('buildings.noDocuments')}
                    </h3>
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

            {/* Tasks Sub-tab */}
            {correspondenceSubTab === 'tasks' && (
              <div>
                {tasks.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✅</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {t('tasks.noTasks')}
                    </h3>
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

            {/* Approvals Sub-tab */}
            {correspondenceSubTab === 'approvals' && (
              <div>
                {approvals.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">✍️</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {t('approvals.noPendingApprovals')}
                    </h3>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {approvals.map((approval) => (
                      <div
                        key={approval.signature_id}
                        className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="text-sm font-medium text-gray-900">
                                {t('approvals.documentId')}: {approval.document_id}
                              </span>
                              <span
                                className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(approval.signature_status)}`}
                              >
                                {approval.signature_status}
                              </span>
                            </div>
                            {approval.signed_at && (
                              <p className="text-sm text-gray-500">
                                {t('approvals.signedDate')}: {new Date(approval.signed_at).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
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
                        <div className="mt-3 flex items-center gap-2">
                          {document.document_type === 'SIGNED_CONTRACT' || document.document_type === 'CONTRACT' ? (
                            <>
                              <button
                                onClick={() => {
                                  setViewingDocument({
                                    documentId: document.document_id,
                                    filename: document.file_name
                                  });
                                }}
                                className="px-3 py-1 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium flex items-center gap-1"
                              >
                                👁️ {t('documents.view')}
                              </button>
                              <button
                                onClick={async () => {
                                  try {
                                    await documentsService.downloadDocument(document.document_id, document.file_name);
                                  } catch (err) {
                                    console.error('Error downloading document:', err);
                                    alert('Failed to download document');
                                  }
                                }}
                                className="px-3 py-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium flex items-center gap-1"
                              >
                                ⬇️ {t('documents.download')}
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={async () => {
                                try {
                                  await documentsService.downloadDocument(document.document_id, document.file_name);
                                } catch (err) {
                                  console.error('Error downloading document:', err);
                                  alert('Failed to download document');
                                }
                              }}
                              className="px-3 py-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium flex items-center gap-1"
                            >
                              ⬇️ {t('documents.download')}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

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

