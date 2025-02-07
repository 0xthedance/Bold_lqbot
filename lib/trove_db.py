import sqlite3
import time
from lib.trove import Trove


def initialize_db(troves_list: list[Trove]):
    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS troves (
            id TEXT PRIMARY KEY,
            coll TEXT NOT NULL,
            debt TEXT NOT NULL
        )
    """
    )
    for trove in troves_list:
        cursor.execute(
            """
            INSERT OR REPLACE INTO troves (id, coll, debt) 
            VALUES (?, ?, ?);
        """,
            (str(trove.trove_id), str(trove.coll), str(trove.debt)),
        )

    conn.commit()
    conn.close()


def fetch_troves() -> list[Trove]:
    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, coll, debt FROM troves WHERE debt!= ?", ("0",))
    rows = cursor.fetchall()

    list_troves = [
        Trove(trove_id=int(row[0]), coll=int(row[1]), debt=int(row[2])) for row in rows
    ]

    conn.close()
    sorted_trove_list = sorted(list_troves, key=lambda trove: trove.coll_debt_ratio)

    return sorted_trove_list


def update_trove(trove: Trove):
    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT OR REPLACE INTO troves (id, coll, debt) 
            VALUES (?, ?, ?)
        """,
        (str(trove.trove_id), str(trove.coll), str(trove.debt)),
    )
    conn.commit()
    conn.close()


def eliminate_from_db(trove_id):

    conn = sqlite3.connect("troves.db")
    cursor = conn.cursor()

    cursor.execute("""DELETE FROM troves WHERE id = ?""", (str(trove_id),))

    conn.commit()
    conn.close()


async def update_db(LQTY_bot):
    """
    Update the troves database with the latest data from the LQTY bot.

    Args:
        LQTY_bot: An instance of the LQTY bot that provides the latest trove data.
    """

    list_troves = LQTY_bot.get_trove_list()

    troves = [
        (str(trove.trove_id), str(trove.coll), str(trove.debt)) for trove in list_troves
    ]

    sql = "UPDATE troves SET coll=?, debt=? WHERE id = ?"

    try:
        with sqlite3.connect("troves.db") as conn:
            cur = conn.cursor()
            cur.executemany(sql, troves)
            conn.commit()
    except sqlite3.OperationalError as e:
        print(e)

    print("updated list of troves")
    time.sleep(10)
