from os import PRIO_PGRP
from vorm.base import *
from vorm.manager import ConnectionManager
from vorm import fields

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
    name = fields.CharField(max_length=250, nullable=False, primary_key=True)
    ted = fields.CharField(max_length=100, nullable=True)
    salary = fields.IntegerField()


class Student(BaseModel):
    manager_class = ConnectionManager
    table_name = "students"
    id = fields.IntegerField(primary_key=True,auto_increment=True)
    name = fields.CharField(max_length=250, nullable=False, default="Johny")
    standard = fields.CharField(max_length=100, nullable=True)
    salary = fields.IntegerField()
    created_at = fields.DateField()



#ConnectionManager.migrate(Employee)
#ConnectionManager.migrate(Student)
#ConnectionManager.migrate(Student)
students = Student.objects.where(name__eq='vishnu',salary__gte=2000)
for i in students :
    print(i.name)

