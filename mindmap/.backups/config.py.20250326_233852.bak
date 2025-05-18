import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.mindmap'
        self.config_file = self.config_dir / 'config.json'
        self.ensure_config_dir()

    def ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.save_api_key('')

    def load_api_key(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('gemini_api_key', '')
        except Exception:
            return ''

    def save_api_key(self, api_key):
        config = {'gemini_api_key': api_key}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

config = Config()
load_api_key = config.load_api_key
save_api_key = config.save_api_key