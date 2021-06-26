from manager import MetaModel


class BaseModel(metaclass=MetaModel):
    
    table_name = ""

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        attrs_format = ", ".join(
            [f"{field}={value}" for field, value in self.__dict__.items()]
        )
        return f"<{self.__class__.__name__}: ({attrs_format})>\n" 
