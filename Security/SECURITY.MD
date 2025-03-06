Security Architecture Overview
Core Components
HashiCorp Vault: Secret management and data protection platform
VaultSecrets: Custom service to initialize and populate Vault with secrets
AppRole Authentication: Role-based access control for services
Policy-based Authorization: Fine-grained access control with HCL policy files
Docker Secrets Management: Secure credential distribution in containerized environment
Component Architecture
HashiCorp Vault Server
Purpose: Centralized secret management system
Features:
Secure secret storage with encryption
Dynamic secrets generation
Access control with policies
Various authentication methods
Audit logging
Configuration:
Auto-unsealing with threshold of 3/5 keys
KV v2 secrets engine enabled at /secret path
AppRole authentication method enabled
VaultSecrets Service
Purpose: Initializes and populates Vault with secrets from environment variables
Features:
Automatic secret creation from .env file
AppRole creation for each service
Policy assignment to AppRoles
Writing role IDs and secret IDs to mounted volumes
Implementation:
Python-based using hvac client library
Reads secrets from .env file
Creates structured secret paths in Vault
Organizes secrets by service
AppRole Authentication
Purpose: Secure service-to-service authentication without human intervention
Features:
Two-factor authentication (role ID + secret ID)
Time-limited credentials
Policy-restricted access
No hardcoded secrets in container images
Configuration:
Default token TTL: 1 hour
Default token max TTL: 4 hours
Secret ID TTL: 1 hour
Policy-based Authorization
Purpose: Fine-grained access control for services
Features:
Principle of least privilege implementation
Path-specific read/write permissions
Service-specific policies
Implementation:
HCL (HashiCorp Configuration Language) policy files
Each service has a dedicated policy file
Policy names follow <service-name>-policy format
Security Workflow
Vault Initialization Process
Vault Server Startup:

Starts with configuration from vault.hcl
Checks initialization status
If not initialized:
Creates 5 unseal keys with 3 key threshold
Stores keys and root token in secure location
If already initialized:
Retrieves stored unseal keys
Unseals Vault with 3 keys
Secrets Population:

VaultSecrets container reads root token from shared volume
Authenticates with Vault using root token
Reads secrets from .env file
Organizes secrets by service
Writes secrets to Vault using KV v2 engine
AppRole Configuration:

For each service (user_db, gateway, chat, etc.):
Creates AppRole with appropriate policies
Generates role ID and secret ID
Writes credentials to shared volume at /vault/approle/<service>/
Service Authentication Flow

Credential Retrieval:
VAULT_TOKEN=$(curl --request POST \
    --data "{\"role_id\":\"$ROLE_ID\",\"secret_id\":\"$SECRET_ID\"}" \
    $VAULT_ADDR/v1/auth/approle/login | jq -r .auth.client_token)

Secret Access:
APP_USER=$(echo $VAULT_RESPONSE | jq -r .data.data.<SERVICE>_DB_USER)
APP_PASSWORD=$(echo $VAULT_RESPONSE | jq -r .data.data.<SERVICE>_DB_PASSWORD)
APP_DB=$(echo $VAULT_RESPONSE | jq -r .data.data.<SERVICE>_DB_NAME)

Service Startup with Retrieved Secrets:
CREATE DATABASE $APP_DB;
CREATE USER $APP_USER WITH ENCRYPTED PASSWORD '$APP_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $APP_DB TO $APP_USER;

Policy Implementation
Policy Structure
Format: HashiCorp Configuration Language (HCL)
Example Policy:
path "secret/data/auth" {
  capabilities = ["read"]
}

path "secret/data/auth_db" {
  capabilities = ["read"]
}

Key Policies
Service-specific Policies:

user-policy.hcl: Access to user service secrets
chat-policy.hcl: Access to chat service secrets
game-policy.hcl: Access to game service secrets
gateway-policy.hcl: Access to API gateway configuration
Database Policies:

user_db-policy.hcl: Access to user database credentials
auth_db-policy.hcl: Access to authentication database credentials
chat_db-policy.hcl: Access to chat database credentials
game_db-policy.hcl: Access to game database credentials
notification_db-policy.hcl: Access to notification database credentials
Monitoring & Logging Policies:

elasticsearch-policy.hcl: Access to Elasticsearch credentials
kibana-policy.hcl: Access to Kibana configuration
logstash-policy.hcl: Access to Logstash settings
filebeat-policy.hcl: Access to Filebeat configuration
grafana-policy.hcl: Access to Grafana admin credentials
Secret Management
Secret Organization
User Service Secrets:

secrets_to_store_user = {
  "USER_DB_USER": env_vars.get("USER_DB_USER"),
  "USER_DB_PASSWORD": env_vars.get("USER_DB_PASSWORD"),
  "USER_DB_HOST": env_vars.get("USER_DB_HOST"),
  "USER_DB_PORT": env_vars.get("USER_DB_PORT"),
  "USER_DB_NAME": env_vars.get("USER_DB_NAME"),
}
