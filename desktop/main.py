import sys
import os
import json
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from core.json_manager import JsonManager
from core.firebase_manager import FirebaseManager
from core.ai_client import AIClient

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('app.log', encoding='utf-8'), logging.StreamHandler(sys.stdout)]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    app.setApplicationName("Türk Dilleri Dil Verisi Yönetim Sistemi")

    # Local JSON yöneticisi
    json_manager = JsonManager("data/turkic_data.json")

    # Firebase bağlantısı
    firebase_manager = None
    fb_config_path = "C:\\Users\\pc\\Desktop\\turk_dilleri_yapay_zeka_destekli_dil_veri_sistemi\\dil_veri_sistemi\\codes\\desktop\\firebase_config.json"
    if os.path.exists(fb_config_path):
        with open(fb_config_path, 'r', encoding='utf-8') as f:
            fb_config = json.load(f)
        service_path = fb_config.get("serviceAccountKeyPath", "")
        if service_path and os.path.exists(service_path):
            try:
                # GÜNCELLENEN KISIM: Doğrudan credentials.Certificate ile bağlan
                import firebase_admin
                from firebase_admin import credentials

                cred = credentials.Certificate(service_path)
                firebase_admin.initialize_app(cred)
                # FirebaseManager artık mevcut uygulamayı kullanacak
                from core.firebase_manager import FirebaseManager
                firebase_manager = FirebaseManager(service_path)  # service_path parametresiz de çalışacak ama yine de verelim
                logger.info("Firebase bağlantısı kuruldu.")
            except Exception as e:
                logger.error(f"Firebase hatası: {e}")
                QMessageBox.warning(None, "Firebase Hatası", f"Firebase'e bağlanılamadı:\n{e}")
        else:
            logger.warning("Firebase anahtar dosyası bulunamadı.")
    else:
        logger.warning("firebase_config.json bulunamadı. Firebase devre dışı.")

    # AI istemcisi
    ai_backend_url = os.getenv("AI_BACKEND_URL", "http://localhost:8000")
    ai_client = AIClient(ai_backend_url)

    window = MainWindow(json_manager, firebase_manager, ai_client)
    window._change_theme("dark")   # <-- bu satırı ekle
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()