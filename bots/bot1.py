import time
import asyncio


from ape.types import ContractLog
from ape import networks, accounts


from silverback import SilverbackBot

from lib.liquidation_bot import LiquidationBot
from lib.liquity import LiquityMethods
from lib.logging import configure_logging
from lib.utils import load_network_constants
from lib.trove_db import initialize_db, eliminate_from_db, update_trove, update_db

bot = SilverbackBot()

network_constants = load_network_constants()

collateral = 1

liquity = LiquityMethods(
    collateral,
    network_constants["TROVE_MANAGER"],
    network_constants["MULTI_TROVE_GETTER"],
    network_constants["BORROWER_OPERATIONS"],
)
LQTY_bot = LiquidationBot(liquity, batch_size=100)

logger = configure_logging()


async def update_list_troves(LQTY_bot):
    print("updating list of troves")

    await update_db(LQTY_bot, coll_index=collateral)


@bot.on_startup()
def start_bot(startup_state):
    """Launch liquidation bot once upon every application startup."""

    list_troves = LQTY_bot.get_trove_list()
    initialize_db(list_troves, coll_index=collateral)

    count = 0
    while True:
        try:
            LQTY_bot.run_bot()
        except Exception as err:
            logger.error("the bot exited due to an error: %s", err)

        logger.info("sleeping")
        time.sleep(10)

        if count == 1:
            asyncio.run(update_list_troves(LQTY_bot))
            count = 0
        count += 1


@bot.on_(liquity.trove_manager.TroveOperation)
def add_new_trove(trove_operation_log: ContractLog, liquity) -> None:
    """Function that executes the necessary actions when a new trove is created
    new_trove (ContractLog): Information from the contract log corresponding to the newly created trove.
    """
    logger.info("TroveOperation Event triggered")
    trove_id = trove_operation_log._troveId
    status = liquity.get_trove_status(trove_id)

    if status == "closedByLiquidation" or "closedByOwner":
        eliminate_from_db(trove_id, coll_index=liquity.coll_index)
        return

    trove = liquity.get_trove_details(trove_id)
    if trove == 0:
        return
    if trove.check(liquity.coll_index):
        liquity.liquidate(trove.trove_id)
    else:
        update_trove(trove, coll_index=liquity.coll_index)
