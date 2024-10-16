import os
import configparser


def read_config():
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, "config.ini")
    config = configparser.ConfigParser()

    try:
        config.read(config_file)
    except Exception as e:
        raise Exception("Failed to read configuration file") from e

    log_level = config.get("Logging", "log_level")
    preferred_project = config.get("General", "preferred_project")
    input_file = config.get("Input", "input_file")

    config_values = {
        "log_level": log_level,
        "preferred_project": preferred_project,
        "input_file": input_file,
    }

    return config_values
