import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Building, CreateBuildingDto } from '../services/buildings';
import { buildingsService } from '../services/buildings';

interface BuildingEditFormProps {
  building: Building;
  onSave: (updatedBuilding: Building) => void;
  onCancel: () => void;
}

export default function BuildingEditForm({ building, onSave, onCancel }: BuildingEditFormProps) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<CreateBuildingDto>>({
    building_name: building.building_name,
    building_code: building.building_code || '',
    address: building.address || '',
    floor_count: building.floor_count,
    total_units: building.total_units,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const updated = await buildingsService.updateBuilding(building.building_id, formData);
      onSave(updated);
    } catch (err: any) {
      console.error('[BUILDING_EDIT] Error updating building', err);
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
            {t('buildings.buildingName')} *
          </label>
          <input
            type="text"
            required
            value={formData.building_name}
            onChange={(e) => setFormData({ ...formData, building_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('buildings.buildingCode')}
          </label>
          <input
            type="text"
            value={formData.building_code || ''}
            onChange={(e) => setFormData({ ...formData, building_code: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('buildings.buildingCode')}
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('buildings.address')}
          </label>
          <input
            type="text"
            value={formData.address || ''}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('buildings.address')}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('buildings.floors')}
          </label>
          <input
            type="number"
            min="0"
            value={formData.floor_count || ''}
            onChange={(e) => setFormData({ ...formData, floor_count: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('buildings.floors')}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('buildings.units')}
          </label>
          <input
            type="number"
            min="0"
            value={formData.total_units || ''}
            onChange={(e) => setFormData({ ...formData, total_units: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('buildings.units')}
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

