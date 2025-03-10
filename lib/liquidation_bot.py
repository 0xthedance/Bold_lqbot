import logging


from lib.liquity import Trove, LiquityMethods
from lib.utils import estimate_gas_price
from lib.constants import MAX_TROVES_TO_LIQUIDATE
from lib.trove_db import fetch_troves

logger = logging.getLogger("my_logger")


class LiquidationBot:
    def __init__(self, liquity: LiquityMethods, batch_size) -> None:
        self.liquity = liquity
        self.batch_size = batch_size

    def get_trove_list(self) -> list[Trove]:
        """Function to obtain all the trove list from MultiTroveGetter"""
        trove_count = self.liquity.get_trove_owners_count()
        n_troves = self.batch_size
        start_ind = 0
        more_troves = trove_count > 0
        trove_list = []

        while more_troves:
            logger.info("quering %s troves", n_troves)

            if trove_count < n_troves:
                n_troves = trove_count
                more_troves = False

            trove_details = self.liquity.get_multiple_sorted_troves(start_ind, n_troves)
            logger.debug(" %s troves obtained by multitrovegetter", trove_details)
            if trove_details == 0:
                break

            start_ind += self.batch_size
            trove_count -= self.batch_size

            for trove in trove_details:
                trove = Trove(trove.id, trove.entireColl, trove.entireDebt)
                trove_list.append(trove)
        logger.debug(" %s troves obtained after processing", trove_list)

        return trove_list

    def check_batch_troves(self, trove_list: list[Trove]) -> list[Trove]:
        """select the troves to be liquidated from a batch of troves"""
        selected = []
        for trove in trove_list:
            if not trove.check(self.liquity.coll_index):
                logger.debug(trove.check(self.liquity.coll_index))
                break
            selected.append(trove)
        logger.info("troves with CR below the minimum:%s", selected)
        return selected

    def liquidate_list_of_troves(self, selected: list[Trove]) -> None:
        """Function that liquidate the list of troves if the transaction is profitable"""
        """ Rough gas requirements:
            * In normal mode:
                - using Stability Pool: 400K + n * 176K
                - using redistribution: 377K + n * 174K
            * In recovery mode:
                - using Stability Pool: 415K + n * 178K
                - using redistribution: 391K        + n * 178K
            `500K + n * 200K` should cover all cases (including starting in recovery mode and ending in
            normal mode) with some margin for safety.
        """
        gas = estimate_gas_price()
        logger.info("Gas price: %s", gas)

        if gas < 0:
            logger.info("It was not possible to proceed with the liquidation")
            return
        compensation = 0
        cost_initial = (500 * 10**3 * gas) * 10**-9  # ETH
        cost_per_trove = (200 * 10**3 * gas) * 10**-9
        last_revenue = -cost_initial
        troves_to_liquidate = []
        for trove in selected:
            compensation = trove.estimate_compensation()
            logger.debug(" coll %s", trove.coll)
            logger.debug("compensation %s", compensation)
            logger.debug("last rev %s", last_revenue)
            new_revenue = last_revenue + compensation - cost_per_trove
            logger.debug("  --> new %s", new_revenue)
            if new_revenue < last_revenue:
                break
            troves_to_liquidate.append(trove)
            last_revenue = new_revenue
        logger.debug("last revenue %s", last_revenue)
        if last_revenue > 0:
            trove_ids = []
            logger.info(
                "Sending to liquidate the following troves %s", troves_to_liquidate
            )
            for trove in troves_to_liquidate:
                trove_ids.append(trove.trove_id)
            self.liquity.batch_liquidate_troves(trove_ids)
        else:
            logger.info(
                "It is not profitable to liquidate troves. The collateral is insufficient, and there is no benefit from this operation."
            )

    def run_bot(self):
        """Launch the bot"""
        selected = []
        logger.info("starting the check")
        list_troves = fetch_troves(self.liquity.coll_index)
        logger.debug(" %s troves fetched from db", list_troves)

        selected = self.check_batch_troves(list_troves)
        logger.debug(" %s troves selected", selected)

        if len(selected) <= 0:
            logger.info("Nothing to liquidate")
        else:
            selected.sort(key=lambda x: x.coll, reverse=True)
            for i in range(0, len(selected), MAX_TROVES_TO_LIQUIDATE):
                self.liquidate_list_of_troves(selected[i: i + MAX_TROVES_TO_LIQUIDATE])
