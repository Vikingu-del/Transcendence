ui = true

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable = 1
}

path "auth/token/lookup" {
  capabilities = ["read"]
}

api_addr = "http://vault:8200"
disable_mlock = true