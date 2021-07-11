import inspect
from vorm.exceptions import VormAttributeError
from .fields import NotProvided
from typing import Any, List
import mysql.connector as connector
from . import fields
from .types import Condition
from pprint import pprint


class _Constants:
    CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
    INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
    SELECT_WHERE_SQL = "SELECT {fields} FROM {name} WHERE {query};"
    SELECT_ALL_SQL = "SELECT {fields} FROM {name};"
    SEPERATOR = "__"
    FIELDS_TO_EXCLUDE_IN_INSPECTION = ["table_name", "manager_class"]


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
    def table_name(self) -> str:
        return self.model_class.table_name or self._get_table_name()

    @property
    def _get_fields(self):
        cursor = self._get_cursor()

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
        _fields_list = [
            ('id', 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY')
        ]
        for name, field in inspect.getmembers(table):
            attr_string = ""
            if name.startswith("_") or name in _Constants.FIELDS_TO_EXCLUDE_IN_INSPECTION:
                continue
            if isinstance(field, fields.ForeignKey):
                _col_name = "{}_id".format(name)
                _fields_list.append((_col_name, 'INT'))
                _fields_list.append(
                    ("FOREIGN KEY({column})".format(
                        column=_col_name),
                        "REFERENCES {table_name}({referred_column})".
                        format(table_name=field.table.table_name, referred_column='id')))
                continue

            if isinstance(field, fields.CharField):
                if field.max_length:
                    attr_string += "VARCHAR({}) ".format(field.max_length)

            if not isinstance(field, fields.CharField):
                attr_string += "{} ".format(field.field_sql_name)

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
        return str(val)

    def _dict_to_model_class(self, d, table):
        return table(**d)

    def _return_foreign_keys_from_a_table(self, model_class, query_dict):
        for name, field in inspect.getmembers(model_class):
            if isinstance(field, fields.ForeignKey):
                column_name = '{}_id'.format(name)
                result_set = field.table.objects.where(
                    id__eq=query_dict[column_name])
                setattr(model_class, name, result_set)
        return model_class

    def where(self, fetch_relations=False, limit=None, **kwargs) -> List:
        condition_list = self._evaluate_user_conditions(kwargs)
        _sql_query = _Constants.SELECT_WHERE_SQL.format(
            name=self.table_name,
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
        self.db_connection.reconnect()
        cur2 = self.db_connection.cursor(buffered=True, dictionary=True)
        if limit:
            _sql_query += ' LIMIT {limit} '.format(limit=limit)
        cur2.execute(_sql_query)
        rows = cur2.fetchall()
        result = list()
        if limit == 1:
            return self._dict_to_model_class(rows[0], self.model_class)

        for i in rows:
            result_class = self._dict_to_model_class(i, self.model_class)
            if fetch_relations:
                result_class = self._return_foreign_keys_from_a_table(
                    result_class, i)

            result.append(result_class)
        return result

    def get_one(self, **kwargs):
        return self.where(limit=1, **kwargs)

    def insert(self, **kwargs):
        fields = list()
        values = list()
        for k, v in kwargs.items():
            fields.append(k)
            values.append(v)
        _sql_query = _Constants.INSERT_SQL.format(
            name='`{}`'.format(self.table_name),
            fields=' , '.join(
                ['`{}`'.format(i) for i in fields]),
            placeholders=' , '.join([self._get_parsed_value(i) for i in values]))
        self._get_cursor().execute(_sql_query)

    def raw(self, query: str):
        return self._execute_query(query)

    @ classmethod
    def save(cls):
        pass


class MetaModel(type):
    manager_class = ConnectionManager

    def _get_manager(cls) -> ConnectionManager:
        return cls.manager_class(model_class=cls)

    @ property
    def objects(cls) -> ConnectionManager:
        return cls._get_manager()

    @ property
    def db_engine(self):
        return self.objects.db_engine
