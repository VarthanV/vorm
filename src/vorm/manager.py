import inspect
from fields import NotProvided
from typing import Any, List
import mysql.connector as connector
import fields
from collections import namedtuple

CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"


class ConnectionManager:
    db_engine = ""
    db_connection = None

    @property
    def table_name(self):
        return self.model_class.table_name or self._get_table_name()

    def _get_table_name(self):
        pass

    def create_connection(self, db_settings: dict):
        self.db_engine = db_settings.pop("ENGINE")
        if self.db_engine == "mysql":
            self._connect_to_mysql(db_settings)

    def __init__(self, db_settings) -> None:
        self.create_connection(db_settings)

    def _connect_to_mysql(self, db_settings: dict):
        try:
            connection = connector.connect(**db_settings)
            connection.autocommit = True
            self.db_connection = connection
        except Exception as e:
            print(e)
            return

    def _get_cursor(self):
        return self.db_connection.cursor()

    def _execute_query(self, query, variables=None):
        print(query)
        if variables:
            return self._get_cursor().execute(query, variables)
        return self.db_connection.cursor().execute(query)

    def migrate(self, table):
        _create_sql = self._get_create_sql(table)
        self._execute_query(query=_create_sql)

    def _get_create_sql(self, table) -> List:
        _fields_list = []
        for name, field in inspect.getmembers(table):
            attr_string = ""
            if name.startswith("_") or name == "table_name":
                continue
            if isinstance(field, fields.CharField):
                if field.max_length:
                    attr_string += "VARCHAR({}) ".format(field.max_length)

            if not isinstance(field, fields.CharField):
                attr_string += "{} ".format(field.field_sql_name)

            if field.primary_key:
                attr_string += "PRIMARY KEY "

            if not field.nullable:
                attr_string += "NOT NULL "

            if field.default is not NotProvided:
                if isinstance(field, fields.CharField):
                    attr_string += "DEFAULT '{}'".format(field.default)
                elif isinstance(field, fields.IntegerField):
                    attr_string += "DEFAULT {}".format(field.default)
            _fields_list.append((name, attr_string))

        _fields_list = [" ".join(x) for x in _fields_list]
        return CREATE_TABLE_SQL.format(
            name=table.table_name, fields=", ".join(_fields_list)
        )

    def select(self, *args) -> Any:
        pass

    def raw(self, query: str):
        return self._execute_query(query)

    @classmethod
    def save(cls, table):
        pass


class MetaModel(type):
    manager = ConnectionManager

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