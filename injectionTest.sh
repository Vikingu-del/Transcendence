#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Testing Security Setup on Localhost..."

# Base URL for the frontend
BASE_URL="http://localhost:5173"

test_security() {
    local test_name=$1
    local endpoint=$2
    
    echo -e "\n🔍 Testing ${test_name}..."
    
    # Full response with headers and body
    response=$(curl -s -i -L \
        -H "Content-Type: application/json" \
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

# SQL Injection tests
test_security "SQL Injection (UNION SELECT)" "/api/profile/?id=1+UNION+SELECT+username,password+FROM+users"
test_security "SQL Injection (UPDATE statement)" "/api/profile/?query=UPDATE+users+SET+role='admin'+WHERE+username='test'"
test_security "SQL Injection (Encoded payload)" "/api/profile/?search=%27%20OR%201%3D1%3B--"

# XSS tests
test_security "XSS (Basic Script)" "/api/profile/?comment=<script>alert('XSS')</script>"
test_security "XSS (Onload Event)" "/api/profile/?img=<img+src=x+onerror=alert(1)>"
test_security "XSS (JavaScript URI)" "/api/profile/?redirect=javascript:alert('XSS')"

echo -e "\n✅ Tests completed"