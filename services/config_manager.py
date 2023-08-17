"""Loads and validates config.json file against a config json schema"""
import locale
import json
import jsonschema


class ConfigManager:
    """Loads and validates config.json file against a config json schema"""

    def __init__(self, file_path: str) -> None:
        config_schema = {
            "type": "object",
            "properties": {
                "bucket": {"type": "string"},
                "awsAccessKeyId": {"type": "string"},
                "awsSecretAccessKey": {"type": "string"},
            },
            "required": ["bucket", "awsAccessKeyId", "awsSecretAccessKey"],
            "additionalProperties": False,
        }

        with open(
            file_path, "r", encoding=locale.getpreferredencoding()
        ) as config_file:
            self.config = json.load(config_file)
            jsonschema.validate(instance=self.config, schema=config_schema)

    @property
    def bucket(self) -> str:
        """The bucket to upload to"""
        return self.config["bucket"]

    @property
    def aws_access_key_id(self) -> str:
        """Your AWS access key"""
        return self.config["awsAccessKeyId"]

    @property
    def aws_secret_access_key(self) -> str:
        """Your AWS secret key"""
        return self.config["awsSecretAccessKey"]
