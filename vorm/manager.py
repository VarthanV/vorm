import inspect
from typing import List
import mysql.connector as connector
from . import fields
from .types import Condition


class _Constants:
    CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
    INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
    SELECT_WHERE_SQL = "SELECT {fields} FROM {name} WHERE {query};"
    SELECT_ALL_SQL = "SELECT {fields} FROM {name};"
    DELETE_ALL_SQL = "DELETE FROM {name} where {conditions}"
    SEPERATOR = "__"
    FIELDS_TO_EXCLUDE_IN_INSPECTION = ["table_name", "manager_class"]
    KNOWN_CLASSES = (int, float, str, tuple)
    OP_EQUAL = 'eq'
    GET_LAST_INSERTED_ID_SQL = "SELECT LAST_INSERT_ID() as id;"


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
        """
        Returns the table name

        Returns :
            table_name:  A string which has the table name.
        """

        return self.model_class.table_name

    @property
    def _get_fields(self) -> List[str]:
        """
        Returns all the name of co
        """
        cursor = self._get_cursor()
        cursor.execute(
            """
            SELECT column_name, data_type FROM information_schema.columns WHERE table_name=%s
            """,
            (self.table_name, )
        )
        return [row['column_name'] for row in cursor.fetchall()]

    @classmethod
    def create_connection(cls, db_settings: dict):
        """
        Creates a db connection to the specified DB driver
        and 

        Parameters:
            db_settings(dict): The dict which contains the connection 
            details of the driver to be connected.

        Returns :
            None    
        """

        cls.db_engine = db_settings.pop("driver")
        if cls.db_engine == "mysql":
            cls._connect_to_mysql(db_settings)

    @classmethod
    def _connect_to_mysql(cls, db_settings: dict):
        """
        Connects to a MYSQL DB ,It is a internal which will will be used
        by the create_connection method and sets the returned connection to
        the db_connection attribute

        Parameters:
            db_settings(dict): The dict which contains the connection 
            details of the driver to be connected. 

        Returns:
            None    
        """

        try:
            connection = connector.connect(**db_settings)
            connection.autocommit = True
            cls.db_connection = connection
        except Exception as e:
            raise Exception(e)

    @classmethod
    def _get_cursor(cls):
        """
        Returns the cursor of the current db_connection

        Parameters:
            None

        Returns:
            cursor(Any) : The cursor object  
        """

        if(not cls.db_connection.is_connected()):
            cls.db_connection.reconnect(attempts=2)
        return cls.db_connection.cursor(buffered=True, dictionary=True)

    @classmethod
    def _execute_query(cls, query, variables=None):
        """
        Executes the query that is passed by the caller , Gets the cursor
        from the current db_connection  , Throws error if there are any that is
        caused by the gluing library

        Parameters:
            query(str) : A valid SQL Query
            variable(tuples|None) : The actual variables which  are needed to be replaced
            in place of placeholders.

        Returns :
            result(Any)    
        """

        return cls._get_cursor().execute(query, variables)

    @classmethod
    def _evaluate_user_conditions(cls, conditions: dict) -> List:
        conditions_list = []
        condition = None
        for k, v in conditions.items():
            if not isinstance(v, _Constants.KNOWN_CLASSES):
                class_name = v.__class__.__name__.lower()
                col_name = f"{class_name}_id"
                condition = Condition(col_name, cls.operators_map["eq"], v.id)

            else:
                val = k.split(_Constants.SEPERATOR)
                """ Fallback to OP_EQUAL if he didnt mention any operator"""
                if len(val) == 1:
                    operator = cls.operators_map[_Constants.OP_EQUAL]
                    condition = Condition(val[0], operator, v)
                else:
                    condition = Condition(val[0], cls.operators_map[val[1]], v)
            conditions_list.append(condition)
        return conditions_list

    @classmethod
    def migrate(cls, table):
        """
        A wrapper for the CREATE TABLE query of the respective
        DB drivers

        Parameters :
            table(BaseModel)  : The class which inherits base model and has 
            the required fields and their types mentioned.
        Example :
            class Student(BaseModel):
                table_name = "students"
                name = fields.CharField(max_length=250, nullable=False)
                standard = fields.CharField(max_length=100,nullable=False)
                age =      fields.IntegerField()
                created_at = fields.DateField()

        Returns :
            result(Any)    
        """
        cls.model_class = table
        if not table.table_name:
            raise ValueError("Expected to have a table_name")

        _create_sql = cls._get_create_sql(table)
        cls._execute_query(query=_create_sql)

    @classmethod
    def _get_create_sql(cls, table) -> str:
        """
        The function which converts the user defined model class 
        in to a tuple form  (column_name,SQL Attributes)  ,Each
        field is evaluated and its corresponding SQL representations
        are added ,After evaluation a sql query is generated for the same.

        Parameters:
            table(BaseModel) - An instance of BaseModel

        Returns:
            query(str) - The sql query    
        """

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
                        "REFERENCES {table_name}({referred_column}) ON DELETE {on_delete}".
                        format(table_name=field.table.table_name, referred_column='id', on_delete=field.on_delete)))
                continue

            if isinstance(field, fields.CharField):
                if not field.max_length:
                    raise ValueError(
                        "A char field always requires a max_length property")

                else:
                    attr_string += "VARCHAR({}) ".format(field.max_length)

            if not isinstance(field, fields.CharField):
                attr_string += "{} ".format(field.field_sql_name)

            if field.auto_increment:
                attr_string += "AUTO_INCREMENT "

            if not field.nullable:
                attr_string += "NOT NULL "

            if field.default is not fields.NotProvided:
                if isinstance(field, fields.CharField):
                    attr_string += "DEFAULT '{}'".format(field.default)
                elif isinstance(field, fields.IntegerField):
                    attr_string += "DEFAULT {}".format(field.default)
            _fields_list.append((name, attr_string))
        _fields_list = [" ".join(x) for x in _fields_list]
        return _Constants.CREATE_TABLE_SQL.format(
            name=table.table_name, fields=", ".join(_fields_list)
        )

    def _return_conditions_as_sql_string(self, conditions: List) -> str:
        """
        Returns the user 
        """

        return " AND ".join(
            [
                "`{}` {} {}".format(
                    i.column, i.operator, self._get_parsed_value(i.value)
                )
                for i in conditions
            ]
        )

    def _get_parsed_value(self, val):
        if type(val) == str:
            return "'{}'".format(val)
        elif type(val) == bool:
            return int(val)

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
            query=self._return_conditions_as_sql_string(condition_list)
        )
        self.db_connection.reconnect()
        cur2 = self.db_connection.cursor(buffered=True, dictionary=True)
        if limit:
            _sql_query += ' LIMIT {limit} '.format(limit=limit)

        cur2.execute(_sql_query)
        rows = cur2.fetchall()
        result = list()
        for i in rows:
            result_class = self._dict_to_model_class(i, self.model_class)
            if fetch_relations:
                result_class = self._return_foreign_keys_from_a_table(
                    result_class, i)

            result.append(result_class)
        return result

    def get_one(self, fetch_relations=False, **kwargs):
        result = self.where(limit=1, fetch_relations=fetch_relations, **kwargs)
        if not len(result):
            return None
        return result[0]

    def insert(self, **kwargs):
        fields = list()
        values = list()
        for k, v in kwargs.items():
            key = k
            value = v
            if not isinstance(v, _Constants.KNOWN_CLASSES):
                key = "{}_id".format(k)
                value = v.id
            fields.append(key)
            values.append(value)

        _sql_query = _Constants.INSERT_SQL.format(
            name='`{}`'.format(self.table_name),
            fields=' , '.join(
                ['`{}`'.format(i) for i in fields]),
            placeholders=' , '.join([self._get_parsed_value(i) for i in values]))
        err = self._get_cursor().execute(_sql_query)

        if not err:
            cur = self._get_cursor()
            cur.execute(_Constants.GET_LAST_INSERTED_ID_SQL)
            last_inserted_id = cur.fetchone()
            kwargs['id'] = last_inserted_id['id']
        return self._dict_to_model_class(kwargs, self.model_class)

    def delete(self, **kwargs):
        condition_list = self._evaluate_user_conditions(kwargs)
        _sql_query = _Constants.DELETE_ALL_SQL.format(
            name=self.table_name, conditions=self._return_conditions_as_sql_string(condition_list))
        cur = self._get_cursor()
        cur.execute(_sql_query)

    def raw(self, query: str):
        return self._execute_query(query)


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
