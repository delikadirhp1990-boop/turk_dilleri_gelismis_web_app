import logging
from datetime import datetime, timezone
from core.json_manager import JsonManager
from core.firebase_manager import FirebaseManager

logger = logging.getLogger(__name__)

class SyncEngine:
    def __init__(self, json_manager: JsonManager, firebase_manager: FirebaseManager):
        self.json_manager = json_manager
        self.fb = firebase_manager

    def push_to_firebase(self, collection: str = "turkish_words") -> int:
        """
        Yereldeki tüm kayıtları Firebase Firestore'a gönderir.
        Kayıtların 'sync.firebase_id' alanını kendi yerel ID'si ile doldurur,
        böylece silme ve sonraki senkronizasyon çalışır.
        """
        local_records = self.json_manager.get_all()
        if not local_records:
            return 0

        for rec in local_records:
            rec.setdefault("sync", {})
            if not rec["sync"].get("firebase_id"):
                rec["sync"]["firebase_id"] = rec.get("id", "")
            rec["sync"]["status"] = "synced"
            rec["sync"]["last_sync"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Firestore'a batch yaz (local id'yi belge id'si olarak kullan)
        self.fb.batch_upload(collection, local_records, id_field="id")

        self.json_manager.set_all(local_records)
        logger.info(f"{len(local_records)} kayıt Firebase'e gönderildi.")
        return len(local_records)

    def pull_from_firebase(self, collection: str = "turkish_words") -> int:
        """
        Firebase Firestore'daki tüm kayıtları yerel JSON'a çeker.
        Belge id'lerini 'sync.firebase_id' alanına yazar.
        """
        # Firestore'dan tüm belgeleri çek (doc.id ile birlikte)
        docs = self.fb.db.collection(collection).stream()
        enriched_records = []
        for doc in docs:
            rec = doc.to_dict()
            rec.setdefault("sync", {})["firebase_id"] = doc.id
            enriched_records.append(rec)

        self.json_manager.set_all(enriched_records)
        logger.info(f"Firebase'den {len(enriched_records)} kayıt çekildi.")
        return len(enriched_records)