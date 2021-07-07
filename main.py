from vorm.base import *
from vorm.manager import ConnectionManager
from vorm.fields import *

db_settings = {
    "ENGINE": "mysql",
    "user": "root",
    "password": "root1234",
    "host": "localhost",
    "port": 3306,
    "database": "pizza_shop",
}

ConnectionManager.create_connection(db_settings)


class Employee(BaseModel):
    table_name = "employees"
    name = CharField(max_length=250, nullable=False, primary_key=True)
    ted = CharField(max_length=100, nullable=True)
    salary = IntegerField()


class Student(BaseModel):
    manager_class = ConnectionManager
    table_name = "students"
    id = IntegerField(primary_key=True,auto_increment=True)
    name = CharField(max_length=250, nullable=False, default="Johny")
    standard = CharField(max_length=100, nullable=True)
    salary = IntegerField()


# c.migrate(Employee)
#c.migrate(Student)
#ConnectionManager.migrate(Student)
students = Student.objects.where(name__eq='vishnu',salary__gte=2000)
print(students)