from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json
import re

class JSONParser:
    @staticmethod
    def extract_json_from_response(response_text):
        # Find JSON content between ```json and ``` markers
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in response")
        else:
            raise ValueError("No JSON content found in response")

    @staticmethod
    def clean_json_string(json_str):
        # Remove any non-JSON content
        json_str = re.sub(r'^.*?{', '{', json_str, flags=re.DOTALL)
        json_str = re.sub(r'}.*?$', '}', json_str, flags=re.DOTALL)
        return json_str