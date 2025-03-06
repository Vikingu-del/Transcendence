# API Gateway

## Overview

The API Gateway serves as the entry point for all client requests in our microservices architecture. It is implemented using NGINX with ModSecurity for enhanced security features.

## Key Features

- **Reverse Proxy**: Routes requests to appropriate backend services
- **Load Balancing**: Distributes traffic across multiple backend instances
- **SSL Termination**: Handles HTTPS connections, offloading SSL processing from backend services
- **Security Layer**: Implements ModSecurity Web Application Firewall (WAF) for protection against common attacks

## Architecture

The API Gateway connects the following services:
- Authentication Service
- User Service
- Chat Service
- Game Service
- Notification Service
- Tournament Service
- Frontend

## Configuration

### NGINX Configuration

The NGINX configuration follows best practices for security and performance:

- HTTP requests are automatically redirected to HTTPS
- All communications are secured with TLS 1.2/1.3
- WebSocket connections are properly configured for real-time features
- Custom error handlers for service unavailability

### ModSecurity Configuration

ModSecurity provides Web Application Firewall capabilities through the following environment variables:

#### Core Settings
- `MODSEC_RULE_ENGINE=On`: Enables active protection mode (vs. DetectionOnly)
- `MODSEC_STATUS_ENGINE=Off`: Disables performance statistics collection

#### Request Body Processing
- `MODSEC_REQUEST_BODY_ACCESS=On`: Enables inspection of request bodies
- `MODSEC_REQUEST_BODY_LIMIT=1048576`: Limits request bodies to 1MB to prevent DoS attacks
- `MODSEC_REQUEST_BODY_NO_FILES_LIMIT=131072`: Limits non-file request portions to 128KB
- `MODSEC_REQUEST_BODY_LIMIT_ACTION=Reject`: Rejects requests exceeding the size limit
- `MODSEC_REQUEST_BODY_JSON_DEPTH=5`: Prevents deeply nested JSON attacks (max depth 5)
- `MODSEC_REQBODY_ERROR_ACTION=deny`: Denies requests with malformed bodies

#### Multipart Form Handling
- `MODSEC_MULTIPART_STRICT_ERROR_ACTION=deny`: Denies malformed multipart requests
- `MODSEC_MULTIPART_UNMATCHED_BOUNDARY_ACTION=deny`: Blocks requests with invalid boundaries

#### RegEx DoS Prevention
- `MODSEC_PCRE_MATCH_LIMIT=1000`: Limits PCRE pattern matching complexity
- `MODSEC_PCRE_MATCH_LIMIT_RECURSION=1000`: Prevents regex recursion DoS attacks

#### Response Body Processing
- `MODSEC_RESPONSE_BODY_ACCESS=On`: Enables inspection of server responses
- `MODSEC_RESPONSE_BODY_MIME_TYPE="text/plain text/html text/xml"`: Only inspects specified content types
- `MODSEC_RESPONSE_BODY_LIMIT=524288`: Limits response inspection to 512KB
- `MODSEC_RESPONSE_BODY_LIMIT_ACTION=ProcessPartial`: Processes responses partially if they exceed the limit

#### File System Configuration
- `MODSEC_TMP_DIR=/var/cache/modsecurity/tmp`: Temporary file storage location
- `MODSEC_DATA_DIR=/var/cache/modsecurity/data`: Persistent data storage location
- `MODSEC_UPLOAD_DIR=/var/cache/modsecurity/upload`: File upload storage location
- `MODSEC_UPLOAD_KEEP_FILES=On`: Preserves uploaded files for security analysis
- `MODSEC_UPLOAD_FILE_MODE=0600`: Sets strict file permissions for uploaded files

#### Logging and Auditing
- `MODSEC_DEBUG_LOG=/var/log/modsecurity/debug.log`: Debug log file location
- `MODSEC_DEBUG_LOG_LEVEL=3`: Sets detailed logging (0=no logging, 9=maximum verbosity)
- `MODSEC_AUDIT_ENGINE=RelevantOnly`: Only logs suspicious transactions
- `MODSEC_AUDIT_LOG_RELEVANT_STATUS="^(?:5|4(?!404))"`: Logs all 5xx and 4xx errors (except 404)
- `MODSEC_AUDIT_LOG_PARTS=ABIJDEFHZ`: Captures comprehensive details in the following format:
  - A: Audit log header
  - B: Request headers
  - C: Request body (not included)
  - D: Response headers
  - E: Response body
  - F: Forensic information
  - G: Event data (not included)
  - H: Audit trailer
  - I: ModSecurity rules that triggered
  - J: Request body (files uploaded)
  - Z: Final boundary marker
- `MODSEC_AUDIT_LOG_TYPE=Serial`: Stores all audit log parts in a single file
- `MODSEC_AUDIT_LOG=/var/log/modsecurity/modsec_audit.log`: Audit log file location

#### Additional Settings
- `MODSEC_ARGUMENT_SEPARATOR=&`: Defines URL parameter separator
- `MODSEC_COOKIE_FORMAT=0`: Uses standard cookie parsing format
- `MODSEC_UNICODE_MAP_FILE=/etc/nginx/modsecurity.d/unicode.mapping`: Path to Unicode character mapping file

### CORS Headers

The API Gateway is configured with appropriate CORS headers to allow:
- Cross-origin requests from specified domains
- Required HTTP methods (GET, POST, OPTIONS, etc.)
- Necessary headers for authentication and content types

## Deployment

### Docker Setup

The API Gateway is containerized using Docker:

# Configuration and setup
### SSL Certificate Generation
- Self-signed certificates are automatically generated during container startup for development environments.
- For production, you should replace these with valid certificates from a trusted CA.

### Monitoring and Logging
Detailed logging is configured for:
- Access logs for all services
- Error logs with debug level information
- ModSecurity audit logs for security events

### Error Handling
Custom error responses are provided for various scenarios:
- Service unavailability (502 responses)
- Bad requests (400 responses)
- Authentication failures
