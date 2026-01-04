#!/usr/bin/env python3
"""
Automated test script for Project Wizard debugging
This script simulates the wizard flow via API calls
"""

import requests
import json
import time
import sys
from datetime import datetime

API_URL = 'http://localhost:8000/api/v1'
LOG_ENDPOINT = 'http://127.0.0.1:7242/ingest/98aaee0a-d131-4306-bd8d-703acea62f78'

# Test credentials
TEST_EMAIL = 'admin@tama38.local'
TEST_PASSWORD = 'Admin123!@#'

access_token = None
draft_id = None

def log(message, data=None):
    """Log to debug endpoint"""
    if data is None:
        data = {}
    
    log_data = {
        'location': 'test_wizard_debug.py',
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000),
        'sessionId': 'debug-session',
        'runId': 'run1',
        'hypothesisId': 'TEST'
    }
    
    try:
        requests.post(LOG_ENDPOINT, json=log_data, timeout=0.1).catch(lambda: None)
    except:
        pass
    
    print(f'[TEST] {message}', json.dumps(data, default=str) if data else '')

def api_call(method, endpoint, data=None):
    """Make API call"""
    headers = {
        'Content-Type': 'application/json',
    }
    
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    
    url = f'{API_URL}{endpoint}'
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f'Unsupported method: {method}')
    
    if not response.ok:
        error_data = response.json() if response.content else {}
        raise Exception(f'API Error: {response.status_code} - {error_data}')
    
    return response.json()

def step1_login():
    """Step 1: Login"""
    log('Step 1: Attempting login', {'email': TEST_EMAIL})
    
    try:
        response = api_call('POST', '/auth/login', {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        })
        
        global access_token
        access_token = response['access_token']
        log('Step 1: Login successful', {'hasToken': bool(access_token)})
        return True
    except Exception as error:
        log('Step 1: Login failed', {'error': str(error)})
        raise

def step2_start_wizard():
    """Step 2: Start Wizard"""
    log('Step 2: Starting wizard')
    
    try:
        response = api_call('POST', '/projects/wizard/start')
        global draft_id
        draft_id = response['draft_id']
        log('Step 2: Wizard started', {'draftId': draft_id, 'expiresAt': response.get('expires_at')})
        return True
    except Exception as error:
        log('Step 2: Wizard start failed', {'error': str(error)})
        raise

def step3_save_step1():
    """Step 3: Save Step 1 (Project Info)"""
    log('Step 3: Saving step 1 (Project Info)')
    
    step1_data = {
        'project_name': 'Test Project',
        'project_code': 'TEST-001',
        'project_type': 'TAMA38_1',
        'location_city': 'Tel Aviv',
        'location_address': '123 Test Street',
        'description': 'Test project for debugging',
        'required_majority_percent': 66.67,
        'critical_threshold_percent': 50.0,
        'majority_calc_type': 'HEADCOUNT',
    }
    
    try:
        response = api_call('POST', '/projects/wizard/step/1', {
            'draft_id': draft_id,
            'data': step1_data,
        })
        log('Step 3: Step 1 saved', {'currentStep': response.get('current_step')})
        return True
    except Exception as error:
        log('Step 3: Step 1 save failed', {'error': str(error)})
        raise

def step4_save_step2():
    """Step 4: Save Step 2 (Buildings)"""
    log('Step 4: Saving step 2 (Buildings)')
    
    step2_data = {
        'buildings': [
            {
                'building_name': 'Building A',
                'building_code': 'BLDG-A',
                'address': '123 Test Street',
                'floor_count': 5,
            },
        ],
    }
    
    try:
        response = api_call('POST', '/projects/wizard/step/2', {
            'draft_id': draft_id,
            'data': step2_data,
        })
        log('Step 4: Step 2 saved', {'currentStep': response.get('current_step')})
        return True
    except Exception as error:
        log('Step 4: Step 2 save failed', {'error': str(error)})
        raise

def step5_save_step3():
    """Step 5: Save Step 3 (Units)"""
    log('Step 5: Saving step 3 (Units)')
    
    step3_data = {
        'units': [
            {
                'building_index': 0,
                'unit_number': '101',
                'floor_number': 1,
                'area_sqm': 80.5,
            },
        ],
    }
    
    try:
        response = api_call('POST', '/projects/wizard/step/3', {
            'draft_id': draft_id,
            'data': step3_data,
        })
        log('Step 5: Step 3 saved', {'currentStep': response.get('current_step')})
        return True
    except Exception as error:
        log('Step 5: Step 3 save failed', {'error': str(error)})
        raise

def step6_save_step4():
    """Step 6: Save Step 4 (Owners)"""
    log('Step 6: Saving step 4 (Owners)')
    
    step4_data = {
        'owners': [
            {
                'unit_index': 0,
                'full_name': 'John Doe',
                'phone': '+972501234567',
                'email': 'john@example.com',
                'ownership_share_percent': 100,
            },
        ],
    }
    
    try:
        response = api_call('POST', '/projects/wizard/step/4', {
            'draft_id': draft_id,
            'data': step4_data,
        })
        log('Step 6: Step 4 saved', {'currentStep': response.get('current_step')})
        return True
    except Exception as error:
        log('Step 6: Step 4 save failed', {'error': str(error)})
        raise

def step7_complete_wizard():
    """Step 7: Complete Wizard"""
    log('Step 7: Completing wizard')
    
    try:
        response = api_call('POST', '/projects/wizard/complete', {
            'draft_id': draft_id,
        })
        log('Step 7: Wizard completed', {
            'projectId': response.get('project_id'),
            'buildingsCreated': response.get('buildings_created'),
            'unitsCreated': response.get('units_created'),
            'ownersCreated': response.get('owners_created'),
        })
        return response
    except Exception as error:
        log('Step 7: Wizard completion failed', {'error': str(error)})
        raise

def main():
    """Run the test"""
    print('=' * 60)
    print('Project Wizard Debug Test')
    print('=' * 60)
    
    try:
        log('Test started')
        
        # Step 1: Login
        step1_login()
        time.sleep(0.5)
        
        # Step 2: Start Wizard
        step2_start_wizard()
        time.sleep(0.5)
        
        # Step 3: Save Step 1
        step3_save_step1()
        time.sleep(0.5)
        
        # Step 4: Save Step 2
        step4_save_step2()
        time.sleep(0.5)
        
        # Step 5: Save Step 3
        step5_save_step3()
        time.sleep(0.5)
        
        # Step 6: Save Step 4
        step6_save_step4()
        time.sleep(0.5)
        
        # Step 7: Complete Wizard
        result = step7_complete_wizard()
        
        log('Test completed successfully', {'projectId': result.get('project_id')})
        print('\n✅ All steps completed successfully!')
        print(f"Project ID: {result.get('project_id')}")
        print(f"Buildings: {result.get('buildings_created')}")
        print(f"Units: {result.get('units_created')}")
        print(f"Owners: {result.get('owners_created')}")
        
    except Exception as error:
        log('Test failed', {'error': str(error)})
        print(f'\n❌ Test failed: {error}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

