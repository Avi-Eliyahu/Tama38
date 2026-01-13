import { useEffect, useState } from 'react';
import { reportsService, ReportType, ReportRequest } from '../services/reports';
import { projectsService, Project } from '../services/projects';
import { buildingsService, Building } from '../services/buildings';
import { authService } from '../services/auth';

export default function Reports() {
  const [reportTypes, setReportTypes] = useState<ReportType[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [selectedReportType, setSelectedReportType] = useState<string>('');
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'excel'>('pdf');
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [selectedBuildingId, setSelectedBuildingId] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const currentUser = authService.getCurrentUserSync();
  void currentUser; // Used for future role-based filtering

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadBuildings(selectedProjectId);
    } else {
      setBuildings([]);
      setSelectedBuildingId('');
    }
  }, [selectedProjectId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [reportTypesData, projectsData] = await Promise.all([
        reportsService.getReportTypes(),
        projectsService.getProjects(),
      ]);
      
      setReportTypes(reportTypesData.report_types);
      setProjects(projectsData);
    } catch (err: any) {
      console.error('[REPORTS] Error loading data', err);
      setError(err.response?.data?.detail || 'Failed to load reports data');
    } finally {
      setLoading(false);
    }
  };

  const loadBuildings = async (projectId: string) => {
    try {
      const data = await buildingsService.getBuildings(projectId);
      setBuildings(data);
    } catch (err: any) {
      console.error('[REPORTS] Error loading buildings', err);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedReportType) {
      setError('Please select a report type');
      return;
    }

    try {
      setGenerating(true);
      setError(null);

      const request: ReportRequest = {
        report_type: selectedReportType as ReportRequest['report_type'],
        format: selectedFormat,
        project_id: selectedProjectId || undefined,
        building_id: selectedBuildingId || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      };

      await reportsService.downloadReport(request);
    } catch (err: any) {
      console.error('[REPORTS] Error generating report', err);
      setError(err.response?.data?.detail || 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const selectedReport = reportTypes.find((rt) => rt.id === selectedReportType);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading reports...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate and download reports in PDF or Excel format
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Report Generation Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Report</h2>

        <div className="space-y-6">
          {/* Report Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Report Type <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reportTypes.map((reportType) => (
                <div
                  key={reportType.id}
                  onClick={() => setSelectedReportType(reportType.id)}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    selectedReportType === reportType.id
                      ? 'border-teal-500 bg-teal-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {reportType.name}
                      </h3>
                      <p className="text-sm text-gray-600">{reportType.description}</p>
                    </div>
                    {selectedReportType === reportType.id && (
                      <div className="text-teal-500 text-xl">✓</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Format Selection */}
          {selectedReport && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Export Format
              </label>
              <div className="flex gap-4">
                {selectedReport.formats.map((format) => (
                  <label
                    key={format}
                    className={`flex items-center px-4 py-2 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedFormat === format
                        ? 'border-teal-500 bg-teal-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="format"
                      value={format}
                      checked={selectedFormat === format}
                      onChange={(e) => setSelectedFormat(e.target.value as 'pdf' | 'excel')}
                      className="mr-2"
                    />
                    <span className="font-medium text-gray-900 uppercase">{format}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Filters */}
          {selectedReport && (
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Filters (Optional)</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Project Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project
                  </label>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  >
                    <option value="">All Projects</option>
                    {projects.map((project) => (
                      <option key={project.project_id} value={project.project_id}>
                        {project.project_name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Building Filter */}
                {selectedProjectId && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Building
                    </label>
                    <select
                      value={selectedBuildingId}
                      onChange={(e) => setSelectedBuildingId(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                    >
                      <option value="">All Buildings</option>
                      {buildings.map((building) => (
                        <option key={building.building_id} value={building.building_id}>
                          {building.building_name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Date Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Generate Button */}
          <div className="flex justify-end pt-4 border-t border-gray-200">
            <button
              onClick={handleGenerateReport}
              disabled={!selectedReportType || generating}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                !selectedReportType || generating
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-teal-600 text-white hover:bg-teal-700'
              }`}
            >
              {generating ? (
                <span className="flex items-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Generating...
                </span>
              ) : (
                `Generate ${selectedFormat.toUpperCase()} Report`
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Report Types Info */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Reports</h2>
        <div className="space-y-4">
          {reportTypes.map((reportType) => (
            <div key={reportType.id} className="border-b border-gray-200 pb-4 last:border-0">
              <h3 className="font-semibold text-gray-900 mb-1">{reportType.name}</h3>
              <p className="text-sm text-gray-600 mb-2">{reportType.description}</p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Formats:</span>
                {reportType.formats.map((format) => (
                  <span
                    key={format}
                    className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium uppercase"
                  >
                    {format}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

