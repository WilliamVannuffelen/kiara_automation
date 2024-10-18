import os
import configparser

from src.objects.config import ConfigOption


def make_config_dict(
    config: configparser.ConfigParser, options: list[ConfigOption], check_option: bool
) -> dict[str, str]:
    return {
        option.option: option.process_config_property(config, check_option)
        for option in options
    }


def read_config():
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, "config.ini")
    config = configparser.ConfigParser(inline_comment_prefixes=("#"))

    config_items = config.read(config_file)

    config_file_read_success = len(config_items) > 0
    if not config_file_read_success:
        print(f"Failed to read config file: '{config_file}'. Using default values.")

    config_values = make_config_dict(
        config=config,
        options=[
            ConfigOption("Logging", "log_level", "info"),
            ConfigOption("General", "preferred_project", ""),
            ConfigOption("Input", "input_file", ""),
            ConfigOption("Browser", "launch_type", "internal"),
            ConfigOption("General", "phone_number", ""),
            ConfigOption("General", "auto_submit", "false"),
        ],
        check_option=config_file_read_success,
    )

    return config_values
