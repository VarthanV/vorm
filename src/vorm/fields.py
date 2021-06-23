from base import BaseModel


class NotProvided:
    pass


class BaseField:
    def __init__(
        self,
        name=None,
        max_length=255,
        nullable=False,
        primary_key=False,
        default=NotProvided,
    ) -> None:
        self.name = name
        self.max_length = max_length
        self.nullable = nullable
        self.primary_key = primary_key
        self.default = default


class CharField(BaseField):
    field_sql_name = {"mysql": "VARCHAR"}


class IntegerField(BaseField):
    field_sql_name = {"mysql": "INT"}


class FloatField(BaseField):
    field_sql_name = {"mysql": "FLOAT"}


class Employee(BaseModel):
    name = CharField(max_length=250)
    salary = IntegerField()
