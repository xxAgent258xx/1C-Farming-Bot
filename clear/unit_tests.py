import unittest
from bot_const import select_from_db
import sqlite3


# DB_NAME = 'unit_tests.db'
# connector = sqlite3.connect(DB_NAME)
# cursor = connector.cursor()
#
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS "main_table" (
# "test_int"	INTEGER,
# "test_str"	TEXT);
# """)
#
# cursor.execute("DELETE FROM main_table")
# cursor.execute('INSERT INTO main_table VALUES(123, "abc")')
# cursor.execute('INSERT INTO main_table VALUES(456, "def")')
#
# connector.commit()
# cursor.close()
# connector.close()


class TestDatabaseOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DB_NAME = 'unit_tests.db'
        connector = sqlite3.connect(DB_NAME)
        cursor = connector.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "main_table" (
        "test_int"	INTEGER,
        "test_str"	TEXT);
        """)

        cursor.execute("DELETE FROM main_table")
        cursor.execute('INSERT INTO main_table VALUES(123, "abc")')
        cursor.execute('INSERT INTO main_table VALUES(456, "def")')

        connector.commit()
        cursor.close()
        connector.close()

    async def test_select_two_rows_two_columns(self):
        result = await select_from_db('SELECT * FROM main_table')
        self.assertEqual(result, [[123, "abc"], [456, "def"]])

    async def test_select_one_row_two_columns(self):
        result = await select_from_db('SELECT * FROM main_table WHERE test_int=123')
        self.assertEqual(result, [123, "abc"])

    async def test_select_two_rows_one_column(self):
        result = await select_from_db('SELECT test_int FROM main_table')
        self.assertEqual(result, [[123], [456]])

    async def test_select_one_row_one_column(self):
        result = await select_from_db('SELECT test_int FROM main_table WHERE test_int=123')
        self.assertEqual(result, [123])


if __name__ == '__main__':
    unittest.main()
