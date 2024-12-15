# db-access-policy.hcl

# Allow read access to database-related secrets
path "secret/database/*" {
  capabilities = ["read", "list"]
}

# Allow read access to database credentials, typically stored in the secret engine
path "database/creds/*" {
  capabilities = ["read"]
}

# If using database configuration paths in Vault, allow read access
path "secret/db-config/*" {
  capabilities = ["read"]
}

# Allow write access to specific database configurations or secrets (e.g., connection details)
path "secret/database/config/*" {
  capabilities = ["create", "update"]
}
