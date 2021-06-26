from base import BaseModel
import inspect
from pprint import pprint

__all__ = ["CharField", "IntegerField", "FloatField"]


class NotProvided:
    pass


class BaseField:
    field_sql_name = ""

    def __init__(
        self,
        name=None,
        max_length=0,
        nullable=False,
        primary_key=False,
        auto_increment= False,
        default=NotProvided,
    ) -> None:
        self.name = name
        self.max_length = max_length
        self.nullable = nullable
        self.primary_key = primary_key
        self.default = default
        self.auto_increment = auto_increment

    @property
    def sql_type(self) -> str:
        return self.field_sql_name


class CharField(BaseField):
    field_sql_name = "VARCHAR"


class IntegerField(BaseField):
    field_sql_name = "INT"


class FloatField(BaseField):
    field_sql_name = "FLOAT"

class DateField(BaseField):
    field_sql_name = "DATE"

class TimeField(BaseField):
    field_sql_name = "TIME"

class DateTimeField(BaseField):
    field_sql_name = "DATETIME"



class Employee(BaseModel):
    name = CharField(max_length=250,nullable=False,primary_key=True)
    ted = CharField(max_length=100,nullable=True)
    salary = IntegerField()


e = Employee()

field_dict = []
for name ,field in inspect.getmembers(e):
    if name.startswith('__'):
        continue
    if isinstance(field,CharField):
        attr_string = ''
        if field.max_length:
            attr_string+='VARCHAR({}) '.format(field.max_length)
        if field.primary_key :
            attr_string+='PRIMARY KEY '
        if not field.nullable:
            attr_string+= 'NOT NULL '
        field_dict.append((name,attr_string))
  

CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
fields = [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ]
f = [" ".join(x) for x in field_dict]
final = CREATE_TABLE_SQL.format(name='foo', fields=", ".join(f))
print(final)