import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { interactionsService, Interaction, CreateInteractionDto } from '../services/interactions';
import { ownersService, Owner } from '../services/owners';

export default function Interactions() {
  const { t } = useTranslation();
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [owners, setOwners] = useState<Owner[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<CreateInteractionDto>>({
    interaction_type: 'PHONE_CALL',
    interaction_date: new Date().toISOString().split('T')[0],
    call_summary: '',
    sentiment: 'NEUTRAL',
  });

  useEffect(() => {
    loadInteractions();
    loadOwners();
  }, []);

  const loadInteractions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await interactionsService.getRecentInteractions();
      setInteractions(data);
    } catch (err: any) {
      console.error('[INTERACTIONS] Error loading interactions', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const loadOwners = async () => {
    try {
      const data = await ownersService.getOwners();
      setOwners(data);
    } catch (err: any) {
      console.error('[INTERACTIONS] Error loading owners', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.owner_id || !formData.call_summary?.trim()) {
      setError(t('interactions.ownerRequired'));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await interactionsService.createInteraction(formData as CreateInteractionDto);
      setShowForm(false);
      setFormData({
        interaction_type: 'PHONE_CALL',
        interaction_date: new Date().toISOString().split('T')[0],
        call_summary: '',
        sentiment: 'NEUTRAL',
      });
      loadInteractions();
    } catch (err: any) {
      console.error('[INTERACTIONS] Error creating interaction', err);
      setError(err.response?.data?.detail || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment?: string) => {
    const colors: Record<string, string> = {
      POSITIVE: 'bg-green-100 text-green-800',
      NEGATIVE: 'bg-red-100 text-red-800',
      NEUTRAL: 'bg-gray-100 text-gray-800',
    };
    return colors[sentiment || 'NEUTRAL'] || colors.NEUTRAL;
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      PHONE_CALL: t('interactions.phoneCall'),
      IN_PERSON_MEETING: t('interactions.inPersonMeeting'),
      VIDEO_CALL: t('interactions.videoCall'),
      SCHEDULED_MEETING: t('interactions.scheduledMeeting'),
      EMAIL: t('interactions.email'),
      WHATSAPP: t('interactions.whatsapp'),
      SMS: t('interactions.sms'),
    };
    return labels[type] || type;
  };

  if (loading && interactions.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('interactions.loadingInteractions')}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('interactions.title')}</h1>
          <p className="mt-1 text-sm text-gray-500">{t('interactions.subtitle')}</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
        >
          {showForm ? t('common.cancel') : `+ ${t('interactions.logInteraction')}`}
        </button>
      </div>

      {/* Log Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('interactions.logNewInteraction')}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('interactions.owner')} *
                </label>
                <select
                  value={formData.owner_id || ''}
                  onChange={(e) => setFormData({ ...formData, owner_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                >
                  <option value="">{t('interactions.selectOwner')}</option>
                  {owners.map((owner) => (
                    <option key={owner.owner_id} value={owner.owner_id}>
                      {owner.full_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('interactions.interactionType')} *
                </label>
                <select
                  value={formData.interaction_type}
                  onChange={(e) => setFormData({ ...formData, interaction_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                >
                  <option value="PHONE_CALL">{t('interactions.phoneCall')}</option>
                  <option value="IN_PERSON_MEETING">{t('interactions.inPersonMeeting')}</option>
                  <option value="VIDEO_CALL">{t('interactions.videoCall')}</option>
                  <option value="SCHEDULED_MEETING">{t('interactions.scheduledMeeting')}</option>
                  <option value="EMAIL">{t('interactions.email')}</option>
                  <option value="WHATSAPP">{t('interactions.whatsapp')}</option>
                  <option value="SMS">{t('interactions.sms')}</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('interactions.date')} *
                </label>
                <input
                  type="date"
                  value={formData.interaction_date}
                  onChange={(e) => setFormData({ ...formData, interaction_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('interactions.sentiment')}
                </label>
                <select
                  value={formData.sentiment}
                  onChange={(e) => setFormData({ ...formData, sentiment: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                >
                  <option value="POSITIVE">{t('interactions.positive')}</option>
                  <option value="NEUTRAL">{t('interactions.neutral')}</option>
                  <option value="NEGATIVE">{t('interactions.negative')}</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('interactions.callSummary')} * ({t('interactions.mandatory')})
              </label>
              <textarea
                value={formData.call_summary}
                onChange={(e) => setFormData({ ...formData, call_summary: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                rows={4}
                placeholder={t('interactions.summaryPlaceholder')}
                required
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50"
              >
                {loading ? t('interactions.logging') : t('interactions.logInteraction')}
              </button>
            </div>
          </form>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Interactions List */}
      {interactions.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-6xl mb-4">📞</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('interactions.noInteractions')}</h3>
          <p className="text-gray-500">Log your first interaction to get started</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="divide-y divide-gray-200">
            {interactions.map((interaction) => (
              <div key={interaction.log_id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-medium text-gray-900">
                        {getTypeLabel(interaction.interaction_type)}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getSentimentColor(interaction.sentiment)}`}>
                        {interaction.sentiment || 'NEUTRAL'}
                      </span>
                      {interaction.duration_minutes && (
                        <span className="text-sm text-gray-500">
                          {interaction.duration_minutes} min
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{interaction.call_summary}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{new Date(interaction.interaction_date).toLocaleDateString()}</span>
                      {interaction.outcome && (
                        <span>Outcome: {interaction.outcome}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
