from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsPathItem, QGraphicsDropShadowEffect, QGraphicsLineItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QCursor, QPixmap, QRadialGradient
import json

class AetherLatexItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, latex_text):
        super().__init__(pixmap)
        self.latex_text = latex_text
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setZValue(100) # Fórmulas sempre acima

class CanvasEngine(QGraphicsView):
    clicked_at = pyqtSignal(QPointF, str) 
    pen_size_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-50000, -50000, 100000, 100000)
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        self.current_path_item = None
        self.preview_line = None
        self.current_path = None
        self.drawing = False
        self.panning = False
        self.last_mouse_pos = None
        self.start_pos = None
        
        self.pen_color = QColor("#5090d0")
        self.pen_width = 4
        self.tool = "pencil"
        
        # Grid no background
        self.update_tool_cursor()

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor("#12151a"))
        pen = QPen(QColor(80, 120, 180, 25))
        pen.setWidth(1)
        painter.setPen(pen)
        gap = 50
        left = int(rect.left()) - (int(rect.left()) % gap)
        top = int(rect.top()) - (int(rect.top()) % gap)
        x = left
        while x < rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += gap
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += gap

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = 1 if event.angleDelta().y() > 0 else -1
            self.change_pen_size(delta)
        else:
            zoom_in_factor = 1.15
            zoom_out_factor = 1 / zoom_in_factor
            zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
            self.scale(zoom_factor, zoom_factor)

    def change_pen_size(self, delta):
        self.pen_width = max(1, min(100, self.pen_width + delta))
        self.pen_size_changed.emit(self.pen_width)
        self.update_tool_cursor()

    def update_tool_cursor(self):
        if self.tool == "eraser":
            size = self.pen_width * 4
        else:
            size = self.pen_width
            if self.tool == "highlighter": size *= 3
            
        pix_size = max(size + 10, 32)
        pixmap = QPixmap(int(pix_size), int(pix_size))
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter()
        try:
            if painter.begin(pixmap):
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                center = pix_size / 2
                color = self.pen_color
                
                if self.tool == "eraser":
                    pen = QPen(QColor("#ffffff"))
                    pen.setWidth(2)
                    pen.setStyle(Qt.PenStyle.DashLine)
                    painter.setPen(pen)
                    painter.drawEllipse(QPointF(center, center), size/2, size/2)
                elif self.tool == "text":
                    self.setCursor(Qt.CursorShape.IBeamCursor)
                    painter.end()
                    return
                else:
                    painter.setBrush(color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(center, center), size/2, size/2)
                painter.end()
        except Exception as e:
            print(f"CURSOR PAINT ERROR: {e}")
            if painter.isActive():
                painter.end()
                
        self.setCursor(QCursor(pixmap))

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.start_pos = scene_pos

        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.ShiftModifier):
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        if self.tool == "move":
            super().mousePressEvent(event)
            return

        if self.tool == "eraser":
            self.erase_at(scene_pos)
            self.drawing = True
            return

        item = self.scene.itemAt(scene_pos, self.transform())
        if self.tool == "text":
            if isinstance(item, AetherLatexItem):
                self.clicked_at.emit(scene_pos, item.latex_text)
                self.scene.removeItem(item)
            else:
                self.clicked_at.emit(scene_pos, "")
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            
            if self.tool == "line":
                self.preview_line = QGraphicsLineItem(scene_pos.x(), scene_pos.y(), scene_pos.x(), scene_pos.y())
                pen = QPen(self.pen_color)
                pen.setWidth(self.pen_width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                self.preview_line.setPen(pen)
                self.scene.addItem(self.preview_line)
                return

            self.current_path = QPainterPath()
            self.current_path.moveTo(scene_pos)
            
            pen = QPen(self.pen_color)
            width = self.pen_width
            
            if self.tool == "highlighter":
                color = QColor(self.pen_color)
                color.setAlpha(80)
                pen.setColor(color)
                pen.setWidth(width * 4)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            else:
                pen.setWidth(width)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            
            self.current_path_item = QGraphicsPathItem(self.current_path)
            self.current_path_item.setPen(pen)
            
            if self.tool == "highlighter":
                self.current_path_item.setZValue(-10)
            
            self.scene.addItem(self.current_path_item)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = self.mapToScene(event.pos()) - self.mapToScene(self.last_mouse_pos)
            self.last_mouse_pos = event.pos()
            self.translate(delta.x(), delta.y())
            return

        if self.tool == "move":
            super().mouseMoveEvent(event)
            return

        scene_pos = self.mapToScene(event.pos())

        if self.drawing:
            if self.tool == "eraser":
                self.erase_at(scene_pos)
                
            elif self.tool == "line" and self.preview_line:
                line = self.preview_line.line()
                line.setP2(scene_pos)
                self.preview_line.setLine(line)
                
            elif self.current_path:
                last_point = self.current_path.currentPosition()
                dist = (scene_pos - last_point).manhattanLength()
                if dist > 2:
                    self.current_path.quadTo(last_point, (last_point + scene_pos) / 2)
                    self.current_path_item.setPath(self.current_path)

    def mouseReleaseEvent(self, event):
        if self.tool == "move":
            super().mouseReleaseEvent(event)

        self.drawing = False
        self.panning = False
        self.update_tool_cursor()
        self.current_path = None
        self.current_path_item = None
        self.preview_line = None

    def erase_at(self, pos):
        size = self.pen_width * 4
        rect = QRectF(pos.x() - size/2, pos.y() - size/2, size, size)
        items = self.scene.items(rect)
        for item in items:
            if isinstance(item, (QGraphicsPathItem, AetherLatexItem, QGraphicsLineItem)):
                self.scene.removeItem(item)
                
    def add_latex(self, pixmap, pos, latex_text):
        item = AetherLatexItem(pixmap, latex_text)
        item.setPos(pos)
        self.scene.addItem(item)
        
    def clear_all(self):
        self.scene.clear()

    # --- SERIALIZATION ---
    def serialize_scene(self):
        items_data = []
        # Invertemos para salvar do fundo para o topo, facilitando o load sequencial
        for item in reversed(self.scene.items()):
            data = {}
            if isinstance(item, AetherLatexItem):
                data['type'] = 'latex'
                data['content'] = item.latex_text
                data['x'] = item.pos().x()
                data['y'] = item.pos().y()
                items_data.append(data)
                
            elif isinstance(item, QGraphicsLineItem):
                data['type'] = 'line'
                line = item.line()
                data['x1'] = line.x1()
                data['y1'] = line.y1()
                data['x2'] = line.x2()
                data['y2'] = line.y2()
                data['color'] = item.pen().color().name(QColor.NameFormat.HexArgb)
                data['width'] = item.pen().width()
                items_data.append(data)
                
            elif isinstance(item, QGraphicsPathItem):
                data['type'] = 'path'
                data['color'] = item.pen().color().name(QColor.NameFormat.HexArgb)
                data['width'] = item.pen().width()
                data['z'] = item.zValue()
                
                # Serializa o Path
                path = item.path()
                path_elements = []
                for i in range(path.elementCount()):
                    elm = path.elementAt(i)
                    path_elements.append({
                        'type': elm.type.value, # 0=MoveTo, 1=LineTo, 2=CurveTo
                        'x': elm.x,
                        'y': elm.y
                    })
                data['path'] = path_elements
                items_data.append(data)
                
        return {'version': '1.0', 'items': items_data}

    def deserialize_scene(self, data):
        self.scene.clear()
        for item_data in data.get('items', []):
            if item_data['type'] == 'latex':
                # O renderizador será chamado externamente pelo controller para evitar dep circular
                pass 
                
            elif item_data['type'] == 'line':
                line_item = QGraphicsLineItem(
                    item_data['x1'], item_data['y1'],
                    item_data['x2'], item_data['y2']
                )
                pen = QPen(QColor(item_data['color']))
                pen.setWidth(item_data['width'])
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                line_item.setPen(pen)
                self.scene.addItem(line_item)
                
            elif item_data['type'] == 'path':
                path = QPainterPath()
                elements = item_data['path']
                if not elements: continue
                
                # Reconstrói Path
                # Qt PainterPath Elements: 0=MoveTo, 1=LineTo, 2=CurveTo, 3=CurveToData
                # Simplificação: Apenas recriamos movimentos.
                
                path.moveTo(elements[0]['x'], elements[0]['y'])
                
                i = 1
                while i < len(elements):
                    elm = elements[i]
                    if elm['type'] == 0: # MoveTo
                        path.moveTo(elm['x'], elm['y'])
                    elif elm['type'] == 1: # LineTo
                        path.lineTo(elm['x'], elm['y'])
                    elif elm['type'] == 2: # CurveTo
                        # Pega os proximos 2 pontos de controle?
                        # quadTo usa 1 ponto de controle e 1 final.
                        # O QPainterPath salva cubicTo internamente geralmente.
                        # Vamos assumir lineTo para simplicidade se complexo, ou tentar quadTo
                        path.quadTo(elm['x'], elm['y'], elm['x'], elm['y']) # Fallback simples
                    
                    # Refinamento: QPainterPath serializado desse jeito é tricky.
                    # Melhora: Vamos apenas linkar os pontos como quadTo suavizado se não for move
                    if i > 0 and elm['type'] != 0:
                        prev = elements[i-1]
                        # path.quadTo(prev['x'], prev['y'], elm['x'], elm['y'])
                        path.lineTo(elm['x'], elm['y']) # Mais seguro
                        
                    i += 1
                
                path_item = QGraphicsPathItem(path)
                pen = QPen(QColor(item_data['color']))
                pen.setWidth(item_data['width'])
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                path_item.setPen(pen)
                if 'z' in item_data:
                     path_item.setZValue(item_data['z'])
                self.scene.addItem(path_item)
