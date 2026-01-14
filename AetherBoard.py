import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFrame, QLineEdit, 
                             QLabel, QGraphicsOpacityEffect, QColorDialog)
from PyQt6.QtCore import Qt, QPointF, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

from CanvasEngine import CanvasEngine
from LatexRenderer import LatexRenderer
from Styles import get_styles
from Snippets import SnippetOverlay

class CommandPalette(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CommandPalette")
        self.setFixedSize(500, 70)
        self.hide()
        
        layout = QVBoxLayout(self)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter LaTeX formula... (ENTER to confirm)")
        layout.addWidget(self.input)
        
    def show_at(self, pos, initial_text=""):
        self.move(int(pos.x() - 250), int(pos.y() - 35))
        self.show()
        self.input.setFocus()
        self.input.setText(initial_text)
        self.input.selectAll()

class AetherBoard(QMainWindow):
    # Paleta de cores padrão
    COLORS = [
        "#ffffff",  # Branco
        "#5090d0",  # Azul
        "#50d090",  # Verde
        "#f0a030",  # Laranja
        "#e05050",  # Vermelho
        "#c060d0",  # Roxo
        "#f0e050",  # Amarelo
    ]
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AETHER BOARD // Engineering Canvas")
        self.resize(1366, 768)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = CanvasEngine()
        # Snippets agora é Overlay
        self.snippets_overlay = SnippetOverlay(self)
        self.snippets_overlay.snippet_selected.connect(self.insert_snippet)
        
        # Layout apenas com Canvas
        self.main_layout.addWidget(self.canvas)
        
        self.cmd_palette = CommandPalette(self)
        self.cmd_palette.input.returnPressed.connect(self.handle_latex_input)
        
        self.setup_ui()
        
        self.canvas.clicked_at.connect(self.open_palette)
        self.canvas.pen_size_changed.connect(self.update_size_hud)
        self.setStyleSheet(get_styles())

    def update_size_hud(self, size):
        self.size_label.setText(f"SIZE: {size}px")

    def get_svg_icon(self, svg_data, color="#80a0c0"):
        svg_content = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
             stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_data}
        </svg>
        """
        renderer = QSvgRenderer(svg_content.encode('utf-8'))
        pixmap = QPixmap(QSize(28, 28))
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Uso seguro do QPainter
        painter = QPainter()
        try:
            if painter.begin(pixmap):
                renderer.render(painter)
                painter.end()
        except Exception as e:
            print(f"ICON PAINT ERROR: {e}")
            if painter.isActive():
                painter.end()
        
        return QIcon(pixmap)

    def setup_ui(self):
        # Status Bar
        self.status_bar = QFrame(self)
        self.status_bar.setObjectName("Toolbar")
        self.status_bar.setFixedHeight(36)
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(15, 0, 15, 0)
        
        self.hud_title = QLabel("AETHER BOARD v4.0 // INFINITE CANVAS")
        self.hud_title.setObjectName("HUD_Title")
        status_layout.addWidget(self.hud_title)
        status_layout.addStretch()
        
        self.size_label = QLabel("SIZE: 4px")
        self.size_label.setObjectName("HUD_Title")
        status_layout.addWidget(self.size_label)
        status_layout.addSpacing(20)
        
        self.mode_label = QLabel("TOOL: PENCIL")
        self.mode_label.setStyleSheet("color: #e0e8f0; font-weight: bold;")
        status_layout.addWidget(self.mode_label)
        
        self.main_layout.addWidget(self.status_bar)

        # Main Toolbar
        self.toolbar = QFrame(self)
        self.toolbar.setObjectName("Toolbar")
        self.toolbar.setFixedHeight(50)
        t_layout = QHBoxLayout(self.toolbar)
        t_layout.setContentsMargins(12, 0, 12, 0)
        t_layout.setSpacing(6)
        
        # Ferramentas
        icons = {
            "library": '<path d="m21.6 17.5-6.6-13.2A2 2 0 0 0 13.2 3L2 5.5a2 2 0 0 0-1.5 2.5l3.5 14A2 2 0 0 0 6 23.5l14-2.5a2 2 0 0 0 1.6-3.5ZM6.5 21 3 7l11.5-2.5L18 18.5 6.5 21Z"/>',
            "move": '<path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/><path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v4"/><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>',
            "pencil": '<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>',
            "highlighter": '<path d="m9 11-6 6v3h9l3-3"/><path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/>',
            "line": '<path d="M5 19L19 5"/>',
            "eraser": '<path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/>',
            "text": '<path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/>',
            "clear": '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>'
        }
        
        self.tools = {}
        for tid, svg in icons.items():
            btn = QPushButton()
            btn.setIcon(self.get_svg_icon(svg))
            btn.setIconSize(QSize(20, 20))
            btn.setToolTip(tid.upper())
            
            if tid == "library":
                btn.clicked.connect(self.toggle_snippets)
            else:
                btn.clicked.connect(lambda ch, t=tid: self.set_tool(t))
                
            self.tools[tid] = btn
            t_layout.addWidget(btn)

        # Separador
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet("background-color: rgba(80, 120, 180, 60);")
        t_layout.addWidget(sep)
        t_layout.addSpacing(10)

        # Seletor de Cores
        self.color_btns = []
        for color in self.COLORS:
            btn = QPushButton()
            btn.setObjectName("ColorBtn")
            btn.setStyleSheet(f"background-color: {color};")
            btn.clicked.connect(lambda ch, c=color: self.set_color(c))
            self.color_btns.append(btn)
            t_layout.addWidget(btn)

        # Botão de cor customizada
        custom_btn = QPushButton("+")
        custom_btn.setObjectName("ColorBtn")
        custom_btn.setStyleSheet("background-color: #333; color: #fff;")
        custom_btn.clicked.connect(self.pick_custom_color)
        t_layout.addWidget(custom_btn)

        # Hints
        self.hints = QFrame(self)
        self.hints.setObjectName("HintContainer")
        self.hints.setFixedSize(280, 120)
        h_layout = QVBoxLayout(self.hints)
        h_layout.setContentsMargins(12, 10, 12, 10)
        
        tips = [
            ("CTRL+SCROLL", "Pen Size"),
            ("SHIFT+DRAG", "Pan Canvas"),
            ("SCROLL", "Zoom"),
            ("SPACE", "Overlay Mode")
        ]
        for k, d in tips:
            row = QHBoxLayout()
            l1 = QLabel(k); l1.setObjectName("ShortcutHint")
            l2 = QLabel(d)
            row.addWidget(l1); row.addStretch(); row.addWidget(l2)
            h_layout.addLayout(row)

        self.set_tool("pencil")
        self.set_color(self.COLORS[1])  # Azul padrão
        
        # Ajusta tamanho da toolbar baseado no conteúdo
        self.toolbar.adjustSize()
        # Garante um minimo
        if self.toolbar.width() < 800:
            self.toolbar.resize(800, 50)

    def set_color(self, color):
        self.canvas.pen_color = QColor(color)
        self.canvas.update_tool_cursor()
        # Atualiza visual dos botões
        for btn in self.color_btns:
            try:
                is_active = btn.styleSheet().find(color) != -1
                btn.setProperty("active", is_active)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            except: pass

    def pick_custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_color(color.name())

    def set_tool(self, tool_id):
        if tool_id == "clear":
            self.canvas.clear_all()
            return
        
        self.canvas.tool = tool_id
        self.canvas.update_tool_cursor()
        self.cmd_palette.hide()
        self.mode_label.setText(f"TOOL: {tool_id.upper()}")
        
        for tid, btn in self.tools.items():
            btn.setProperty("active", tid == tool_id)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def open_palette(self, pos, initial_text=""):
        global_pos = self.canvas.mapFromScene(pos)
        self.last_click_pos = pos
        self.cmd_palette.show_at(global_pos, initial_text)

    def handle_latex_input(self):
        latex = self.cmd_palette.input.text()
        if latex:
            self.insert_snippet(latex, self.last_click_pos)
        self.cmd_palette.hide()

    def insert_snippet(self, latex, pos=None):
        try:
            pix = LatexRenderer.render(latex, color='#5090d0')
            if pos is None:
                pos = self.canvas.mapToScene(self.canvas.rect().center())
            self.canvas.add_latex(pix, pos, latex)
        except Exception as e:
            print(f"Error: {e}")

    def toggle_snippets(self):
        if self.snippets_overlay.isVisible():
            self.snippets_overlay.hide()
        else:
            self.snippets_overlay.show_centered()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'toolbar'):
            self.toolbar.adjustSize() # Garante que cabe tudo
            t_width = self.toolbar.width()
            self.toolbar.move(int((self.width() - t_width)/2), 20)
        
        if hasattr(self, 'hints'):
            self.hints.move(self.width() - 320, self.height() - 180)
        # Fecha overlay ao redimensionar (opcional, mas bom pra evitar glitch)
        if hasattr(self, 'snippets_overlay'):
             if self.snippets_overlay.isVisible():
                 self.snippets_overlay.show_centered()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_snippets()
        elif event.key() == Qt.Key.Key_Space:
            self.setWindowOpacity(1.0 if self.windowOpacity() < 1.0 else 0.6)
        elif event.key() == Qt.Key.Key_Escape:
            self.cmd_palette.hide()
            self.snippets_overlay.hide()
        elif event.key() == Qt.Key.Key_Delete:
            for item in self.canvas.scene.selectedItems():
                self.canvas.scene.removeItem(item)

    def closeEvent(self, event):
        self.save_state()
        super().closeEvent(event)

    def save_state(self):
        import json
        import os
        try:
            data = self.canvas.serialize_scene()
            path = os.path.join(os.getcwd(), 'board_data.json')
            with open(path, 'w') as f:
                json.dump(data, f)
            print("BOARD STATE SAVED.")
        except Exception as e:
            print(f"SAVE ERROR: {e}")

    def load_state(self):
        import json
        import os
        path = os.path.join(os.getcwd(), 'board_data.json')
        if not os.path.exists(path):
            return
            
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Carrega primitivas (Linhas/Paths)
            self.canvas.deserialize_scene(data)
            
            # Carrega LaTeX separadamente (precisa do renderer)
            for item in data.get('items', []):
                if item.get('type') == 'latex':
                    try:
                        latex = item['content']
                        x, y = item['x'], item['y']
                        pix = LatexRenderer.render(latex, color='#5090d0')
                        self.canvas.add_latex(pix, QPointF(x, y), latex)
                    except: pass
            
            print("BOARD STATE RESTORED.")
        except Exception as e:
            print(f"LOAD ERROR: {e}")
            # Se o arquivo estiver corrompido, faz backup e deleta para não travar o app
            try:
                import shutil
                backup_path = path + ".bak"
                shutil.move(path, backup_path)
                print(f"Corrupted save file moved to {backup_path}")
            except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AetherBoard()
    # Carrega estado salvo após mostrar a janela para evitar lag no startup
    QTimer.singleShot(100, window.load_state)
    window.show()
    sys.exit(app.exec())
