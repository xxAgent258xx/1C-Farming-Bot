import unittest
import asyncio
from bot_const import select_from_db, insert_into_db

DB_NAME = 'unit_tests.db'


class TestDatabaseOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        asyncio.run(insert_into_db("""
        CREATE TABLE IF NOT EXISTS "main_table" (
        "test_int"	INTEGER,
        "test_str"	TEXT);
        """, db_name=DB_NAME))

        asyncio.run(insert_into_db("DELETE FROM main_table", db_name=DB_NAME))
        asyncio.run(insert_into_db('INSERT INTO main_table VALUES(123, "abc")', db_name=DB_NAME))
        asyncio.run(insert_into_db('INSERT INTO main_table VALUES(456, "def")', db_name=DB_NAME))

    def test_select_two_rows_two_columns(self):
        result = asyncio.run(select_from_db('SELECT * FROM main_table', db_name=DB_NAME))
        self.assertEqual(result, [[123, "abc"], [456, "def"]])

    def test_select_one_row_two_columns(self):
        result = asyncio.run(select_from_db('SELECT * FROM main_table WHERE test_int=123', db_name=DB_NAME))
        self.assertEqual(result, [123, "abc"])

    def test_select_two_rows_one_column(self):
        result = asyncio.run(select_from_db('SELECT test_int FROM main_table', db_name=DB_NAME))
        self.assertEqual(result, [[123], [456]])

    def test_select_one_row_one_column(self):
        result = asyncio.run(select_from_db('SELECT test_int FROM main_table WHERE test_int=123', db_name=DB_NAME))
        self.assertEqual(result, [123])


if __name__ == '__main__':
    unittest.main()
