from os import PathLike
from typing import List, Union
from uuid import UUID

import yaml
from pydantic import Field

from models import discovery
from models.base import BaseModel
from models.plugin import (
    CustomPlugin,
    DiscoveredPlugin,
    Plugin,
    Plugins,
    PluginTypeEnum,
    find_plugin,
)


class Project(BaseModel):
    version: int
    project_id: UUID
    plugins: Plugins[Union[CustomPlugin, DiscoveredPlugin]] = Plugins()
    send_anonymous_usage_stats: bool = True
    include_paths: List[str] = Field(default_factory=list)

    @classmethod
    def from_yaml_file(cls, path: PathLike):
        with open(path) as f:
            data = yaml.safe_load(f)
            return cls.parse_obj(data)


def get_plugin_definition(
    index: discovery.PluginIndex,
    project: Project,
    plugin_type: PluginTypeEnum,
    name: str,
) -> Union[CustomPlugin, Plugin]:
    plugin = find_plugin(project.plugins, plugin_type, name)

    if isinstance(plugin, CustomPlugin):
        return plugin

    return discovery.get_plugin_definition(index, plugin_type, plugin)
