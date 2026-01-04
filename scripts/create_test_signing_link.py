#!/usr/bin/env python3
"""
Helper script to create a test signing link for UI testing
Creates a fresh signature with WAIT_FOR_SIGN status
"""
import requests
import sys

API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@tama38.local"
PASSWORD = "Admin123!@#"

def main():
    # Login
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"ERROR: Login failed: {response.status_code}")
        sys.exit(1)
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get first owner (or create one if none exists)
    response = requests.get(f"{API_URL}/owners?limit=1", headers=headers)
    if response.status_code != 200:
        print(f"ERROR: Failed to get owners: {response.status_code}")
        sys.exit(1)
    
    owners = response.json()
    if not owners:
        print("ERROR: No owners found. Please create an owner first.")
        sys.exit(1)
    
    owner_id = owners[0]["owner_id"]
    owner_name = owners[0]["full_name"]
    
    # Get first document (or create one if none exists)
    response = requests.get(f"{API_URL}/documents?limit=1", headers=headers)
    if response.status_code != 200:
        print(f"ERROR: Failed to get documents: {response.status_code}")
        sys.exit(1)
    
    documents = response.json()
    if not documents:
        print("ERROR: No documents found. Please upload a document first.")
        sys.exit(1)
    
    document_id = documents[0]["document_id"]
    document_name = documents[0]["file_name"]
    
    # Initiate signature
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
        print(f"ERROR: Signature initiation failed: {response.status_code} - {response.text}")
        sys.exit(1)
    
    signature_response = response.json()
    signing_token = signature_response["signing_token"]
    
    print("\n" + "="*60)
    print("Test Signing Link Created Successfully!")
    print("="*60)
    print(f"\nOwner: {owner_name}")
    print(f"Document: {document_name}")
    print(f"Signing Token: {signing_token}")
    print(f"\nSigning URL:")
    print(f"  http://localhost:3000/sign/{signing_token}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

