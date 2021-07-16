from vorm import base,fields

class Student(base.BaseModel) :
    table_name="students"
    name = fields.CharField(max_length=300)
    clas = fields.CharField(max_length=200)
    age = fields.IntegerField()
