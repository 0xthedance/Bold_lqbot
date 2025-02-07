from unittest.mock import patch, call
from typing import Literal

import pytest

from lib.liquidation_bot import LiquidationBot
from lib.liquity import Trove

from tests.liquity_mock import LiquityMock, mock_liquity
from lib.trove_db import initialize_db


class LiquityTrove:
    """Mock Trove class"""

    def __init__(self, id, coll, debt) -> None:
        self.id = id
        self.coll = coll
        self.debt = debt


troves = [
    LiquityTrove(1, coll=100 * 10**18, debt=3500 * 10**18),
    LiquityTrove(2, coll=150 * 10**18, debt=10000 * 10**18),
    LiquityTrove(3, coll=5 * 10**18, debt=3000 * 10**18),
    LiquityTrove(4, coll=20 * 10**18, debt=8000 * 10**18),
    LiquityTrove(5, coll=1000 * 10**18, debt=1000000 * 10**18),
    LiquityTrove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
    LiquityTrove(7, coll=0.5 * 10**18, debt=4000 * 10**18),
]

troves_list = [
    Trove(1, coll=100 * 10**18, debt=3500 * 10**18),
    Trove(2, coll=150 * 10**18, debt=10000 * 10**18),
    Trove(3, coll=5 * 10**18, debt=3000 * 10**18),
    Trove(4, coll=20 * 10**18, debt=8000 * 10**18),
    Trove(5, coll=1000 * 10**18, debt=1000000 * 10**18),
    Trove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
    Trove(7, coll=5 * 10**17, debt=4000 * 10**18),
]

sorted_trove_list = [
    Trove(7, coll=5 * 10**17, debt=4000 * 10**18),
    Trove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
    Trove(5, coll=1000 * 10**18, debt=1000000 * 10**18),
    Trove(3, coll=5 * 10**18, debt=3000 * 10**18),
    Trove(4, coll=20 * 10**18, debt=8000 * 10**18),
    Trove(2, coll=150 * 10**18, debt=10000 * 10**18),
    Trove(1, coll=100 * 10**18, debt=3500 * 10**18),
]
troves_total_liquidation = [
    Trove(7, coll=5 * 10**17, debt=4000 * 10**18),
    Trove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
    Trove(5, coll=1000 * 10**18, debt=1000000 * 10**18),
    Trove(3, coll=5 * 10**18, debt=3000 * 10**18),
    Trove(4, coll=20 * 10**18, debt=8000 * 10**18),
    Trove(2, coll=150 * 10**18, debt=10000 * 10**18),
    Trove(1, coll=100 * 10**18, debt=3500 * 10**18),
]

troves_partial_liquidation = [
    Trove(7, coll=0.5 * 10**18, debt=4000 * 10**18),
    Trove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
]


@pytest.mark.parametrize(
    "test_trove,expected_output",
    [
        (
            Trove("0xAddress1", coll=0.5 * 10**18, debt=5000 * 10**18),
            True,
        ),  # liquidation case
        (Trove("0xAddress1", coll=5.5 * 10**18, debt=5000 * 10**18), False),
        (Trove("0xAddress1", coll=5.5 * 10**18, debt=0), False),
    ],
)
@patch("lib.trove.get_eth_price")
def test_check(mock_get_eth_price, test_trove, expected_output):
    mock_get_eth_price.return_value = 2000
    assert test_trove.check() == expected_output


@pytest.mark.parametrize(
    "batch_size,expected_output",
    [
        (2, troves_list),
        (7, troves_list),
        (9, troves_list),
    ],
)
def test_get_trove_list(
    mock_liquity: LiquityMock,
    batch_size: Literal[2, 7, 9],
    expected_output: list[Trove],
) -> None:
    """test get_trove_list method from LiquidationBot class"""

    bot = mock_liquity(troves, batch_size)

    result = bot.get_trove_list()

    assert result == expected_output


@pytest.mark.parametrize(
    "eth_price,expected_output",
    [
        (30, troves_total_liquidation),  # All troves
        (1500, troves_partial_liquidation),
        (10000, []),  # No troves
    ],
)
@patch("lib.trove.get_eth_price")
def test_check_batch_troves(
    mock_get_eth_price,
    mock_liquity: LiquityMock,
    eth_price,
    expected_output: list[Trove],
) -> None:
    """test check_batch_trove method from LiquidationBot class"""
    mock_get_eth_price.return_value = eth_price

    bot = mock_liquity(troves_list, 3)
    result = bot.check_batch_troves(sorted_trove_list)
    assert result == expected_output


@pytest.mark.parametrize(
    "mock_gas_response,address_liquidated",
    [
        (
            1,
            ["0xAddress4", "0xAddress7", "0xAddress6", "0xAddress5"],
        ),  # the compensation is higher than the gas, batch_liquidate_troves is called
        (8, ["0xAddress4", "0xAddress7", "0xAddress6"]),
        (
            15,
            [],
        ),  # the compensation is lower than the gas, batch_liquidate_troves is not called
    ],
)
@patch.object(LiquityMock, "batch_liquidate_troves")
@patch("lib.liquidation_bot.estimate_gas_price")
def test_liquidate_list_of_troves(
    mock_gas_estimation,
    mock_batch_liquidate,
    mock_liquity,
    mock_gas_response,
    address_liquidated,
):
    mock_gas_estimation.return_value = mock_gas_response
    bot = mock_liquity(troves_list, 5)
    troves = [
        Trove("0xAddress4", coll=2 * 10**18, debt=900 * 10**18),
        Trove("0xAddress7", coll=0.5 * 10**18, debt=900 * 10**18),
        Trove("0xAddress6", coll=0.4 * 10**18, debt=8000 * 10**18),
        Trove("0xAddress5", coll=0.1 * 10**18, debt=2000 * 10**18),
    ]

    bot.liquidate_list_of_troves(troves)

    if mock_gas_response == 15:
        mock_batch_liquidate.assert_not_called()
    else:
        mock_batch_liquidate.assert_called_once_with(address_liquidated)


@pytest.mark.parametrize(
    "eth_price, expected_calls, calls",
    [
        (10000, 0, []),
        (
            30,
            2,
            [
                call(
                    [
                        Trove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
                        Trove(5, coll=1000 * 10**18, debt=1000000 * 10**18),
                        Trove(2, coll=150 * 10**18, debt=10000 * 10**18),
                        Trove(1, coll=100 * 10**18, debt=3500 * 10**18),
                    ]
                ),
                call(
                    [
                        Trove(4, coll=20 * 10**18, debt=8000 * 10**18),
                        Trove(3, coll=5 * 10**18, debt=3000 * 10**18),
                        Trove(7, coll=5 * 10**17, debt=4000 * 10**18),
                    ]
                ),
            ],
        ),
        (
            1500,
            1,
            [
                call(
                    [
                        Trove(6, coll=350000 * 10**18, debt=900000000 * 10**18),
                        Trove(7, coll=0.5 * 10**18, debt=4000 * 10**18),
                    ]
                )
            ],
        ),
    ],
)
@patch.object(LiquidationBot, "liquidate_list_of_troves")
@patch("lib.trove.get_eth_price")
def test_run_bot(
    mock_geth_eth_price,
    mock_liquidation,
    mock_liquity,
    eth_price,
    expected_calls,
    calls,
):

    initialize_db(troves_list)

    mock_geth_eth_price.return_value = eth_price

    bot = mock_liquity(troves_list, 5)
    bot.run_bot()
    assert mock_liquidation.call_count == expected_calls
    if expected_calls > 0:
        mock_liquidation.assert_has_calls(calls)
