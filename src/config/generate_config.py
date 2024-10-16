import configparser


def create_config():
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config["General"] = {
        "preferred_project": "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
    }
    config["Logging"] = {"log_level": "debug"}
    config["Input"] = {
        "input_file": "timsheet (version 2) (version 2) (version 2) (version 1)(AutoRecovered) OK-2024(AutoRecovered).xlsx"
    }

    # Write the configuration to a file
    with open("config.ini", "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    create_config()
