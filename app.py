from flask import Flask, request, jsonify, render_template
import os
import re
import json
from nltk.corpus import stopwords
# تأكد من وجود ملف search_engine.py بنفس المجلد
from search_engine import AdvancedMatchingEngine

app = Flask(__name__)

# --- إعداد المسارات ---
INDEX_FILE_PATH = "inverted_index.json"
ARTICLES_FOLDER_PATH = "articles"
ARTICLES_DATA_PATH = "articles_data.json"

# --- تحميل البيانات بشكل صحيح (الإصلاح الأول) ---
# نحول القائمة إلى قاموس يعتمد على ترتيب الملفات (1, 2, 3...) لضمان توافق الـ ID
ARTICLES_MAP = {}
try:
    with open(ARTICLES_DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        # إذا كانت البيانات قائمة، نقوم بتحويلها لقاموس مفتاحه هو رقم المستند (كـ نص)
        if isinstance(raw_data, list):
            for i, item in enumerate(raw_data):
                # نستخدم i+1 لأن setup_articles.py أنشأ الملفات بأسماء doc1, doc2...
                ARTICLES_MAP[str(i + 1)] = item
        else:
            # في حال كان الملف أصلاً قاموس
            ARTICLES_MAP = raw_data
            
    print(f"--- Data Loaded: {len(ARTICLES_MAP)} articles ---")
except Exception as e:
    print(f"Error loading articles data: {e}")
    ARTICLES_MAP = {}

# --- تهيئة محرك البحث ---
engine = None
try:
    engine = AdvancedMatchingEngine(INDEX_FILE_PATH, ARTICLES_FOLDER_PATH)
    print("--- Engine Ready ---")
except Exception as e:
    print(f"Error initializing engine: {e}")

# تحميل كلمات التوقف للهايلايت
stop_words = set(stopwords.words('english'))

def generate_smart_snippet_with_highlight(text, query):
    if not text: return ""
    raw_words = query.lower().split()
    keywords = [re.sub(r'[^a-z0-9]', '', w) for w in raw_words if w not in stop_words and len(w) > 2]
    
    lower_text = text.lower()
    best_pos = 0
    max_found = 0
    
    # البحث عن أفضل موقع يظهر فيه أكبر عدد من الكلمات المفتاحية
    # (تم تبسيط المنطق هنا للسرعة)
    for kw in keywords:
        pos = lower_text.find(kw)
        if pos != -1:
            best_pos = pos
            break 
            
    start = max(0, best_pos - 50)
    end = min(len(text), start + 300)
    snippet = text[start:end] + "..."
    
    # إضافة التظليل (Highlight)
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        snippet = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", snippet)
        
    return snippet

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 5

    if not query or not engine:
        return jsonify({'results': [], 'total': 0, 'page': 1})

    # 1. الحصول على النتائج الخام
    all_results = engine.search(query)
    
    # 2. حساب السكور النسبي (الإصلاح الثاني: منع القسمة على صفر)
    filtered_results = []
    if all_results:
        max_raw_score = all_results[0]['score']
        # إذا كان السكور صفر (نادر الحدوث)، نجعله 1 لتجنب NaN
        if max_raw_score == 0:
            max_raw_score = 1.0

        for res in all_results:
            # الحساب: (الدرجة / أعلى درجة) * 98
            try:
                relative_score = (res['score'] / max_raw_score) * 98
            except ZeroDivisionError:
                relative_score = 0

            # تصفية النتائج الضعيفة جداً
            if relative_score > 1: 
                res['percentage'] = round(relative_score, 1)
                filtered_results.append(res)
    
    # 3. تقسيم الصفحات (Pagination)
    total_results = len(filtered_results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_results = filtered_results[start_idx:end_idx]
    
    # 4. تجهيز البيانات النهائية
    formatted_results = []
    for item in page_results:
        doc_id = str(item['doc_id']) # تأكد أنه نص للبحث في القاموس
        
        # جلب البيانات من القاموس الذي أصلحناه بالأعلى
        doc_data = ARTICLES_MAP.get(doc_id, {})

        # التعامل مع احتمالية عدم وجود بيانات
        title = doc_data.get("title", f"Document #{doc_id}")
        url = doc_data.get("url", "#")
        full_content = doc_data.get("content", "") or doc_data.get("text", "")

        snippet = generate_smart_snippet_with_highlight(full_content, query)

        formatted_results.append({
            'doc_id': item['doc_id'],
            'title': title,
            'url': url,
            'snippet': snippet,
            'percentage': item.get('percentage', 0)
        })

    return jsonify({
    'success': True,
    'results': formatted_results,
    'total': total_results,
    'page': page,
    'total_pages': (total_results + per_page - 1) // per_page
})


if __name__ == '__main__':
    app.run(debug=True, port=5000)