from models.project import Project
from models.discovery import PluginIndex


if __name__ == "__main__":
    print(Project.schema_json(indent=2))
    print(PluginIndex.schema_json(indent=2))
