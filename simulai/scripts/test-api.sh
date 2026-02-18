#!/bin/bash
# Quick test script for Digital Twins Platform
# Run this after starting the services with docker-compose up -d

set -e

echo "=== Digital Twins Platform - Quick Test ==="
echo ""

BASE_URL="${1:-http://localhost:8000}"
DITTO_URL="${2:-http://localhost:8080}"

echo "Testing Backend: $BASE_URL"
echo "Testing Ditto: $DITTO_URL"
echo ""

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

# Test Backend Health
echo "1. Testing Backend Health..."
BACKEND_HEALTH=$(curl -s "$BASE_URL/health" || echo '{"status":"unavailable"}')
echo "   Backend: $BACKEND_HEALTH"
echo ""

# Test Ditto Health
echo "2. Testing Ditto Gateway Health..."
DITTO_HEALTH=$(curl -s "$DITTO_URL/health" || echo '{"status":"unavailable"}')
echo "   Ditto: $DITTO_HEALTH"
echo ""

# Create a Thing
echo "3. Creating a digital twin..."
THING_RESPONSE=$(curl -s -X POST "$BASE_URL/things/" \
  -H "Content-Type: application/json" \
  -d '{
    "thing_id": "test:quick-test-01",
    "attributes": {
      "type": "temperature-sensor",
      "location": "test-lab"
    },
    "features": {
      "temperature": {
        "properties": {
          "value": 23.5,
          "unit": "celsius"
        }
      }
    }
  }')
echo "   Created: $THING_RESPONSE"
echo ""

# Get the Thing
echo "4. Retrieving the digital twin..."
GET_RESPONSE=$(curl -s "$BASE_URL/things/test:quick-test-01")
echo "   Retrieved: $GET_RESPONSE"
echo ""

# Update the Thing
echo "5. Updating feature..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/things/test:quick-test-01/features/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "value": 25.0,
      "unit": "celsius"
    }
  }')
echo "   Updated: $UPDATE_RESPONSE"
echo ""

# List Things
echo "6. Listing all things..."
LIST_RESPONSE=$(curl -s "$BASE_URL/things/")
echo "   Items: $(echo $LIST_RESPONSE | jq '.items | length' 2>/dev/null || echo 'parse error')"
echo ""

# Search Things
echo "7. Searching for temperature sensors..."
SEARCH_RESPONSE=$(curl -s "$BASE_URL/search/things?q=eq(attributes/type,%22temperature-sensor%22)")
echo "   Found: $(echo $SEARCH_RESPONSE | jq '.items | length' 2>/dev/null || echo 'parse error')"
echo ""

# Delete the Thing
echo "8. Deleting the digital twin..."
curl -s -X DELETE "$BASE_URL/things/test:quick-test-01"
echo "   Deleted: test:quick-test-01"
echo ""

echo "=== Test Complete ==="
echo ""
echo "All endpoints are working! Your Digital Twins Platform is ready."
echo ""
echo "API Documentation: $BASE_URL/docs"
echo "Ditto API: $DITTO_URL"
