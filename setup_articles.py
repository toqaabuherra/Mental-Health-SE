import json
import os

# 1. إعداد المسارات
json_file_path = 'articles_data.json'  # الملف الذي رفعتَه
output_folder = 'articles'             # المجلد الذي سيتم إنشاؤه

# 2. إنشاء المجلد إذا لم يكن موجوداً
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"✅ Created folder: {output_folder}")

# 3. قراءة البيانات من ملف JSON وتحويلها لملفات نصية
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # نفترض أن الملف يحتوي على قائمة مقالات، أو قاموس به مفتاح للمقالات
    # سأضع كوداً مرناً يتعامل مع الحالتين
    articles = data if isinstance(data, list) else data.get('articles', [])

    print(f"🔄 Processing {len(articles)} articles...")

    for i, article in enumerate(articles):
        # اسم الملف يجب أن يكون doc1, doc2... ليتوافق مع نظامك
        filename = f"doc{i+1}.txt"
        file_path = os.path.join(output_folder, filename)
        
        # استخراج العنوان والمحتوى (تأكد أن المفاتيح تطابق ملفك)
        title = article.get('title', 'No Title')
        url = article.get('url', 'No URL')
        content = article.get('content', '') or article.get('text', '') # احتياطاً لو اختلف الاسم

        # الكتابة داخل الملف
        with open(file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(f"{title}\n")
            txt_file.write(f"{url}\n\n")
            txt_file.write(content)
            
    print(f"✅ Success! Created {len(articles)} text files in '{output_folder}'.")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{json_file_path}'. Make sure it's in the same folder.")
except Exception as e:
    print(f"❌ Error: {e}")