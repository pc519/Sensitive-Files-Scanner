import requests
from datetime import datetime
import webbrowser
import os

SENSITIVE_PATHS = [
    (".env", "ملف إعدادات البيئة وكلمات المرور (خطر حرج جداً)", "Critical"),
    (".git/config", "مجلد الكود المصدري Git مكشوف للعامة", "High"),
    ("backup.zip", "نسخة احتياطية مضغوطة للموقع قابلة للتحميل", "Critical"),
    ("backup.sql", "نسخة احتياطية لقاعدة البيانات مكشوفة", "Critical"),
    ("db.sql", "ملف قاعدة بيانات مكشوف", "Critical"),
    ("phpinfo.php", "ملف معلومات الخادم الحساسة (PHP Info)", "Medium"),
    ("wp-config.php.bak", "نسخة احتياطية لملف إعدادات ووردبريس", "Critical"),
    ("robots.txt", "ملف توجيه محركات البحث (قد يكشف مسارات مخفية)", "Info"),
    (".htaccess", "ملف إعدادات خادم Apache", "Medium"),
    ("admin/", "لوحة تحكم الإدارة مكشوفة على مسار افتراضي", "Low")
]
def scan_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    url = url.rstrip("/")
    print(f"\n[*] جاري فحص المسارات والملفات الحساسة للموقع: {url} ...")
    
    findings = []
    headers = {"User-Agent": "Mozilla/5.0 (Security-Audit-Tool)"}

    for path, desc, severity in SENSITIVE_PATHS:
        target_url = f"{url}/{path}"
        try:
            res = requests.get(target_url, headers=headers, timeout=5, allow_redirects=False)
            if res.status_code == 200 and len(res.text) > 0:
                print(f"[!] تم العثور على: {target_url} ({severity})")
                findings.append((target_url, desc, severity))
        except Exception:
            pass

    rows = ""
    for f_url, desc, sev in findings:
        color = "#ef4444" if sev in ["Critical", "High"] else ("#f59e0b" if sev == "Medium" else "#38bdf8")
        rows += f"<tr><td dir='ltr'>{f_url}</td><td>{desc}</td><td style='color:{color};font-weight:bold'>{sev}</td></tr>"

    if not rows:
        rows = "<tr><td colspan='3' style='text-align:center;color:#10b981'>✅ لم يتم العثور على ملفات حساسة مكشوفة في القائمة المفحوصة!</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>Sensitive Files Report</title>
<style>body{{font-family:Tahoma,sans-serif;background:#0f172a;color:#f8fafc;padding:30px}}
.box{{max-width:900px;margin:auto;background:#1e293b;padding:25px;border-radius:10px}}
table{{width:100%;border-collapse:collapse;margin-top:20px}}
th,td{{padding:12px;border-bottom:1px solid #334155;text-align:right}}
th{{background:#0f172a;color:#38bdf8}}</style></head>
<body><div class="box"><h2>🔍 تقرير فحص الملفات والمسارات الحساسة</h2>
<p><strong>الموقع:</strong> <span dir="ltr">{url}</span> | <strong>التاريخ:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
<p><strong>عدد النتائج المكتشفة:</strong> {len(findings)}</p>
<table><tr><th>المسار المكتشف</th><th>الوصف الأمني</th><th>درجة الخطورة</th></tr>{rows}</table></div></body></html>"""

    fname = f"files_report_{url.replace('https://','').replace('http://','').replace('.','_')}.html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] تم حفظ التقرير بنجاح: {fname}")
    webbrowser.open('file://' + os.path.realpath(fname))

if __name__ == "__main__":
    site = input("Enter website URL (e.g. github.com): ").strip()
    if site:
        scan_website(site)