from base import *
from manager import ConnectionManager
from fields import *

db_settings = {
    "ENGINE": "mysql",
    "user": "root",
    "password": "root1234",
    "host": "localhost",
    "port": 3306,
    "database": "pizza_shop",
}

c = ConnectionManager(db_settings)


class Employee(BaseModel):
    table_name = "employees"
    name = CharField(max_length=250, nullable=False, primary_key=True)
    ted = CharField(max_length=100, nullable=True)
    salary = IntegerField()


class Student(BaseModel):
    table_name = "students"
    id = IntegerField(primary_key=True)
    name = CharField(max_length=250, nullable=False, default="Johny")
    standard = CharField(max_length=100, nullable=True)
    salary = IntegerField()


# c.migrate(Employee)
c.migrate(Student)