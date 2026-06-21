import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore
from sentence_transformers import SentenceTransformer
import numpy as np

# Ortam değişkenlerini yükle
load_dotenv()

# Log yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask uygulaması
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'flask-super-secret-key-2024')

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Admin kullanıcı adı ve şifresi (çevre değişkenlerinden)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'GucluSifre123!')

# Firebase Admin SDK başlatma
cred = credentials.Certificate(os.getenv('FIREBASE_KEY_PATH', 'firebase_key.json'))
firebase_admin.initialize_app(cred)
db = firestore.client()
COLLECTION = 'turkish_words'

# Sentence Transformers modeli (soru cevaplama için)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ------------------------------------------------------------------
# Flask-Login kullanıcı sınıfı
class AdminUser:
    def __init__(self):
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return 'admin'

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return AdminUser()
    return None

# ------------------------------------------------------------------
# Yardımcı fonksiyonlar
def get_all_records() -> List[Dict[str, Any]]:
    """Firestore'daki tüm kayıtları döndürür."""
    docs = db.collection(COLLECTION).stream()
    records = []
    for doc in docs:
        rec = doc.to_dict()
        rec['firestore_id'] = doc.id
        records.append(rec)
    return records

def find_best_answer(question: str) -> Optional[Dict[str, Any]]:
    """Sorulan soruya en uygun kaydı embedding benzerliği ile bulur."""
    records = get_all_records()
    if not records:
        return None

    question_emb = model.encode(question)
    best_score = -1.0
    best_record = None

    for rec in records:
        emb = rec.get('ai_metadata', {}).get('embedding', [])
        if not emb:
            text = rec.get('title', '') + ' ' + rec.get('content', {}).get('definition', '')
            emb = model.encode(text)
        emb = np.array(emb)
        score = np.dot(question_emb, emb) / (np.linalg.norm(question_emb) * np.linalg.norm(emb) + 1e-9)
        if score > best_score:
            best_score = score
            best_record = rec

    return best_record

# ------------------------------------------------------------------
# Kullanıcı arayüzü (herkese açık)
@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    question = ''
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            best = find_best_answer(question)
            if best:
                answer = {
                    'title': best.get('title', 'Başlıksız'),
                    'definition': best.get('content', {}).get('definition', 'Tanım bulunamadı.'),
                    'category': best.get('category', ''),
                    'language': best.get('language', ''),
                }
            else:
                answer = {'title': 'Üzgünüm', 'definition': 'Bu soruya uygun bir kayıt bulunamadı.'}
    return render_template('index.html', answer=answer, question=question)

# ------------------------------------------------------------------
# Admin girişi
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = AdminUser()
            login_user(user)
            flash('Başarıyla giriş yapıldı.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# ------------------------------------------------------------------
# Admin Paneli (Kayıt listesi, hata giderme, silme)
@app.route('/admin')
@login_required
def admin_dashboard():
    records = get_all_records()
    faulty = []
    for rec in records:
        errors = []
        if not rec.get('title', '').strip():
            errors.append('Başlık boş')
        if not rec.get('content', {}).get('definition', '').strip():
            errors.append('Tanım boş')
        if not rec.get('ai_metadata', {}).get('embedding'):
            errors.append('Embedding eksik')
        if errors:
            rec['_errors'] = errors
            faulty.append(rec)
    return render_template('admin_dashboard.html', records=records, faulty=faulty, total=len(records))

@app.route('/admin/delete/<firestore_id>', methods=['POST'])
@login_required
def admin_delete(firestore_id):
    try:
        db.collection(COLLECTION).document(firestore_id).delete()
        flash('Kayıt silindi.', 'success')
    except Exception as e:
        flash(f'Silme hatası: {str(e)}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit/<firestore_id>', methods=['GET', 'POST'])
@login_required
def admin_edit(firestore_id):
    doc = db.collection(COLLECTION).document(firestore_id).get()
    if not doc.exists:
        flash('Kayıt bulunamadı.', 'error')
        return redirect(url_for('admin_dashboard'))

    record = doc.to_dict()
    if request.method == 'POST':
        title = request.form.get('title', '')
        definition = request.form.get('definition', '')
        category = request.form.get('category', '')
        language = request.form.get('language', '')
        record['title'] = title
        record['category'] = category
        record['language'] = language
        record['content'] = record.get('content', {})
        record['content']['definition'] = definition
        record['ai_metadata']['embedding'] = []
        db.collection(COLLECTION).document(firestore_id).set(record)
        flash('Kayıt güncellendi.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_edit.html', record=record, firestore_id=firestore_id)

@app.route('/admin/regenerate_embedding/<firestore_id>', methods=['POST'])
@login_required
def regenerate_embedding(firestore_id):
    doc = db.collection(COLLECTION).document(firestore_id).get()
    if not doc.exists:
        flash('Kayıt bulunamadı.', 'error')
        return redirect(url_for('admin_dashboard'))

    record = doc.to_dict()
    text = record.get('title', '') + ' ' + record.get('content', {}).get('definition', '')
    emb = model.encode(text).tolist()
    record.setdefault('ai_metadata', {})['embedding'] = emb
    db.collection(COLLECTION).document(firestore_id).set(record)
    flash('Embedding yeniden oluşturuldu.', 'success')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)