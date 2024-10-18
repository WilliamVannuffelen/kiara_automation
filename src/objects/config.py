import configparser


class ConfigOption:
    def __init__(self, section: str, option: str, default: str):
        self.section = section
        self.option = option
        self.default = default

    def process_config_property(
        self, config: configparser.ConfigParser, config_file_read_success: bool
    ) -> str:
        if not config_file_read_success:
            return self.default
        try:
            value = config.get(section=self.section, option=self.option)
        except configparser.NoSectionError:
            self.print_warning(
                warning_type="section",
                section=self.section,
                option=self.option,
                default=self.default,
            )
            value = self.default
        except configparser.NoOptionError:
            self.print_warning(
                warning_type="option",
                section=self.section,
                option=self.option,
                default=self.default,
            )
            value = self.default
        return value

    def print_warning(
        self, warning_type: str, section: str, option: str, default: str
    ) -> None:
        if warning_type == "section":
            print(
                f"Warning: Section '{section}' not found in the configuration file. "
                f"Defaulting to '{default}' for '{option}'."
            )
        elif warning_type == "option":
            print(
                f"Warning: {option} option not found in the configuration file. "
                f"Should be in section '{section}'. "
                f"Defaulting to '{default}'."
            )

    def __repr__(self):
        return f"ConfigOption(section={self.section}, option={self.option}, default={self.default})"
