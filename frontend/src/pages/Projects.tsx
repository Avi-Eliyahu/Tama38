import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { projectsService, Project } from '../services/projects';
import { authService } from '../services/auth';
import Modal from '../components/Modal';
import ProjectEditForm from '../components/ProjectEditForm';

export default function Projects() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const currentUser = authService.getCurrentUserSync();
  const isAdmin = currentUser?.role === 'SUPER_ADMIN';
  const isManager = currentUser?.role === 'PROJECT_MANAGER';
  const canCreateProject = isAdmin || isManager;

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsService.getProjects();
      setProjects(data);
    } catch (err: any) {
      console.error('[PROJECTS] Error loading projects', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getStageColor = (stage: string) => {
    const colors: Record<string, string> = {
      PLANNING: 'bg-gray-100 text-gray-800',
      ACTIVE: 'bg-blue-100 text-blue-800',
      APPROVAL: 'bg-yellow-100 text-yellow-800',
      COMPLETED: 'bg-green-100 text-green-800',
      ARCHIVED: 'bg-gray-100 text-gray-600',
    };
    return colors[stage] || colors.PLANNING;
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      TAMA38_1: 'TAMA38 Type 1',
      TAMA38_2: 'TAMA38 Type 2',
      PINUI_BINUI: 'Pinui Binui',
    };
    return labels[type] || type;
  };

  const handleEditProject = (project: Project) => {
    setEditingProject(project);
    setIsEditModalOpen(true);
  };

  const handleSaveProject = (updatedProject: Project) => {
    setProjects(projects.map(p => p.project_id === updatedProject.project_id ? updatedProject : p));
    setIsEditModalOpen(false);
    setEditingProject(null);
  };

  const handleDeleteProject = async (project: Project) => {
    if (window.confirm(`${t('projects.confirmDelete')} "${project.project_name}"?`)) {
      try {
        await projectsService.deleteProject(project.project_id);
        loadProjects(); // Reload projects list
      } catch (err: any) {
        console.error('[PROJECTS] Error deleting project', err);
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('projects.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">
            {t('projects.subtitle')}
          </p>
        </div>
        {canCreateProject && (
          <Link
            to="/projects/new"
            className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
          >
            <span className="mr-2">+</span>
            {t('projects.createProject')}
          </Link>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Projects List */}
      {projects.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">🏗️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('projects.noProjects')}</h3>
          <p className="text-gray-500 mb-6">{t('projects.createFirst')}</p>
          <Link
            to="/projects/new"
            className="inline-block px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
          >
            {t('projects.createProject')}
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.project_id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow relative"
            >
              {isAdmin && (
                <div className="absolute top-4 right-4 flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditProject(project);
                    }}
                    className="p-1 text-gray-400 hover:text-teal-600 transition-colors"
                    title={t('common.edit')}
                  >
                    ✏️
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title={t('common.delete')}
                  >
                    🗑️
                  </button>
                </div>
              )}
              <Link
                to={`/projects/${project.project_id}`}
                className="block"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {project.project_name}
                    </h3>
                    <p className="text-sm text-gray-500">{project.project_code}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${getStageColor(project.project_stage)}`}
                  >
                    {project.project_stage}
                  </span>
                </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">{t('projects.projectType')}:</span>
                  <span className="font-medium text-gray-900">
                    {getTypeLabel(project.project_type)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">{t('projects.majorityRequired')}:</span>
                  <span className="font-medium text-gray-900">
                    {project.required_majority_percent}%
                  </span>
                </div>
                {project.location_city && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">{t('projects.location')}:</span>
                    <span className="font-medium text-gray-900">{project.location_city}</span>
                  </div>
                )}
              </div>
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingProject && (
        <Modal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingProject(null);
          }}
          title={t('projects.editProject')}
          size="lg"
        >
          <ProjectEditForm
            project={editingProject}
            onSave={handleSaveProject}
            onCancel={() => {
              setIsEditModalOpen(false);
              setEditingProject(null);
            }}
          />
        </Modal>
      )}
    </div>
  );
}

