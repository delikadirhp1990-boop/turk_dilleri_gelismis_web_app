import os
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from io import BytesIO

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_file, session
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np

# İsteğe bağlı AI
try:
    from sentence_transformers import SentenceTransformer
    HAS_AI = True
except ImportError:
    HAS_AI = False

load_dotenv()

# Log yapılandırması
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler('app.log', encoding='utf-8')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'süper-gizli-anahtar')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

cred = credentials.Certificate(os.getenv('FIREBASE_KEY_PATH', 'firebase_key.json'))
firebase_admin.initialize_app(cred)
db = firestore.client()
COLLECTION = 'turkish_words'

if HAS_AI:
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
else:
    model = None

# ------------------------------------------------------------------
# Yardımcı fonksiyonlar
def sanitize_input(text: str) -> str:
    return re.sub(r'<[^>]*>', '', text)

def get_all_records() -> List[Dict[str, Any]]:
    docs = db.collection(COLLECTION).stream()
    records = []
    for doc in docs:
        rec = doc.to_dict()
        rec['firestore_id'] = doc.id
        records.append(rec)
    return records

def find_best_answer(question: str) -> Optional[Dict[str, Any]]:
    if not HAS_AI:
        return None
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

def get_logs(tail=100):
    try:
        with open('app.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return ''.join(lines[-tail:])
    except FileNotFoundError:
        return "Log dosyası bulunamadı."

def log_to_firestore(action: str, details: str, record_id: str = None):
    try:
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'details': details,
            'record_id': record_id,
        }
        db.collection('system_logs').add(log_entry)
    except Exception as e:
        logger.error(f"Firestore loglama hatası: {e}")

def analyze_grammar(text: str) -> dict:
    """Basit dil bilgisi analizi (AI modeli yoksa kural tabanlı)."""
    text_lower = text.lower()
    features = {
        'vowel_drop': False,
        'consonant_softening': False,
        'vowel_harmony': False,
        'suffixes': [],
        'root': ''
    }
    # Temel kontroller
    if 'burun' in text_lower and 'u' in text_lower:
        features['vowel_drop'] = True
        features['root'] = 'burun'
        features['suffixes'] = ['u']
    if 'kitap' in text_lower and 'b' in text_lower:
        features['consonant_softening'] = True
        features['root'] = 'kitap'
        features['suffixes'] = ['ı']
    if 'araba' in text_lower:
        features['vowel_harmony'] = True
    return features

# ------------------------------------------------------------------
# Kullanıcı sınıfı
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
# ANA SAYFA (herkese açık)
@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    question = ''
    if request.method == 'POST':
        question = sanitize_input(request.form.get('question', '').strip())
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
# ADMIN GİRİŞ
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = AdminUser()
            login_user(user, remember=True)
            session.permanent = True
            logger.info(f"Admin girişi: {username}")
            flash('Giriş başarılı.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            logger.warning(f"Başarısız giriş denemesi: {username}")
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# ------------------------------------------------------------------
# YÖNETİM PANELİ
@app.route('/admin')
@login_required
def admin_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    query = request.args.get('query', '').strip()
    language = request.args.get('language', '').strip()
    category = request.args.get('category', '').strip()

    records = get_all_records()

    if query:
        q = query.lower()
        records = [r for r in records if
                   q in r.get('title', '').lower() or
                   q in r.get('content', {}).get('definition', '').lower()]
    if language:
        records = [r for r in records if r.get('language') == language]
    if category:
        records = [r for r in records if r.get('category') == category]

    total = len(records)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = records[start:end]

    faulty = []
    for r in paginated_records:
        errors = []
        if not r.get('title', '').strip():
            errors.append('Başlık boş')
        if not r.get('content', {}).get('definition', '').strip():
            errors.append('Tanım boş')
        if not r.get('ai_metadata', {}).get('embedding'):
            errors.append('Embedding eksik')
        if errors:
            r['_errors'] = errors
            faulty.append(r)

    all_records = get_all_records()
    categories = sorted({r.get('category', '') for r in all_records if r.get('category')})
    languages = sorted({r.get('language', '') for r in all_records if r.get('language')})

    return render_template('admin_dashboard.html',
                           records=paginated_records,
                           faulty=faulty,
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           categories=categories,
                           languages=languages,
                           query=query,
                           selected_language=language,
                           selected_category=category)

# ------------------------------------------------------------------
# YENİ KAYIT EKLEME
@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def admin_add():
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', '').strip())
        if not title:
            flash('Başlık zorunludur.', 'error')
            return redirect(url_for('admin_add'))

        record = {
            'id': '',
            'language': request.form.get('language', 'TR'),
            'category': sanitize_input(request.form.get('category', '')),
            'title': title,
            'content': {
                'definition': sanitize_input(request.form.get('definition', '')),
                'examples': [],
                'etymology': sanitize_input(request.form.get('etymology', '')),
                'phonetics': '',
                'morphology': '',
                'syntax': '',
                'notes': '',
                'sources': []
            },
            'linguistic_features': {},
            'ai_metadata': {
                'embedding': [],
                'auto_tags': [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
                'difficulty': request.form.get('difficulty', 'A1'),
                'similar_items': []
            },
            'metadata': {
                'difficulty': request.form.get('difficulty', 'A1'),
                'tags': [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            },
            'sync': {
                'firebase_id': '',
                'last_sync': '',
                'status': 'local'
            }
        }
        db.collection(COLLECTION).add(record)
        log_to_firestore('CREATE', f"Yeni kayıt eklendi: {title}")
        logger.info(f"Yeni kayıt eklendi: {title}")
        flash('Kayıt eklendi.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_add.html')

# ------------------------------------------------------------------
# KAYIT DÜZENLEME
@app.route('/admin/edit/<firestore_id>', methods=['GET', 'POST'])
@login_required
def admin_edit(firestore_id):
    doc = db.collection(COLLECTION).document(firestore_id).get()
    if not doc.exists:
        flash('Kayıt bulunamadı.', 'error')
        return redirect(url_for('admin_dashboard'))

    record = doc.to_dict()
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', '').strip())
        if not title:
            flash('Başlık zorunludur.', 'error')
            return redirect(url_for('admin_edit', firestore_id=firestore_id))

        record['title'] = title
        record['language'] = request.form.get('language', record.get('language', 'TR'))
        record['category'] = sanitize_input(request.form.get('category', ''))
        record['content']['definition'] = sanitize_input(request.form.get('definition', ''))
        record['content']['etymology'] = sanitize_input(request.form.get('etymology', ''))
        record['ai_metadata']['auto_tags'] = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
        record['metadata']['tags'] = record['ai_metadata']['auto_tags']
        record['metadata']['updated_at'] = datetime.now(timezone.utc).isoformat()
        record['ai_metadata']['embedding'] = []

        db.collection(COLLECTION).document(firestore_id).set(record)
        log_to_firestore('UPDATE', f"Kayıt güncellendi: {title}", firestore_id)
        logger.info(f"Kayıt güncellendi: {title}")
        flash('Kayıt güncellendi.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_edit.html', record=record, firestore_id=firestore_id)

# ------------------------------------------------------------------
# KAYIT SİLME
@app.route('/admin/delete/<firestore_id>', methods=['POST'])
@login_required
def admin_delete(firestore_id):
    try:
        db.collection(COLLECTION).document(firestore_id).delete()
        log_to_firestore('DELETE', f"Kayıt silindi: {firestore_id}", firestore_id)
        logger.warning(f"Kayıt silindi: {firestore_id}")
        flash('Kayıt silindi.', 'success')
    except Exception as e:
        logger.error(f"Silme hatası: {e}")
        flash(f'Silme hatası: {e}', 'error')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# TOPLU SİLME
@app.route('/admin/delete_multiple', methods=['POST'])
@login_required
def admin_delete_multiple():
    ids = request.form.getlist('record_ids')
    if not ids:
        flash('Hiç kayıt seçilmedi.', 'error')
        return redirect(url_for('admin_dashboard'))
    for doc_id in ids:
        db.collection(COLLECTION).document(doc_id).delete()
    log_to_firestore('DELETE_MULTIPLE', f"Toplu silme: {len(ids)} kayıt", ','.join(ids))
    logger.warning(f"Toplu silme: {len(ids)} kayıt")
    flash(f'{len(ids)} kayıt silindi.', 'success')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# EMBEDDING YENİDEN OLUŞTURMA (tek)
@app.route('/admin/regenerate_embedding/<firestore_id>', methods=['POST'])
@login_required
def regenerate_embedding(firestore_id):
    if not HAS_AI:
        flash('AI modeli yüklü değil.', 'error')
        return redirect(url_for('admin_dashboard'))
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
# TOPLU EMBEDDING OLUŞTURMA (yeni)
@app.route('/admin/regenerate_all_embeddings', methods=['POST'])
@login_required
def regenerate_all_embeddings():
    if not HAS_AI:
        flash('AI modeli yüklü değil.', 'error')
        return redirect(url_for('admin_dashboard'))
    records = get_all_records()
    count = 0
    for rec in records:
        emb = rec.get('ai_metadata', {}).get('embedding')
        if not emb:
            text = rec.get('title', '') + ' ' + rec.get('content', {}).get('definition', '')
            rec['ai_metadata']['embedding'] = model.encode(text).tolist()
            db.collection(COLLECTION).document(rec['firestore_id']).set(rec)
            count += 1
    flash(f'{count} kaydın embedding\'i oluşturuldu.', 'success')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# AI DİL BİLGİSİ ANALİZİ (tek kayıt)
@app.route('/admin/analyze/<firestore_id>', methods=['POST'])
@login_required
def analyze_record(firestore_id):
    doc = db.collection(COLLECTION).document(firestore_id).get()
    if not doc.exists:
        flash('Kayıt bulunamadı.', 'error')
        return redirect(url_for('admin_dashboard'))
    record = doc.to_dict()
    text = record.get('title', '') + ' ' + record.get('content', {}).get('definition', '')
    features = analyze_grammar(text)
    record['linguistic_features'] = features
    db.collection(COLLECTION).document(firestore_id).set(record)
    log_to_firestore('AI_ANALYZE', f"AI analizi yapıldı: {record.get('title')}", firestore_id)
    flash('Dil bilgisi analizi tamamlandı.', 'success')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# FIREBASE SENKRONİZASYON (Push/Pull)
@app.route('/admin/sync/push', methods=['POST'])
@login_required
def sync_push():
    records = get_all_records()
    for rec in records:
        rec.setdefault('sync', {})
        rec['sync']['status'] = 'synced'
        rec['sync']['last_sync'] = datetime.now(timezone.utc).isoformat()
        db.collection(COLLECTION).document(rec['firestore_id']).set(rec, merge=True)
    log_to_firestore('SYNC', f"Push yapıldı: {len(records)} kayıt")
    flash(f'{len(records)} kaydın sync durumu güncellendi.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/sync/pull', methods=['POST'])
@login_required
def sync_pull():
    flash('Veriler zaten canlı olarak Firestore\'dan gelmektedir.', 'info')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# FIREBASE'DEN SEÇİLİ KAYDI SİL (sync silme)
@app.route('/admin/firebase_delete/<firestore_id>', methods=['POST'])
@login_required
def firebase_delete(firestore_id):
    try:
        db.collection(COLLECTION).document(firestore_id).delete()
        log_to_firestore('DELETE', f"Firebase'den silindi: {firestore_id}", firestore_id)
        flash('Kayıt Firebase\'den silindi.', 'success')
    except Exception as e:
        flash(f'Silme hatası: {e}', 'error')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# İSTATİSTİKLER
@app.route('/admin/stats')
@login_required
def admin_stats():
    records = get_all_records()
    total = len(records)

    cat_counts = {}
    for r in records:
        cat = r.get('category', 'Bilinmeyen')
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    lang_counts = {}
    for r in records:
        lang = r.get('language', 'Bilinmeyen')
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    daily_counts = {}
    for r in records:
        created = r.get('metadata', {}).get('created_at', '')
        if created:
            day = created[:10]
            daily_counts[day] = daily_counts.get(day, 0) + 1

    stats = {
        'total': total,
        'category_labels': json.dumps(list(cat_counts.keys())),
        'category_values': json.dumps(list(cat_counts.values())),
        'language_labels': json.dumps(list(lang_counts.keys())),
        'language_values': json.dumps(list(lang_counts.values())),
        'daily_labels': json.dumps(list(sorted(daily_counts.keys()))),
        'daily_values': json.dumps(list(sorted(daily_counts.values())))
    }
    return render_template('admin_statistics.html', stats=stats)

# ------------------------------------------------------------------
# LOG GÖRÜNTÜLEME
@app.route('/admin/logs')
@login_required
def admin_logs():
    log_content = get_logs(tail=200)
    return render_template('admin_logs.html', log_content=log_content)

@app.route('/admin/firebase_logs')
@login_required
def admin_firebase_logs():
    logs_ref = db.collection('system_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(500)
    logs = [doc.to_dict() for doc in logs_ref.stream()]
    return render_template('admin_firebase_logs.html', logs=logs)

@app.route('/admin/clear_logs', methods=['POST'])
@login_required
def admin_clear_logs():
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    logs_ref = db.collection('system_logs').where('timestamp', '<', cutoff.isoformat())
    deleted = 0
    for doc in logs_ref.stream():
        doc.reference.delete()
        deleted += 1
    flash(f'{deleted} eski log temizlendi.', 'success')
    return redirect(url_for('admin_firebase_logs'))

# ------------------------------------------------------------------
# JSON İŞLEMLERİ
@app.route('/admin/export_json')
@login_required
def export_json():
    records = get_all_records()
    export_data = {
        'export_info': {
            'date': datetime.now(timezone.utc).isoformat(),
            'total_records': len(records)
        },
        'data': records
    }
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    return send_file(
        BytesIO(json_str.encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name='turkce_verileri_export.json'
    )

@app.route('/admin/import_json', methods=['POST'])
@login_required
def import_json():
    if 'json_file' not in request.files:
        flash('Dosya seçilmedi.', 'error')
        return redirect(url_for('admin_dashboard'))
    file = request.files['json_file']
    if file.filename == '':
        flash('Dosya adı boş.', 'error')
        return redirect(url_for('admin_dashboard'))
    try:
        content = file.read().decode('utf-8')
        data = json.loads(content)
        records = data.get('data', []) if isinstance(data, dict) else data
        if not isinstance(records, list):
            flash('JSON formatı geçersiz.', 'error')
            return redirect(url_for('admin_dashboard'))
        for rec in records:
            db.collection(COLLECTION).add(rec)
        log_to_firestore('CREATE_MULTIPLE', f"JSON içe aktarıldı: {len(records)} kayıt")
        flash(f'{len(records)} kayıt içe aktarıldı.', 'success')
    except Exception as e:
        logger.error(f"İçe aktarma hatası: {e}")
        flash(f'İçe aktarma hatası: {e}', 'error')
    return redirect(url_for('admin_dashboard'))

# ------------------------------------------------------------------
# ŞİFRE DEĞİŞTİRME
@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    global ADMIN_PASSWORD
    if request.method == 'POST':
        old_pass = request.form.get('old_password', '')
        new_pass = request.form.get('new_password', '')
        if old_pass != ADMIN_PASSWORD:
            flash('Mevcut şifre yanlış!', 'error')
        elif len(new_pass) < 6:
            flash('Yeni şifre en az 6 karakter olmalı.', 'error')
        else:
            ADMIN_PASSWORD = new_pass
            with open('.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open('.env', 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith('ADMIN_PASSWORD='):
                        f.write(f'ADMIN_PASSWORD={new_pass}\n')
                    else:
                        f.write(line)
            flash('Şifre başarıyla değiştirildi.', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_change_password.html')

# ------------------------------------------------------------------
# KULLANIM KILAVUZU
@app.route('/admin/guide')
@login_required
def admin_guide():
    return render_template('admin_guide.html')

# ------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)