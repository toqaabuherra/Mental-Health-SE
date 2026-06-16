import json
import os
import re
import math
from collections import Counter, defaultdict
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

# التأكد من تحميل المكتبات
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

class AdvancedMatchingEngine:
    
    def __init__(self, index_path, articles_folder):
        print("Initializing Search Engine...")
        self.articles_folder = articles_folder
        
        # أدوات المعالجة
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # تحميل الفهرس
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                self.inverted_index = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Index file '{index_path}' not found.")
            self.inverted_index = {}
        
        # حساب عدد المستندات
        all_doc_ids = set()
        for word in self.inverted_index:
            # التأكد من أن القيم هي أرقام صحيحة
            doc_list = self.inverted_index[word]
            if isinstance(doc_list, list):
                all_doc_ids.update(doc_list)
        
        self.total_docs = len(all_doc_ids) if all_doc_ids else 1
        
        # بناء المتجهات
        self.tfidf_vectors = self._build_all_tfidf_vectors()
        print(f"✅ Engine Ready. Indexed {self.total_docs} documents.")

    def _process_text(self, text):
        """دالة التنظيف والستيمينج الموحدة"""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        tokens = text.split()
        return [self.stemmer.stem(t) for t in tokens if t not in self.stop_words]

    def _calculate_tf(self, doc_id):
        # --- الإصلاح هنا: تعديل اسم الملف ليطابق docX.txt ---
        file_path = os.path.join(self.articles_folder, f"doc{doc_id}.txt")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tokens = self._process_text(content)
            return Counter(tokens)
        except FileNotFoundError:
            print(f"⚠️ Warning: File '{file_path}' not found during TF calculation.")
            return Counter()
        except Exception as e:
            print(f"⚠️ Error reading '{file_path}': {e}")
            return Counter()

    def _calculate_idf(self, term):
        doc_freq = len(self.inverted_index.get(term, []))
        if doc_freq == 0: return 0
        return math.log10(self.total_docs / doc_freq)

    def _build_all_tfidf_vectors(self):
        print("Building TF-IDF vectors...")
        all_vectors = {}
        all_ids = set()
        for term in self.inverted_index:
            all_ids.update(self.inverted_index[term])
            
        for doc_id in all_ids:
            tf_counts = self._calculate_tf(doc_id)
            doc_vector = {}
            if not tf_counts: continue # تخطي إذا لم يوجد كلمات

            for term, count in tf_counts.items():
                idf = self._calculate_idf(term)
                tfidf = count * idf
                if tfidf > 0:
                    doc_vector[term] = tfidf
            all_vectors[doc_id] = doc_vector
        return all_vectors

    def _vectorize_query(self, query_tokens):
        query_vector = {}
        tf_counts = Counter(query_tokens)
        for term, count in tf_counts.items():
            # نستخدم IDF الموجود في الفهرس للكلمات الموجودة في الكويري
            idf = self._calculate_idf(term)
            tfidf = count * idf
            if tfidf > 0:
                query_vector[term] = tfidf
        return query_vector

    def _cosine_similarity(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        
        # حماية ضد القسمة على صفر
        if sum1 == 0 or sum2 == 0: return 0.0
        return float(numerator) / (math.sqrt(sum1) * math.sqrt(sum2))

    def search(self, query):
        if not query: return []
        
        # 1. تنظيف الكويري
        if isinstance(query, str):
            query_tokens = self._process_text(query)
        else:
            query_tokens = query

        if not query_tokens: return []

        query_vector = self._vectorize_query(query_tokens)
        
        # إذا كانت كلمات البحث غير موجودة تماماً في الفهرس
        if not query_vector:
            return []

        scores = {}
        for doc_id, doc_vector in self.tfidf_vectors.items():
            score = self._cosine_similarity(query_vector, doc_vector)
            if score > 0:
                scores[doc_id] = score
        
        ranked_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        return [{'doc_id': doc_id, 'score': score} for doc_id, score in ranked_docs]