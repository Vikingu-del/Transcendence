import hvac
from dotenv import dotenv_values
import os

env_vars = dotenv_values('/internal/secrets/.env')
vault_token = os.environ.get("VAULT_TOKEN")

if not vault_token:
    raise ValueError("Vault root token not found. Ensure VAULT_ROOT_TOKEN is set in the .env file.")
print("Vault root token loaded.")

# Initialize the Vault client
vault_client = hvac.Client(
    url="http://vault:8200",
    token=vault_token,
)

if not vault_client.is_authenticated():
    raise ValueError("Failed to authenticate with Vault. Check the VAULT_ROOT_TOKEN.")

print("✅ Successfully authenticated with Vault.")

def write_secret_to_vault(path, secrets):
    try:
        vault_client.secrets.kv.v2.create_or_update_secret(
            path=path, # Store under a specific service path eg. "user_db"
            secret=secrets, # Dictionary of all keys
        )
        print(f"✅ Secrets successfully written to Vault at '{path}'")
    except hvac.exceptions.VaultError as e:
        print(f"❌ Failed to write secrets to Vault. Error: {e}")


def read_secret_from_vault(path, key, default=None):
    # Read a specific secret key from a give Vault path.
    try:
        response = vault_client.secrets.kv.v2.read_secret_version(
            path=path,
            # remove the warning message
            raise_on_deleted_version=True, # avoid fetching deleted secrets
        )
        # Extract the secrets dictionary
        secrets = response['data']['data']
        return secrets.get(key, default) # Return specific key value or default
    except hvac.exceptions.VaultError as e:
        print(f"❌ Failed to read secret '{key}' from Vault at '{path}'. Error: {e}")
        return default

def create_approle(role_name, policies, secret_id_ttl="1h", token_ttl="1h", token_max_ttl="4h"):
    try:
        # Enable AppRole if not already enabled
        auth_methods = vault_client.sys.list_auth_methods()
        if 'approle/' not in auth_methods:
            vault_client.sys.enable_auth_method(method_type='approle', path='approle', mount_point='approle')

        # Create the AppRole using the correct write method
        vault_client.write(
            f'auth/approle/role/{role_name}',
            policies=policies,
            secret_id_ttl=secret_id_ttl,
            token_ttl=token_ttl,
            token_max_ttl=token_max_ttl,
        )

        # Retrieve Role ID
        role_id_response = vault_client.read(f'auth/approle/role/{role_name}/role-id')
        if role_id_response is None:
            raise ValueError(f"Failed to retrieve role ID for {role_name}")
        role_id = role_id_response['data']['role_id']

        # Generate a Secret ID
        secret_id_response = vault_client.write(f'auth/approle/role/{role_name}/secret-id')
        if secret_id_response is None or 'wrap_info' not in secret_id_response:
            raise ValueError(f"Failed to generate secret ID for {role_name}")
        secret_id = secret_id_response['data']['secret_id']

        # Store credentials securely to the specified mounted paths in Vault
        secret_path = f"/vault/approle/{role_name}"
        os.makedirs(secret_path, exist_ok=True)
        with open(f"{secret_path}/role_id", "w") as f: {
            f.write(role_id)
        }
        with open(f"{secret_path}/secret_id", "w") as f: {
            f.write(secret_id)
        }
        print(f"✅ AppRole '{role_name}' created and stored in '{secret_path}'")
        return role_id, secret_id
    except hvac.exceptions.VaultError as e:
        print(f"❌ Failed to create AppRole '{role_name}'. Error: {e}")
        return None, None


# Write secrets under "user_db" path
secrets_to_store_user = {
    "USER_DB_USER": env_vars.get("USER_DB_USER"),
    "USER_DB_PASSWORD": env_vars.get("USER_DB_PASSWORD"),
    "USER_DB_HOST": env_vars.get("USER_DB_HOST"),
    "USER_DB_PORT": env_vars.get("USER_DB_PORT"),
    "USER_DB_NAME": env_vars.get("USER_DB_NAME"),
}

secrets_to_store_chat = {
    "CHAT_DB_USER": env_vars.get("CHAT_DB_USER"),
    "CHAT_DB_PASSWORD": env_vars.get("CHAT_DB_PASSWORD"),
    "CHAT_DB_HOST": env_vars.get("CHAT_DB_HOST"),
    "CHAT_DB_PORT": env_vars.get("CHAT_DB_PORT"),
    "CHAT_DB_NAME": env_vars.get("CHAT_DB_NAME"),
}

secrets_to_store_gateway = {
    "CURRENT_HOST": env_vars.get("CURRENT_HOST"),
}

write_secret_to_vault("user_db", secrets_to_store_user)
write_secret_to_vault("gateway", secrets_to_store_gateway)
write_secret_to_vault("user", secrets_to_store_user)
write_secret_to_vault("chat_db", secrets_to_store_chat)
write_secret_to_vault("chat", secrets_to_store_chat)

# Generate AppRoles for services
services = ['user_db', 'gateway', 'user', 'chat_db', 'chat']
for service in services:
    role_id, secret_id = create_approle(
        role_name=service, 
        policies=[f'{service}-policy']
    )
    if role_id and secret_id:
        secret_path = f"/vault/approle/{service}"
        os.makedirs(secret_path, exist_ok=True)
        with open(f"{secret_path}/role_id", "w") as f:
            f.write(role_id)
        with open(f"{secret_path}/secret_id", "w") as f:
            f.write(secret_id)

# Read specific secrets
# postgres_password = read_secret_from_vault("user_db", "DB_PASSWORD")
# print("DB_PASSWORD:", postgres_password)

LocalHost = read_secret_from_vault("gateway", "CURRENT_HOST")
print("CURRENT_HOST:", LocalHost)