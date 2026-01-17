import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { CreateOwnerDto, Owner } from '../services/owners';
import { ownersService } from '../services/owners';

interface OwnerCreateFormProps {
  unitId: string;
  onSave: (newOwner: Owner) => void;
  onCancel: () => void;
}

export default function OwnerCreateForm({ unitId, onSave, onCancel }: OwnerCreateFormProps) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Owner[]>([]);
  const [linkToExisting, setLinkToExisting] = useState(false);
  const [selectedExistingOwner, setSelectedExistingOwner] = useState<string>('');
  const [formData, setFormData] = useState<CreateOwnerDto>({
    unit_id: unitId,
    full_name: '',
    id_number: '',
    phone: '',
    email: '',
    ownership_share_percent: 100,
    preferred_contact_method: 'PHONE',
    preferred_language: 'he',
    link_to_existing: false,
    existing_owner_id: undefined,
  });

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timeoutId = setTimeout(() => {
        searchOwners();
      }, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const searchOwners = async () => {
    try {
      const results = await ownersService.searchOwners(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error('[OWNER_CREATE] Error searching owners', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      const submitData: CreateOwnerDto = {
        ...formData,
        link_to_existing: linkToExisting,
        existing_owner_id: linkToExisting && selectedExistingOwner ? selectedExistingOwner : undefined,
      };
      
      const newOwner = await ownersService.createOwner(submitData);
      onSave(newOwner);
    } catch (err: any) {
      console.error('[OWNER_CREATE] Error creating owner', err);
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

      {/* Link to existing owner option */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="linkToExisting"
          checked={linkToExisting}
          onChange={(e) => {
            setLinkToExisting(e.target.checked);
            if (!e.target.checked) {
              setSelectedExistingOwner('');
              setSearchQuery('');
              setSearchResults([]);
            }
          }}
          className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
        />
        <label htmlFor="linkToExisting" className="ml-2 block text-sm text-gray-700">
          {t('owners.linkToExistingOwner')}
        </label>
      </div>

      {linkToExisting ? (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('owners.searchExistingOwner')}
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            placeholder={t('owners.searchPlaceholder')}
          />
          {searchResults.length > 0 && (
            <div className="mt-2 border border-gray-200 rounded-lg max-h-40 overflow-y-auto">
              {searchResults.map((owner) => (
                <div
                  key={owner.owner_id}
                  onClick={() => {
                    setSelectedExistingOwner(owner.owner_id);
                    setSearchQuery(owner.full_name);
                    setSearchResults([]);
                  }}
                  className={`p-2 cursor-pointer hover:bg-gray-50 ${
                    selectedExistingOwner === owner.owner_id ? 'bg-teal-50' : ''
                  }`}
                >
                  <div className="font-medium">{owner.full_name}</div>
                  {owner.phone_for_contact && (
                    <div className="text-sm text-gray-600">{owner.phone_for_contact}</div>
                  )}
                  {owner.email && (
                    <div className="text-sm text-gray-600">{owner.email}</div>
                  )}
                </div>
              ))}
            </div>
          )}
          {selectedExistingOwner && (
            <div className="mt-2 text-sm text-teal-600">
              {t('owners.selectedOwner')}: {searchQuery}
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.ownerName')} *
              </label>
              <input
                type="text"
                required={!linkToExisting}
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.idNumber')}
              </label>
              <input
                type="text"
                value={formData.id_number || ''}
                onChange={(e) => setFormData({ ...formData, id_number: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.phone')}
              </label>
              <input
                type="tel"
                value={formData.phone || ''}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="+972-50-123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.email')}
              </label>
              <input
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.ownershipShare')} (%) *
              </label>
              <input
                type="number"
                required
                min="0"
                max="100"
                step="0.01"
                value={formData.ownership_share_percent}
                onChange={(e) => setFormData({ ...formData, ownership_share_percent: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.preferredContactMethod')}
              </label>
              <select
                value={formData.preferred_contact_method || 'PHONE'}
                onChange={(e) => setFormData({ ...formData, preferred_contact_method: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              >
                <option value="PHONE">{t('owners.contactMethods.PHONE')}</option>
                <option value="EMAIL">{t('owners.contactMethods.EMAIL')}</option>
                <option value="WHATSAPP">{t('owners.contactMethods.WHATSAPP')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('owners.preferredLanguage')}
              </label>
              <select
                value={formData.preferred_language || 'he'}
                onChange={(e) => setFormData({ ...formData, preferred_language: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              >
                <option value="he">{t('common.languages.he')}</option>
                <option value="en">{t('common.languages.en')}</option>
                <option value="ar">{t('common.languages.ar')}</option>
                <option value="ru">{t('common.languages.ru')}</option>
              </select>
            </div>
          </div>
        </>
      )}

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
          disabled={loading || (linkToExisting && !selectedExistingOwner)}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-50"
        >
          {loading ? t('common.saving') : t('common.save')}
        </button>
      </div>
    </form>
  );
}

