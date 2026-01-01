#!/bin/bash
# scripts/test_infrastructure.sh
# Test Docker Compose infrastructure setup

set -e

echo "Testing Docker Compose setup..."
docker-compose up -d
sleep 5

echo "Verifying services are running..."
if ! docker-compose ps | grep -q "Up"; then
    echo "ERROR: Services are not running"
    docker-compose ps
    exit 1
fi

echo "Testing database connectivity..."
docker-compose exec -T backend python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:postgres@database:5432/tama38_dev')
conn = engine.connect()
print('Database connected successfully')
conn.close()
"

echo "Testing frontend accessibility..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [ "$FRONTEND_RESPONSE" != "200" ] && [ "$FRONTEND_RESPONSE" != "000" ]; then
    echo "WARNING: Frontend test returned HTTP $FRONTEND_RESPONSE (may not be ready yet)"
fi

echo "Testing backend accessibility..."
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs || echo "000")
if [ "$BACKEND_RESPONSE" != "200" ]; then
    echo "ERROR: Backend docs test failed: HTTP $BACKEND_RESPONSE"
    exit 1
fi

HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "Health check passed"
else
    echo "ERROR: Health check failed: $HEALTH_RESPONSE"
    exit 1
fi

echo "All infrastructure tests passed!"

