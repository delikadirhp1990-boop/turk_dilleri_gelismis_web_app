import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FirebaseManager:
    def __init__(self, service_account_path: str = None):
        # Eğer daha önce initialize_app çağrılmadıysa, yap.
        if not firebase_admin._apps:
            if service_account_path:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                raise ValueError("Firebase başlatılamadı: servis hesabı anahtarı gerekli.")
        self.db = firestore.client()
        # Koleksiyonlar
        self.collections = {
            "turkish_words": self.db.collection("turkish_words"),
            "grammar_rules": self.db.collection("grammar_rules"),
            "sentences": self.db.collection("sentences"),
            "etymology": self.db.collection("etymology"),
            "notes": self.db.collection("notes")
        }

    def add_document(self, collection_name: str, data: Dict[str, Any], doc_id: str = None) -> str:
        col = self.collections[collection_name]
        if doc_id:
            col.document(doc_id).set(data)
            return doc_id
        else:
            _, doc_ref = col.add(data)
            return doc_ref.id

    def get_all_documents(self, collection_name: str) -> List[Dict[str, Any]]:
        col = self.collections[collection_name]
        return [doc.to_dict() for doc in col.stream()]

    def update_document(self, collection_name: str, doc_id: str, data: Dict[str, Any]):
        col = self.collections[collection_name]
        col.document(doc_id).set(data, merge=True)

    def delete_document(self, collection_name: str, doc_id: str):
        col = self.collections[collection_name]
        col.document(doc_id).delete()

    def batch_upload(self, collection_name: str, records: List[Dict[str, Any]], id_field: str = "id"):
        col = self.collections[collection_name]
        batch = self.db.batch()
        for rec in records:
            doc_id = rec.get(id_field) or col.document().id
            batch.set(col.document(doc_id), rec)
        batch.commit()

    def fetch_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        return {name: self.get_all_documents(name) for name in self.collections}