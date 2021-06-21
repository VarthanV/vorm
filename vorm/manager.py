from mysql.connector import connect


class ConnectionManager:
    db_cursor = None
    db_engine = ''

    @property
    def table_name(self):
        return self.model.table_name

    @classmethod
    def create_connection(cls, db_settings: dict):
        cls.db_engine = db_settings.pop('ENGINE')
        if cls.db_engine == 'mysql':
            cls.db_connection = cls._connect_to_mysql(db_settings)

    @classmethod
    def _connect_to_mysql(cls, db_settings: dict):
        try:
            db_name = db_settings.pop('db_name')
            connection = connect(**db_settings)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(f'USE {db_name}')
            return cursor
        except Exception as e:
            print(e)

    @classmethod
    def _get_cursor(cls):
        return cls.db_cursor

    @classmethod
    def _execute_query(cls, query, variables):
        cls.db_cursor.execute(query, variables)
