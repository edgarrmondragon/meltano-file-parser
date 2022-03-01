from datetime import date, datetime
from pathlib import Path
from typing import Generic, List, TypeVar, Union

from pydantic import Field, SecretStr, validator
from typing_extensions import Annotated, Literal

from models.base import BaseModel, GenericModel

T = TypeVar("T")


class _BaseSettingDefinition(GenericModel, Generic[T]):
    name: str
    kind: str
    value: T = None
    label: str = None
    docs: str = None
    documentation: str = None
    description: str = None
    placeholder: str = None
    env: str = None
    env_aliases: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    value_post_processor: str = None
    value_processor: str = None


class StringSetting(_BaseSettingDefinition[str]):
    kind: Literal["string"]
    protected: bool = False


class EmailSetting(_BaseSettingDefinition[str]):
    kind: Literal["email"]


class IntegerSetting(_BaseSettingDefinition[int]):
    kind: Literal["integer"]


class PasswordSetting(_BaseSettingDefinition[SecretStr]):
    kind: Literal["password"]


class DatetimeSetting(_BaseSettingDefinition[Union[datetime, date]]):
    kind: Literal["date_iso8601"]


class BooleanSetting(_BaseSettingDefinition[bool]):
    kind: Literal["boolean"]


class ChoiceSetting(_BaseSettingDefinition[str]):
    class Choice(BaseModel):
        label: str
        value: str

    kind: Literal["options"]
    options: List[Choice]


class ObjectSetting(_BaseSettingDefinition[dict]):
    kind: Literal["object"]


class ArraySetting(_BaseSettingDefinition[list]):
    kind: Literal["array"]


class OAuthSetting(_BaseSettingDefinition[str]):
    class OAuth(BaseModel):
        provider: str

    kind: Literal["oauth"]
    oauth: OAuth


class FileSetting(_BaseSettingDefinition[Path]):
    kind: Literal["file"]


class SettingDefinition(BaseModel):
    __root__: Annotated[
        Union[
            ArraySetting,
            BooleanSetting,
            ChoiceSetting,
            DatetimeSetting,
            EmailSetting,
            FileSetting,
            IntegerSetting,
            OAuthSetting,
            ObjectSetting,
            PasswordSetting,
            StringSetting,
        ],
        Field(discriminator="kind"),
    ]

    @validator("__root__", pre=True)
    def ensure_kind(cls, v):
        if "kind" not in v:
            v["kind"] = "string"
        return v

    # These are required because __root__ doesn't expose the wrapped type attributes

    @property
    def name(self):
        return self.__root__.name

    @property
    def label(self):
        return self.__root__.label

    @property
    def value(self):
        return self.__root__.value

    @property
    def kind(self):
        return self.__root__.kind

    @property
    def description(self):
        return self.__root__.description

    @property
    def placeholder(self):
        return self.__root__.placeholder
