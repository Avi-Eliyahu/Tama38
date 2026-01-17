import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CreateUnitDto, Unit } from '../services/units';
import { unitsService } from '../services/units';

interface UnitCreateFormProps {
  buildingId: string;
  onSave: (newUnit: Unit) => void;
  onCancel: () => void;
}

export default function UnitCreateForm({ buildingId, onSave, onCancel }: UnitCreateFormProps) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CreateUnitDto>({
    building_id: buildingId,
    floor_number: undefined,
    unit_number: '',
    unit_code: '',
    area_sqm: undefined,
    room_count: undefined,
    estimated_value_ils: undefined,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const newUnit = await unitsService.createUnit(formData);
      onSave(newUnit);
    } catch (err: any) {
      console.error('[UNIT_CREATE] Error creating unit', err);
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
            {t('units.unitNumber')} *
          </label>
          <input
            type="text"
            required
            value={formData.unit_number}
            onChange={(e) => setFormData({ ...formData, unit_number: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder="101"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('units.floorNumber')}
          </label>
          <input
            type="number"
            min="0"
            value={formData.floor_number || ''}
            onChange={(e) => setFormData({ ...formData, floor_number: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder="1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('units.unitCode')}
          </label>
          <input
            type="text"
            value={formData.unit_code || ''}
            onChange={(e) => setFormData({ ...formData, unit_code: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('units.unitCode')}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('units.area')} (m²)
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={formData.area_sqm || ''}
            onChange={(e) => setFormData({ ...formData, area_sqm: e.target.value ? parseFloat(e.target.value) : undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder="65.0"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('units.roomCount')}
          </label>
          <input
            type="number"
            min="0"
            value={formData.room_count || ''}
            onChange={(e) => setFormData({ ...formData, room_count: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder="3"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('units.estimatedValue')} (ILS)
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={formData.estimated_value_ils || ''}
            onChange={(e) => setFormData({ ...formData, estimated_value_ils: e.target.value ? parseFloat(e.target.value) : undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder="1500000"
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

