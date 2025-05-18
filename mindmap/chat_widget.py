from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .json_parser import JSONParser
from .ai_chat import AIChat
from .config import save_api_key

class ChatWidget(QWidget):
    mindMapGenerated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_chat = AIChat()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # API Key input
        api_key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter Gemini API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        save_key_btn = QPushButton("Save API Key")
        save_key_btn.clicked.connect(self.save_api_key)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(save_key_btn)
        layout.addLayout(api_key_layout)
        
        # Topic input
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter topic for mind map")
        layout.addWidget(self.topic_input)
        
        # Generate button
        generate_btn = QPushButton("Generate Mind Map")
        generate_btn.clicked.connect(self.generate_mindmap)
        layout.addWidget(generate_btn)
        
        # Response display
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        layout.addWidget(self.response_display)
        
        self.setLayout(layout)

    def save_api_key(self):
        api_key = self.api_key_input.text()
        if api_key:
            try:
                save_api_key(api_key)
                self.ai_chat.api_key = api_key
                self.ai_chat.setup_model()
                QMessageBox.information(self, "Success", "API Key saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save API key: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "Please enter an API key")
        
    def generate_mindmap(self):
        topic = self.topic_input.text()
        if not topic:
            QMessageBox.warning(self, "Error", "Please enter a topic!")
            return
            
        try:
            response = self.ai_chat.generate_mindmap(topic)
            self.response_display.setText(f"Topic: {topic}\nResponse: {response}")
            
            # Parse JSON from response
            mind_map_data = JSONParser.extract_json_from_response(response)
            self.mindMapGenerated.emit(mind_map_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mind map: {str(e)}")