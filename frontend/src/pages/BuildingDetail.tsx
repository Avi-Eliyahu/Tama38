import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { buildingsService, Building } from '../services/buildings';
import { unitsService, Unit } from '../services/units';
import { projectsService, Project } from '../services/projects';
import { ownersService, Owner } from '../services/owners';
import { authService } from '../services/auth';
import Breadcrumbs, { BreadcrumbItem } from '../components/Breadcrumbs';
import Modal from '../components/Modal';
import BuildingEditForm from '../components/BuildingEditForm';
import UnitCreateForm from '../components/UnitCreateForm';
import UnitEditForm from '../components/UnitEditForm';
import OwnerCreateForm from '../components/OwnerCreateForm';
import OwnerEditForm from '../components/OwnerEditForm';

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
  const [isAddUnitModalOpen, setIsAddUnitModalOpen] = useState(false);
  const [editingUnit, setEditingUnit] = useState<Unit | null>(null);
  const [isEditUnitModalOpen, setIsEditUnitModalOpen] = useState(false);
  const [deletingUnitId, setDeletingUnitId] = useState<string | null>(null);
  const [deleteUnitConfirmStep, setDeleteUnitConfirmStep] = useState<number>(0);
  const [isAddOwnerModalOpen, setIsAddOwnerModalOpen] = useState(false);
  const [selectedUnitForOwner, setSelectedUnitForOwner] = useState<string | null>(null);
  const [editingOwner, setEditingOwner] = useState<{ owner: Owner; unit: Unit } | null>(null);
  const [isEditOwnerModalOpen, setIsEditOwnerModalOpen] = useState(false);
  const [deletingOwnerId, setDeletingOwnerId] = useState<string | null>(null);
  const [deleteOwnerConfirmStep, setDeleteOwnerConfirmStep] = useState<number>(0);
  const [deleteBuildingConfirmStep, setDeleteBuildingConfirmStep] = useState<number>(0);
  const navigate = useNavigate();
  const currentUser = authService.getCurrentUserSync();
  const isAdmin = currentUser?.role === 'SUPER_ADMIN';
  const isManager = currentUser?.role === 'PROJECT_MANAGER';
  const canEdit = isAdmin || isManager;

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
    if (deleteBuildingConfirmStep === 0) {
      setDeleteBuildingConfirmStep(1);
      return;
    }
    
    if (deleteBuildingConfirmStep === 1) {
      const confirmText = prompt(`${t('buildings.confirmDelete')} "${building.building_name}"?\n${t('buildings.typeConfirmDelete')}: ${building.building_name}`);
      if (confirmText === building.building_name) {
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
          setDeleteBuildingConfirmStep(0);
        }
      } else {
        alert(t('buildings.deleteCancelled'));
        setDeleteBuildingConfirmStep(0);
      }
    }
  };

  const handleAddUnit = () => {
    setIsAddUnitModalOpen(true);
  };

  const handleSaveNewUnit = (newUnit: Unit) => {
    setUnits([...units, newUnit].sort((a, b) => {
      const numA = parseInt(a.unit_number) || 0;
      const numB = parseInt(b.unit_number) || 0;
      return numA - numB;
    }));
    setIsAddUnitModalOpen(false);
    loadBuildingData(); // Reload to get latest data including updated total_units
  };

  const handleEditUnit = (unit: Unit) => {
    setEditingUnit(unit);
    setIsEditUnitModalOpen(true);
  };

  const handleSaveUnit = (updatedUnit: Unit) => {
    setUnits(units.map(u => u.unit_id === updatedUnit.unit_id ? updatedUnit : u));
    setIsEditUnitModalOpen(false);
    setEditingUnit(null);
    loadBuildingData(); // Reload to get latest data
  };

  const handleDeleteUnit = async (unit: Unit) => {
    if (deleteUnitConfirmStep === 0) {
      setDeletingUnitId(unit.unit_id);
      setDeleteUnitConfirmStep(1);
      return;
    }
    
    if (deleteUnitConfirmStep === 1 && deletingUnitId === unit.unit_id) {
      const confirmText = prompt(`${t('units.confirmDelete')} "${unit.unit_number}"?\n${t('units.typeConfirmDelete')}: ${unit.unit_number}`);
      if (confirmText === unit.unit_number) {
        try {
          await unitsService.deleteUnit(unit.unit_id);
          setUnits(units.filter(u => u.unit_id !== unit.unit_id));
          setDeletingUnitId(null);
          setDeleteUnitConfirmStep(0);
          loadBuildingData(); // Reload to get latest data including updated total_units
        } catch (err: any) {
          console.error('[BUILDING_DETAIL] Error deleting unit', err);
          alert(err.response?.data?.detail || t('common.error'));
          setDeletingUnitId(null);
          setDeleteUnitConfirmStep(0);
        }
      } else {
        alert(t('units.deleteCancelled'));
        setDeletingUnitId(null);
        setDeleteUnitConfirmStep(0);
      }
    }
  };

  const handleAddOwner = (unitId?: string) => {
    setSelectedUnitForOwner(unitId || null);
    setIsAddOwnerModalOpen(true);
  };

  const handleSaveNewOwner = (newOwner: Owner) => {
    // Find the unit for this owner
    const unit = units.find(u => u.unit_id === newOwner.unit_id);
    if (unit) {
      setAllOwners([...allOwners, { owner: newOwner, unit }]);
    }
    setIsAddOwnerModalOpen(false);
    setSelectedUnitForOwner(null);
    loadBuildingData(); // Reload to get latest data
  };

  const handleEditOwner = (owner: Owner, unit: Unit) => {
    setEditingOwner({ owner, unit });
    setIsEditOwnerModalOpen(true);
  };

  const handleSaveOwner = (updatedOwner: Owner) => {
    setAllOwners(allOwners.map(({ owner, unit }) => 
      owner.owner_id === updatedOwner.owner_id 
        ? { owner: updatedOwner, unit } 
        : { owner, unit }
    ));
    setIsEditOwnerModalOpen(false);
    setEditingOwner(null);
    loadBuildingData(); // Reload to get latest data
  };

  const handleDeleteOwner = async (owner: Owner) => {
    if (deleteOwnerConfirmStep === 0) {
      setDeletingOwnerId(owner.owner_id);
      setDeleteOwnerConfirmStep(1);
      return;
    }
    
    if (deleteOwnerConfirmStep === 1 && deletingOwnerId === owner.owner_id) {
      const confirmText = prompt(`${t('owners.confirmDelete')} "${owner.full_name}"?\n${t('owners.typeConfirmDelete')}: ${owner.full_name}`);
      if (confirmText === owner.full_name) {
        try {
          await ownersService.deleteOwner(owner.owner_id);
          setAllOwners(allOwners.filter(({ owner: o }) => o.owner_id !== owner.owner_id));
          setDeletingOwnerId(null);
          setDeleteOwnerConfirmStep(0);
          loadBuildingData(); // Reload to get latest data
        } catch (err: any) {
          console.error('[BUILDING_DETAIL] Error deleting owner', err);
          alert(err.response?.data?.detail || t('common.error'));
          setDeletingOwnerId(null);
          setDeleteOwnerConfirmStep(0);
        }
      } else {
        alert(t('owners.deleteCancelled'));
        setDeletingOwnerId(null);
        setDeleteOwnerConfirmStep(0);
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
          {canEdit && (
            <div className="flex gap-2">
              <button
                onClick={handleEditBuilding}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
              >
                {t('common.edit')}
              </button>
              {isAdmin && (
                <button
                  onClick={() => handleDeleteBuilding(building)}
                  className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                    deleteBuildingConfirmStep === 1
                      ? 'bg-red-700 text-white'
                      : 'bg-red-600 text-white hover:bg-red-700'
                  }`}
                >
                  {t('common.delete')}
                </button>
              )}
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
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{t('buildings.units')}</h3>
              {canEdit && (
                <button
                  onClick={handleAddUnit}
                  className="px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700 transition-colors font-medium"
                >
                  + {t('units.addUnit')}
                </button>
              )}
            </div>
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
                      {canEdit && (
                        <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('common.actions')}
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                      {units.map((unit) => (
                      <tr
                        key={unit.unit_id}
                        className="hover:bg-gray-50"
                      >
                        <td 
                          className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/units/${unit.unit_id}`)}
                        >
                          <div className="text-sm font-medium text-teal-600 hover:text-teal-700">
                            {t('buildings.unit')} {unit.unit_number}
                          </div>
                          <div className="text-sm text-gray-500">
                            {unit.floor_number !== undefined && `${t('buildings.floor')} ${unit.floor_number} | `}
                            {unit.area_sqm && `${unit.area_sqm} m²`}
                          </div>
                        </td>
                        <td 
                          className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/units/${unit.unit_id}`)}
                        >
                          {unit.area_sqm || '-'}
                        </td>
                        <td 
                          className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/units/${unit.unit_id}`)}
                        >
                          {unit.total_owners}
                        </td>
                        <td 
                          className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/units/${unit.unit_id}`)}
                        >
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getUnitStatusColor(unit.unit_status)}`}
                          >
                            {getUnitStatusLabel(unit.unit_status)}
                          </span>
                        </td>
                        {canEdit && (
                          <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                            <div className="flex gap-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleEditUnit(unit);
                                }}
                                className="p-1.5 bg-teal-600 text-white rounded hover:bg-teal-700 transition-colors"
                                title={t('common.edit')}
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteUnit(unit);
                                }}
                                className={`p-1.5 rounded transition-colors ${
                                  deletingUnitId === unit.unit_id && deleteUnitConfirmStep === 1
                                    ? 'bg-red-700 text-white'
                                    : 'bg-red-600 text-white hover:bg-red-700'
                                }`}
                                title={t('common.delete')}
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            </div>
                          </td>
                        )}
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
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{t('owners.title')}</h3>
              {canEdit && (
                <div className="flex gap-2">
                  {units.length > 0 && (
                    <select
                      value={selectedUnitForOwner || ''}
                      onChange={(e) => {
                        if (e.target.value) {
                          handleAddOwner(e.target.value);
                        }
                      }}
                      className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                    >
                      <option value="">{t('owners.selectUnitToAdd')}</option>
                      {units.map(unit => (
                        <option key={unit.unit_id} value={unit.unit_id}>
                          {t('buildings.unit')} {unit.unit_number}
                        </option>
                      ))}
                    </select>
                  )}
                  <button
                    onClick={() => handleAddOwner()}
                    className="px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700 transition-colors font-medium"
                  >
                    + {t('owners.addOwner')}
                  </button>
                </div>
              )}
            </div>
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
                      {canEdit && (
                        <th className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('common.actions')}
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {allOwners.map(({ owner, unit }) => (
                      <tr
                        key={owner.owner_id}
                        className="hover:bg-gray-50"
                      >
                        <td 
                          className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromBuilding: true, buildingId } })}
                        >
                          <div className="text-sm font-medium text-teal-600 hover:text-teal-700">
                            {owner.full_name}
                          </div>
                        </td>
                        <td 
                          className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromBuilding: true, buildingId } })}
                        >
                          <div className="text-sm text-gray-900">
                            {t('buildings.unit')} {unit.unit_number}
                          </div>
                        </td>
                        <td 
                          className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromBuilding: true, buildingId } })}
                        >
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
                        <td 
                          className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromBuilding: true, buildingId } })}
                        >
                          {owner.ownership_share_percent}%
                        </td>
                        <td 
                          className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'} cursor-pointer`}
                          onClick={() => navigate(`/owners/${owner.owner_id}`, { state: { fromBuilding: true, buildingId } })}
                        >
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(owner.owner_status)}`}
                          >
                            {getOwnerStatusLabel(owner.owner_status)}
                          </span>
                        </td>
                        {canEdit && (
                          <td className={`px-6 py-4 whitespace-nowrap ${isRTL ? 'text-right' : 'text-left'}`}>
                            <div className="flex gap-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleEditOwner(owner, unit);
                                }}
                                className="p-1.5 bg-teal-600 text-white rounded hover:bg-teal-700 transition-colors"
                                title={t('common.edit')}
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteOwner(owner);
                                }}
                                className={`p-1.5 rounded transition-colors ${
                                  deletingOwnerId === owner.owner_id && deleteOwnerConfirmStep === 1
                                    ? 'bg-red-700 text-white'
                                    : 'bg-red-600 text-white hover:bg-red-700'
                                }`}
                                title={t('common.delete')}
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            </div>
                          </td>
                        )}
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

      {/* Edit Building Modal */}
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

      {/* Add Unit Modal */}
      {building && (
        <Modal
          isOpen={isAddUnitModalOpen}
          onClose={() => setIsAddUnitModalOpen(false)}
          title={t('units.addUnit')}
          size="lg"
        >
          <UnitCreateForm
            buildingId={building.building_id}
            onSave={handleSaveNewUnit}
            onCancel={() => setIsAddUnitModalOpen(false)}
          />
        </Modal>
      )}

      {/* Edit Unit Modal */}
      {editingUnit && (
        <Modal
          isOpen={isEditUnitModalOpen}
          onClose={() => {
            setIsEditUnitModalOpen(false);
            setEditingUnit(null);
          }}
          title={t('units.editUnit')}
          size="lg"
        >
          <UnitEditForm
            unit={editingUnit}
            onSave={handleSaveUnit}
            onCancel={() => {
              setIsEditUnitModalOpen(false);
              setEditingUnit(null);
            }}
          />
        </Modal>
      )}

      {/* Add Owner Modal */}
      {building && (
        <Modal
          isOpen={isAddOwnerModalOpen}
          onClose={() => {
            setIsAddOwnerModalOpen(false);
            setSelectedUnitForOwner(null);
          }}
          title={t('owners.addOwner')}
          size="lg"
        >
          {selectedUnitForOwner ? (
            <OwnerCreateForm
              unitId={selectedUnitForOwner}
              onSave={handleSaveNewOwner}
              onCancel={() => {
                setIsAddOwnerModalOpen(false);
                setSelectedUnitForOwner(null);
              }}
            />
          ) : units.length > 0 ? (
            <div className="space-y-4">
              <p className="text-gray-600">{t('owners.selectUnitToAddOwner')}</p>
              <div className="space-y-2">
                {units.map(unit => (
                  <button
                    key={unit.unit_id}
                    onClick={() => setSelectedUnitForOwner(unit.unit_id)}
                    className="w-full px-4 py-2 text-left border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    {t('buildings.unit')} {unit.unit_number}
                    {unit.floor_number !== undefined && ` | ${t('buildings.floor')} ${unit.floor_number}`}
                  </button>
                ))}
              </div>
              <div className="flex justify-end">
                <button
                  onClick={() => {
                    setIsAddOwnerModalOpen(false);
                    setSelectedUnitForOwner(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-600">{t('units.noUnitsToAddOwner')}</p>
              <button
                onClick={() => {
                  setIsAddOwnerModalOpen(false);
                  setSelectedUnitForOwner(null);
                }}
                className="mt-4 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {t('common.cancel')}
              </button>
            </div>
          )}
        </Modal>
      )}

      {/* Edit Owner Modal */}
      {editingOwner && (
        <Modal
          isOpen={isEditOwnerModalOpen}
          onClose={() => {
            setIsEditOwnerModalOpen(false);
            setEditingOwner(null);
          }}
          title={t('owners.editOwner')}
          size="lg"
        >
          <OwnerEditForm
            owner={editingOwner.owner}
            onSave={handleSaveOwner}
            onCancel={() => {
              setIsEditOwnerModalOpen(false);
              setEditingOwner(null);
            }}
          />
        </Modal>
      )}

      {/* Delete Unit Confirmation Alert */}
      {deletingUnitId && deleteUnitConfirmStep === 1 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {t('units.confirmDelete')}
            </h3>
            <p className="text-gray-600 mb-4">
              {t('units.deleteWarning')}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setDeletingUnitId(null);
                  setDeleteUnitConfirmStep(0);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => {
                  const unit = units.find(u => u.unit_id === deletingUnitId);
                  if (unit) {
                    handleDeleteUnit(unit);
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                {t('common.continue')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Owner Confirmation Alert */}
      {deletingOwnerId && deleteOwnerConfirmStep === 1 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {t('owners.confirmDelete')}
            </h3>
            <p className="text-gray-600 mb-4">
              {t('owners.deleteWarning')}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setDeletingOwnerId(null);
                  setDeleteOwnerConfirmStep(0);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => {
                  const ownerData = allOwners.find(({ owner }) => owner.owner_id === deletingOwnerId);
                  if (ownerData) {
                    handleDeleteOwner(ownerData.owner);
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                {t('common.continue')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

