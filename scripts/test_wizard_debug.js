/**
 * Automated test script for Project Wizard debugging
 * This script simulates the wizard flow via API calls
 */

const API_URL = 'http://localhost:8000/api/v1';
const LOG_ENDPOINT = 'http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78';

// Test credentials
const TEST_EMAIL = 'admin@tama38.local';
const TEST_PASSWORD = 'Admin123!@#';

let accessToken = null;
let draftId = null;

async function log(message, data = {}) {
  const logData = {
    location: 'test_wizard_debug.js',
    message,
    data,
    timestamp: Date.now(),
    sessionId: 'debug-session',
    runId: 'run1',
    hypothesisId: 'TEST'
  };
  
  try {
    await fetch(LOG_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData)
    }).catch(() => {});
  } catch (e) {
    // Ignore log errors
  }
  
  console.log(`[TEST] ${message}`, data);
}

async function apiCall(method, endpoint, data = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  const options = {
    method,
    headers,
  };
  
  if (data) {
    options.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, options);
  const responseData = await response.json();
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} - ${JSON.stringify(responseData)}`);
  }
  
  return responseData;
}

async function step1_login() {
  await log('Step 1: Attempting login', { email: TEST_EMAIL });
  
  try {
    const response = await apiCall('POST', '/auth/login', {
      email: TEST_EMAIL,
      password: TEST_PASSWORD,
    });
    
    accessToken = response.access_token;
    await log('Step 1: Login successful', { hasToken: !!accessToken });
    return true;
  } catch (error) {
    await log('Step 1: Login failed', { error: error.message });
    throw error;
  }
}

async function step2_startWizard() {
  await log('Step 2: Starting wizard');
  
  try {
    const response = await apiCall('POST', '/projects/wizard/start');
    draftId = response.draft_id;
    await log('Step 2: Wizard started', { draftId, expiresAt: response.expires_at });
    return true;
  } catch (error) {
    await log('Step 2: Wizard start failed', { error: error.message });
    throw error;
  }
}

async function step3_saveStep1() {
  await log('Step 3: Saving step 1 (Project Info)');
  
  const step1Data = {
    project_name: 'Test Project',
    project_code: 'TEST-001',
    project_type: 'TAMA38_1',
    location_city: 'Tel Aviv',
    location_address: '123 Test Street',
    description: 'Test project for debugging',
    required_majority_percent: 66.67,
    critical_threshold_percent: 50.0,
    majority_calc_type: 'HEADCOUNT',
  };
  
  try {
    const response = await apiCall('POST', '/projects/wizard/step/1', {
      draft_id: draftId,
      data: step1Data,
    });
    await log('Step 3: Step 1 saved', { currentStep: response.current_step });
    return true;
  } catch (error) {
    await log('Step 3: Step 1 save failed', { error: error.message });
    throw error;
  }
}

async function step4_saveStep2() {
  await log('Step 4: Saving step 2 (Buildings)');
  
  const step2Data = {
    buildings: [
      {
        building_name: 'Building A',
        building_code: 'BLDG-A',
        address: '123 Test Street',
        floor_count: 5,
      },
    ],
  };
  
  try {
    const response = await apiCall('POST', '/projects/wizard/step/2', {
      draft_id: draftId,
      data: step2Data,
    });
    await log('Step 4: Step 2 saved', { currentStep: response.current_step });
    return true;
  } catch (error) {
    await log('Step 4: Step 2 save failed', { error: error.message });
    throw error;
  }
}

async function step5_saveStep3() {
  await log('Step 5: Saving step 3 (Units)');
  
  const step3Data = {
    units: [
      {
        building_index: 0,
        unit_number: '101',
        floor_number: 1,
        area_sqm: 80.5,
      },
    ],
  };
  
  try {
    const response = await apiCall('POST', '/projects/wizard/step/3', {
      draft_id: draftId,
      data: step3Data,
    });
    await log('Step 5: Step 3 saved', { currentStep: response.current_step });
    return true;
  } catch (error) {
    await log('Step 5: Step 3 save failed', { error: error.message });
    throw error;
  }
}

async function step6_saveStep4() {
  await log('Step 6: Saving step 4 (Owners)');
  
  const step4Data = {
    owners: [
      {
        unit_index: 0,
        full_name: 'John Doe',
        phone: '+972501234567',
        email: 'john@example.com',
        ownership_share_percent: 100,
      },
    ],
  };
  
  try {
    const response = await apiCall('POST', '/projects/wizard/step/4', {
      draft_id: draftId,
      data: step4Data,
    });
    await log('Step 6: Step 4 saved', { currentStep: response.current_step });
    return true;
  } catch (error) {
    await log('Step 6: Step 4 save failed', { error: error.message });
    throw error;
  }
}

async function step7_completeWizard() {
  await log('Step 7: Completing wizard');
  
  try {
    const response = await apiCall('POST', '/projects/wizard/complete', {
      draft_id: draftId,
    });
    await log('Step 7: Wizard completed', {
      projectId: response.project_id,
      buildingsCreated: response.buildings_created,
      unitsCreated: response.units_created,
      ownersCreated: response.owners_created,
    });
    return response;
  } catch (error) {
    await log('Step 7: Wizard completion failed', { error: error.message });
    throw error;
  }
}

async function runTest() {
  console.log('='.repeat(60));
  console.log('Project Wizard Debug Test');
  console.log('='.repeat(60));
  
  try {
    await log('Test started');
    
    // Step 1: Login
    await step1_login();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 2: Start Wizard
    await step2_startWizard();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 3: Save Step 1
    await step3_saveStep1();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 4: Save Step 2
    await step4_saveStep2();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 5: Save Step 3
    await step5_saveStep3();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 6: Save Step 4
    await step6_saveStep4();
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 7: Complete Wizard
    const result = await step7_completeWizard();
    
    await log('Test completed successfully', { projectId: result.project_id });
    console.log('\n✅ All steps completed successfully!');
    console.log(`Project ID: ${result.project_id}`);
    console.log(`Buildings: ${result.buildings_created}`);
    console.log(`Units: ${result.units_created}`);
    console.log(`Owners: ${result.owners_created}`);
    
  } catch (error) {
    await log('Test failed', { error: error.message, stack: error.stack });
    console.error('\n❌ Test failed:', error.message);
    console.error('Stack:', error.stack);
    process.exit(1);
  }
}

// Run the test
runTest().catch(console.error);

