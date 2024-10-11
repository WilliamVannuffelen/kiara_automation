# Python lib

Contains reusable helper functions commonly needed for automation.

# Features

- AzureDevopsLogger: Azure DevOps pipeline output compatible logger

- init_logger: A logger init wrapper

- _terminate_script: Controlled process termination with success/fail return code

- get_env_var: Wrapper around fetching env vars with flow control depending on them being optional or mandatory

- get_secretclient: Init a KeyVault client with Managed Identiy or ClientID/Secret

- put_keyvault_secret: Provision a secret in a KeyVault

# Usage

```python
import lib.helpers as help
import lib.azhelpers as azhelp


if __name__ == "__main__":
    try:
        log = help.init_logger(
            log_class="azuredevops", log_formatter="azuredevops", log_level="debug"
        )
    except Exception as e:
        print(f"Failed to initiate logger.")
        print(e)
        help._terminate_script(1)
    
    vault_url = help.get_env_var({"name": "VAULT_URL", "required": True})

    secretclient = azhelp.get_secretclient(vault_url=vault_url)

    azhelp.put_keyvault_secret(secretclient, account, password)
```