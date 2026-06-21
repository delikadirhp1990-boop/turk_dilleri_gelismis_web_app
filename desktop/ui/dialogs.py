from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel
)
import json

class StatisticsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İstatistikler")
        self.resize(600, 500)
        layout = QVBoxLayout(self)
        text = QTextEdit()
        text.setReadOnly(True)
        html = f"<h2>Toplam Kayıt: {stats['total']}</h2>"
        html += "<h3>Dillere Göre:</h3><ul>"
        for lang, cnt in stats.get("language_counts", {}).items():
            html += f"<li>{lang}: {cnt}</li>"
        html += "</ul>"
        text.setHtml(html)
        layout.addWidget(text)
        btn = QPushButton("Kapat")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)