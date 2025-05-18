from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .scene import MindMapScene
from .config import Config
from .chat_widget import ChatWidget
import json

class MindMapView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.scale(0.8, 0.8)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

class MindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        config = Config()
        load_api_key = config.load_api_key
        
    def initUI(self):
        self.setWindowTitle('AI-Powered Mind Map Creator')
        self.setGeometry(100, 100, 1500, 800)
        
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)
        
        # Mind map view
        self.scene = MindMapScene()
        self.view = MindMapView(self.scene)
        splitter.addWidget(self.view)
        
        # Chat widget
        self.chat_widget = ChatWidget()
        self.chat_widget.mindMapGenerated.connect(self.create_mind_map)
        splitter.addWidget(self.chat_widget)
        
        splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        
        self.createToolBar()
        
    def create_mind_map(self, json_str):
        try:
            if isinstance(json_str, str):
                data = json.loads(json_str)
            else:
                data = json_str
            self.scene.create_from_json(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create mind map: {str(e)}")
            
    def createToolBar(self):
        toolbar = self.addToolBar('Tools')
        toolbar.setMovable(False)
        
        # Add actions
        actions = [
            ('Zoom In', 'Ctrl++', lambda: self.view.scale(1.1, 1.1)),
            ('Zoom Out', 'Ctrl+-', lambda: self.view.scale(0.9, 0.9)),
            ('Reset Zoom', 'Ctrl+0', lambda: self.view.setTransform(QTransform())),
            ('Export as Image', 'Ctrl+E', self.exportImage),
            ('Clear', 'Ctrl+N', lambda: self.scene.clear())
        ]
        
        for name, shortcut, callback in actions:
            action = QAction(name, self)
            action.setShortcut(shortcut)
            action.triggered.connect(callback)
            toolbar.addAction(action)
            
    def exportImage(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Export as Image", "", "PNG Files (*.png)")
        if fileName:
            rect = self.scene.itemsBoundingRect()
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter, QRectF(image.rect()), rect)
            painter.end()
            
            image.save(fileName)