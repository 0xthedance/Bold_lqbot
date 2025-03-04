import logging

from ape import Contract, chain, accounts, networks
from ape.exceptions import ContractLogicError


from lib.constants import (
    ACCOUNT_ALIAS,
    DEFAULT_PRIORITY_FEE,
    NETWORK_CONFIG,
)

account = accounts.load(ACCOUNT_ALIAS)
account.set_autosign(True)

logger = logging.getLogger("my_logger")


def load_network_constants() -> dict:
    network_name = networks.provider.network.name
    print("net:", network_name)
    if network_name not in NETWORK_CONFIG:
        raise ValueError(f"Network not supported: {network_name}")

    network_constants = {
        "TROVE_MANAGER": NETWORK_CONFIG[network_name]["TROVE_MANAGER"],
        "MULTI_TROVE_GETTER": NETWORK_CONFIG[network_name]["MULTI_TROVE_GETTER"],
        "BORROWER_OPERATIONS": NETWORK_CONFIG[network_name]["BORROWER_OPERATIONS"],
        "FLASHBOT": NETWORK_CONFIG[network_name]["FLASHBOT"],
    }
    return network_constants


def activate_flashbot() -> bool:
    return load_network_constants()["FLASHBOT"]


def get_eth_price(coll_index) -> float:
    """Fetch ETH price in a smart contract Oracle"""
    decimals = 10**18
    network_name = networks.provider.network.name
    if network_name == "mainnet":
        COLL_USD_PRICE_FEED = NETWORK_CONFIG[network_name]["COLL_USD_PRICE_FEED"][
            coll_index
        ]
        contract = Contract(COLL_USD_PRICE_FEED)
        try:
            eth_price = contract.fetchPrice.call()
            print(eth_price[0], "eth_price")
            return eth_price[0] / decimals
        except ContractLogicError as err:
            logger.error("Cannot fetch eth price due this error %s", err)
            return -1
    else:
        return 2000  # for testing purposes,


def estimate_gas_price() -> int:
    """Function that estimates the actual gas price fetching it from the last block.
    returns gas price in GWei
    Don't pay a priority fee by default when using Flashbots"""
    network_constants = load_network_constants()

    try:
        block = chain.provider.get_block("latest")  # obtain base fee
    except Exception as err:
        logger.error("Imposible to obtain base fee due an error: %s", err)
        return -1
    if network_constants["FLASHBOT"]:
        priority_fee = 0
    else:
        priority_fee = DEFAULT_PRIORITY_FEE
    max_gas_fee = (block.base_fee * 2) + priority_fee
    return max_gas_fee * 10**-9  # convert to Gwei
