from os import PathLike
from typing import List

import yaml
from pydantic import Field

from models.plugin import (
    DiscoveredPlugin,
    Plugin,
    PluginModel,
    Plugins,
    PluginTypeEnum,
    PluginVariant,
    find_plugin,
    find_variant,
)


class IndexedPlugin(PluginModel):
    namespace: str
    variants: List[PluginVariant] = Field(default_factory=list)


class PluginIndex(Plugins[IndexedPlugin]):
    version: int

    @classmethod
    def from_yaml_file(cls, path: PathLike):
        with open(path) as f:
            data = yaml.safe_load(f)
            return cls.parse_obj(data)


def discover_plugin(
    index: PluginIndex,
    plugin_type: PluginTypeEnum,
    plugin_name: str,
    variant_name: str = None,
) -> DiscoveredPlugin:
    plugin = find_plugin(index, plugin_type, plugin_name)

    if variant_name is None:
        if plugin.variants:
            default_variant = plugin.variants[0]
            return DiscoveredPlugin(
                name=plugin.name,
                variant=default_variant.name,
                pip_url=default_variant.pip_url,
            )
        else:
            # There are no variants
            return DiscoveredPlugin(
                name=plugin.name,
                pip_url=plugin.pip_url,
            )

    variant = find_variant(plugin.variants, variant_name)

    return DiscoveredPlugin(
        name=plugin_name,
        variant=variant_name,
        pip_url=variant.pip_url,
    )


def get_plugin_definition(
    index: PluginIndex,
    plugin_type: PluginTypeEnum,
    discovered: DiscoveredPlugin,
) -> Plugin:
    index_plugin = find_plugin(index, plugin_type, discovered.name)

    if discovered.variant is None:
        if index_plugin.variants:
            Plugin(
                name=index_plugin.name,
                namespace=index_plugin.namespace,
                **index_plugin.variants[0].dict(exclude={"name"}),
            )
        else:
            return Plugin.parse_obj(index_plugin.dict(exclude={"variants"}))

    variant = find_variant(index_plugin.variants, discovered.variant)

    return Plugin(
        name=index_plugin.name,
        namespace=index_plugin.namespace,
        **variant.dict(exclude={"name"}),
    )
