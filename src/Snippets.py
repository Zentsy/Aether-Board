from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, 
                             QScrollArea, QLineEdit, QListWidget, QListWidgetItem,
                             QGraphicsOpacityEffect, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer

class SnippetOverlay(QFrame):
    snippet_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SnippetOverlay")
        self.setFixedSize(400, 500)
        self.hide()
        
        # Sombra
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header com Busca
        search_frame = QFrame()
        search_frame.setObjectName("SearchFrame")
        s_layout = QVBoxLayout(search_frame)
        s_layout.setContentsMargins(0,0,0,0)
        
        header = QLabel("FORMULA DATABASE SEARCH")
        header.setObjectName("OverlayHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.addWidget(header)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search formulas (e.g., 'integral', 'newton')...")
        self.search_input.textChanged.connect(self.filter_snippets)
        s_layout.addWidget(self.search_input)
        
        layout.addWidget(search_frame)
        
        # Lista de Resultados
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("SnippetList")
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # Dica
        hint = QLabel("Press ESC to close")
        hint.setStyleSheet("color: #5090d0; font-size: 10px; font-style: italic;")
        hint.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(hint)
        
        self.all_snippets = []
        self.load_database()
        self.refresh_list("")

    def load_database(self):
        # Database Centralizada
        self.all_snippets = [
            # CÁLCULO
            ("Deriv. Exp", r"\frac{d}{dx}e^x = e^x"),
            ("Integral Power", r"\int x^n dx = \frac{x^{n+1}}{n+1}"),
            ("Limit Sin", r"\lim_{x \to 0} \frac{\sin x}{x} = 1"),
            ("Divergence", r"\nabla \cdot \mathbf{F}"),
            ("Curl", r"\nabla \times \mathbf{F}"),
            ("Chain Rule", r"\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx}"),
            ("Integration by Parts", r"\int u dv = uv - \int v du"),
            
            # FÍSICA CLÁSSICA
            ("Newton 2nd Law", r"F = m a"),
            ("Kinetic Energy", r"E_k = \frac{1}{2}mv^2"),
            ("Potential Energy", r"U = mgh"),
            ("Momentum", r"p = mv"),
            ("Torque", r"\tau = r \times F"),
            ("Gravitation", r"F = G\frac{m_1m_2}{r^2}"),
            ("Hooke's Law", r"F = -kx"),
            
            # ELETROMAGNETISMO
            ("Gauss Law", r"\nabla \cdot E = \frac{\rho}{\epsilon_0}"),
            ("Gauss Mag", r"\nabla \cdot B = 0"),
            ("Faraday's Law", r"\nabla \times E = -\frac{\partial B}{\partial t}"),
            ("Lorentz Force", r"F = q(E + v \times B)"),
            ("Ohm's Law", r"V = IR"),
            ("Capacitance", r"Q = CV"),
            ("Power Elec", r"P = VI"),
            
            # QUÂNTICA
            ("Schrodinger Eq", r"i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi"),
            ("Heisenberg Uncert", r"\Delta x \Delta p \geq \frac{\hbar}{2}"),
            ("Photon Energy", r"E = hf"),
            ("De Broglie", r"\lambda = \frac{h}{p}"),
            
            # QUÍMICA
            ("Ideal Gas", r"PV = nRT"),
            ("pH Definition", r"pH = -\log[H^+]"),
            ("Gibbs Free Energy", r"\Delta G = \Delta H - T\Delta S"),
            ("Molarity", r"M = \frac{n}{V}"),
            
            # ÁLGEBRA
            ("Quadratic Formula", r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"),
            ("Euler Identity", r"e^{i\pi} + 1 = 0"),
            ("Sum 1 to n", r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}"),
            ("Pythagoras", r"a^2 + b^2 = c^2")
        ]

    def filter_snippets(self, text):
        self.refresh_list(text)

    def refresh_list(self, filter_text):
        self.list_widget.clear()
        filter_text = filter_text.lower()
        
        for name, latex in self.all_snippets:
            if filter_text in name.lower() or filter_text in latex.lower():
                item = QListWidgetItem(f"{name}")
                item.setData(Qt.ItemDataRole.UserRole, latex)
                self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        latex = item.data(Qt.ItemDataRole.UserRole)
        self.snippet_selected.emit(latex)
        self.hide()

    def show_centered(self):
        if self.parent():
            geo = self.parent().geometry()
            # Centraliza na tela
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(x, y)
        self.show()
        self.search_input.setFocus()
        self.search_input.clear()
