from pydantic import SecretStr

from models.discovery import discover_plugin, get_plugin_definition, PluginIndex
from models.plugin import CustomPlugin, PluginTypeEnum
from models.project import Project


if __name__ == "__main__":
    project = Project.from_yaml_file("./meltano.yml")
    tap_github = project.plugins.extractors[0]
    assert isinstance(tap_github, CustomPlugin)
    assert tap_github.commands["info"].args == "--test"
    assert tap_github.settings[0].kind == "string"
    assert tap_github.settings[1].value == SecretStr("s3cr3t")
    assert tap_github.settings[2].value == 10
    assert tap_github.settings[3].value.year == 2021

    index = PluginIndex.from_yaml_file("./discovery.yml")
    tap_gitlab = discover_plugin(index, PluginTypeEnum.EXTRACTORS, "tap-gitlab")
    assert tap_gitlab.name

    default_target_postgres = discover_plugin(
        index,
        PluginTypeEnum.LOADERS,
        "target-postgres",
    )
    assert default_target_postgres.variant == "transferwise"

    meltano_target_postgres = discover_plugin(
        index,
        PluginTypeEnum.LOADERS,
        "target-postgres",
        "meltano",
    )
    assert meltano_target_postgres.variant == "meltano"

    plugin_def = get_plugin_definition(
        index,
        PluginTypeEnum.LOADERS,
        meltano_target_postgres,
    )
    assert plugin_def.namespace == "target_postgres"
    assert plugin_def.docs == "https://hub.meltano.com/loaders/postgres--meltano.html"

    dbt = discover_plugin(index, PluginTypeEnum.TRANSFORMERS, "dbt")
    assert dbt.variant is None

    dbt_definition = get_plugin_definition(index, PluginTypeEnum.TRANSFORMERS, dbt)
    assert dbt_definition.namespace == "dbt"
    assert "run" in dbt_definition.commands
