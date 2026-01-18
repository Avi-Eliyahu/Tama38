import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { projectsService, Project } from '../services/projects';
import { buildingsService, Building } from '../services/buildings';
import { authService } from '../services/auth';
import { BreadcrumbItem } from '../components/Breadcrumbs';
import Modal from '../components/Modal';
import ProjectEditForm from '../components/ProjectEditForm';
import BuildingCreateForm from '../components/BuildingCreateForm';
import BuildingEditForm from '../components/BuildingEditForm';

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const { t } = useTranslation();
  const [project, setProject] = useState<Project | null>(null);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loading, setLoading] = useState(true);
  const [buildingsLoading, setBuildingsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddBuildingModalOpen, setIsAddBuildingModalOpen] = useState(false);
  const [editingBuilding, setEditingBuilding] = useState<Building | null>(null);
  const [isEditBuildingModalOpen, setIsEditBuildingModalOpen] = useState(false);
  const [deletingBuildingId, setDeletingBuildingId] = useState<string | null>(null);
  const [deleteConfirmStep, setDeleteConfirmStep] = useState<number>(0);
  const navigate = useNavigate();
  const currentUser = authService.getCurrentUserSync();
  const isAdmin = currentUser?.role === 'SUPER_ADMIN';
  const isManager = currentUser?.role === 'PROJECT_MANAGER';
  const canEdit = isAdmin || isManager;

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadBuildings();
    }
  }, [projectId]);

  const loadProject = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await projectsService.getProject(projectId);
      setProject(data);
      // Set breadcrumbs
      setBreadcrumbs([
        { label: t('projects.title'), path: '/projects' },
        { label: data.project_name, path: `/projects/${projectId}` },
      ]);
    } catch (err: any) {
      console.error('[PROJECT_DETAIL] Error loading project', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const loadBuildings = async () => {
    if (!projectId) return;
    try {
      setBuildingsLoading(true);
      const data = await buildingsService.getBuildings(projectId);
      setBuildings(data);
    } catch (err: any) {
      console.error('[PROJECT_DETAIL] Error loading buildings', err);
    } finally {
      setBuildingsLoading(false);
    }
  };

  const getTrafficLightColor = (status: string) => {
    const colors: Record<string, string> = {
      GREEN: 'bg-green-100 text-green-800 border-green-300',
      YELLOW: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      RED: 'bg-red-100 text-red-800 border-red-300',
      GRAY: 'bg-gray-100 text-gray-800 border-gray-300',
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      INITIAL: 'bg-gray-100 text-gray-800',
      NEGOTIATING: 'bg-blue-100 text-blue-800',
      APPROVED: 'bg-green-100 text-green-800',
      RENOVATION_PLANNING: 'bg-yellow-100 text-yellow-800',
      RENOVATION_ONGOING: 'bg-orange-100 text-orange-800',
      COMPLETED: 'bg-green-100 text-green-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const handleEditProject = () => {
    setIsEditModalOpen(true);
  };

  const handleSaveProject = (updatedProject: Project) => {
    setProject(updatedProject);
    setIsEditModalOpen(false);
    loadProject(); // Reload to get latest data
  };

  const handleDeleteProject = async (project: Project) => {
    if (window.confirm(`${t('projects.confirmDelete')} "${project.project_name}"?`)) {
      try {
        await projectsService.deleteProject(project.project_id);
        navigate('/projects');
      } catch (err: any) {
        console.error('[PROJECT_DETAIL] Error deleting project', err);
        alert(err.response?.data?.detail || t('common.error'));
      }
    }
  };

  const handleAddBuilding = () => {
    setIsAddBuildingModalOpen(true);
  };

  const handleSaveNewBuilding = (newBuilding: Building) => {
    setBuildings([...buildings, newBuilding]);
    setIsAddBuildingModalOpen(false);
    loadBuildings(); // Reload to get latest data
  };

  const handleEditBuilding = (building: Building) => {
    setEditingBuilding(building);
    setIsEditBuildingModalOpen(true);
  };

  const handleSaveBuilding = (updatedBuilding: Building) => {
    setBuildings(buildings.map(b => b.building_id === updatedBuilding.building_id ? updatedBuilding : b));
    setIsEditBuildingModalOpen(false);
    setEditingBuilding(null);
    loadBuildings(); // Reload to get latest data
  };

  const handleDeleteBuilding = async (building: Building) => {
    if (deleteConfirmStep === 0) {
      setDeletingBuildingId(building.building_id);
      setDeleteConfirmStep(1);
      return;
    }
    
    if (deleteConfirmStep === 1 && deletingBuildingId === building.building_id) {
      // Second confirmation
      const confirmText = prompt(`${t('buildings.confirmDelete')} "${building.building_name}"?\n${t('buildings.typeConfirmDelete')}: ${building.building_name}`);
      if (confirmText === building.building_name) {
        try {
          await buildingsService.deleteBuilding(building.building_id);
          setBuildings(buildings.filter(b => b.building_id !== building.building_id));
          setDeletingBuildingId(null);
          setDeleteConfirmStep(0);
        } catch (err: any) {
          console.error('[PROJECT_DETAIL] Error deleting building', err);
          alert(err.response?.data?.detail || t('common.error'));
          setDeletingBuildingId(null);
          setDeleteConfirmStep(0);
        }
      } else {
        alert(t('buildings.deleteCancelled'));
        setDeletingBuildingId(null);
        setDeleteConfirmStep(0);
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

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">{t('projects.projectNotFound')}</p>
        <Link to="/projects" className="text-teal-600 hover:text-teal-700 mt-4 inline-block">
          ← {t('common.back')} {t('projects.title')}
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{project.project_name}</h1>
          <p className="mt-1 text-sm text-gray-500">{project.project_code}</p>
        </div>
        {canEdit && (
          <div className="flex gap-2">
            <button
              onClick={handleEditProject}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
            >
              {t('common.edit')}
            </button>
            {isAdmin && (
              <button
                onClick={() => handleDeleteProject(project)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                {t('common.delete')}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Project Details */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('projects.projectDetails')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="text-sm font-medium text-gray-600">{t('projects.projectType')}</label>
            <p className="mt-1 text-sm text-gray-900">{project.project_type}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">{t('projects.stage')}</label>
            <p className="mt-1 text-sm text-gray-900">{project.project_stage}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">{t('projects.majorityRequired')}</label>
            <p className="mt-1 text-sm text-gray-900">{project.required_majority_percent}%</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">{t('projects.calculationType')}</label>
            <p className="mt-1 text-sm text-gray-900">{project.majority_calc_type}</p>
          </div>
          {project.location_city && (
            <div>
              <label className="text-sm font-medium text-gray-600">{t('projects.location')}</label>
              <p className="mt-1 text-sm text-gray-900">{project.location_city}</p>
            </div>
          )}
          {project.location_address && (
            <div>
              <label className="text-sm font-medium text-gray-600">{t('buildings.address')}</label>
              <p className="mt-1 text-sm text-gray-900">{project.location_address}</p>
            </div>
          )}
        </div>
      </div>

      {/* Buildings List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">{t('buildings.title')}</h2>
          <div className="flex items-center gap-3">
            {canEdit && (
              <button
                onClick={handleAddBuilding}
                className="px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700 transition-colors font-medium"
              >
                + {t('buildings.addBuilding')}
              </button>
            )}
            <Link
              to="/buildings"
              className="text-sm text-teal-600 hover:text-teal-700 font-medium"
            >
              {t('projects.viewAll')} →
            </Link>
          </div>
        </div>

        {buildingsLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mx-auto"></div>
            <p className="text-gray-500 mt-2">{t('buildings.loadingBuildings')}</p>
          </div>
        ) : buildings.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">🏢</div>
            <p className="text-gray-500">{t('buildings.noBuildings')}</p>
            <p className="text-sm text-gray-400 mt-1">
              {t('buildings.createThroughWizard')}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {buildings.map((building) => (
              <div
                key={building.building_id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow relative"
              >
                {canEdit && (
                  <div className="absolute top-2 right-2 flex gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditBuilding(building);
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
                        handleDeleteBuilding(building);
                      }}
                      className={`p-1.5 rounded transition-colors ${
                        deletingBuildingId === building.building_id && deleteConfirmStep === 1
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
                )}
                <Link
                  to={`/buildings/${building.building_id}`}
                  className="block"
                >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {building.building_name}
                    </h3>
                    {building.building_code && (
                      <p className="text-xs text-gray-500">{building.building_code}</p>
                    )}
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded border ${getTrafficLightColor(
                      building.traffic_light_status
                    )}`}
                  >
                    {building.traffic_light_status}
                  </span>
                </div>

                <div className="space-y-1 text-sm mb-3">
                  {building.address && (
                    <div className="flex items-center text-gray-600 text-xs">
                      <span className="mr-1">📍</span>
                      <span className="truncate">{building.address}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600">{t('buildings.status')}:</span>
                    <span
                      className={`px-2 py-0.5 font-medium rounded ${getStatusColor(
                        building.current_status
                      )}`}
                    >
                      {building.current_status.replace('_', ' ')}
                    </span>
                  </div>
                  {building.total_units !== undefined && (
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">{t('buildings.units')}:</span>
                      <span className="font-medium text-gray-900">
                        {building.total_units}
                      </span>
                    </div>
                  )}
                </div>

                {/* Signature Progress */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-700">
                      {t('buildings.signatureProgress')}
                    </span>
                    <span className="text-xs font-semibold text-gray-900">
                      {building.signature_percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${
                        building.signature_percentage >= 66.67
                          ? 'bg-green-500'
                          : building.signature_percentage >= 50
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(building.signature_percentage, 100)}%` }}
                    />
                  </div>
                </div>
              </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Project Modal */}
      {project && (
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          title={t('projects.editProject')}
          size="lg"
        >
          <ProjectEditForm
            project={project}
            onSave={handleSaveProject}
            onCancel={() => setIsEditModalOpen(false)}
          />
        </Modal>
      )}

      {/* Add Building Modal */}
      {project && (
        <Modal
          isOpen={isAddBuildingModalOpen}
          onClose={() => setIsAddBuildingModalOpen(false)}
          title={t('buildings.addBuilding')}
          size="lg"
        >
          <BuildingCreateForm
            projectId={project.project_id}
            onSave={handleSaveNewBuilding}
            onCancel={() => setIsAddBuildingModalOpen(false)}
          />
        </Modal>
      )}

      {/* Edit Building Modal */}
      {editingBuilding && (
        <Modal
          isOpen={isEditBuildingModalOpen}
          onClose={() => {
            setIsEditBuildingModalOpen(false);
            setEditingBuilding(null);
          }}
          title={t('buildings.editBuilding')}
          size="lg"
        >
          <BuildingEditForm
            building={editingBuilding}
            onSave={handleSaveBuilding}
            onCancel={() => {
              setIsEditBuildingModalOpen(false);
              setEditingBuilding(null);
            }}
          />
        </Modal>
      )}

      {/* Delete Confirmation Alert */}
      {deletingBuildingId && deleteConfirmStep === 1 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {t('buildings.confirmDelete')}
            </h3>
            <p className="text-gray-600 mb-4">
              {t('buildings.deleteWarning')}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setDeletingBuildingId(null);
                  setDeleteConfirmStep(0);
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => {
                  const building = buildings.find(b => b.building_id === deletingBuildingId);
                  if (building) {
                    handleDeleteBuilding(building);
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

