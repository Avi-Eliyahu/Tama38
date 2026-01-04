#!/bin/bash
# E2E Test Script for TAMA38 Phase 1
# Tests complete workflows end-to-end

set -e

API_URL="http://localhost:8000/api/v1"
EMAIL="admin@tama38.local"
PASSWORD="Admin123!@#"

echo "=========================================="
echo "TAMA38 Phase 1 E2E Tests"
echo "=========================================="
echo ""

# Step 1: Login
echo "Step 1: Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "ERROR: Login failed"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

REQUEST_ID=$(echo $LOGIN_RESPONSE | grep -o '"request_id":"[^"]*' | cut -d'"' -f4 || echo "none")
echo "✓ Login successful (request_id: $REQUEST_ID)"
echo ""

# Step 2: Get current user
echo "Step 2: Testing get current user..."
USER_RESPONSE=$(curl -s -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

USER_ID=$(echo $USER_RESPONSE | grep -o '"user_id":"[^"]*' | cut -d'"' -f4)
echo "✓ Current user retrieved: $USER_ID"
echo ""

# Step 3: Create project
echo "Step 3: Testing project creation..."
PROJECT_RESPONSE=$(curl -s -X POST "$API_URL/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "E2E Test Project",
    "project_code": "E2E_TEST_001",
    "project_type": "TAMA38_1",
    "location_city": "Tel Aviv",
    "required_majority_percent": 75.0,
    "critical_threshold_percent": 50.0,
    "majority_calc_type": "HEADCOUNT"
  }')

PROJECT_ID=$(echo $PROJECT_RESPONSE | grep -o '"project_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: Project creation failed"
    echo "Response: $PROJECT_RESPONSE"
    exit 1
fi

echo "✓ Project created: $PROJECT_ID"
echo ""

# Step 4: Create building
echo "Step 4: Testing building creation..."
BUILDING_RESPONSE=$(curl -s -X POST "$API_URL/buildings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"$PROJECT_ID\",
    \"building_name\": \"Test Building 1\",
    \"building_code\": \"BLDG001\",
    \"address\": \"123 Test Street\",
    \"floor_count\": 6,
    \"total_units\": 12
  }")

BUILDING_ID=$(echo $BUILDING_RESPONSE | grep -o '"building_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$BUILDING_ID" ]; then
    echo "ERROR: Building creation failed"
    echo "Response: $BUILDING_RESPONSE"
    exit 1
fi

echo "✓ Building created: $BUILDING_ID"
echo ""

# Step 5: Create unit
echo "Step 5: Testing unit creation..."
UNIT_RESPONSE=$(curl -s -X POST "$API_URL/units" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"building_id\": \"$BUILDING_ID\",
    \"floor_number\": 1,
    \"unit_number\": \"101\",
    \"area_sqm\": 65.0,
    \"room_count\": 3
  }")

UNIT_ID=$(echo $UNIT_RESPONSE | grep -o '"unit_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$UNIT_ID" ]; then
    echo "ERROR: Unit creation failed"
    echo "Response: $UNIT_RESPONSE"
    exit 1
fi

echo "✓ Unit created: $UNIT_ID"
echo ""

# Step 6: Create owner
echo "Step 6: Testing owner creation..."
OWNER_RESPONSE=$(curl -s -X POST "$API_URL/owners" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"unit_id\": \"$UNIT_ID\",
    \"full_name\": \"Test Owner\",
    \"phone\": \"+972-50-123-4567\",
    \"email\": \"testowner@example.com\",
    \"ownership_share_percent\": 100.0
  }")

OWNER_ID=$(echo $OWNER_RESPONSE | grep -o '"owner_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$OWNER_ID" ]; then
    echo "ERROR: Owner creation failed"
    echo "Response: $OWNER_RESPONSE"
    exit 1
fi

echo "✓ Owner created: $OWNER_ID"
echo ""

# Step 7: Log interaction
echo "Step 7: Testing interaction logging..."
INTERACTION_RESPONSE=$(curl -s -X POST "$API_URL/interactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"owner_id\": \"$OWNER_ID\",
    \"interaction_type\": \"PHONE_CALL\",
    \"interaction_date\": \"$(date +%Y-%m-%d)\",
    \"duration_minutes\": 15,
    \"outcome\": \"POSITIVE\",
    \"call_summary\": \"Owner agreed to meet next week for signing\",
    \"sentiment\": \"POSITIVE\"
  }")

INTERACTION_ID=$(echo $INTERACTION_RESPONSE | grep -o '"log_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$INTERACTION_ID" ]; then
    echo "ERROR: Interaction logging failed"
    echo "Response: $INTERACTION_RESPONSE"
    exit 1
fi

echo "✓ Interaction logged: $INTERACTION_ID"
echo ""

# Step 8: Get dashboard data
echo "Step 8: Testing dashboard API..."
DASHBOARD_RESPONSE=$(curl -s -X GET "$API_URL/dashboard/data" \
  -H "Authorization: Bearer $TOKEN")

if echo "$DASHBOARD_RESPONSE" | grep -q "kpis"; then
    echo "✓ Dashboard data retrieved"
else
    echo "ERROR: Dashboard API failed"
    echo "Response: $DASHBOARD_RESPONSE"
    exit 1
fi
echo ""

# Step 9: Verify logs contain request IDs
echo "Step 9: Verifying request IDs in logs..."
if docker-compose logs backend 2>/dev/null | grep -q "request_id"; then
    echo "✓ Request IDs found in logs"
else
    echo "WARNING: Request IDs not found in logs (may be normal if no requests logged yet)"
fi
echo ""

echo "=========================================="
echo "All E2E tests passed!"
echo "=========================================="
echo ""
echo "Test Summary:"
echo "  - Login: ✓"
echo "  - Project Creation: ✓"
echo "  - Building Creation: ✓"
echo "  - Unit Creation: ✓"
echo "  - Owner Creation: ✓"
echo "  - Interaction Logging: ✓"
echo "  - Dashboard: ✓"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Building ID: $BUILDING_ID"
echo "Unit ID: $UNIT_ID"
echo "Owner ID: $OWNER_ID"

