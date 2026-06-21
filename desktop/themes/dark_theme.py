def get_stylesheet() -> str:
    return """
    /* ======================= GENEL ======================= */
    QWidget {
        background-color: #1e1e1e;
        color: #dcdcdc;
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 13px;
    }

    QMainWindow::separator {
        background-color: #2d2d2d;
        width: 1px;
        height: 1px;
    }

    /* ===================== MENÜ ÇUBUĞU ===================== */
    QMenuBar {
        background-color: #2d2d2d;
        color: #dcdcdc;
        padding: 2px 4px;
        border-bottom: 1px solid #3e3e3e;
    }
    QMenuBar::item {
        padding: 4px 12px;
        background: transparent;
        border-radius: 4px;
    }
    QMenuBar::item:selected, QMenuBar::item:pressed {
        background-color: #3e3e3e;
    }

    QMenu {
        background-color: #252526;
        color: #dcdcdc;
        border: 1px solid #3e3e3e;
        padding: 4px;
    }
    QMenu::item {
        padding: 6px 30px 6px 20px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #094771;
    }
    QMenu::separator {
        height: 1px;
        background-color: #3e3e3e;
        margin: 4px 8px;
    }

    /* ===================== ARAÇ ÇUBUĞU ===================== */
    QToolBar {
        background-color: #252526;
        border-bottom: 1px solid #3e3e3e;
        padding: 4px;
        spacing: 6px;
    }
    QToolBar::separator {
        background-color: #3e3e3e;
        width: 1px;
        margin: 4px 6px;
    }

    /* ===================== BUTONLAR ===================== */
    QPushButton {
        background-color: #0e639c;
        color: #ffffff;
        border: 1px solid #0a4d7a;
        border-radius: 4px;
        padding: 6px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1177bb;
        border-color: #0e639c;
    }
    QPushButton:pressed {
        background-color: #094771;
        border-color: #073a5a;
    }
    QPushButton:disabled {
        background-color: #3c3c3c;
        color: #888888;
        border-color: #555555;
    }

    /* ===================== GİRİŞ ALANLARI ===================== */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
        background-color: #2d2d2d;
        color: #dcdcdc;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px;
        selection-background-color: #094771;
        selection-color: #ffffff;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #007acc;
    }
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #252525;
        color: #888888;
    }

    /* ===================== AÇILIR KUTU (COMBOBOX) ===================== */
    QComboBox {
        background-color: #2d2d2d;
        color: #dcdcdc;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 100px;
    }
    QComboBox:hover {
        border-color: #007acc;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: 1px solid #555555;
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #dcdcdc;
        margin-top: 2px;
    }
    QComboBox QAbstractItemView {
        background-color: #252526;
        color: #dcdcdc;
        selection-background-color: #094771;
        border: 1px solid #3e3e3e;
    }

    /* ===================== TABLO ===================== */
    QTableWidget, QTableView {
        background-color: #1e1e1e;
        alternate-background-color: #252526;
        color: #dcdcdc;
        gridline-color: #3e3e3e;
        border: 1px solid #3e3e3e;
        selection-background-color: #094771;
        selection-color: #ffffff;
    }
    QTableWidget::item, QTableView::item {
        padding: 4px 8px;
    }
    QHeaderView::section {
        background-color: #2d2d2d;
        color: #dcdcdc;
        padding: 6px 8px;
        border: 1px solid #3e3e3e;
        font-weight: bold;
    }
    QHeaderView::section:hover {
        background-color: #3e3e3e;
    }

    /* ===================== AĞAÇ GÖRÜNÜMÜ ===================== */
    QTreeWidget, QTreeView {
        background-color: #1e1e1e;
        color: #dcdcdc;
        border: 1px solid #3e3e3e;
        selection-background-color: #094771;
        selection-color: #ffffff;
    }
    QTreeWidget::item, QTreeView::item {
        padding: 4px 6px;
    }
    QTreeWidget::item:hover, QTreeView::item:hover {
        background-color: #2a2a2a;
    }

    /* ===================== KAYDIRMA ÇUBUĞU ===================== */
    QScrollBar:horizontal {
        background-color: #1e1e1e;
        height: 12px;
        border: none;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background-color: #555555;
        min-width: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #777777;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar:vertical {
        background-color: #1e1e1e;
        width: 12px;
        border: none;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #555555;
        min-height: 25px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #777777;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    /* ===================== SEKMELER ===================== */
    QTabWidget::pane {
        border: 1px solid #3e3e3e;
        background-color: #1e1e1e;
    }
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #dcdcdc;
        border: 1px solid #3e3e3e;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #1e1e1e;
        border-bottom: 2px solid #007acc;
        color: #ffffff;
    }
    QTabBar::tab:hover:!selected {
        background-color: #3e3e3e;
    }

    /* ===================== GRUP KUTUSU ===================== */
    QGroupBox {
        background-color: #252526;
        border: 1px solid #3e3e3e;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 18px;
        font-weight: bold;
        color: #dcdcdc;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #ffffff;
    }

    /* ===================== AYIRICI (SPLITTER) ===================== */
    QSplitter::handle {
        background-color: #3e3e3e;
        width: 2px;
        height: 2px;
    }
    QSplitter::handle:hover {
        background-color: #007acc;
    }

    /* ===================== DURUM ÇUBUĞU ===================== */
    QStatusBar {
        background-color: #007acc;
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
        background-color: #2d2d2d;
        border: 1px solid #3e3e3e;
        border-radius: 4px;
        text-align: center;
        color: #dcdcdc;
        height: 20px;
    }
    QProgressBar::chunk {
        background-color: #007acc;
        border-radius: 3px;
    }

    /* ===================== ETİKETLER ===================== */
    QLabel {
        color: #dcdcdc;
    }
    QLabel:disabled {
        color: #888888;
    }

    /* ===================== ONAY KUTUSU / RADYO ===================== */
    QCheckBox, QRadioButton {
        color: #dcdcdc;
        spacing: 8px;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #555555;
        border-radius: 3px;
        background-color: #2d2d2d;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #007acc;
        border-color: #007acc;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #007acc;
    }

    /* ===================== DİĞER ===================== */
    QToolTip {
        background-color: #252526;
        color: #dcdcdc;
        border: 1px solid #3e3e3e;
        padding: 4px;
        border-radius: 4px;
    }
    QDialog {
        background-color: #1e1e1e;
    }
    """