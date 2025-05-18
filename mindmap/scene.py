from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .models import Node, Connection
import math

class MindMapScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.setBackgroundBrush(QColor("#FFFFFF"))
        
        # المتغيرات المسؤولة عن المسافات
        self.initial_radius = 500        # المسافة الأساسية من المركز
        self.level_spacing = 400         # المسافة بين المستويات
        self.min_node_distance = 250     # الحد الأدنى للمسافة بين العقد
        self.sibling_spacing = 300       # المسافة بين العقد الشقيقة
        self.branch_angle = 60           # زاوية توزيع الفروع
        
        self.root_node = None

    def create_from_json(self, data):
        self.clear()
        self.root_node = Node(data['center'], 0)
        self.addItem(self.root_node)
        self.root_node.setPos(0, 0)
        
        if 'branches' in data:
            branches = data['branches']
            # توزيع الفروع بشكل دائري
            angle_step = 360 / len(branches)
            
            for i, branch_data in enumerate(branches):
                angle = math.radians(i * angle_step)
                # استخدام المسافة الأساسية للمستوى الأول
                self.create_branch(self.root_node, branch_data, angle, self.initial_radius, 1)
        
        self.optimize_layout()
        self.update_all_connections()

    def create_branch(self, parent_node, branch_data, angle, radius, level):
        branch_node = Node(branch_data['text'], level)
        self.addItem(branch_node)
        
        # حساب موقع العقدة مع مراعاة المستوى
        level_factor = 1 - (level * 0.1)  # تقليل المسافة تدريجياً مع زيادة المستوى
        adjusted_radius = radius * level_factor
        
        x = parent_node.pos().x() + adjusted_radius * math.cos(angle)
        y = parent_node.pos().y() + adjusted_radius * math.sin(angle)
        branch_node.setPos(x, y)
        
        connection = self.create_curved_connection(parent_node, branch_node)
        self.addItem(connection)
        
        # معالجة العقد الفرعية
        if 'children' in branch_data and branch_data['children']:
            children = branch_data['children']
            # تعديل زاوية توزيع الأطفال
            child_angle_range = math.radians(self.branch_angle)
            child_radius = self.level_spacing * level_factor
            
            # توزيع العقد الفرعية
            for i, child_data in enumerate(children):
                child_angle = angle - (child_angle_range/2) + (child_angle_range * (i+1)/(len(children)+1))
                self.create_branch(branch_node, child_data, child_angle, child_radius, level + 1)


    def optimize_layout(self):
        iterations = 50
        damping = 0.6  # معامل تخميد للحركة
        
        for _ in range(iterations):
            moved = False
            for item1 in self.items():
                if not isinstance(item1, Node):
                    continue
                
                total_force_x = 0
                total_force_y = 0
                
                for item2 in self.items():
                    if not isinstance(item2, Node) or item1 == item2:
                        continue
                    
                    pos1 = item1.pos()
                    pos2 = item2.pos()
                    dx = pos2.x() - pos1.x()
                    dy = pos2.y() - pos1.y()
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # تطبيق قوة التنافر عندما تكون المسافة أقل من الحد الأدنى
                    if distance < self.min_node_distance:
                        force = self.min_node_distance - distance
                        angle = math.atan2(dy, dx)
                        force_x = -force * math.cos(angle) * damping
                        force_y = -force * math.sin(angle) * damping
                        
                        total_force_x += force_x
                        total_force_y += force_y
                        moved = True
                
                # تطبيق القوة الإجمالية
                if item1 != self.root_node and moved:
                    new_x = pos1.x() + total_force_x
                    new_y = pos1.y() + total_force_y
                    item1.setPos(new_x, new_y)
            
            if not moved:
                break
        
        self.update_all_connections()


    def organize_branches(self, parent_node, branches_data, level=1):
        if not branches_data:
            return
            
        total_width = len(branches_data) * self.node_spacing_x
        start_x = -total_width / 2
        
        for i, branch_data in enumerate(branches_data):
            # إنشاء عقدة الفرع
            branch_node = Node(branch_data['text'], level)
            self.addItem(branch_node)
            
            # حساب الموقع
            x = start_x + (i * self.node_spacing_x)
            y = parent_node.pos().y() + self.node_spacing_y
            branch_node.setPos(x, y)
            
            # إنشاء الرابط
            connection = self.create_curved_connection(parent_node, branch_node)
            self.addItem(connection)
            
            # معالجة الفروع الفرعية
            if 'children' in branch_data and branch_data['children']:
                self.organize_children(branch_node, branch_data['children'], level + 1)

    def organize_children(self, parent_node, children_data, level):
        total_width = len(children_data) * (self.node_spacing_x * 0.8)  # تقليل المسافة للمستويات الأعمق
        start_x = parent_node.pos().x() - (total_width / 2)
        
        for i, child_data in enumerate(children_data):
            child_node = Node(child_data['text'], level)
            self.addItem(child_node)
            
            # حساب الموقع مع مراعاة موقع الأب
            x = start_x + (i * (self.node_spacing_x * 0.8))
            y = parent_node.pos().y() + self.node_spacing_y
            child_node.setPos(x, y)
            
            # إنشاء رابط منحني
            connection = self.create_curved_connection(parent_node, child_node)
            self.addItem(connection)
            
            # معالجة الأبناء بشكل متكرر
            if 'children' in child_data and child_data['children']:
                self.organize_children(child_node, child_data['children'], level + 1)

    def create_curved_connection(self, start_node, end_node):
        connection = Connection(start_node, end_node)
        self.update_connection_position(connection)
        return connection

    def update_connection_position(self, connection):
        if not connection.startNode or not connection.endNode:
            return
        
        start_pos = connection.startNode.pos()
        end_pos = connection.endNode.pos()
        
        # تحسين شكل الخط
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        distance = math.sqrt(dx*dx + dy*dy)
        
        # إنشاء منحنى جميل
        mid_x = (start_pos.x() + end_pos.x()) / 2
        mid_y = (start_pos.y() + end_pos.y()) / 2
        
        # حساب نقطة التحكم للمنحنى
        angle = math.atan2(dy, dx)
        curve_strength = distance * 0.2
        
        control_point = QPointF(
            mid_x + curve_strength * math.cos(angle + math.pi/2),
            mid_y + curve_strength * math.sin(angle + math.pi/2)
        )
        
        # تحديث الخط
        line = QLineF(start_pos, end_pos)
        connection.setLine(line)
        
        # تحسين مظهر الخط
        pen = QPen(QColor("#90A4AE"), 2, Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        connection.setPen(pen)

    def update_all_connections(self):
        for item in self.items():
            if isinstance(item, Connection):
                self.update_connection_position(item)
                
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.update_all_connections()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update_all_connections()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.update_all_connections()

    def wheelEvent(self, event):
        # تحسين التكبير/التصغير
        if event.modifiers() == Qt.ControlModifier:
            factor = 1.1 if event.delta() > 0 else 0.9
            view = self.views()[0]
            view.scale(factor, factor)
        else:
            super().wheelEvent(event)