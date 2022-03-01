import enum
from pathlib import Path
from typing import Any, Dict, Generic, List, TypeVar

from pydantic import Field
from pydantic.generics import GenericModel

from models.base import BaseModel
from models.command import Command
from models.setting import SettingDefinition

PluginT = TypeVar("PluginT", bound="BasePlugin")


class PluginNotFound(Exception):
    pass


class VariantNotFound(Exception):
    pass


class CapabilitiesEnum(str, enum.Enum):
    STATE = "state"
    DISCOVER = "discover"
    CATALOG = "catalog"
    PROPERTIES = "properties"
    ACTIVATE_VERSION = "activate-version"
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    DATATYPE_FAILSAFE = "datatype-failsafe"
    RECORD_FLATTENING = "record-flattening"


class PluginTypeEnum(str, enum.Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    TRANSFORMERS = "transformers"
    TRANSFORMS = "transforms"
    MODELS = "models"
    DASHBOARDS = "dashboards"
    ORCHESTRATORS = "orchestrators"
    FILES = "files"
    UTILITIES = "utilities"


class BasePlugin(BaseModel):
    name: str = Field(..., allow_mutation=False)


class PluginModel(BasePlugin):
    label: str = None
    description: str = None
    logo_url: str = None
    pip_url: str = None
    repo: str = None
    config: Dict[str, Any] = Field(default_factory=dict)
    executable: str = None
    settings: List[SettingDefinition] = Field(default_factory=list)
    docs: str = None
    settings_group_validation: List[List[str]] = Field(default_factory=list)
    commands: Dict[str, Command] = Field(default_factory=dict)

    hidden: bool = False
    original: bool = False

    # Tap
    select: List[str] = Field(default_factory=list)
    metadata: Dict[str, dict] = Field(default_factory=dict)
    capabilities: List[CapabilitiesEnum] = Field(default_factory=list)

    # Target
    dialect: str = None
    target_schema: str = None

    # Files
    update: Dict[Path, bool] = Field(default_factory=dict)


class PluginVariant(PluginModel):
    pass


class Plugin(PluginModel):
    namespace: str


class DiscoveredPlugin(BasePlugin):
    pip_url: str
    variant: str = None


class CustomPlugin(PluginModel):
    namespace: str = None
    inherit_from: str = None


class Plugins(GenericModel, BaseModel, Generic[PluginT]):
    extractors: List[PluginT] = Field(default_factory=list)
    loaders: List[PluginT] = Field(default_factory=list)
    transformers: List[PluginT] = Field(default_factory=list)
    # transforms: List[PluginT] = Field(default_factory=list)
    # models: List[PluginT] = Field(default_factory=list)
    # dashboards: List[PluginT] = Field(default_factory=list)
    transforms: list = Field(default_factory=list)
    models: list = Field(default_factory=list)
    dashboards: list = Field(default_factory=list)
    orchestrators: List[PluginT] = Field(default_factory=list)
    files: List[PluginT] = Field(default_factory=list)
    utilities: List[PluginT] = Field(default_factory=list)

    @property
    def mapping(self) -> Dict[PluginTypeEnum, List[PluginT]]:
        return {
            PluginTypeEnum.EXTRACTORS: self.extractors,
            PluginTypeEnum.LOADERS: self.loaders,
            PluginTypeEnum.TRANSFORMERS: self.transformers,
            PluginTypeEnum.TRANSFORMS: self.transforms,
            PluginTypeEnum.MODELS: self.models,
            PluginTypeEnum.DASHBOARDS: self.dashboards,
            PluginTypeEnum.ORCHESTRATORS: self.orchestrators,
            PluginTypeEnum.FILES: self.files,
            PluginTypeEnum.UTILITIES: self.utilities,
        }


def find_plugin(
    plugins: Plugins[PluginT],
    plugin_type: PluginTypeEnum,
    name: str,
) -> PluginT:
    plugin = next(filter(lambda p: p.name == name, plugins.mapping[plugin_type]), None)

    if plugin is None:
        raise PluginNotFound(f"No plugin '{name}' was found")

    return plugin


def find_variant(variants: List[PluginVariant], name: str) -> PluginVariant:
    variant = next(filter(lambda v: v.name == name, variants), None)

    if variant is None:
        raise VariantNotFound(f"No variant '{name}' was found")

    return variant
