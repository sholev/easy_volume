import json
import os

from utils import get_path


def init_config():
    config.set_defaults({
        "selected_device_state": "Active",
        'appearance': 'system',
        'theme': 'blue',
        'start_minimized': False
    })


class Config:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', encoding='utf-8') as file:
                json.dump({}, file)

        with open(self.filepath, mode='r', encoding='utf-8') as file:
            self.config = json.load(file)

    def save(self):
        with open(self.filepath, mode='w', encoding='utf-8') as file:
            json.dump(self.config, file, indent=4)

    def get(self, key, default=None):
        if key in self.config:
            return self.config[key]

        return default

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def set_defaults(self, defaults):
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
        self.save()


config = Config(get_path('config.json'))
init_config()
