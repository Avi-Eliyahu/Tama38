#!/usr/bin/env python3
"""
E2E Test Script for Stage 17: Mobile Web Signing Interface
Tests the complete signing workflow from initiation to approval
"""
import requests
import json
import sys
from uuid import uuid4

API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@tama38.local"
PASSWORD = "Admin123!@#"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)

def print_success(message):
    print(f"[OK] {message}")

def print_error(message):
    print(f"[ERROR] {message}")
    sys.exit(1)

def main():
    print("\n" + "="*60)
    print("TAMA38 Stage 17: Signing Workflow E2E Test")
    print("="*60)
    
    # Step 1: Login
    print_step(1, "Login as Admin")
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print_error(f"Login failed: {response.status_code} - {response.text}")
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_success(f"Logged in successfully")
    
    # Step 2: Create a project (if needed)
    print_step(2, "Create Test Project")
    project_data = {
        "project_name": f"Signing Test Project {uuid4().hex[:8]}",
        "project_code": f"SIGN_TEST_{uuid4().hex[:8]}",
        "project_type": "TAMA38_1",
        "location_city": "Tel Aviv",
        "required_majority_percent": 75.0,
        "critical_threshold_percent": 50.0,
        "majority_calc_type": "HEADCOUNT"
    }
    response = requests.post(f"{API_URL}/projects", json=project_data, headers=headers)
    if response.status_code != 201:
        print_error(f"Project creation failed: {response.status_code} - {response.text}")
    
    project_id = response.json()["project_id"]
    print_success(f"Project created: {project_id}")
    
    # Step 3: Create a building
    print_step(3, "Create Test Building")
    building_data = {
        "project_id": project_id,
        "building_name": "Test Building",
        "building_code": "TB001",
        "address": "123 Test St"
    }
    response = requests.post(f"{API_URL}/buildings", json=building_data, headers=headers)
    if response.status_code != 201:
        print_error(f"Building creation failed: {response.status_code} - {response.text}")
    
    building_id = response.json()["building_id"]
    print_success(f"Building created: {building_id}")
    
    # Step 4: Create a unit
    print_step(4, "Create Test Unit")
    unit_data = {
        "building_id": building_id,
        "unit_number": "1",
        "floor_number": 1,
        "area_sqm": 80.0
    }
    response = requests.post(f"{API_URL}/units", json=unit_data, headers=headers)
    if response.status_code != 201:
        print_error(f"Unit creation failed: {response.status_code} - {response.text}")
    
    unit_id = response.json()["unit_id"]
    print_success(f"Unit created: {unit_id}")
    
    # Step 5: Create an owner
    print_step(5, "Create Test Owner")
    owner_data = {
        "unit_id": unit_id,
        "full_name": "Test Owner",
        "phone": "+972501234567",
        "email": "testowner@example.com",
        "ownership_share_percent": 100.0
    }
    response = requests.post(f"{API_URL}/owners", json=owner_data, headers=headers)
    if response.status_code != 201:
        print_error(f"Owner creation failed: {response.status_code} - {response.text}")
    
    owner_id = response.json()["owner_id"]
    print_success(f"Owner created: {owner_id}")
    
    # Step 6: Upload a document
    print_step(6, "Upload Test Document")
    # Create a dummy PDF file content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
    
    files = {
        "file": ("test_contract.pdf", pdf_content, "application/pdf")
    }
    form_data = {
        "owner_id": owner_id,
        "document_type": "CONTRACT",
        "description": "Test contract for signing"
    }
    response = requests.post(
        f"{API_URL}/documents/upload",
        files=files,
        data=form_data,
        headers=headers
    )
    if response.status_code != 201:
        print_error(f"Document upload failed: {response.status_code} - {response.text}")
    
    document_id = response.json()["document_id"]
    print_success(f"Document uploaded: {document_id}")
    
    # Step 7: Initiate signature
    print_step(7, "Initiate Signature Process")
    signature_data = {
        "owner_id": owner_id,
        "document_id": document_id
    }
    response = requests.post(
        f"{API_URL}/approvals/signatures/initiate",
        json=signature_data,
        headers=headers
    )
    if response.status_code != 201:
        print_error(f"Signature initiation failed: {response.status_code} - {response.text}")
    
    signature_response = response.json()
    signature_id = signature_response["signature_id"]
    signing_token = signature_response["signing_token"]
    print_success(f"Signature initiated: {signature_id}")
    print_success(f"Signing token: {signing_token}")
    
    # Step 8: Validate token (public endpoint, no auth)
    print_step(8, "Validate Signing Token (Public Endpoint)")
    response = requests.get(f"{API_URL}/approvals/sign/validate/{signing_token}")
    if response.status_code != 200:
        print_error(f"Token validation failed: {response.status_code} - {response.text}")
    
    token_info = response.json()
    print_success(f"Token validated successfully")
    print(f"  - Owner: {token_info['owner_name']}")
    print(f"  - Document: {token_info['document_name']}")
    print(f"  - Status: {token_info['signature_status']}")
    print(f"  - Valid: {token_info['is_valid']}")
    
    if not token_info['is_valid']:
        print_error("Token validation returned invalid")
    
    # Step 9: Sign document (public endpoint, no auth)
    print_step(9, "Sign Document (Public Endpoint)")
    # Create a dummy signature (base64 encoded small image)
    dummy_signature = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    # Extract just the base64 part
    signature_base64 = dummy_signature.split(",")[1] if "," in dummy_signature else dummy_signature
    
    sign_data = {
        "signing_token": signing_token,
        "signature_data": signature_base64
    }
    response = requests.post(
        f"{API_URL}/approvals/sign/{signing_token}",
        json=sign_data
    )
    if response.status_code != 200:
        print_error(f"Signing failed: {response.status_code} - {response.text}")
    
    signed_response = response.json()
    print_success(f"Document signed successfully")
    print(f"  - Signature ID: {signed_response['signature_id']}")
    print(f"  - Status: {signed_response['signature_status']}")
    print(f"  - Signed at: {signed_response.get('signed_at', 'N/A')}")
    
    if signed_response['signature_status'] != 'SIGNED_PENDING_APPROVAL':
        print_error(f"Expected status SIGNED_PENDING_APPROVAL, got {signed_response['signature_status']}")
    
    # Step 10: Check approval queue
    print_step(10, "Check Approval Queue")
    response = requests.get(f"{API_URL}/approvals/queue", headers=headers)
    if response.status_code != 200:
        print_error(f"Failed to get approval queue: {response.status_code} - {response.text}")
    
    queue = response.json()
    print_success(f"Approval queue retrieved: {len(queue)} pending signatures")
    
    # Find our signature in the queue
    found = False
    for sig in queue:
        if sig['signature_id'] == signature_id:
            found = True
            print_success(f"Found signature in approval queue")
            break
    
    if not found:
        print_error("Signature not found in approval queue")
    
    # Step 11: Approve signature
    print_step(11, "Approve Signature")
    approval_data = {
        "reason": "Test approval - signature verified and document reviewed. All terms are acceptable."
    }
    response = requests.post(
        f"{API_URL}/approvals/{signature_id}/approve",
        json=approval_data,
        headers=headers
    )
    if response.status_code != 200:
        print_error(f"Approval failed: {response.status_code} - {response.text}")
    
    approved_response = response.json()
    print_success(f"Signature approved successfully")
    print(f"  - Status: {approved_response['signature_status']}")
    print(f"  - Approved at: {approved_response.get('approved_at', 'N/A')}")
    
    if approved_response['signature_status'] != 'FINALIZED':
        print_error(f"Expected status FINALIZED, got {approved_response['signature_status']}")
    
    # Step 12: Test invalid token
    print_step(12, "Test Invalid Token Validation")
    invalid_token = "invalid-token-12345"
    response = requests.get(f"{API_URL}/approvals/sign/validate/{invalid_token}")
    if response.status_code == 200:
        print_error("Invalid token should return 404, got 200")
    print_success(f"Invalid token correctly rejected: {response.status_code}")
    
    # Step 13: Test signing with invalid token
    print_step(13, "Test Signing with Invalid Token")
    invalid_sign_data = {
        "signing_token": invalid_token,
        "signature_data": signature_base64
    }
    response = requests.post(
        f"{API_URL}/approvals/sign/{invalid_token}",
        json=invalid_sign_data
    )
    if response.status_code == 200:
        print_error("Signing with invalid token should fail, got 200")
    print_success(f"Invalid token signing correctly rejected: {response.status_code}")
    
    # Step 14: Test signing already signed document
    print_step(14, "Test Signing Already Signed Document")
    response = requests.post(
        f"{API_URL}/approvals/sign/{signing_token}",
        json=sign_data
    )
    if response.status_code == 200:
        print_error("Signing already signed document should fail, got 200")
    print_success(f"Already signed document correctly rejected: {response.status_code}")
    
    print("\n" + "="*60)
    print("[SUCCESS] All tests passed!")
    print("="*60)
    print("\nSummary:")
    print(f"  - Project: {project_id}")
    print(f"  - Building: {building_id}")
    print(f"  - Unit: {unit_id}")
    print(f"  - Owner: {owner_id}")
    print(f"  - Document: {document_id}")
    print(f"  - Signature: {signature_id}")
    print(f"  - Signing Token: {signing_token}")
    print("\nYou can test the signing interface at:")
    print(f"  http://localhost:3000/sign/{signing_token}")
    print("\nNote: The token above is already used, create a new signature to test the UI.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

