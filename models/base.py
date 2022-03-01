from pydantic import BaseModel as Base
from pydantic import Extra
from pydantic.generics import GenericModel as Generic


class BaseModel(Base, extra=Extra.forbid, validate_assignment=True):
    pass


class GenericModel(Generic, extra=Extra.forbid, validate_assignment=True):
    pass
