import google.generativeai as genai
from .config import load_api_key

class AIChat:
    def __init__(self):
        self.api_key = load_api_key()
        self.setup_model()

    def setup_model(self):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        self.chat = self.model.start_chat(history=[])

    def generate_mindmap(self, topic):
        prompt = f"""Create a detailed mind map structure for the topic: {topic}
        The response must be in JSON format with the following structure:
        {{
            "center": "main topic",
            "branches": [
                {{
                    "text": "branch topic",
                    "children": [
                        {{"text": "sub-topic"}},
                        {{"text": "sub-topic", "children": [{{"text": "detail"}}]}}
                    ]
                }}
            ]
        }}
        Provide the response in a code block with ```json and ``` markers."""

        response = self.chat.send_message(prompt)
        return response.text