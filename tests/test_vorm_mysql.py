import unittest
from . mock_data import Student
from vorm.manager import ConnectionManager as db


class TestVorm(unittest.TestCase):

    def test_create_sql_with_valid_table(self):
        expected_query = 'CREATE TABLE students (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `age` INT NOT NULL , `clas` VARCHAR(200) NOT NULL , `name` VARCHAR(300) NOT NULL );'
        sql_query = db._get_create_sql(Student)
        self.assertEqual(sql_query, expected_query)


if __name__ == "__main__":
    unittest.main()
