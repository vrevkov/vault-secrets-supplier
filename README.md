# Description
Script for managing secrets in Hashicorp Vault. Is able to:
1. Export all screts from particular path to yaml-file;
2. Import secrets from yaml-file to Vault;
3. Remove all secrets from particular path.

# Install
pip install -r requirements.txt

# Configuration
config.yaml - file with configuration of Vault connection
```
vault_url:   http://vault:8200
vault_token: 111
```

# Usage
vault-secrets-supplier.py --help
## Export
```
vault-secrets-supplier.py export --path '/path/to/secrets/' --file secrets.yaml
```
Secrets will be saved in format:
/path/to/particular/secret:
  key: value
If file doesn't set 'exported.yaml' will be used.

## Import
```
vault-secrets-supplier.py import --file secrets.yaml
```
There is 'force' argument which allows to rewrite already existed secrets.
If file doesn't set 'secrets.yaml' will be used.

## Removing
```
vault-secrets-supplier.py delete --path '/path/to/secrets/'
```
By default confirmation of every removing secret is needed, but you can use 'force' argument which would allow to avoid this behavior.
