# ===================================================================
# 🔬 ملف بناء الفهرس - build_index.py (النسخة المصححة والنهائية)
# ===================================================================
import os, re, json, nltk, time
from collections import defaultdict

print("[*] Checking NLTK packages...")
try:
    nltk.data.find('tokenizers/punkt'); nltk.data.find('corpora/stopwords'); nltk.data.find('tokenizers/punkt_tab')
    print("[+] Packages are ready.")
except LookupError:
    print("[!] Downloading missing packages..."); nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True)
    print("[+] Download complete.")

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

stop_words = set(stopwords.words('english')); stemmer = PorterStemmer()
INPUT_FOLDER = "articles"; OUTPUT_FILE = "inverted_index.json"

def clean_text(text):
    text = text.lower(); text = re.sub(r'[^a-z\s]', '', text)
    tokens = word_tokenize(text)
    return [stemmer.stem(token) for token in tokens if token not in stop_words]

def build_inverted_index():
    inverted_index = defaultdict(set)
    try:
        all_files = os.listdir(INPUT_FOLDER)
        # --- هذا هو الإصلاح: فلترة الملفات التي لا تحتوي على أرقام ---
        file_names = [f for f in all_files if re.search(r'doc\d+\.txt', f)]
        file_names = sorted(file_names, key=lambda x: int(re.search(r'\d+', x).group()))
        # ---------------------------------------------------------
    except (FileNotFoundError):
        print(f"Error: Cannot find '{INPUT_FOLDER}' folder. Please check the path.")
        return

    start_time = time.time(); total_files = len(file_names)
    print(f"\n--- Building index for {total_files} files ---")

    for i, file_name in enumerate(file_names):
        doc_id = int(re.search(r'\d+', file_name).group())
        file_path = os.path.join(INPUT_FOLDER, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
            for token in clean_text(content): inverted_index[token].add(doc_id)
            if (i + 1) % 100 == 0: print(f"Processed {i + 1}/{total_files} files...")
        except Exception as e: print(f"Error processing {file_name}: {e}")

    final_index = {token: sorted(list(doc_ids)) for token, doc_ids in inverted_index.items()}
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: json.dump(final_index, f, indent=4)
    end_time = time.time()

    print(f"\n--- Index built successfully! ---")
    print(f"Saved to: {OUTPUT_FILE}"); print(f"Unique words: {len(final_index)}"); print(f"Time taken: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    build_inverted_index()
