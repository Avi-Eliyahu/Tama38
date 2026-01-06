import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Project, CreateProjectDto } from '../services/projects';
import { projectsService } from '../services/projects';

interface ProjectEditFormProps {
  project: Project;
  onSave: (updatedProject: Project) => void;
  onCancel: () => void;
}

export default function ProjectEditForm({ project, onSave, onCancel }: ProjectEditFormProps) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<CreateProjectDto>>({
    project_name: project.project_name,
    project_code: project.project_code,
    project_type: project.project_type,
    location_city: project.location_city || '',
    location_address: project.location_address || '',
    required_majority_percent: project.required_majority_percent,
    majority_calc_type: project.majority_calc_type,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const updated = await projectsService.updateProject(project.project_id, formData);
      onSave(updated);
    } catch (err: any) {
      console.error('[PROJECT_EDIT] Error updating project', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('projects.projectName')} *
          </label>
          <input
            type="text"
            required
            value={formData.project_name}
            onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('projects.projectCode')} *
          </label>
          <input
            type="text"
            required
            value={formData.project_code}
            onChange={(e) => setFormData({ ...formData, project_code: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('projects.projectType')} *
          </label>
          <select
            required
            value={formData.project_type}
            onChange={(e) => setFormData({ ...formData, project_type: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="TAMA38_1">TAMA38 Type 1</option>
            <option value="TAMA38_2">TAMA38 Type 2</option>
            <option value="PINUI_BINUI">Pinui Binui</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('projects.majorityRequired')} (%) *
          </label>
          <input
            type="number"
            required
            min="0"
            max="100"
            step="0.01"
            value={formData.required_majority_percent}
            onChange={(e) => setFormData({ ...formData, required_majority_percent: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('projects.calculationType')} *
          </label>
          <select
            required
            value={formData.majority_calc_type}
            onChange={(e) => setFormData({ ...formData, majority_calc_type: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          >
            <option value="HEADCOUNT">Headcount</option>
            <option value="AREA">Area</option>
            <option value="WEIGHTED">Weighted</option>
            <option value="CUSTOM">Custom</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('projects.location')}
          </label>
          <input
            type="text"
            value={formData.location_city || ''}
            onChange={(e) => setFormData({ ...formData, location_city: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('projects.location')}
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('buildings.address')}
          </label>
          <input
            type="text"
            value={formData.location_address || ''}
            onChange={(e) => setFormData({ ...formData, location_address: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('buildings.address')}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          {t('common.cancel')}
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-50"
        >
          {loading ? t('common.saving') : t('common.save')}
        </button>
      </div>
    </form>
  );
}

