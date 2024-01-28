import sys
import json
from logging import Logger

DEFAULT_DISPLAY_CONFIG = {
    "display": {
        # TODO: Validate: this should always be >0
        "refresh_period_secs": 86400,
        "allowed_image_extensions": [".jpg", ".jpeg", ".png"],
        # TODO: Required fields like this should be validated to be set to an existent directory on program startup and log on failure.
        "image_source_dir": "~/Pictures"
    },
}


class DisplayConfig():
    """TODO"""
    # TODO: It would be good to enforce typing against this config to trust it's always well-formed.
    # TODO: It would be good to add some validation to ensure that required fields are provided.
    # TODO: Make the config take on default values. Could do a dict merge with the dict read from the JSON.
    config = DEFAULT_DISPLAY_CONFIG

    def __init__(self, logger: Logger, config_file_path=None):
        self.logger = logger

        # If a config file is specified, override defaults.
        if config_file_path:
            self.extract_config_from_file(config_file_path)
        else:
            self.logger.warning('No config file specified.')

    def extract_config_from_file(self, config_file_path):
        try:
            with open(config_file_path, 'r') as file:
                display_config_dict = json.load(file)
            self.logger.info("Successfully loaded display_config.json.")
            self.logger.info(json.dumps(display_config_dict, indent=4))
            merged_config = self.config.copy()
            merged_config.update(display_config_dict)
            self.config = merged_config
        except FileNotFoundError:
            self.logger.critical(
                f"Error: File '{config_file_path}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.critical(
                f"Error decoding JSON in '{config_file_path}': {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred: {e}")
            sys.exit(1)
