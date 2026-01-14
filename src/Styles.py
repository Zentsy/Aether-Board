def get_styles():
    return """
    QMainWindow {
        background-color: #1a1d24;
    }
    
    QGraphicsView {
        border: none;
        background-color: #12151a;
    }
    
    #Toolbar {
        background-color: rgba(30, 35, 45, 240);
        border: 1px solid rgba(80, 120, 180, 80);
        border-radius: 12px;
    }
    
    #Toolbar QPushButton {
        background-color: rgba(60, 80, 120, 40);
        color: #a0c0e0;
        border: 1px solid rgba(80, 120, 180, 60);
        border-radius: 8px;
        padding: 8px;
        min-width: 36px;
        min-height: 36px;
    }
    
    #Toolbar QPushButton:hover {
        background-color: rgba(80, 120, 180, 80);
        border: 1px solid #5090d0;
        color: #ffffff;
    }
    
    #Toolbar QPushButton[active="true"] {
        background-color: rgba(80, 140, 220, 150);
        border: 2px solid #60a0e0;
        color: #ffffff;
    }
    
    #ColorBtn {
        border-radius: 14px;
        border: 2px solid rgba(255, 255, 255, 80);
        min-width: 28px;
        min-height: 28px;
        max-width: 28px;
        max-height: 28px;
    }
    
    #ColorBtn:hover {
        border: 2px solid #ffffff;
    }
    
    #ColorBtn[active="true"] {
        border: 3px solid #ffffff;
    }
    
    #CommandPalette {
        background-color: rgba(20, 25, 35, 250);
        border: 2px solid #5090d0;
        border-radius: 15px;
    }
    
    QLineEdit {
        background-color: rgba(255, 255, 255, 10);
        border: 1px solid rgba(80, 140, 220, 60);
        border-radius: 10px;
        color: #e0e8f0;
        font-family: 'Consolas', monospace;
        font-size: 14px;
        padding: 10px 15px;
    }

    QLineEdit:focus {
        border: 2px solid #5090d0;
        background-color: rgba(80, 140, 220, 10);
    }
    
    #SnippetPanel {
        background-color: rgba(20, 25, 35, 250);
        border-right: 1px solid rgba(80, 120, 180, 60);
    }
    
    #SnippetPanel QLabel {
        color: #8090a0;
    }
    
    #SnippetPanel QPushButton {
        background-color: rgba(60, 80, 120, 30);
        color: #c0d0e0;
        border: 1px solid rgba(80, 120, 180, 40);
        border-radius: 6px;
        padding: 8px 12px;
        text-align: left;
        font-size: 12px;
    }
    
    #SnippetPanel QPushButton:hover {
        background-color: rgba(80, 120, 180, 60);
        border: 1px solid #5090d0;
        color: #ffffff;
    }

    #ShortcutHint {
        background-color: rgba(60, 80, 120, 40);
        color: #80a0c0;
        border: 1px solid rgba(80, 120, 180, 60);
        border-radius: 4px;
        padding: 3px 8px;
        font-family: 'Consolas', monospace;
        font-size: 10px;
    }

    #HintContainer {
        background-color: rgba(20, 25, 35, 200);
        border: 1px solid rgba(80, 120, 180, 40);
        border-radius: 10px;
    }
    
    QLabel {
        color: #a0b0c0;
        font-family: 'Segoe UI', sans-serif;
    }
    
    #HUD_Title {
        color: #80a0c0;
        font-weight: bold;
        letter-spacing: 2px;
        font-size: 11px;
    }
    
    #SectionLabel {
        color: #5090d0;
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 1px;
    }
    
    /* OVERLAY STYLES */
    #SnippetOverlay {
        background-color: rgba(20, 25, 30, 250);
        border: 2px solid #5090d0;
        border-radius: 12px;
    }
    
    #SearchFrame {
        background-color: transparent;
        border: none;
    }
    
    #OverlayHeader {
        color: #ffffff;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 5px;
        letter-spacing: 2px;
    }
    
    #SnippetList {
        background-color: rgba(10, 12, 16, 180);
        border: 1px solid rgba(80, 120, 180, 40);
        border-radius: 6px;
        color: #d0e0f0;
        font-size: 14px;
        padding: 5px;
    }
    
    #SnippetList::item {
        padding: 10px;
        border-bottom: 1px solid rgba(80, 120, 180, 20);
    }
    
    #SnippetList::item:hover {
        background-color: rgba(80, 120, 180, 40);
        color: #ffffff;
    }
    
    #SnippetList::item:selected {
        background-color: rgba(80, 140, 220, 60);
        border-left: 3px solid #5090d0;
        color: #ffffff;
    }
    """
