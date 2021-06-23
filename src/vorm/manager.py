from typing import Any
from mysql.connector import connect


class ConnectionManager:
    db_cursor = None
    db_engine = ""

    def __init__(self, model_class) -> None:
        self.model_class = model_class

    @property
    def table_name(self):
        return self.model.table_name

    @classmethod
    def create_connection(cls, db_settings: dict):
        cls.db_engine = db_settings.pop("ENGINE")
        if cls.db_engine == "mysql":
            cls.db_cursor = cls._connect_to_mysql(db_settings)

    @classmethod
    def _connect_to_mysql(cls, db_settings: dict):
        try:
            db_name = db_settings.pop("db_name")
            connection = connect(**db_settings)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(f"USE {db_name}")
            return cursor
        except Exception as e:
            print(e)

    @classmethod
    def _get_cursor(cls):
        return cls.db_cursor

    @classmethod
    def _execute_query(cls, query, variables):
        cls.db_cursor.execute(query, variables)

    def select(self, **kwargs) -> Any:
        print(kwargs)

    def raw(self, query: str):
        return self._execute_query(query)


class MetaModel(type):
    manager = ConnectionManager

    def _get_manager(cls) -> ConnectionManager:
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls) -> ConnectionManager:
        return cls._get_manager()
