import json
from datetime import datetime, timezone
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QLineEdit, QTextEdit, QPushButton, QLabel, QComboBox,
    QMessageBox, QFileDialog, QMenuBar, QAction, QToolBar,
    QStatusBar, QApplication, QAbstractItemView, QGroupBox,
    QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.json_manager import JsonManager
from core.firebase_manager import FirebaseManager
from core.ai_client import AIClient
from core.sync_engine import SyncEngine
from core.search_engine import SearchEngine
from core.statistics import Statistics
from ui.dialogs import StatisticsDialog

class MainWindow(QMainWindow):
    SUPPORTED_LANGUAGES = ["TR", "KZ", "UZ", "TM", "AZ", "KY"]
    CATEGORIES = [
        "Kelimeler", "Dil Bilgisi", "Ses Bilgisi", "Yazım", "Noktalama",
        "Sözcük Türleri", "Cümle Bilgisi", "Atasözleri", "Deyimler", "Etimoloji",
        "Morfoloji", "Sözdizimi", "Fonetik", "Kendi Notlarım"
    ]

    def __init__(self, json_manager: JsonManager, firebase_manager: FirebaseManager, ai_client: AIClient):
        super().__init__()
        self.json_manager = json_manager
        self.firebase_manager = firebase_manager
        self.ai_client = ai_client
        self.sync_engine = SyncEngine(json_manager, firebase_manager) if firebase_manager else None
        self.current_records = []
        self.selected_record = None

        self.setWindowTitle("Türk Dilleri Dil Verisi Yönetim Sistemi")

        # ---------- Ekrana sığacak pencere boyutu ----------
        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            width = int(available.width() * 0.85)
            height = int(available.height() * 0.85)
            x = (available.width() - width) // 2
            y = (available.height() - height) // 2
            self.setGeometry(x, y, width, height)
        else:
            self.resize(1400, 800)
        self.setMinimumSize(1024, 680)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Üst ve alt splitter
        vert_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(vert_splitter)

        horz_splitter = QSplitter(Qt.Horizontal)
        vert_splitter.addWidget(horz_splitter)

        # Sol panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Dil Seçimi"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(self.SUPPORTED_LANGUAGES)
        self.lang_combo.currentTextChanged.connect(self._apply_filters)
        left_layout.addWidget(self.lang_combo)
        left_layout.addWidget(QLabel("Kategoriler"))
        self.cat_tree = QTreeWidget()
        self.cat_tree.setHeaderLabel("Kategori")
        self._populate_cat_tree()
        self.cat_tree.currentItemChanged.connect(self._on_cat_selected)
        left_layout.addWidget(self.cat_tree)

        # Orta panel – kayıt tablosu
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Başlık", "Dil", "Kategori", "Tarih"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_record_selected)

        # Sağ panel – detay / düzenleme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Form grubu
        form_grp = QGroupBox("Kayıt Düzenleyici")
        form_layout = QVBoxLayout(form_grp)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Başlık")
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(self.CATEGORIES)
        self.cat_combo.setEditable(True)
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Etiketler (virgülle)")
        self.def_edit = QTextEdit()
        self.def_edit.setPlaceholderText("Tanım")
        self.ai_input_edit = QLineEdit()
        self.ai_input_edit.setPlaceholderText("AI için giriş metni")
        form_layout.addWidget(QLabel("Başlık"))
        form_layout.addWidget(self.title_edit)
        form_layout.addWidget(QLabel("Kategori"))
        form_layout.addWidget(self.cat_combo)
        form_layout.addWidget(QLabel("Etiketler"))
        form_layout.addWidget(self.tags_edit)
        form_layout.addWidget(QLabel("Tanım"))
        form_layout.addWidget(self.def_edit)
        form_layout.addWidget(QLabel("AI Giriş"))
        form_layout.addWidget(self.ai_input_edit)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.new_btn = QPushButton("Yeni")
        self.save_btn = QPushButton("Kaydet")
        self.del_btn = QPushButton("Sil")
        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.del_btn)
        form_layout.addLayout(btn_layout)
        right_layout.addWidget(form_grp)

        # AI grubu
        ai_grp = QGroupBox("AI İşlemleri")
        ai_layout = QVBoxLayout(ai_grp)
        self.analyze_btn = QPushButton("Dil Bilgisi Analizi")
        self.auto_tag_btn = QPushButton("Otomatik Etiketle")
        self.semantic_btn = QPushButton("Semantik Arama")
        self.embed_btn = QPushButton("Embedding Hesapla (tümü)")
        ai_layout.addWidget(self.analyze_btn)
        ai_layout.addWidget(self.auto_tag_btn)
        ai_layout.addWidget(self.semantic_btn)
        ai_layout.addWidget(self.embed_btn)
        right_layout.addWidget(ai_grp)

        # Sync grubu
        sync_grp = QGroupBox("Firebase Sync")
        sync_layout = QHBoxLayout(sync_grp)
        self.sync_label = QLabel("Durum: " + ("Bağlı" if firebase_manager else "Bağlantı yok"))
        self.push_btn = QPushButton("☁️ Gönder")
        self.pull_btn = QPushButton("☁️ Çek")
        self.delete_fb_btn = QPushButton("🗑️ Firebase'den Sil")   # yeni buton
        sync_layout.addWidget(self.sync_label)
        sync_layout.addWidget(self.push_btn)
        sync_layout.addWidget(self.pull_btn)
        sync_layout.addWidget(self.delete_fb_btn)
        right_layout.addWidget(sync_grp)

        # Bölücülere ekle
        horz_splitter.addWidget(left_panel)
        horz_splitter.addWidget(self.table)
        horz_splitter.addWidget(right_panel)
        horz_splitter.setStretchFactor(0, 1)
        horz_splitter.setStretchFactor(1, 3)
        horz_splitter.setStretchFactor(2, 2)

        # Alt panel – JSON önizleme
        json_grp = QGroupBox("JSON Önizleme")
        json_layout = QVBoxLayout(json_grp)
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Consolas", 10))
        json_layout.addWidget(self.json_preview)
        vert_splitter.addWidget(json_grp)
        vert_splitter.setStretchFactor(0, 3)
        vert_splitter.setStretchFactor(1, 1)

        # Menü ve araç çubuğu
        self._create_menus()
        self._create_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Sinyaller
        self.new_btn.clicked.connect(self._clear_form)
        self.save_btn.clicked.connect(self._save_record)
        self.del_btn.clicked.connect(self._delete_record)
        self.analyze_btn.clicked.connect(self._analyze_linguistics)
        self.auto_tag_btn.clicked.connect(self._auto_tag_current)
        self.semantic_btn.clicked.connect(self._semantic_search)
        self.embed_btn.clicked.connect(self._generate_embeddings)
        self.push_btn.clicked.connect(self._sync_push)
        self.pull_btn.clicked.connect(self._sync_pull)
        self.delete_fb_btn.clicked.connect(self._delete_from_firebase)   # yeni bağlantı

        self._refresh_all()

        # ✅ Varsayılan koyu tema
        self._change_theme("dark")

    def _create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Dosya")
        file_menu.addAction("JSON İçe Aktar", self._import_json)
        file_menu.addAction("JSON Dışa Aktar", self._export_json)
        file_menu.addSeparator()
        file_menu.addAction("Çıkış", self.close)

        view_menu = menubar.addMenu("Görünüm")
        view_menu.addAction("Açık Tema", lambda: self._change_theme("light"))
        view_menu.addAction("Koyu Tema", lambda: self._change_theme("dark"))

        tools_menu = menubar.addMenu("Araçlar")
        tools_menu.addAction("İstatistikler", self._show_statistics)

    def _create_toolbar(self):
        toolbar = QToolBar("Ana Araç Çubuğu")
        self.addToolBar(toolbar)
        toolbar.addWidget(QLabel("Ara:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Metin ara...")
        toolbar.addWidget(self.search_box)
        self.search_box.textChanged.connect(self._apply_filters)

    def _populate_cat_tree(self):
        self.cat_tree.clear()
        all_item = QTreeWidgetItem(["Tümü"])
        all_item.setData(0, Qt.UserRole, None)
        self.cat_tree.addTopLevelItem(all_item)
        for cat in self.CATEGORIES:
            item = QTreeWidgetItem([cat])
            item.setData(0, Qt.UserRole, cat)
            self.cat_tree.addTopLevelItem(item)

    def _apply_filters(self):
        query = self.search_box.text()
        lang = self.lang_combo.currentText()
        cat_item = self.cat_tree.currentItem()
        cat = cat_item.data(0, Qt.UserRole) if cat_item else None
        all_rec = self.json_manager.get_all()
        results = SearchEngine.search(all_rec, query=query, language=lang, category=cat)
        self._populate_table(results)
        self.status_bar.showMessage(f"{len(results)} kayıt listeleniyor.")

    def _populate_table(self, records):
        self.table.setRowCount(0)
        for i, rec in enumerate(records):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(rec.get("id", "")))
            self.table.setItem(i, 1, QTableWidgetItem(rec.get("title", "")))
            self.table.setItem(i, 2, QTableWidgetItem(rec.get("language", "")))
            self.table.setItem(i, 3, QTableWidgetItem(rec.get("category", "")))
            self.table.setItem(i, 4, QTableWidgetItem(rec.get("metadata", {}).get("created_at", "")))
        self.current_records = records

    def _on_cat_selected(self):
        self._apply_filters()

    def _on_record_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            if idx < len(self.current_records):
                self.selected_record = self.current_records[idx]
                self._display_record(self.selected_record)

    def _display_record(self, rec):
        self.title_edit.setText(rec.get("title", ""))
        self.cat_combo.setCurrentText(rec.get("category", ""))
        self.tags_edit.setText(", ".join(rec.get("metadata", {}).get("tags", [])))
        self.def_edit.setPlainText(rec.get("content", {}).get("definition", ""))
        self.ai_input_edit.setText(rec.get("ai_training_data", {}).get("input_text", ""))
        self.json_preview.setPlainText(json.dumps(rec, ensure_ascii=False, indent=2))

    def _clear_form(self):
        self.title_edit.clear()
        self.cat_combo.setCurrentIndex(0)
        self.tags_edit.clear()
        self.def_edit.clear()
        self.ai_input_edit.clear()
        self.json_preview.clear()
        self.selected_record = None

    def _save_record(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Uyarı", "Başlık zorunludur.")
            return
        record = {
            "id": self.selected_record["id"] if self.selected_record else "",
            "language": self.lang_combo.currentText(),
            "category": self.cat_combo.currentText(),
            "title": title,
            "content": {
                "definition": self.def_edit.toPlainText(),
                "examples": [],
                "etymology": "",
                "phonetics": "",
                "morphology": "",
                "syntax": "",
                "notes": "",
                "sources": []
            },
            "linguistic_features": {},
            "ai_metadata": {
                "embedding": [],
                "auto_tags": [],
                "difficulty": "A1",
                "similar_items": []
            },
            "metadata": {
                "difficulty": "A1",
                "tags": [t.strip() for t in self.tags_edit.text().split(",") if t.strip()],
                "created_at": self.selected_record["metadata"]["created_at"] if self.selected_record else datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "updated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            "sync": {
                "firebase_id": self.selected_record.get("sync", {}).get("firebase_id", "") if self.selected_record else "",
                "status": "local",
                "last_sync": ""
            }
        }
        if self.selected_record:
            self.json_manager.update(self.selected_record["id"], record)
        else:
            self.json_manager.add(record)
        self._refresh_all()

    def _delete_record(self):
        if not self.selected_record:
            return
        if QMessageBox.question(self, "Onay", "Kaydı sil?") == QMessageBox.Yes:
            self.json_manager.delete(self.selected_record["id"])
            self._refresh_all()

    # ---------- Firebase'den silme ----------
    def _delete_from_firebase(self):
        if not self.firebase_manager:
            QMessageBox.warning(self, "Uyarı", "Firebase bağlantısı yok.")
            return

        # Seçili satırları al
        selected_rows = set()
        for model_index in self.table.selectionModel().selectedRows():
            selected_rows.add(model_index.row())
        if not selected_rows:
            QMessageBox.information(self, "Bilgi", "Lütfen silinecek kayıtları seçin.")
            return

        # İşlem yapılacak kayıtları belirle
        records_to_delete = []
        for row in selected_rows:
            if row < len(self.current_records):
                rec = self.current_records[row]
                fb_id = rec.get("sync", {}).get("firebase_id", "").strip()
                if fb_id:
                    records_to_delete.append((rec, fb_id))
                else:
                    QMessageBox.warning(self, "Hata", f"'{rec.get('title', 'İsimsiz')}' kaydının Firebase ID'si yok. Yalnızca senkronize kayıtlar silinebilir.")
                    return

        if not records_to_delete:
            return

        # Onay al
        titles = [r[0].get("title", "") for r in records_to_delete]
        msg = f"Aşağıdaki {len(titles)} kayıt Firebase'den silinecek:\n" + "\n".join(titles)
        reply = QMessageBox.question(self, "Firebase'den Sil", msg,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # Ayrıca yerel kopyayı da silmek ister misin?
        also_local = QMessageBox.question(self, "Yerel Kayıt",
                                          "Kayıtlar yerel JSON'dan da silinsin mi?",
                                          QMessageBox.Yes | QMessageBox.No)

        # Firebase silme işlemi (hata yönetimiyle)
        try:
            for rec, fb_id in records_to_delete:
                # Varsayılan koleksiyon "turkish_words"
                self.firebase_manager.delete_document("turkish_words", fb_id)
            QMessageBox.information(self, "Başarılı", f"{len(records_to_delete)} kayıt Firebase'den silindi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Firebase silme hatası:\n{e}")
            return

        # Yerel temizlik
        if also_local == QMessageBox.Yes:
            ids = [r[0].get("id") for r in records_to_delete]
            self.json_manager.delete_multiple(ids)

        self._refresh_all()
        self._clear_form()
    # ---------------------------------------

    def _refresh_all(self):
        self._populate_cat_tree()
        self._apply_filters()

    def _analyze_linguistics(self):
        if not self.selected_record:
            return
        text = self.def_edit.toPlainText() + " " + self.ai_input_edit.text()
        if not text.strip():
            return
        res = self.ai_client.analyze_grammar(text)
        if res:
            QMessageBox.information(self, "Analiz", json.dumps(res, indent=2))
            self.selected_record["linguistic_features"] = res
        else:
            QMessageBox.critical(self, "Hata", "AI bağlantısı başarısız.")

    def _auto_tag_current(self):
        if not self.selected_record:
            return
        text = self.def_edit.toPlainText()
        tags = self.ai_client.auto_tag(text)
        if tags is not None:
            self.tags_edit.setText(", ".join(tags))

    def _semantic_search(self):
        query, ok = QInputDialog.getText(self, "Semantik Arama", "Aranacak metin:")
        if ok and query:
            results = self.ai_client.similarity_search(query, self.json_manager.get_all())
            if results:
                self._populate_table(results)
            else:
                QMessageBox.critical(self, "Hata", "AI bağlantısı başarısız.")

    def _generate_embeddings(self):
        records = self.json_manager.get_all()
        for rec in records:
            text = rec.get("title", "") + " " + rec.get("content", {}).get("definition", "")
            emb = self.ai_client.get_embedding(text)
            if emb:
                rec.setdefault("ai_metadata", {})["embedding"] = emb
        self.json_manager.set_all(records)
        QMessageBox.information(self, "Başarılı", "Tüm kayıtlar için embedding oluşturuldu.")

    def _sync_push(self):
        if self.sync_engine:
            cnt = self.sync_engine.push_to_firebase()
            QMessageBox.information(self, "Başarılı", f"{cnt} kayıt Firebase'e gönderildi.")
        else:
            QMessageBox.warning(self, "Uyarı", "Firebase bağlantısı yok.")

    def _sync_pull(self):
        if self.sync_engine:
            cnt = self.sync_engine.pull_from_firebase()
            QMessageBox.information(self, "Başarılı", f"{cnt} kayıt Firebase'den alındı.")
            self._refresh_all()
        else:
            QMessageBox.warning(self, "Uyarı", "Firebase bağlantısı yok.")

    def _import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "JSON İçe Aktar", "", "JSON (*.json)")
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for rec in data:
                    self.json_manager.add(rec)
                self._refresh_all()
                QMessageBox.information(self, "Başarılı", f"{len(data)} kayıt eklendi.")

    def _export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "JSON Dışa Aktar", "export.json", "JSON (*.json)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.json_manager.get_all(), f, ensure_ascii=False, indent=2)

    def _change_theme(self, theme_name):
        if theme_name == "dark":
            from themes.dark_theme import get_stylesheet
            QApplication.instance().setStyleSheet(get_stylesheet())
        else:
            from themes.light_theme import get_stylesheet
            QApplication.instance().setStyleSheet(get_stylesheet())

    def _show_statistics(self):
        stats = Statistics.calculate(self.json_manager.get_all())
        dlg = StatisticsDialog(stats, self)
        dlg.exec_()