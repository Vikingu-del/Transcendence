import hvac
from dotenv import dotenv_values
import os

env_vars = dotenv_values('secrets/.env')
vault_token = env_vars.get("VAULT_ROOT_TOKEN")
if not vault_token:
    raise ValueError("Vault root token not found. Ensure VAULT_ROOT_TOKEN is set in the .env file.")
print("Vault root token loaded.")

# Initialize the Vault client
vault_client = hvac.Client(
    url="http://vault:8200",
    token=vault_token,
)

vault_client.is_authenticated()

# Function to write secrets to Vault
def write_secret_to_vault(key, value):
    secret_path = f"secret/{key}"
    try:
        vault_client.secrets.kv.v2.create_or_update_secret(
            path=key,
            secret={key: value},
        )
        print(f"Secret '{key}' successfully written to Vault at '{secret_path}'")
    except hvac.exceptions.VaultError as e:
        print(f"Failed to write secret '{key}' to Vault. Error: {e}")

def read_secret_from_vault(key, default=None):
    secret_path = f"secret/{key}"
    try:
        response = vault_client.secrets.kv.v2.read_secret_version(
            path=key,
            # remove the warning message
            raise_on_deleted_version=True,
        )
        return response['data']['data'][key]
    except hvac.exceptions.VaultError as e:
        print(f"Failed to read secret '{key}' at '{secret_path}' from Vault. Error: {e}")
        return default

# Function to create AppRole
def create_approle(role_name, policies, secret_id_ttl="1h", token_ttl="1h", token_max_ttl="4h"):
    try:
        # Enable AppRole if not already enabled
        auth_methods = vault_client.sys.list_auth_methods()
        if 'approle/' not in auth_methods:
            vault_client.sys.enable_auth_method(method_type='approle', path='approle', mount_point='approle')

        # Create the AppRole
        vault_client.write(
            f'auth/approle/role/{role_name}',
            policies=policies,
            secret_id_ttl=secret_id_ttl,
            token_ttl=token_ttl,
            token_max_ttl=token_max_ttl,
        )

        # Retrieve Role ID and Secret ID
        role_id = vault_client.read(f'auth/approle/role/{role_name}/role-id')['data']['role_id']
        secret_id = vault_client.write(f'auth/approle/role/{role_name}/secret-id')['data']['secret_id']
        print(f"AppRole '{role_name}' created with Role ID: {role_id} and Secret ID: {secret_id}")
        return role_id, secret_id
    except hvac.exceptions.VaultError as e:
        print(f"Failed to create AppRole '{role_name}'. Error: {e}")
        return None, None

# Write each key-value pair to Vault
for key, value in env_vars.items():
    write_secret_to_vault(key, value)

# # Generate tokens for services
services = ['user_service', 'gateway_service']

# Create AppRoles for services (Optional)
approle_credentials = {}
for service in services:
    role_id, secret_id = create_approle(role_name=service, policies=[f'{service}-policy'])
    if role_id and secret_id:
        approle_credentials[service] = {'role_id': role_id, 'secret_id': secret_id}

# Save AppRole credentials to a shared volume (Optional)
for service, creds in approle_credentials.items():
    role_id_path = f'/vault/agent/config/{service}_role_id'
    secret_id_path = f'/vault/agent/config/{service}_secret_id'
    os.makedirs(os.path.dirname(role_id_path), exist_ok=True)
    with open(role_id_path, 'w') as role_file:
        role_file.write(creds['role_id'])
    with open(secret_id_path, 'w') as secret_file:
        secret_file.write(creds['secret_id'])

# Read specific secrets
postgres_password = read_secret_from_vault("POSTGRES_PASSWORD")
print("POSTGRES_PASSWORD:", postgres_password)