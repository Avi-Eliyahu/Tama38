import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CreateUnitDto, Unit } from '../services/units';
import { unitsService } from '../services/units';
import { CreateOwnerDto, ownersService } from '../services/owners';

interface OwnerDraft {
  full_name: string;
  id_number: string;
  phone: string;
  email: string;
  ownership_share_percent: number;
}

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
    area_sqm: undefined,
  });
  const [owners, setOwners] = useState<OwnerDraft[]>([
    { full_name: '', id_number: '', phone: '', email: '', ownership_share_percent: 100 },
  ]);

  const updateOwner = (index: number, updates: Partial<OwnerDraft>) => {
    setOwners((prev) =>
      prev.map((owner, i) => (i === index ? { ...owner, ...updates } : owner)),
    );
  };

  const addOwner = () => {
    setOwners((prev) => [
      ...prev,
      { full_name: '', id_number: '', phone: '', email: '', ownership_share_percent: 100 },
    ]);
  };

  const removeOwner = (index: number) => {
    setOwners((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      if (!formData.unit_number || !formData.floor_number || !formData.area_sqm) {
        setError(t('units.validation.requiredFields'));
        return;
      }

      const validOwners = owners
        .map((owner) => ({
          ...owner,
          full_name: owner.full_name.trim(),
          id_number: owner.id_number.trim(),
          phone: owner.phone.trim(),
          email: owner.email.trim(),
        }))
        .filter(
          (owner) =>
            owner.full_name || owner.id_number || owner.phone || owner.email,
        );

      for (const owner of validOwners) {
        if (!owner.full_name) {
          setError(t('owners.validation.nameRequired'));
          return;
        }
        if (!owner.id_number && !owner.phone) {
          setError(t('owners.validation.idOrPhoneRequired'));
          return;
        }
      }

      const newUnit = await unitsService.createUnit(formData);

      if (validOwners.length > 0) {
        const ownerRequests = validOwners.map((owner) =>
          ownersService.createOwner({
            unit_id: newUnit.unit_id,
            full_name: owner.full_name,
            id_number: owner.id_number || undefined,
            phone: owner.phone || undefined,
            email: owner.email || undefined,
            ownership_share_percent: owner.ownership_share_percent,
          } as CreateOwnerDto),
        );
        await Promise.all(ownerRequests);
      }
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
            {t('units.fields.unitNumber')} *
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
            {t('units.fields.floorNumber')} *
          </label>
          <input
            type="number"
            min="0"
            required
            value={formData.floor_number ?? ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                floor_number: e.target.value ? parseInt(e.target.value, 10) : undefined,
              })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('units.placeholders.floorNumber')}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('units.fields.area')} (m²) *
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            required
            value={formData.area_sqm ?? ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                area_sqm: e.target.value ? parseFloat(e.target.value) : undefined,
              })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('units.placeholders.area')}
          />
        </div>
      </div>

      <div className="border-t border-gray-200 pt-4 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-base font-semibold text-gray-900">
            {t('owners.sectionTitle')}
          </h4>
          <button
            type="button"
            onClick={addOwner}
            className="px-3 py-1.5 text-sm rounded-lg bg-teal-600 text-white hover:bg-teal-700 transition-colors"
          >
            + {t('owners.addOwner')}
          </button>
        </div>

        {owners.map((owner, index) => (
          <div key={`owner-${index}`} className="space-y-3 rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">
                {t('owners.ownerLabel')} {index + 1}
              </span>
              {owners.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeOwner(index)}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  {t('common.delete')}
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('owners.ownerName')} *
                </label>
                <input
                  type="text"
                  value={owner.full_name}
                  onChange={(e) => updateOwner(index, { full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('owners.idNumber')}
                </label>
                <input
                  type="text"
                  value={owner.id_number}
                  onChange={(e) => updateOwner(index, { id_number: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('owners.phone')}
                </label>
                <input
                  type="tel"
                  value={owner.phone}
                  onChange={(e) => updateOwner(index, { phone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('owners.email')}
                </label>
                <input
                  type="email"
                  value={owner.email}
                  onChange={(e) => updateOwner(index, { email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('owners.ownershipShare')} (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={owner.ownership_share_percent}
                  onChange={(e) =>
                    updateOwner(index, {
                      ownership_share_percent: e.target.value
                        ? parseFloat(e.target.value)
                        : 0,
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
            </div>

            <p className="text-xs text-gray-500">
              {t('owners.validation.idOrPhoneNote')}
            </p>
          </div>
        ))}
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

