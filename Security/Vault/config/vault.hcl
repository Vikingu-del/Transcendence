ui = true

storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable = 1
}

path "auth/token/lookup" {
  capabilities = ["read"]
}

api_addr = "https://vault:8200" # Set to the external address if needed
disable_mlock = true