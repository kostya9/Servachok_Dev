from configparser import ConfigParser
import os


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


class Config(ConfigParser):
    """
    Config class to parse, save and work with configuration values
    """
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        config_file_path = os.path.abspath(os.path.join(ROOT_PATH, "../etc/config.ini"))
        super(Config, self).__init__(allow_no_value=True)
        with open(config_file_path) as lines:
            self.read_file(lines)
