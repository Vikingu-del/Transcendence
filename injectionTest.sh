#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Testing Security Setup on Localhost..."

# Base URL and auth token from successful login
BASE_URL="http://localhost:8000"
AUTH_TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"username": "my_username", "password": "my_password"}' \
    "${BASE_URL}/api/login/" | jq -r '.auth_token')

test_security() {
    local test_name=$1
    local endpoint=$2
    
    echo -e "\n🔍 Testing ${test_name}..."
    
    # Full response with headers and body
    response=$(curl -s -i \
        -H "Content-Type: application/json" \
        -H "Authorization: Token ${AUTH_TOKEN}" \
        "${BASE_URL}${endpoint}")
    
    # Extract status code
    status_code=$(echo "$response" | grep "HTTP/" | awk '{print $2}')
    
    # Print detailed results
    echo -e "${YELLOW}Status Code:${NC} $status_code"
    echo -e "${YELLOW}Response Headers:${NC}"
    echo "$response" | grep -E "^(X-|Content-Security|Strict-Transport)"
    
    # Check if protection is in place
    if [[ $status_code == "403" || $status_code == "400" ]]; then
        echo -e "${GREEN}✓ Protection active${NC}"
    else
        echo -e "${RED}✗ No protection detected${NC}"
    fi
}

echo "Starting security tests..."

# SQL Injection test
test_security "SQL Injection" \
    "/api/profile/?id=1'+UNION+SELECT+*+FROM+users--"

# XSS test
test_security "XSS Protection" \
    "/api/profile/?input=<img+src=x+onerror=alert(1)>"

# Directory Traversal test
test_security "Directory Traversal" \
    "/api/profile/..%2F..%2Fetc%2Fpasswd"

# Command Injection test
test_security "Command Injection" \
    "/api/profile/?cmd=;cat+/etc/passwd"

# CSRF test
test_security "CSRF Protection" \
    "/api/profile/"

echo -e "\n✅ Tests completed"