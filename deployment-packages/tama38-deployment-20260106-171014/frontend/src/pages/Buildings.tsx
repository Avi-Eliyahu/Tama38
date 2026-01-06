import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { buildingsService, Building } from '../services/buildings';
import { projectsService, Project } from '../services/projects';
import { authService } from '../services/auth';
import Modal from '../components/Modal';
import BuildingEditForm from '../components/BuildingEditForm';

export default function Buildings() {
  const { t } = useTranslation();
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingBuilding, setEditingBuilding] = useState<Building | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const currentUser = authService.getCurrentUserSync();
  const isAdmin = currentUser?.role === 'SUPER_ADMIN';

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    loadBuildings();
  }, [selectedProjectId]);

  const loadProjects = async () => {
    try {
      const data = await projectsService.getProjects();
      setProjects(data);
    } catch (err: any) {
      console.error('[BUILDINGS] Error loading projects', err);
    }
  };

  const loadBuildings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await buildingsService.getBuildings(selectedProjectId || undefined);
      setBuildings(data);
    } catch (err: any) {
      console.error('[BUILDINGS] Error loading buildings', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getTrafficLightColor = (status: string) => {
    const colors: Record<string, string> = {
      GREEN: 'bg-green-100 text-green-800 border-green-300',
      YELLOW: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      RED: 'bg-red-100 text-red-800 border-red-300',
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      ACTIVE: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      ON_HOLD: 'bg-yellow-100 text-yellow-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const handleEditBuilding = (building: Building) => {
    setEditingBuilding(building);
    setIsEditModalOpen(true);
  };

  const handleSaveBuilding = (updatedBuilding: Building) => {
    setBuildings(buildings.map(b => b.building_id === updatedBuilding.building_id ? updatedBuilding : b));
    setIsEditModalOpen(false);
    setEditingBuilding(null);
  };

  const handleDeleteBuilding = async (building: Building) => {
    if (window.confirm(`${t('buildings.confirmDelete')} "${building.building_name}"?`)) {
      try {
        await buildingsService.deleteBuilding(building.building_id);
        loadBuildings(); // Reload buildings list
      } catch (err: any) {
        console.error('[BUILDINGS] Error deleting building', err);
        alert(err.response?.data?.detail || t('common.error'));
      }
    }
  };

  if (loading && buildings.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('buildings.loadingBuildings')}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('buildings.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">{t('buildings.subtitle')}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">{t('buildings.filterByProject')}:</label>
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="">{t('buildings.allProjects')}</option>
            {projects.map((project) => (
              <option key={project.project_id} value={project.project_id}>
                {project.project_name} ({project.project_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Buildings List */}
      {buildings.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">🏢</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('buildings.noBuildings')}</h3>
          <p className="text-gray-500">
            {selectedProjectId
              ? 'No buildings in this project yet. Create buildings through the project wizard.'
              : 'No buildings found. Create a project first and add buildings through the wizard.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {buildings.map((building) => (
            <div
              key={building.building_id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow relative"
            >
              {isAdmin && (
                <div className="absolute top-4 right-4 flex gap-2 z-10">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditBuilding(building);
                    }}
                    className="p-1 text-gray-400 hover:text-teal-600 transition-colors"
                    title={t('common.edit')}
                  >
                    ✏️
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteBuilding(building);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title={t('common.delete')}
                  >
                    🗑️
                  </button>
                </div>
              )}
              <Link
                to={`/buildings/${building.building_id}`}
                className="block"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {building.building_name}
                    </h3>
                    {building.building_code && (
                      <p className="text-sm text-gray-500">{building.building_code}</p>
                    )}
                  </div>
                  <div
                    className={`px-2 py-1 text-xs font-medium rounded border ${getTrafficLightColor(
                      building.traffic_light_status
                    )}`}
                  >
                    {building.traffic_light_status}
                  </div>
                </div>

              <div className="space-y-2 text-sm mb-4">
                {building.address && (
                  <div className="flex items-center text-gray-600">
                    <span className="mr-2">📍</span>
                    <span className="truncate">{building.address}</span>
                  </div>
                )}
                {building.floor_count && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('buildings.floors')}:</span>
                    <span className="font-medium text-gray-900">{building.floor_count}</span>
                  </div>
                )}
                {building.total_units !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('buildings.units')}:</span>
                    <span className="font-medium text-gray-900">{building.total_units}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">{t('buildings.status')}:</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(building.current_status)}`}>
                    {building.current_status}
                  </span>
                </div>
              </div>

              {/* Signature Progress */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{t('buildings.signatureProgress')}</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {building.signature_percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
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

      {/* Edit Modal */}
      {editingBuilding && (
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingBuilding(null);
          }}
          title={t('buildings.editBuilding')}
          size="lg"
        >
          <BuildingEditForm
            building={editingBuilding}
            onSave={handleSaveBuilding}
            onCancel={() => {
              setIsEditModalOpen(false);
              setEditingBuilding(null);
            }}
          />
        </Modal>
      )}
    </div>
  );
}
