from os import name
from vorm.manager import ConnectionManager as db
from vorm.base import *
from vorm import fields

db_settings = {
    "driver": "mysql",
    "user": "root",
    "password": "root1234",
    "host": "localhost",
    "port": 3306,
    "database": "pizza_shop",
}

db.create_connection(db_settings)


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


class Pizza(BaseModel):
    table_name="pizza"
    name = fields.CharField(max_length=200)

class Juice(BaseModel):
    table_name="juice"
    name = fields.CharField(max_length=300)

class Shop(BaseModel):
    table_name="shop"
    name = fields.CharField(max_length=200)
    juices = fields.ForeignKey(Juice)
    pizzas = fields.ForeignKey(Pizza)

# db.migrate(Juice)
# db.migrate(Pizza)
# db.migrate(Shop)

# j = Juice.objects.insert(name="test")
# pizza = Pizza.objects.insert(name="testp")
# shop =  Shop.objects.insert(juices =j ,pizzas=pizza)
sj   = Shop.objects.get_one(id=2,fetch_relations=True)
print(sj.juices)
for j in sj.juices:
    print(j)
# Juice.objects.delete(id__eq=1)