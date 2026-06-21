def get_stylesheet() -> str:
    return """
    /* ======================= GENEL ======================= */
    QWidget {
        background-color: #f5f5f5;
        color: #1a1a1a;
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 13px;
    }

    QMainWindow::separator {
        background-color: #e0e0e0;
        width: 1px;
        height: 1px;
    }

    /* ===================== MENÜ ÇUBUĞU ===================== */
    QMenuBar {
        background-color: #f0f0f0;
        color: #1a1a1a;
        padding: 2px 4px;
        border-bottom: 1px solid #d0d0d0;
    }
    QMenuBar::item {
        padding: 4px 12px;
        background: transparent;
        border-radius: 4px;
    }
    QMenuBar::item:selected, QMenuBar::item:pressed {
        background-color: #e0e0e0;
    }

    QMenu {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #d0d0d0;
        padding: 4px;
    }
    QMenu::item {
        padding: 6px 30px 6px 20px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #0078d7;
        color: #ffffff;
    }
    QMenu::separator {
        height: 1px;
        background-color: #e0e0e0;
        margin: 4px 8px;
    }

    /* ===================== ARAÇ ÇUBUĞU ===================== */
    QToolBar {
        background-color: #f0f0f0;
        border-bottom: 1px solid #d0d0d0;
        padding: 4px;
        spacing: 6px;
    }
    QToolBar::separator {
        background-color: #d0d0d0;
        width: 1px;
        margin: 4px 6px;
    }

    /* ===================== BUTONLAR ===================== */
    QPushButton {
        background-color: #0078d7;
        color: #ffffff;
        border: 1px solid #005a9e;
        border-radius: 4px;
        padding: 6px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1c8ae8;
        border-color: #0078d7;
    }
    QPushButton:pressed {
        background-color: #005a9e;
        border-color: #004578;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #888888;
        border-color: #aaaaaa;
    }

    /* ===================== GİRİŞ ALANLARI ===================== */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #a0a0a0;
        border-radius: 4px;
        padding: 5px;
        selection-background-color: #0078d7;
        selection-color: #ffffff;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #0078d7;
    }
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #f0f0f0;
        color: #888888;
    }

    /* ===================== AÇILIR KUTU (COMBOBOX) ===================== */
    QComboBox {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #a0a0a0;
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 100px;
    }
    QComboBox:hover {
        border-color: #0078d7;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: 1px solid #a0a0a0;
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #1a1a1a;
        margin-top: 2px;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #1a1a1a;
        selection-background-color: #0078d7;
        selection-color: #ffffff;
        border: 1px solid #d0d0d0;
    }

    /* ===================== TABLO ===================== */
    QTableWidget, QTableView {
        background-color: #ffffff;
        alternate-background-color: #f9f9f9;
        color: #1a1a1a;
        gridline-color: #e0e0e0;
        border: 1px solid #d0d0d0;
        selection-background-color: #0078d7;
        selection-color: #ffffff;
    }
    QTableWidget::item, QTableView::item {
        padding: 4px 8px;
    }
    QHeaderView::section {
        background-color: #f0f0f0;
        color: #1a1a1a;
        padding: 6px 8px;
        border: 1px solid #d0d0d0;
        font-weight: bold;
    }
    QHeaderView::section:hover {
        background-color: #e0e0e0;
    }

    /* ===================== AĞAÇ GÖRÜNÜMÜ ===================== */
    QTreeWidget, QTreeView {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #d0d0d0;
        selection-background-color: #0078d7;
        selection-color: #ffffff;
    }
    QTreeWidget::item, QTreeView::item {
        padding: 4px 6px;
    }
    QTreeWidget::item:hover, QTreeView::item:hover {
        background-color: #e8f4ff;
    }

    /* ===================== KAYDIRMA ÇUBUĞU ===================== */
    QScrollBar:horizontal {
        background-color: #f5f5f5;
        height: 12px;
        border: none;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        min-width: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar:vertical {
        background-color: #f5f5f5;
        width: 12px;
        border: none;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        min-height: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    /* ===================== SEKMELER ===================== */
    QTabWidget::pane {
        border: 1px solid #d0d0d0;
        background-color: #f5f5f5;
    }
    QTabBar::tab {
        background-color: #e8e8e8;
        color: #1a1a1a;
        border: 1px solid #d0d0d0;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: 2px solid #0078d7;
        color: #000000;
    }
    QTabBar::tab:hover:!selected {
        background-color: #dcdcdc;
    }

    /* ===================== GRUP KUTUSU ===================== */
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 18px;
        font-weight: bold;
        color: #1a1a1a;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #000000;
    }

    /* ===================== AYIRICI (SPLITTER) ===================== */
    QSplitter::handle {
        background-color: #d0d0d0;
        width: 2px;
        height: 2px;
    }
    QSplitter::handle:hover {
        background-color: #0078d7;
    }

    /* ===================== DURUM ÇUBUĞU ===================== */
    QStatusBar {
        background-color: #0078d7;
        color: #ffffff;
        border-top: 1px solid #005a9e;
        padding: 2px 8px;
        font-weight: bold;
    }
    QStatusBar::item {
        border: none;
    }
    QStatusBar QLabel {
        color: #ffffff;
    }

    /* ===================== İLERLEME ÇUBUĞU ===================== */
    QProgressBar {
        background-color: #e8e8e8;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        text-align: center;
        color: #1a1a1a;
        height: 20px;
    }
    QProgressBar::chunk {
        background-color: #0078d7;
        border-radius: 3px;
    }

    /* ===================== ETİKETLER ===================== */
    QLabel {
        color: #1a1a1a;
    }
    QLabel:disabled {
        color: #888888;
    }

    /* ===================== ONAY KUTUSU / RADYO ===================== */
    QCheckBox, QRadioButton {
        color: #1a1a1a;
        spacing: 8px;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #a0a0a0;
        border-radius: 3px;
        background-color: #ffffff;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #0078d7;
        border-color: #0078d7;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #0078d7;
    }

    /* ===================== DİĞER ===================== */
    QToolTip {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #d0d0d0;
        padding: 4px;
        border-radius: 4px;
    }
    QDialog {
        background-color: #f5f5f5;
    }
    """