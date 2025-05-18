1. `project markmap/mindmap/models.py`:
```python
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Node(QGraphicsItem):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.connections = []
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self._color = QColor("#2196F3")
        self._hover_color = QColor("#64B5F6")
        self._text_color = QColor("#FFFFFF")
        self._is_hovered = False
        
    def boundingRect(self):
        return QRectF(-60, -40, 120, 80)
        
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self._hover_color if self._is_hovered else self._color)
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(self.boundingRect(), 10, 10)
        
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(self._text_color))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)
    
    def hoverEnterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for connection in self.connections:
                connection.updatePosition()
        return super().itemChange(change, value)

class Connection(QGraphicsLineItem):
    def __init__(self, startNode, endNode):
        super().__init__()
        self.startNode = startNode
        self.endNode = endNode
        self.startNode.connections.append(self)
        self.endNode.connections.append(self)
        self._color = QColor("#90A4AE")
        self._pen_width = 2
        self.setZValue(-1)
        self.setPen(QPen(self._color, self._pen_width))
        self.updatePosition()
        
    def updatePosition(self):
        line = QLineF(self.startNode.pos(), self.endNode.pos())
        self.setLine(line)
```

2. `project markmap/mindmap/scene.py`:
```python
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .models import Node, Connection

class MindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.startNode = None
        self.setSceneRect(-2000, -2000, 4000, 4000)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            text, ok = QInputDialog.getText(None, "Add Node", "Enter node text:")
            if ok and text:
                node = Node(text)
                node.setPos(event.scenePos())
                self.addItem(node)
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if isinstance(item, Node):
            if not self.startNode:
                self.startNode = item
                self.startNode.setSelected(True)
            else:
                if self.startNode != item:
                    connection = Connection(self.startNode, item)
                    self.addItem(connection)
                self.startNode.setSelected(False)
                self.startNode = None
        super().mouseDoubleClickEvent(event)
```

3. `project markmap/mindmap/window.py`:
```python
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .scene import MindMapScene
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
        self.scale(0.8, 0.8)
        
    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 0.9
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

class MindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('MindMap Creator Pro')
        self.setGeometry(100, 100, 1200, 800)
        
        self.scene = MindMapScene()
        self.view = MindMapView(self.scene)
        self.setCentralWidget(self.view)
        
        self.createToolBar()
        self.createStatusBar()
        
    def createToolBar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        saveAction = QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveMindMap)
        toolbar.addAction(saveAction)
        
        loadAction = QAction('Load', self)
        loadAction.setShortcut('Ctrl+O')
        loadAction.triggered.connect(self.loadMindMap)
        toolbar.addAction(loadAction)
        
        clearAction = QAction('Clear', self)
        clearAction.setShortcut('Ctrl+N')
        clearAction.triggered.connect(self.clearMindMap)
        toolbar.addAction(clearAction)
        
    def createStatusBar(self):
        statusBar = self.statusBar()
        statusBar.showMessage('Right click: Add Node | Double click: Connect Nodes | Ctrl+Mouse Wheel: Zoom')
        
    def saveMindMap(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Mind Map", "", "Mind Map Files (*.mmap)")
        if fileName:
            try:
                self.saveToFile(fileName)
                self.statusBar().showMessage('Mind map saved successfully', 3000)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save mind map: {str(e)}')
                
    def loadMindMap(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Mind Map", "", "Mind Map Files (*.mmap)")
        if fileName:
            try:
                self.loadFromFile(fileName)
                self.statusBar().showMessage('Mind map loaded successfully', 3000)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load mind map: {str(e)}')
    
    def saveToFile(self, fileName):
        data = {
            'nodes': [],
            'connections': []
        }
        
        nodes = []
        for item in self.scene.items():
            if isinstance(item, Node):
                nodes.append(item)
                data['nodes'].append({
                    'text': item.text,
                    'x': item.pos().x(),
                    'y': item.pos().y()
                })
            elif isinstance(item, Connection):
                data['connections'].append({
                    'start': nodes.index(item.startNode),
                    'end': nodes.index(item.endNode)
                })
                
        with open(fileName, 'w') as f:
            json.dump(data, f)
            
    def loadFromFile(self, fileName):
        self.clearMindMap()
        
        with open(fileName, 'r') as f:
            data = json.load(f)
            
        nodes = []
        for nodeData in data['nodes']:
            node = Node(nodeData['text'])
            node.setPos(nodeData['x'], nodeData['y'])
            self.scene.addItem(node)
            nodes.append(node)
            
        for connData in data['connections']:
            conn = Connection(nodes[connData['start']], nodes[connData['end']])
            self.scene.addItem(conn)
            
    def clearMindMap(self):
        reply = QMessageBox.question(self, 'Clear Mind Map',
                                   'Are you sure you want to clear the mind map?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.scene.clear()
            self.statusBar().showMessage('Mind map cleared', 3000)
```

4. `project markmap/mindmap/__init__.py`:
```python
from .window import MindMapWindow
from .scene import MindMapScene
from .models import Node, Connection

__version__ = '1.0.0'
```

5. `project markmap/main.py`:
```python
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mindmap import MindMapWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = MindMapWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

6. `project markmap/requirements.txt`:
```
PyQt5>=5.15.0
```
