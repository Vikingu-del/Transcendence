# readonly-policy.hcl

# Allow read access to secrets, but not write or delete
path "secret/*" {
  capabilities = ["read", "list"]
}

# No access to system paths or token management
path "sys/*" {
  capabilities = []
}

# No ability to create, update, or delete secrets
path "auth/*" {
  capabilities = []
}
