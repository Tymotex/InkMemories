import json


class DisplayConfig():
    # TODO: It would be good to enforce typing against this config to trust it's always well-formed.
    # TODO: It would be good to add some validation to ensure that required fields are provided.
    # TODO: Make the config take on default values. Could do a dict merge with the dict read from the JSON.
    config = {
        "display": {
            # TODO: Validate: this should always be >0
            "refresh_period_secs": 86400,
            "allowed_image_extensions": [".jpg", ".jpeg", ".png"],
            # TODO: Required fields like this should be validated to be set to an existent directory on program startup and log on failure.
            "image_source_dir": ""
        },
        "logging": {
            "log_file_path": "~/.ink-memories-log"
        }
    }

    def __init__(self, config_file_path):
        self.extract_config_from_file(config_file_path)

    def extract_config_from_file(self, config_file_path):
        try:
            with open(config_file_path, 'r') as file:
                display_config_dict = json.load(file)
            print("Successfully loaded display_config.json.")
            print(json.dumps(display_config_dict, indent=4))
            merged_config = self.config.copy()
            merged_config.update(display_config_dict)
            self.config = merged_config
        except FileNotFoundError:
            print(f"Error: File '{config_file_path}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in '{config_file_path}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
