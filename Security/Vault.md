Vault's Ports
Port 8200:

This is the primary port used by Vault for API requests and client interactions.
All communications with Vault (such as storing secrets, retrieving data, or configuring settings) happen over this port.
This port is mandatory to expose for Vault to function.
Port 8201:

This port is used by Vault internally for cluster communication in a high-availability (HA) setup.
It allows multiple Vault instances to communicate for leader election and replication.
This port is only necessary if you are setting up Vault in an HA configuration.


When to Use Port 8201
If you later decide to enable Vault’s HA mode (e.g., using a storage backend like Consul or etcd), you’ll need to expose port 8201 for cluster communications. In that case, you would also modify the vault.hcl file to include an ha_storage block.

For now, you can safely remove port 8201 unless HA is part of your setup plan. Let me know if you'd like help with that!