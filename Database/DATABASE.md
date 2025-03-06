# Database Architecture Overview

## Database Strategy

## Isolation Model

- **Separate PostgreSQL Instances**: Each service has its own dedicated PostgreSQL database
- **Data Isolation**: Services can only access their own data, enhancing security
- **Independent Scaling**: Each database can be scaled according to its specific workload
- **Failure Containment**: Issues in one database don't affect other services

## Database Containers

### Authentication Database
- **Container**: auth_db
- **Purpose**: Stores authentication-related data
- **Key Data**:
  - User credentials
  - Authentication tokens
  - Two-factor authentication secrets
  - OAuth state information

### User Database
- **Container**: user_db
- **Purpose**: Stores user profile and relationship data
- **Key Data**:
  - User profiles
  - Friend relationships
  - User preferences
  - Avatar images (stored as paths)

### Chat Database
- **Container**: chat_db
- **Purpose**: Stores messaging data
- **Key Data**:
  - Chat messages
  - Chat channels
  - Message history
  - Read receipts

### Game Database
- **Container**: game_db
- **Purpose**: Stores game and match data
- **Key Data**:
  - Match history
  - Player statistics
  - Game sessions
  - Tournament records

### Notification Database
- **Container**: notification_db
- **Purpose**: Stores notification data
- **Key Data**:
  - User notifications
  - Notification status (read/unread)
  - Notification preferences

## Security Implementation

### HashiCorp Vault Integration
- **Credential Management**: All database credentials are stored and retrieved from HashiCorp Vault
- **Secure Provisioning**:
  - AppRole authentication with Vault
  - Role IDs and Secret IDs stored in separate locations
  - Short-lived tokens for database credential access

### Access Control Flow
1. Database container starts and authenticates with Vault using AppRole
2. Container retrieves database credentials from Vault
3. PostgreSQL instance is initialized with secure credentials
4. Application services connect using these credentials

## Technical Implementation

### Container Configuration
- **Base Image**: PostgreSQL official Docker image
- **Additional Tools**:
  - Vault client for credential management
  - jq for JSON parsing
  - Healthcheck scripts

### Initialization Process

#### Vault Authentication
Timeout Handling: Configurable timeouts prevent cascading failures
This architecture supports the microservices approach by ensuring each service has complete ownership of its data while maintaining secure isolation between different parts of the application.

```bash
VAULT_TOKEN=$(curl --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)
```

#### Secret Retrieval:
```bash
APP_USER=$(echo $VAULT_RESPONSE | jq -r .data.data.<SERVICE>_DB_USER)
APP_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.<SERVICE>_DB_PASSWORD)
APP_DB=$(echo $VAULT_RESPONSE | jq -r .data.data.<SERVICE>_DB_NAME)
```

#### Database Creation:
```bash
CREATE DATABASE $APP_DB;
CREATE USER $APP_USER WITH ENCRYPTED PASSWORD '$APP_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $APP_DB TO $APP_USER;
```

### Health Monitoring
- **Regular Health Checks**: Each database has a dedicated healthcheck script
- **Validation Process**:
  - Authentication with Vault
  - Credential retrieval
  - Connection testing using pg_isready
- **Logging**: Detailed logs maintained for troubleshooting

### Database Independence
The database-per-service pattern provides several benefits:

- **Schema Evolution**: Each service can evolve its database schema independently
- **Technology Selection**: Different database technologies could be used if needed
- **Resource Allocation**: Database resources can be tailored to each service's needs
- **Security Boundaries**: Compromising one database doesn't expose all application data

### Connection Management
- **Connection Pooling**: Each service manages its own database connection pool
- **Retry Logic**: Services implement connection retry logic for resilience
- **Timeout Handling**: Configurable timeouts prevent cascading failures

This architecture supports the microservices approach by ensuring each service has complete ownership of its data while maintaining secure isolation between different parts of the application.

