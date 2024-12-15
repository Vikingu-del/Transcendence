# admin-policy.hcl

# Allow all actions on secrets
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Allow read and write access to all system paths
path "sys/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Allow token creation and management
path "auth/token/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Allow app role management
path "auth/approle/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Allow management of the Vault configuration
path "sys/config/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
