from manager import ConnectionManager


db_settings = {
    'ENGINE': 'mysql',
    'user': 'root',
    'password': 'root1234',
    'host': 'localhost',
    'port': 3306,
    'db_name': 'pizza_shop',
}

c = ConnectionManager()
conn = c.create_connection(db_settings)
