# -*- coding: utf-8 -*-
import json
from os.path import expanduser, isfile, join
from ..utils.decorators import singleton

@singleton
class Auth:
    testrail_config_dir = join(expanduser('~'), ".testrail")
    testrail_config_path = join(testrail_config_dir, 'testrail_config.json')

    def __init__(self):
        self.config = self._get_config()
        self.url = self.config['url']
        self.username = self.config['username']
        self.password = self.config['password']

    def _get_config(self) -> dict:
        return self._file_read(self.testrail_config_path)

    @staticmethod
    def _file_read(path: str) -> dict:
        """
        Reads the contents of a JSON file from the given path.
        
        :param path: The file path to read the JSON data from.
        :return: A dictionary containing the file's JSON contents.
        
        :raises FileNotFoundError: If the file does not exist at the specified path.
        """
        if not isfile(path):
            raise FileNotFoundError(f"Can't found token file: {path}")

        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
