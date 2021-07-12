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
        auto_increment=False,
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

class BooleanField(BaseField) :
    field_sql_name = "TINYINT"
    
class ForeignKey :
    def __init__(self,table,nullable=True):
        self.table = table
        self.nullable = nullable