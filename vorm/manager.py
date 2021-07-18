import inspect
import re
from typing import List
import mysql.connector as connector
from . import fields
from .types import Condition
import psycopg2
import psycopg2.extras


class _Constants:
    CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
    INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
    SELECT_WHERE_SQL = "SELECT {fields} FROM {name} WHERE {query}"
    SELECT_ALL_SQL = "SELECT {fields} FROM {name}"
    DELETE_ALL_SQL = "DELETE FROM {name} WHERE {conditions};"
    UPDATE_SQL = "UPDATE {name} SET {new_data} WHERE {conditions};"
    SEPERATOR = "__"
    FIELDS_TO_EXCLUDE_IN_INSPECTION = ["table_name", "manager_class"]
    KNOWN_CLASSES = (int, float, str, tuple)
    OP_EQUAL = 'eq'
    GET_LAST_INSERTED_ID_MYSQL = "SELECT LAST_INSERT_ID() as id;"
    GET_LAST_INSERTED_ID_POSTGRESQL = "SELECT currval(pg_get_serial_sequence('{table_name}','id')) as id;"


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
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'

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

        if cls.db_engine == "postgresql":
            cls._connect_to_postgresql(db_settings)

        return cls

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
    def _connect_to_postgresql(cls, db_settings: dict):
        try:
            connection = psycopg2.connect(**db_settings)
            connection.autocommit = True
            cls.db_connection = connection

        except Exception as e:
            print(e)

    @classmethod
    def _get_cursor(cls):
        """
        Returns the cursor of the current db_connection

        Parameters:
            None

        Returns:
            cursor(Any) : The cursor object  
        """
        if cls.db_engine == cls.MYSQL:
            if(not cls.db_connection.is_connected()):
                cls.db_connection.reconnect(attempts=2)
            return cls.db_connection.cursor(buffered=True, dictionary=True)

        return cls.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        """
        Evaluvates the user conditions and  returns it as 
        list of tuples
        Eg : {'price__gt':200 , 'os':'android'} - > [('price','>',200),('os','=','android')]

        Params:
            Conditions dict
        Returns:
            List[tuple]   
        """
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
    def _get_corresponding_auto_increment_sql_type(cls) -> str:
        if cls.db_engine == cls.MYSQL:
            return 'INT', 'AUTO_INCREMENT'
        return 'SERIAL', ''

    @classmethod
    def _escape_column_names(cls, val):
        if cls.db_engine == cls.MYSQL:
            return f'`{val}`'
        return f'"{val}"'

    def _get_last_inserted_sql(self):
        if self.db_engine == self.MYSQL:
            return _Constants.GET_LAST_INSERTED_ID_MYSQL
        return _Constants.GET_LAST_INSERTED_ID_POSTGRESQL.format(table_name=self.table_name)

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

        _type, field_name = cls._get_corresponding_auto_increment_sql_type()
        _fields_list = [
            ('`id`', '{type} NOT NULL {field} PRIMARY KEY'.format(
                type=_type, field=field_name))
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
            _fields_list.append((cls._escape_column_names(name), attr_string))
        print(_fields_list)
        _fields_list = [" ".join(x) for x in _fields_list]
        return _Constants.CREATE_TABLE_SQL.format(
            name=table.table_name, fields=", ".join(_fields_list)
        )

    def _return_conditions_as_sql_string(self, conditions: List) -> str:
        """
        Returns the users condtion as string joined with AND clause

        Params: 
            conditions(List) : The list of user conditions as tuple

        Returns:
            sql_string(str)  :  The sql equivalent string 
        """
        return " AND ".join(
            [
                "{} {} {}".format(
                    self._escape_column_names(
                        i.column), i.operator, self._get_escaped_value(i.value)
                )
                for i in conditions
            ]
        )

    def _get_escaped_value(self, val):
        if type(val) == str:
            return "'{}'".format(val)
        elif type(val) == bool:
            return int(val)

        return str(val)

    def _dict_to_model_class(self, d, table):
        """
        Converts the given dict to the specified model_class

        Params:
            d(dict) : The dict representation of the class
            table(BaseModel | Any) : The class which we want the values to be spread

        Returns :
            table : The table with the values of the dict spreaded     
        """

        return table(**d)

    def _return_foreign_keys_from_a_table(self, model_class, query_dict):
        """
        Finds foreign_key fields from a table ,queries it
        and attaches to the found attribute in the model class.
        """
        for name, field in inspect.getmembers(model_class):
            if isinstance(field, fields.ForeignKey):
                column_name = '{}_id'.format(name)
                result_set = field.table.objects.where(
                    id__eq=query_dict[column_name])
                setattr(model_class, name, result_set)
        return model_class

    def where(self, fetch_relations=False, limit=None, **kwargs) -> List:
        """
        A wrapper for  the SQL's  WHERE clause , You mention the constraints for the
        attributes , It will convert them in equivalent SQL query and returns a instance 
        of the model class

        Eg : first_employee = Employee.objects.get(id=1)

        Params:
            kwargs :The constraints that you want to query the DB with
            fetch_relations(bool) : Defaults to false,  If you want to fetch the foreign keys
            you can set it to True
            limit(int): The limit of the query set

        Returns :
            The model class    
        """
        cur2 = self._get_cursor()
        print('kwargs is', kwargs)
        if bool(kwargs):
            condition_list = self._evaluate_user_conditions(kwargs)
            _sql_query = _Constants.SELECT_WHERE_SQL.format(
                name=self.table_name,
                fields="*",
                query=self._return_conditions_as_sql_string(condition_list)
            )
        else:
            _sql_query = _Constants.SELECT_ALL_SQL.format(
                fields="*", name=self.table_name)

        if limit:
            _sql_query += ' LIMIT {limit} ;'.format(limit=limit)
        else:
            _sql_query += ' ;'

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
        """
        Calls the where method and returns the first result from 
        the query_set
        """

        result = self.where(limit=1, fetch_relations=fetch_relations, **kwargs)
        if not len(result):
            return None
        return result[0]

    def all(self, fetch_relations=False):
        return self.where(fetch_relations=fetch_relations)

    def insert(self, **kwargs):
        """
        Inserts a record into the database by converting the model class into its
        equivalent SQL query

        Eg  : student = Student.objects.insert(name='Vishnu Varthan' ,class='12C')
        """

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
            name=self._escape_column_names(self.table_name),
            fields=' , '.join(
                [self._escape_column_names(i) .format(i) for i in fields]),
            placeholders=' , '.join([self._get_escaped_value(i) for i in values]))
        err = self._get_cursor().execute(_sql_query)

        if not err and not kwargs.get('id'):
            cur = self._get_cursor()
            cur.execute(self._get_last_inserted_sql())
            last_inserted_id = cur.fetchone()
            kwargs['id'] = last_inserted_id['id']

        return self._dict_to_model_class(kwargs, self.model_class)

    def update(self, new_data: dict, **kwargs):
        """
        Updates the specified table in the database by evaluvating the conditions 
        we specified
        p = Pizza.objects.update(new_data={'name':'Paneer pizza'},id=1)
        SQL Query : UPDATE pizza SET `name` = 'Paneer pizza' WHERE `id` = 1

        Params:
            new_data(dict) : A dict which contains the new values , column_name
            being the key and the  new value for the column being the value for
            the key
            conditions(kwargs) : Conditions for the  row to be updated

        Returns :
            model_class    
        """
        new_data_list = ', '.join(
            [f'{self._escape_column_names(field_name)} = {self._get_escaped_value(value)}' for field_name, value in new_data.items()])
        condition_list = self._evaluate_user_conditions(kwargs)
        condition_string = self._return_conditions_as_sql_string(
            condition_list)
        _sql_query = _Constants.UPDATE_SQL.format(
            name=self.table_name, new_data=new_data_list, conditions=condition_string)
        cur = self._get_cursor()
        cur.execute(_sql_query)

        for k, v in new_data.items():
            kwargs[k] = v

        return self.get_one(**kwargs)

    def delete(self, **kwargs):
        """
        Delete a record from database
        """
        condition_list = self._evaluate_user_conditions(kwargs)
        _sql_query = _Constants.DELETE_ALL_SQL.format(
            name=self.table_name, conditions=self._return_conditions_as_sql_string(condition_list))
        cur = self._get_cursor()
        cur.execute(_sql_query)


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
