import unittest
from vorm.types import Condition
from . mock_data import Student
from vorm.manager import ConnectionManager as db


class TestVorm(unittest.TestCase):
    mysql_db_settings = {
        "driver": "mysql",
        "user": "root",
        "password": "root1234",
        "host": "localhost",
        "port": 3306,
        "database": "pizza_shop",
    }
    condition_tuple_list = [Condition(column='age', operator='>', value=15),
                            Condition(column='name', operator='=', value='Vishnu')]

    def setUp(self) -> None:
        self.mysql_db_settings['driver'] = 'mysql'
        self.db = db.create_connection(self.mysql_db_settings)

    def test_create_sql_with_valid_table_method_with_valid_class(self):
        expected_query = 'CREATE TABLE students (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `age` INT NOT NULL , `clas` VARCHAR(200) NOT NULL , `name` VARCHAR(300) NOT NULL );'
        sql_query = self.db._get_create_sql(Student)
        self.assertEqual(sql_query, expected_query)

    def test_evaluate_user_conditions_method_with_valid_condition_dict(self):
        condition_dict = {'age__gt': 15, 'name': 'Vishnu'}
        self.assertEqual(self.db._evaluate_user_conditions(
            condition_dict), self.condition_tuple_list)

if __name__ == "__main__":
    unittest.main()
