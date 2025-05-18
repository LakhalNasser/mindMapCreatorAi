import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Node(QGraphicsItem):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.connections = []
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
    def boundingRect(self):
        return QRectF(-50, -30, 100, 60)
        
    def paint(self, painter, option, widget):
        painter.drawEllipse(-50, -30, 100, 60)
        painter.drawText(-45, -10, 90, 30, Qt.AlignCenter, self.text)
        
    def mousePressEvent(self, event):
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.update()
        super().mouseReleaseEvent(event)

class Connection(QGraphicsLineItem):
    def __init__(self, startNode, endNode):
        super().__init__()
        self.startNode = startNode
        self.endNode = endNode
        self.startNode.connections.append(self)
        self.endNode.connections.append(self)
        self.updatePosition()
        
    def updatePosition(self):
        line = QLineF(self.startNode.pos(), self.endNode.pos())
        self.setLine(line)

class MindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.startNode = None
        
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
            else:
                connection = Connection(self.startNode, item)
                self.addItem(connection)
                self.startNode = None
        super().mouseDoubleClickEvent(event)

class MindMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Mind Map Creator')
        self.setGeometry(100, 100, 800, 600)
        
        # Create scene and view
        self.scene = MindMapScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        # Create toolbar
        toolbar = self.addToolBar('Tools')
        
        # Save action
        saveAction = QAction('Save', self)
        saveAction.triggered.connect(self.saveMindMap)
        toolbar.addAction(saveAction)
        
        # Load action
        loadAction = QAction('Load', self)
        loadAction.triggered.connect(self.loadMindMap)
        toolbar.addAction(loadAction)
        
        # Clear action
        clearAction = QAction('Clear', self)
        clearAction.triggered.connect(self.clearMindMap)
        toolbar.addAction(clearAction)
        
        self.statusBar().showMessage('Right click to add node, Double click two nodes to connect')
        
    def saveMindMap(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Mind Map", "", "Mind Map Files (*.mm)")
        if fileName:
            nodes = []
            connections = []
            
            for item in self.scene.items():
                if isinstance(item, Node):
                    nodes.append({
                        'text': item.text,
                        'x': item.pos().x(),
                        'y': item.pos().y()
                    })
                elif isinstance(item, Connection):
                    connections.append({
                        'start': self.scene.items().index(item.startNode),
                        'end': self.scene.items().index(item.endNode)
                    })
                    
            with open(fileName, 'w') as f:
                import json
                json.dump({'nodes': nodes, 'connections': connections}, f)
                
    def loadMindMap(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Mind Map", "", "Mind Map Files (*.mm)")
        if fileName:
            self.clearMindMap()
            
            with open(fileName, 'r') as f:
                import json
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
        self.scene.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MindMapWindow()
    window.show()
    sys.exit(app.exec_())