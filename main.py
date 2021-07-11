from os import PRIO_PGRP
from pprint import pprint
import vorm
from vorm.manager import ConnectionManager
from vorm.base import *
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


class Student(BaseModel):
    table_name = "students"
    name = fields.CharField(max_length=250, nullable=False, default="Johny")
    standard = fields.CharField(max_length=100, nullable=True)
    salary = fields.IntegerField()
    created_at = fields.DateField()


class Klass(BaseModel):
    table_name = "class"
    name = fields.CharField(max_length=250, nullable=True)
    student = fields.ForeignKey(Student)


# ConnectionManager.migrate(Student)
# ConnectionManager.migrate(Student)
# ConnectionManager.migrate(Klass)
# ConnectionManager.migrate(Employee)
# students = Student.objects.where(name__eq='vishnu',salary__gte=2000)
# for i in students :
#     print(i.name)

# s = Student.objects.get_one(name__eq='vishnu',salary__eq=50000)
# print(s.name)

# k = Klass.objects.get_one(id__eq=1)
# print(k)

k = Klass.objects.where(name__eq='A', fetch_relations=True)
s = Student.objects.get_one(id__eq=1)

klass_student_has_enrolled = Klass.objects.where(student_id__eq=s.id)
