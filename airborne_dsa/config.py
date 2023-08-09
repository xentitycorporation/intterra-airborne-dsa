"""Loads and validates config.json file against a config json schema"""
import locale
import json
import jsonschema

# root_directory = os.path.dirname(os.path.realpath(__file__))
# with open(
#           root_directory + "/config.json", "r", encoding=locale.getpreferredencoding()
#       ) as config_file:


class Config:
    """Loads and validates config.json file against a config json schema"""

    @staticmethod
    def load_config(file_path: str) -> object:
        """Load config by providing a file path"""
        config_schema = {
            "type": "object",
            "properties": {"bucket": {"type": "string"}},
            "required": ["bucket"],
        }

        with open(
            file_path, "r", encoding=locale.getpreferredencoding()
        ) as config_file:
            config = json.load(config_file)
            jsonschema.validate(instance=config, schema=config_schema)
            return config
