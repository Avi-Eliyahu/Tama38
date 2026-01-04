import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { buildingsService, Building } from '../services/buildings';
import { unitsService, Unit } from '../services/units';
import { projectsService, Project } from '../services/projects';
import { ownersService, Owner } from '../services/owners';
import { authService } from '../services/auth';
import Breadcrumbs, { BreadcrumbItem } from '../components/Breadcrumbs';
import Modal from '../components/Modal';
import BuildingEditForm from '../components/BuildingEditForm';

export default function BuildingDetail() {
  const { buildingId } = useParams<{ buildingId: string }>();
  const { t, i18n } = useTranslation();
  const isRTL = ['he', 'ar'].includes(i18n.language);
  const [building, setBuilding] = useState<Building | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [units, setUnits] = useState<Unit[]>([]);
  const [allOwners, setAllOwners] = useState<Array<{ owner: any; unit: Unit }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'units' | 'owners' | 'interactions' | 'tasks'>('units');
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const navigate = useNavigate();
  const currentUser = authService.getCurrentUserSync();
  const isAdmin = currentUser?.role === 'SUPER_ADMIN';

  useEffect(() => {
    if (buildingId) {
      loadBuildingData();
    }
  }, [buildingId]);

  const loadBuildingData = async () => {
    if (!buildingId) return;

    try {
      setLoading(true);
      setError(null);

      // Load building details
      const buildingData = await buildingsService.getBuilding(buildingId);
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
            { label: buildingData.building_name || buildingData.building_code || t('buildings.title'), path: `/buildings/${buildingId}` },
          ]);
        } catch (err) {
          console.error('[BUILDING_DETAIL] Error loading project', err);
        }
      }

      // Load units for this building
      const unitsData = await unitsService.getUnits(buildingId);
      // Sort units by apartment number (unit_number) - convert to number for proper sorting
      const sortedUnits = [...unitsData].sort((a, b) => {
        const numA = parseInt(a.unit_number) || 0;
        const numB = parseInt(b.unit_number) || 0;
        return numA - numB;
      });
      setUnits(sortedUnits);

      // Load all owners for all units in this building
      const ownersList: Array<{ owner: Owner; unit: Unit }> = [];
      for (const unit of sortedUnits) {
        try {
          const unitOwners = await ownersService.getOwners(unit.unit_id);
          for (const owner of unitOwners) {
            ownersList.push({ owner, unit });
          }
        } catch (err) {
          console.error(`[BUILDING_DETAIL] Error loading owners for unit ${unit.unit_id}`, err);
        }
      }
      setAllOwners(ownersList);
    } catch (err: any) {
      console.error('[BUILDING_DETAIL] Error loading building data', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getTrafficLightColor = (status: string) => {
    const colors: Record<string, string> = {
      GREEN: 'text-green-600',
      YELLOW: 'text-yellow-600',
      RED: 'text-red-600',
    };
    return colors[status] || 'text-gray-600';
  };

  const getTrafficLightEmoji = (status: string) => {
    const emojis: Record<string, string> = {
      GREEN: '🟢',
      YELLOW: '🟡',
      RED: '🔴',
    };
    return emojis[status] || '⚪';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      SIGNED: 'bg-green-100 text-green-800',
      PENDING: 'bg-yellow-100 text-yellow-800',
      NEGOTIATING: 'bg-blue-100 text-blue-800',
      AGREED_TO_SIGN: 'bg-blue-100 text-blue-800',
      WAIT_FOR_SIGN: 'bg-yellow-100 text-yellow-800',
      REJECTED: 'bg-red-100 text-red-800',
      REFUSED: 'bg-red-100 text-red-800',
      NOT_CONTACTED: 'bg-gray-100 text-gray-800',
      ACTIVE: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      ON_HOLD: 'bg-yellow-100 text-yellow-800',
      CANCELLED: 'bg-red-100 text-red-800',
      DECEASED: 'bg-gray-100 text-gray-800',
      INCAPACITATED: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

    const getOwnerStatusLabel = (status: string) => {
      const labels: Record<string, string> = {
        NOT_CONTACTED: t('owners.statusLabels.NOT_CONTACTED'),
        PENDING_SIGNATURE: t('owners.statusLabels.PENDING_SIGNATURE'),
        NEGOTIATING: t('owners.statusLabels.NEGOTIATING'),
        AGREED_TO_SIGN: t('owners.statusLabels.AGREED_TO_SIGN'),
        WAIT_FOR_SIGN: t('owners.statusLabels.WAIT_FOR_SIGN'),
        SIGNED: t('owners.statusLabels.SIGNED'),
        REFUSED: t('owners.statusLabels.REFUSED'),
        DECEASED: t('owners.statusLabels.DECEASED'),
        INCAPACITATED: t('owners.statusLabels.INCAPACITATED'),
      };
      return labels[status] || status;
    };

  const getUnitStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      SIGNED: 'bg-green-100 text-green-800',
      PARTIALLY_SIGNED: 'bg-yellow-100 text-yellow-800',
      NOT_SIGNED: 'bg-gray-100 text-gray-800',
      NOT_CONTACTED: 'bg-gray-100 text-gray-800',
      NEGOTIATING: 'bg-blue-100 text-blue-800',
      AGREED_TO_SIGN: 'bg-purple-100 text-purple-800',
      FINALIZED: 'bg-green-100 text-green-800',
      REFUSED: 'bg-red-100 text-red-800',
      INACTIVE: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getUnitStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      SIGNED: t('units.status.signed'),
      PARTIALLY_SIGNED: t('units.status.partiallySigned'),
      NOT_SIGNED: t('units.status.notSigned'),
      NOT_CONTACTED: t('units.status.notContacted'),
      NEGOTIATING: t('units.status.negotiating'),
      AGREED_TO_SIGN: t('units.status.agreedToSign'),
      FINALIZED: t('units.status.finalized'),
      REFUSED: t('units.status.refused'),
      INACTIVE: t('units.status.inactive'),
    };
    return labels[status] || status;
  };

  const handleEditBuilding = () => {
    setIsEditModalOpen(true);
  };

  const handleSaveBuilding = (updatedBuilding: Building) => {
    setBuilding(updatedBuilding);
    setIsEditModalOpen(false);
    loadBuildingData(); // Reload to get latest data
  };

  const handleDeleteBuilding = async (building: Building) => {
    if (window.confirm(`${t('buildings.confirmDelete')} "${building.building_name}"?`)) {
      try {
        await buildingsService.deleteBuilding(building.building_id);
        if (project) {
          navigate(`/projects/${project.project_id}`);
        } else {
          navigate('/buildings');
        }
      } catch (err: any) {
        console.error('[BUILDING_DETAIL] Error deleting building', err);
        alert(err.response?.data?.detail || t('common.error'));
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('common.loading')}</div>
      </div>
    );
  }

  if (error || !building) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error || t('buildings.buildingNotFound')}
      </div>
    );
  }

  const signedOwners = units.reduce((sum, unit) => sum + unit.owners_signed, 0);
  const totalOwners = units.reduce((sum, unit) => sum + unit.total_owners, 0);
  
  // Calculate actual signature percentage based on signed units
  const totalUnits = building.total_units || units.length;
  const signedUnits = building.units_signed ?? 0;
  const actualSignaturePercentage = totalUnits > 0 ? (signedUnits / totalUnits) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && <Breadcrumbs items={breadcrumbs} />}

      {/* Header */}
      <div>
        {project && (
          <button
            onClick={() => navigate(`/projects/${project.project_id}`)}
            className="text-sm text-teal-600 hover:text-teal-700 mb-4 inline-block"
          >
            ← {t('common.back')} {t('projects.title')}
          </button>
        )}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {building.building_code || building.building_name}
              {building.address && ` | ${building.address}`}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {project && `${project.project_name} | `}
              {building.address && `${building.address}`}
            </p>
          </div>
          {isAdmin && (
            <div className="flex gap-2">
              <button
                onClick={handleEditBuilding}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
              >
                {t('common.edit')}
              </button>
              <button
                onClick={() => handleDeleteBuilding(building)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                {t('common.delete')}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.signatureProgress')}
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {actualSignaturePercentage.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {signedUnits} {t('buildings.of')} {totalUnits} {t('buildings.units')}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.totalUnits')}
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {building.total_units || units.length}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {t('buildings.allIdentified')}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.trafficLight')}
          </div>
          <div className={`text-4xl ${getTrafficLightColor(building.traffic_light_status)}`}>
            {getTrafficLightEmoji(building.traffic_light_status)}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {building.traffic_light_status === 'GREEN' && t('buildings.excellentProgress')}
            {building.traffic_light_status === 'YELLOW' && t('buildings.goodProgress')}
            {building.traffic_light_status === 'RED' && t('buildings.needsAttention')}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">
            {t('buildings.assignedAgent')}
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {building.assigned_agent_name ? (
              <span className="text-sm text-gray-900">{building.assigned_agent_name}</span>
            ) : (
              <span className="text-sm text-gray-400">{t('buildings.unassigned')}</span>
            )}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {building.assigned_agent_email ? building.assigned_agent_email : t('buildings.noAgentAssigned')}
          </div>
        </div>
      </div>

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
              {t('buildings.units')} ({units.length})
            </button>
            <button
              onClick={() => setActiveTab('owners')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'owners'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('owners.title')} ({totalOwners})
            </button>
            <button
              onClick={() => setActiveTab('interactions')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'interactions'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('interactions.title')}
            </button>
            <button
              onClick={() => setActiveTab('tasks')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'tasks'
                  ? 'border-teal-500 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('tasks.title')}
            </button>
          </nav>
        </div>

        {/* Units Tab */}
        {activeTab === 'units' && (
          <div className="p-6">
            {units.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🏠</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {t('buildings.noUnits')}
                </h3>
                <p className="text-gray-500">
                  {t('buildings.unitsWillAppear')}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('buildings.unit')}
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('buildings.area')} (m²)
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('buildings.owners')}
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('buildings.status')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                      {units.map((unit) => (
                      <tr
                        key={unit.unit_id}
                        onClick={() => navigate(`/units/${unit.unit_id}`)}
                        className="hover:bg-gray-50 cursor-pointer"
                      >
                        <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                          <div className="text-sm font-medium text-teal-600 hover:text-teal-700">
                            {t('buildings.unit')} {unit.unit_number}
                          </div>
                          <div className="text-sm text-gray-500">
                            {unit.floor_number !== undefined && `${t('buildings.floor')} ${unit.floor_number} | `}
                            {unit.area_sqm && `${unit.area_sqm} m²`}
                          </div>
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {unit.area_sqm || '-'}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {unit.total_owners}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getUnitStatusColor(unit.unit_status)}`}
                          >
                            {getUnitStatusLabel(unit.unit_status)}
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

        {/* Owners Tab */}
        {activeTab === 'owners' && (
          <div className="p-6">
            {allOwners.length === 0 ? (
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
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('owners.ownerName')}
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('buildings.unit')}
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('owners.contact')}
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('owners.ownershipShare')}
                      </th>
                      <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                        {t('owners.status')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {allOwners.map(({ owner, unit }) => (
                      <tr
                        key={owner.owner_id}
                        onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromBuilding: true, buildingId } })}
                        className="hover:bg-gray-50 cursor-pointer"
                      >
                        <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                          <div className="text-sm font-medium text-teal-600 hover:text-teal-700">
                            {owner.full_name}
                          </div>
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                          <div className="text-sm text-gray-900">
                            {t('buildings.unit')} {unit.unit_number}
                          </div>
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                          <div className={`text-sm text-gray-900 ${isRTL ? 'text-right' : ''}`}>
                            {owner.phone_for_contact && (
                              <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
                                <span className={isRTL ? 'ml-2' : 'mr-2'}>📞</span>
                                <span>{owner.phone_for_contact}</span>
                              </div>
                            )}
                            {owner.email && (
                              <div className={`flex items-center mt-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                                <span className={isRTL ? 'ml-2' : 'mr-2'}>✉️</span>
                                <span>{owner.email}</span>
                              </div>
                            )}
                            {!owner.phone_for_contact && !owner.email && (
                              <span className="text-gray-400">{t('owners.noContactInfo')}</span>
                            )}
                          </div>
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {owner.ownership_share_percent}%
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(owner.owner_status)}`}
                          >
                            {getOwnerStatusLabel(owner.owner_status)}
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
            <div className="text-center py-12">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {t('buildings.interactionsTabComingSoon')}
              </h3>
              <p className="text-gray-500">
                {t('buildings.interactionsTabDescription')}
              </p>
            </div>
          </div>
        )}

        {/* Tasks Tab */}
        {activeTab === 'tasks' && (
          <div className="p-6">
            <div className="text-center py-12">
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {t('buildings.tasksTabComingSoon')}
              </h3>
              <p className="text-gray-500">
                {t('buildings.tasksTabDescription')}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {building && (
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          title={t('buildings.editBuilding')}
          size="lg"
        >
          <BuildingEditForm
            building={building}
            onSave={handleSaveBuilding}
            onCancel={() => setIsEditModalOpen(false)}
          />
        </Modal>
      )}
    </div>
  );
}

