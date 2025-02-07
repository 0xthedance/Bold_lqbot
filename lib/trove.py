import logging

from lib.utils import get_eth_price
from lib.constants import MIN_CLR


logger = logging.getLogger("my_logger")


class Trove:
    """Class to create LQTY trove instances"""

    def __init__(self, trove_id: int, coll: int, debt: int) -> None:
        self.trove_id = trove_id
        self.coll = coll
        self.debt = debt
        self.coll_debt_ratio = coll / debt if debt != 0 else None

    def __repr__(self) -> str:

        return f"Trove(trove_id='{self.trove_id}', coll={self.coll}, debt={self.debt})"

    def __eq__(self, other_test_class):
        if not isinstance(other_test_class, Trove):
            return False
        return (
            (self.trove_id == other_test_class.trove_id)
            and (self.coll == other_test_class.coll)
            and (self.debt == other_test_class.debt)
        )

    def check(self) -> bool:
        """Funtion to check if CR is below the threshold"""
        if self.debt == 0:
            return False

        eth_price = get_eth_price()
        logger.info("eth price: %s", eth_price)

        if eth_price < 0:
            return False

        coll_ratio = (self.coll * eth_price) / (self.debt)
        logger.info("price %s{} CR %s", eth_price, coll_ratio)

        return coll_ratio < MIN_CLR

    def estimate_compensation(self) -> float:
        """returns trove liquidation compensation in ETH"""
        decimals = 10**18
        return 5 * (10**-3) * (self.coll / decimals)
