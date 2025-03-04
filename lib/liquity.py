import logging

from ape.exceptions import ContractLogicError, OutOfGasError
from ape import Contract

from lib.utils import estimate_gas_price, account, activate_flashbot

from lib.trove import Trove
from lib.trove_db import eliminate_from_db

logger = logging.getLogger("my_logger")


class LiquityMethods:
    """Class containing the LQTY methods"""

    def __init__(
        self,
        coll_index,
        trove_manager_address,
        multi_trove_getter_address,
        borrower_operations_address,
    ) -> None:
        self.coll_index = coll_index
        self.trove_manager = Contract(trove_manager_address[coll_index])
        self.multi_trove_getter = Contract(multi_trove_getter_address[coll_index])
        self.borrower_operations = Contract(borrower_operations_address[coll_index])

    def get_trove_owners_count(self) -> int:
        """Query trove manager to fetch number of troves in the protocol"""
        try:
            return self.trove_manager.getTroveIdsCount()
        except ContractLogicError as err:
            logger.error("Cannot fetch trove count due this error %s", err)
            return 0

    def get_multiple_sorted_troves(self, start_ind, n_troves) -> list:
        """Query MultiTroveGetter to fecth n_troves starting in start_ind"""
        try:
            trove_details = self.multi_trove_getter.getMultipleSortedTroves(
                self.coll_index, start_ind, n_troves
            )  # CombinedTroveData
            print(trove_details, "trove_details")
            return trove_details
        except ContractLogicError as err:
            logger.error("Cannot fetch troves due this error %s", err)
            return 0

    def batch_liquidate_troves(self, trove_ids):
        """Call trove manager contract to liquidate a batch of trove_ids"""
        logger.info("   %s", trove_ids)
        logger.debug("   %s", self.trove_manager)
        logger.debug("   %s", activate_flashbot)

        try:
            self.trove_manager.batchLiquidateTroves(
                trove_ids, sender=account, private=activate_flashbot
            )
            eliminate_from_db(trove_ids, self.coll_index)
        except ContractLogicError as err:
            logger.error(
                "It was not possible to liquidate the troves batch due the following error: %s",
                err,
            )
        except OutOfGasError as err:
            logger.critical(
                "Out of gas. Exiting Liquidation : %s",
                err,
            )
            exit()

    def get_trove_details(self, trove_id) -> Trove:
        """Call trove manager contract to obtain the details (call and debt) from a trove id"""

        try:
            trove_details = self.trove_manager.getLatestTroveData(trove_id)  # troveId
            trove = Trove(trove_id, trove_details.coll, trove_details.debt)
            return trove
        except ContractLogicError as err:
            logger.error(err)
            return 0

    def get_trove_status(self, trove_id) -> str:
        """Call trove manager contract to obtain the trove Status"""
        return self.trove_manager.getTroveStatus(trove_id)

    def liquidate(self, trove) -> None:
        """Call trove manager contract to liquidate a single trove"""
        gas = estimate_gas_price()
        if gas < 0:
            logger.info("It was not possible to proceed with the liquidation")
            return
        compensation = trove.estimate_compensation()
        cost = ((500 * 10**3) + (200 * 10**3) * gas) * 10**-9
        rev = compensation - cost
        if rev > 0:
            try:
                self.trove_manager.liquidate(
                    trove.trove_id, sender=account, private=activate_flashbot
                )  # private to send it through Flashs.Alchemy already supports it.
                logger.info(
                    "The following trove %s has been liquidated with a compensation of %s",
                    trove.trove_id,
                    compensation,
                )
                eliminate_from_db(trove.trove_id, self.coll_index)

            except ContractLogicError as err:
                logger.error(
                    "It was not possible to liquidate the trove due a contract error %s",
                    err,
                )

            except OutOfGasError as err:
                logger.critical(
                    "Out of gas. Exiting Liquidation : %s",
                    err,
                )
                exit()
