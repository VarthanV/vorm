import inspect
from vorm.exceptions import VormAttributeError
from .fields import NotProvided
from typing import Any, List
import mysql.connector as connector
from . import fields
from .types import Condition
from pprint import pprint


# https://stackoverflow.com/questions/775296/mysql-parameterized-queries


class _Constants:
    CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
    INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
    SELECT_WHERE_SQL = "SELECT {fields} FROM {name} WHERE {query};"
    SELECT_ALL_SQL = "SELECT {fields} FROM {name};"
    SEPERATOR = "__"


class ConnectionManager:
    db_engine = ""
    db_connection = None
    operators_map = {
        "eq": "=",
        "gt": ">",
        "lt": "<",
        "gte": ">=",
        "lte": "<=",
        "in": "IN",
        "like": "LIKE",
    }

    def __init__(self, model_class) -> None:
        self.model_class = model_class

    @property
    def table_name(self):
        return self.model_class.table_name or self._get_table_name()

    @classmethod
    def create_connection(cls, db_settings: dict):
        cls.db_engine = db_settings.pop("ENGINE")
        if cls.db_engine == "mysql":
            cls._connect_to_mysql(db_settings)

    @classmethod
    def _connect_to_mysql(cls, db_settings: dict):
        try:
            connection = connector.connect(**db_settings)
            connection.autocommit = True
            cls.db_connection = connection
        except Exception as e:
            print(e)
            return

    @classmethod
    def _get_cursor(cls):
        return cls.db_connection.cursor()

    @classmethod
    def _execute_query(cls, query, variables=None):
        cls._get_cursor().execute(query, variables)

    @classmethod
    def _evaluate_user_conditions(cls, conditions: dict) -> List:
        conditions_list = []
        for k, v in conditions.items():
            val = k.split(_Constants.SEPERATOR)
            condition = Condition(val[0], cls.operators_map[val[1]], v)
            conditions_list.append(condition)
        return conditions_list

    @classmethod
    def migrate(cls, table):
        cls.model_class = table
        if not cls.table_name:
            raise ValueError("Expected to have a table_name")

        _create_sql = cls._get_create_sql(table)
        cls._execute_query(query=_create_sql)

    @classmethod
    def _get_create_sql(cls, table) -> List:
        pprint(table)
        _fields_list = []
        for name, field in inspect.getmembers(table):
            attr_string = ""
            if name.startswith("_") or name in ["table_name", "manager_class"]:
                continue
            if isinstance(field, fields.CharField):
                if field.max_length:
                    attr_string += "VARCHAR({}) ".format(field.max_length)

            if not isinstance(field, fields.CharField):
                attr_string += "{} ".format(field.field_sql_name)

            if field.primary_key:
                attr_string += "PRIMARY KEY "

            if field.auto_increment:
                attr_string += "AUTO_INCREMENT "

            if not field.nullable:
                attr_string += "NOT NULL "

            if field.default is not NotProvided:
                if isinstance(field, fields.CharField):
                    attr_string += "DEFAULT '{}'".format(field.default)
                elif isinstance(field, fields.IntegerField):
                    attr_string += "DEFAULT {}".format(field.default)
            _fields_list.append((name, attr_string))

        _fields_list = [" ".join(x) for x in _fields_list]
        return _Constants.CREATE_TABLE_SQL.format(
            name=table.table_name, fields=", ".join(_fields_list)
        )

    def _get_parsed_value(self, val):
        if type(val) == str:
            return "'{}'".format(val)
        return val

    def where(self, **kwargs) -> List:
        condition_list = self._evaluate_user_conditions(kwargs)
        _sql_query = _Constants.SELECT_WHERE_SQL.format(
            name="students",
            fields="*",
            query=" AND ".join(
                [
                    "`{}` {} {}".format(
                        i.column, i.operator, self._get_parsed_value(i.value)
                    )
                    for i in condition_list
                ]
            ),
        )
        cur2 = self.db_connection.cursor(buffered=True, dictionary=True)
        cur2.execute(_sql_query)
        rows = cur2.fetchall()
        result = list()
        for i in rows:
            result.append(self.model_class(**i))
        return result

    def raw(self, query: str):
        return self._execute_query(query)

    @classmethod
    def save(cls, table):
        pass


class MetaModel(type):
    manager_class = ConnectionManager

    def _get_manager(cls) -> ConnectionManager:
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls) -> ConnectionManager:
        return cls._get_manager()

    @property
    def db_engine(self):
        return self.objects.db_engine


# Manager -> Exectues db transaction,connects with db ,retries ,checks idle connection

# MetaClass -> bridges the manager and model mexposes specific methods from manager to model and required fields from model to manager

# Model -> End user sees , Pythonic representation , Movie


# def eval(**kwargs):
#   for k ,v in kwargs.items():
#     val =  k.split('__')
#     if val[1] == 'eq':
#       s = (val[0],'=',v)
#       print(s)
#     if val[1] == 'gt' :
#       s = (val[0],'>',v)
#       print(s)


# eval(name__eq = 'vishnu',age__gt= 30)
