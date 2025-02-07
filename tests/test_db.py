import sqlite3
from lib.trove import Trove
from unittest.mock import patch

   
from lib.trove_db import  initialize_db, fetch_troves, update_trove, eliminate_from_db
from tests.liquity_mock import LiquityMock, mock_liquity


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


def test_save_trove_list():

    initialize_db(troves_list)


    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM troves")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == len(troves_list)


def test_fetch_troves():

    troves_fetched = fetch_troves()

    assert troves_fetched == sorted_trove_list


def test_update_trove():

    updated_data = Trove(1, 100, 50)
    update_trove(updated_data)

    # Assert
    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, coll, debt FROM troves WHERE id = 1")
    updated_data = cursor.fetchone()
    conn.close()

    assert updated_data == ("1", "100", "50"), "Trove should be updated with new values"


def test_eliminate_from_db():
    # Arrange

    eliminate_from_db(1)

    # Assert
    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM troves WHERE id = ? LIMIT 1", (1,))
    count = cursor.fetchone()
    conn.close()

    assert count is None


def test_update_db():
    
    updated_troves = 

    bot = mock_liquity(troves_list, 5)

    update_db(bot)

    # Assert
    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM troves WHERE id = ? LIMIT 1", (1,))
    count = cursor.fetchone()
    conn.close()

    assert count is None