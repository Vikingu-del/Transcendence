# gateway_service-policy.hcl

# Allow read access to secrets related to the gateway service
path "secret/data/gateway/*" {
  capabilities = ["read"]
}

# Allow list access to other services
path "secret/data/*" {
  capabilities = ["list"]
}

# Allow the service to authenticate using AppRole
path "auth/approle/login" {
  capabilities = ["create", "update"]
}

# Example: Allow access to specific system secrets for configuration (if needed)
path "sys/mounts" {
  capabilities = ["read"]
}
