import os
import click
from ape import accounts, project
from ape.cli import ConnectedProviderCommand


@click.command(cls=ConnectedProviderCommand)
def cli(network, provider):
    # You need an account to deploy, as it requires a transaction.
    print("Deploying contract to", network)
    account = accounts.load(
        os.environ["ACCOUNT_ALIAS"]
    )  # NOTE: <ACCOUNT_ALIAS> refers to your account alias!
    contract = account.deploy(
        project.MultiTroveGetter, "0x55cefb9c04724ba3c67d92df5e386c6f1585a83b"
    )
    print("Deployed to", contract.address)
