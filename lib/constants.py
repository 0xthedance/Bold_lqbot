import os

# collateral: ETH, Lido ETH (wstETH) and Rocket Pool ETH (rETH).
NETWORK_CONFIG = {
    "mainnet": {
        "TROVE_MANAGER": [
            "0x81d78814df42da2cab0e8870c477bc3ed861de66",
            "0xb47eF60132dEaBc89580Fd40e49C062D93070046",
            "0xde026433882a9DdED65cAc4FfF8402FAFFF40FcA",
        ],
        "MULTI_TROVE_GETTER": [
            "0x0C6Ae14FFdfA799b6d456483bEBf52D7bC2Ec978",
            "0x0C6Ae14FFdfA799b6d456483bEBf52D7bC2Ec978",
            "0x0C6Ae14FFdfA799b6d456483bEBf52D7bC2Ec978",
        ],
        "BORROWER_OPERATIONS": [
            "0x0B995602B5a797823f92027E8b40c0F2D97Aff1C",
            "0x94C1610a7373919BD9Cfb09Ded19894601f4a1be",
            "0xA351d5B9cDa9Eb518727c3CEFF02208915fda60d",
        ],
        "COLL_USD_PRICE_FEED": [
            "0x3279e2B49ff60dAFb276FBAFF847383B67a7ec2d",
            "0x4c275608887ad2eB049d9006E6852BC3ee8A00Fa",
            "0x93d3a2234e67C2aD494735cd6676fb4b79a6De97",
        ],
        "FLASHBOT": True,
    },
    "sepolia": {
        "TROVE_MANAGER": [
            "0x70fa06222e169329f7a2f386ed70ad69a61228a5",
            "0xa7B57913b5643025A15C80ca3a56Eb6fb59D095D",
            "0x310fa1d1d711c75da45952029861bcf0d330aa81",
        ],
        "MULTI_TROVE_GETTER": [
            "0x4fd20634B666E0d6A62499934484054B1634250B",
            "0x4fd20634B666E0d6A62499934484054B1634250B",
            "0x4fd20634B666E0d6A62499934484054B1634250B",
        ],
        "BORROWER_OPERATIONS": [
            "0x2377b5a07bdfa02812203bab749e7bd43e4c596c",
            "0x4e7de0a55e967a174f47621b9f993068f96f6898",
            "0x274ba4234b3e0a16f830b4a07bc99a33fbc19ba8",
        ],
        "FLASHBOT": False,
    },
}


# Recipient of liquidation rewards
ACCOUNT_ALIAS = os.environ["ACCOUNT_ALIAS"]

MIN_CR = [1.10, 1.20, 1.20]

# About 2M gas required to liquidate 10 Troves (much of it is refunded though).
MAX_TROVES_TO_LIQUIDATE = 4


DEFAULT_PRIORITY_FEE = 5 * 10**9
