import argparse
import yaml
import hvac


def parse_vault_path(client, vault_path, secret_paths):
    if not client.read(vault_path):
        for key in client.list(vault_path)['data']['keys']:
            parse_vault_path(client, vault_path + key, secret_paths)
    else:
        secret_paths.append(vault_path)
    return secret_paths


def export_secrets(client, vault_path, file='exported.yaml'):
    ''' Export secrets from vault to file
    '''
    secret_paths = []
    result = {}
    parse_vault_path(client, vault_path, secret_paths)
    for secret_path in secret_paths:
        secret_data = client.read(secret_path)['data']
        result[secret_path] = secret_data
    try:
        with open(file, 'w') as f:
            yaml.dump(result, f)
    except Exception as e:
        print(e)
    else:
        print("{} secrets were exported.".format(len(result)))


def import_secrets(client, file='secrets.yaml', force=False):
    ''' Import secrets from file to vault
    '''
    secrets = yaml.load(open(file), Loader=yaml.BaseLoader)
    for secret in secrets:
        if client.read(secret) and force is False:
            print("The secret {} already exists. "
                "You can use '-f' argument to force rewrite it.".format(secret))
        else:
            try:
                client.write(secret, **secrets[secret])
            except Exception as e:
                print(e)
            else:
                print("The secret {} was successfully wrote.".format(secret))


def delete_secrets(client, vault_path, force=False):
    ''' Delete secrets from vault
    '''
    secret_paths = []
    parse_vault_path(client, vault_path, secret_paths)
    for secret_path in secret_paths:
        approve = False
        if not force:
            if input('Deleting secret {} Are you sure? [no] '.format(secret_path)) == 'yes':
                approve = True
        if approve or force:
            try:
                client.delete(secret_path)
            except Exception as e:
                print(e)
            else:
                print("The secret {} was successfully deleted.".format(secret_path))


def get_cli_args():
    ''' Get arguments from command line
    '''
    parser = argparse.ArgumentParser(description='vault-secrets-supplier')
    parser.set_defaults(func=lambda: parser.print_usage())
    subparsers = parser.add_subparsers(title='subcommands',
                                       help='List of subcommands',
                                       dest="subcommands")
    export_sub = subparsers.add_parser('export', help='Export secrets from Vault')
    import_sub = subparsers.add_parser('import', help='Import secrets to Vault')
    delete_sub = subparsers.add_parser('delete', help='Delete secrets')
    export_sub.add_argument('--path', dest='path',
                        help='Path to secrets', required=True)
    export_sub.add_argument('--file', dest='file',
                        help='File to export secrets to', required=False)
    import_sub.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force rewrite secrets', required=False)
    import_sub.add_argument('--file', dest='file',
                        help='File to import secrets from', required=False)
    delete_sub.add_argument('--path', dest='path',
                        help='Path to secrets', required=True)
    delete_sub.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force delete secrets', required=False)
    return parser.parse_args()


def main():
    config = yaml.load(open('config.yaml'), Loader=yaml.BaseLoader)
    client = hvac.Client(url=config["vault_url"], token=config["vault_token"],
                         verify=False)
    args = get_cli_args()
    if args.subcommands == 'export':
        export_secrets(client, args.path, args.file)
    elif args.subcommands == 'import':
        import_secrets(client, args.file, args.force)
    elif args.subcommands == 'delete':
        delete_secrets(client, args.path, args.force)
    else:
        args.func()


if __name__ == "__main__":
    main()
