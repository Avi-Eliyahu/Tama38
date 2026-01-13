import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { wizardService } from '../services/wizard';

const steps = [
  { number: 1, title: 'Project Info', description: 'Basic project information' },
  { number: 2, title: 'Buildings', description: 'Add buildings to the project' },
  { number: 3, title: 'Units', description: 'Define units for each building' },
  { number: 4, title: 'Owners', description: 'Add owners to units' },
  { number: 5, title: 'Review', description: 'Review and complete' },
];

interface Building {
  building_name: string;
  building_code?: string;
  address?: string;
  floor_count?: number;
  structure_type?: string;
}

interface Unit {
  building_index: number;
  unit_number: string;
  floor_number?: number;
  area_sqm?: number;
  room_count?: number;
}

interface Owner {
  unit_index: number;
  full_name: string;
  id_number?: string;
  phone?: string; // Note: Wizard API accepts 'phone' but maps to 'phone_for_contact' in database
  email?: string;
  ownership_share_percent: number;
  preferred_contact_method?: string;
  preferred_language?: string;
}

export default function ProjectWizard() {
  const navigate = useNavigate();
  const [draftId, setDraftId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Project Info
  const [step1Data, setStep1Data] = useState({
    project_name: '',
    project_code: '',
    project_type: 'TAMA38_1',
    location_city: '',
    location_address: '',
    description: '',
    required_majority_percent: 66.67,
    critical_threshold_percent: 50.0,
    majority_calc_type: 'HEADCOUNT',
    launch_date: '',
    estimated_completion_date: '',
  });

  // Step 2: Buildings
  const [buildings, setBuildings] = useState<Building[]>([]);

  // Step 3: Units
  const [units, setUnits] = useState<Unit[]>([]);

  // Step 4: Owners
  const [owners, setOwners] = useState<Owner[]>([]);

  // Initialize wizard on mount
  useEffect(() => {
    const initWizard = async () => {      try {        const response = await wizardService.startWizard();        setDraftId(response.draft_id);
        console.log('[WIZARD] Started with draft_id:', response.draft_id);
      } catch (err: any) {        console.error('[WIZARD] Error starting wizard', err);
        setError('Failed to initialize wizard. Please try again.');
      }
    };
    initWizard();
  }, []);

  const handleStep1Change = (field: string, value: any) => {
    setStep1Data((prev) => ({ ...prev, [field]: value }));
  };

  const handleNext = async () => {    if (!draftId) {      setError('Wizard not initialized');
      return;
    }

    try {
      setSaving(true);
      setError(null);      // Save current step before moving forward
      if (currentStep === 1) {        await wizardService.saveStep1(draftId, step1Data);      } else if (currentStep === 2) {
        if (buildings.length === 0) {          setError('Please add at least one building');
          return;
        }        await wizardService.saveStep2(draftId, { buildings });      } else if (currentStep === 3) {
        if (units.length === 0) {          setError('Please add at least one unit');
          return;
        }        await wizardService.saveStep3(draftId, { units });      } else if (currentStep === 4) {
        if (owners.length === 0) {          setError('Please add at least one owner');
          return;
        }
        // Validate ownership shares sum to 100% per unit
        const unitOwnershipMap = new Map<number, number>();
        owners.forEach((owner) => {
          const current = unitOwnershipMap.get(owner.unit_index) || 0;
          unitOwnershipMap.set(owner.unit_index, current + owner.ownership_share_percent);
        });
        for (const [unitIndex, total] of unitOwnershipMap.entries()) {
          if (Math.abs(total - 100) > 0.01) {            setError(`Unit ${unitIndex + 1} ownership shares must total 100% (currently ${total.toFixed(2)}%)`);
            return;
          }
        }        await wizardService.saveStep4(draftId, { owners });      }      setCurrentStep(currentStep + 1);    } catch (err: any) {      console.error('[WIZARD] Error saving step', err);
      setError(err.response?.data?.detail || 'Failed to save step');    } finally {      setSaving(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError(null);
    }
  };

  const handleSubmit = async () => {    if (!draftId) {      setError('Wizard not initialized');
      return;
    }

    try {
      setLoading(true);
      setError(null);      const result = await wizardService.completeWizard(draftId);      console.log('[WIZARD] Project created', result);
      navigate(`/projects/${result.project_id}`);
    } catch (err: any) {      console.error('[WIZARD] Error completing wizard', err);
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const addBuilding = () => {
    setBuildings([...buildings, { building_name: '', building_code: '', address: '' }]);
  };

  const updateBuilding = (index: number, field: keyof Building, value: any) => {
    const updated = [...buildings];
    updated[index] = { ...updated[index], [field]: value };
    setBuildings(updated);
  };

  const removeBuilding = (index: number) => {
    setBuildings(buildings.filter((_, i) => i !== index));
    // Also remove units and owners for this building
    setUnits(units.filter((u) => u.building_index !== index));
    // Update building indices for remaining units
    setUnits((prev) =>
      prev.map((u) => {
        if (u.building_index > index) {
          return { ...u, building_index: u.building_index - 1 };
        }
        return u;
      })
    );
  };

  const addUnit = () => {
    if (buildings.length === 0) {
      setError('Please add buildings first');
      return;
    }
    setUnits([...units, { building_index: 0, unit_number: '', floor_number: undefined, area_sqm: undefined }]);
  };

  const updateUnit = (index: number, field: keyof Unit, value: any) => {
    const updated = [...units];
    updated[index] = { ...updated[index], [field]: value };
    setUnits(updated);
  };

  const removeUnit = (index: number) => {
    setUnits(units.filter((_, i) => i !== index));
    // Also remove owners for this unit
    setOwners(owners.filter((o) => o.unit_index !== index));
    // Update unit indices for remaining owners
    setOwners((prev) =>
      prev.map((o) => {
        if (o.unit_index > index) {
          return { ...o, unit_index: o.unit_index - 1 };
        }
        return o;
      })
    );
  };

  const addOwner = () => {
    if (units.length === 0) {
      setError('Please add units first');
      return;
    }
    setOwners([...owners, { unit_index: 0, full_name: '', ownership_share_percent: 100 }]);
  };

  const updateOwner = (index: number, field: keyof Owner, value: any) => {
    const updated = [...owners];
    updated[index] = { ...updated[index], [field]: value };
    setOwners(updated);
  };

  const removeOwner = (index: number) => {
    setOwners(owners.filter((_, i) => i !== index));
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Name *
              </label>
              <input
                type="text"
                value={step1Data.project_name}
                onChange={(e) => handleStep1Change('project_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="e.g., Tel Aviv Central Renewal"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Code *
              </label>
              <input
                type="text"
                value={step1Data.project_code}
                onChange={(e) => handleStep1Change('project_code', e.target.value.toUpperCase())}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="e.g., TLV-CENTRAL-001"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Type *
              </label>
              <select
                value={step1Data.project_type}
                onChange={(e) => handleStep1Change('project_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              >
                <option value="TAMA38_1">TAMA38 Type 1</option>
                <option value="TAMA38_2">TAMA38 Type 2</option>
                <option value="PINUI_BINUI">Pinui Binui</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={step1Data.location_city}
                  onChange={(e) => handleStep1Change('location_city', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="e.g., Tel Aviv"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Required Majority %
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={step1Data.required_majority_percent}
                  onChange={(e) => handleStep1Change('required_majority_percent', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
              <textarea
                value={step1Data.location_address}
                onChange={(e) => handleStep1Change('location_address', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                rows={3}
                placeholder="Full address"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Calculation Type
              </label>
              <select
                value={step1Data.majority_calc_type}
                onChange={(e) => handleStep1Change('majority_calc_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              >
                <option value="HEADCOUNT">Headcount</option>
                <option value="AREA">Area</option>
                <option value="WEIGHTED">Weighted</option>
                <option value="CUSTOM">Custom</option>
              </select>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">Add buildings to this project</p>
              <button
                onClick={addBuilding}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
              >
                + Add Building
              </button>
            </div>
            {buildings.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No buildings added yet. Click "Add Building" to get started.
              </div>
            ) : (
              <div className="space-y-4">
                {buildings.map((building, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <h4 className="font-medium text-gray-900">Building {index + 1}</h4>
                      <button
                        onClick={() => removeBuilding(index)}
                        className="text-red-600 hover:text-red-700 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Building Name *</label>
                        <input
                          type="text"
                          value={building.building_name}
                          onChange={(e) => updateBuilding(index, 'building_name', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                          placeholder="e.g., Building A"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Building Code</label>
                        <input
                          type="text"
                          value={building.building_code || ''}
                          onChange={(e) => updateBuilding(index, 'building_code', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                          placeholder="e.g., BLDG-A"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Address</label>
                        <input
                          type="text"
                          value={building.address || ''}
                          onChange={(e) => updateBuilding(index, 'address', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Floor Count</label>
                        <input
                          type="number"
                          value={building.floor_count || ''}
                          onChange={(e) => updateBuilding(index, 'floor_count', e.target.value ? parseInt(e.target.value) : undefined)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">Add units to buildings</p>
              <button
                onClick={addUnit}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
              >
                + Add Unit
              </button>
            </div>
            {units.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No units added yet. Click "Add Unit" to get started.
              </div>
            ) : (
              <div className="space-y-4">
                {units.map((unit, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <h4 className="font-medium text-gray-900">Unit {index + 1}</h4>
                      <button
                        onClick={() => removeUnit(index)}
                        className="text-red-600 hover:text-red-700 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Building *</label>
                        <select
                          value={unit.building_index}
                          onChange={(e) => updateUnit(index, 'building_index', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        >
                          {buildings.map((b, i) => (
                            <option key={i} value={i}>
                              {b.building_name || `Building ${i + 1}`}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Unit Number *</label>
                        <input
                          type="text"
                          value={unit.unit_number}
                          onChange={(e) => updateUnit(index, 'unit_number', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                          placeholder="e.g., 101"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Floor Number</label>
                        <input
                          type="number"
                          value={unit.floor_number || ''}
                          onChange={(e) => updateUnit(index, 'floor_number', e.target.value ? parseInt(e.target.value) : undefined)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Area (sqm)</label>
                        <input
                          type="number"
                          step="0.01"
                          value={unit.area_sqm || ''}
                          onChange={(e) => updateUnit(index, 'area_sqm', e.target.value ? parseFloat(e.target.value) : undefined)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">Add owners to units</p>
              <button
                onClick={addOwner}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
              >
                + Add Owner
              </button>
            </div>
            {owners.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No owners added yet. Click "Add Owner" to get started.
              </div>
            ) : (
              <div className="space-y-4">
                {owners.map((owner, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <h4 className="font-medium text-gray-900">Owner {index + 1}</h4>
                      <button
                        onClick={() => removeOwner(index)}
                        className="text-red-600 hover:text-red-700 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Unit *</label>
                        <select
                          value={owner.unit_index}
                          onChange={(e) => updateOwner(index, 'unit_index', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        >
                          {units.map((u, i) => (
                            <option key={i} value={i}>
                              {buildings[u.building_index]?.building_name || `Building ${u.building_index + 1}`} - Unit {u.unit_number}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Full Name *</label>
                        <input
                          type="text"
                          value={owner.full_name}
                          onChange={(e) => updateOwner(index, 'full_name', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Phone</label>
                        <input
                          type="tel"
                          value={owner.phone || ''}
                          onChange={(e) => updateOwner(index, 'phone', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Email</label>
                        <input
                          type="email"
                          value={owner.email || ''}
                          onChange={(e) => updateOwner(index, 'email', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Ownership Share % *</label>
                        <input
                          type="number"
                          step="0.01"
                          value={owner.ownership_share_percent}
                          onChange={(e) => updateOwner(index, 'ownership_share_percent', parseFloat(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 text-sm"
                          required
                        />
                      </div>
                    </div>
                  </div>
                ))}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
                  <strong>Note:</strong> Ownership shares for each unit must total 100%.
                </div>
              </div>
            )}
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Review Project Details</h3>
            
            {/* Project Info */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="font-medium text-gray-900 mb-2">Project Information</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Project Name:</span>
                  <span className="font-medium">{step1Data.project_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Project Code:</span>
                  <span className="font-medium">{step1Data.project_code}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-medium">{step1Data.project_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Majority Required:</span>
                  <span className="font-medium">{step1Data.required_majority_percent}%</span>
                </div>
              </div>
            </div>

            {/* Buildings Summary */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="font-medium text-gray-900 mb-2">Buildings ({buildings.length})</h4>
              {buildings.map((b, i) => (
                <div key={i} className="text-sm">
                  {i + 1}. {b.building_name} {b.building_code && `(${b.building_code})`}
                </div>
              ))}
            </div>

            {/* Units Summary */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="font-medium text-gray-900 mb-2">Units ({units.length})</h4>
              {units.map((u, i) => (
                <div key={i} className="text-sm">
                  {i + 1}. {buildings[u.building_index]?.building_name || `Building ${u.building_index + 1}`} - Unit {u.unit_number}
                </div>
              ))}
            </div>

            {/* Owners Summary */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="font-medium text-gray-900 mb-2">Owners ({owners.length})</h4>
              {owners.map((o, i) => (
                <div key={i} className="text-sm">
                  {i + 1}. {o.full_name} - {buildings[units[o.unit_index]?.building_index]?.building_name || 'Building'} Unit {units[o.unit_index]?.unit_number} ({o.ownership_share_percent}%)
                </div>
              ))}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
              <strong>Ready to create?</strong> Click "Complete" below to create the project with all buildings, units, and owners.
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (!draftId) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Initializing wizard...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Create New Project</h1>
        <p className="mt-1 text-sm text-gray-500">Step-by-step project creation wizard</p>
      </div>

      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    currentStep >= step.number
                      ? 'bg-teal-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step.number}
                </div>
                <div className="mt-2 text-center">
                  <div
                    className={`text-xs font-medium ${
                      currentStep >= step.number ? 'text-teal-600' : 'text-gray-500'
                    }`}
                  >
                    {step.title}
                  </div>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`h-1 flex-1 mx-2 ${
                    currentStep > step.number ? 'bg-teal-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {steps[currentStep - 1].title}
          </h2>
          <p className="text-sm text-gray-500">{steps[currentStep - 1].description}</p>
        </div>

        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleBack}
          disabled={currentStep === 1 || saving || loading}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Back
        </button>
        <div className="flex gap-3">
          {currentStep < steps.length ? (
            <button
              onClick={handleNext}
              disabled={saving || loading}
              className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Next'}
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Complete'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
