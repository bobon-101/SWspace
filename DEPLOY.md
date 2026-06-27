# Deploy & Update Guide — PythonAnywhere

---

## ภาพรวม Workflow

```
แก้โค้ด (local) → test → commit → push → pull บน PA → reload
```

ทุกอย่างวนซ้ำขั้นตอนนี้ทุกครั้งที่อัพเดต

---

## ส่วน A: Deploy ครั้งแรก

ทำครั้งเดียวตอนตั้งระบบ ใช้เวลาประมาณ 15–20 นาที

```bash
# บน PythonAnywhere Bash console

git clone https://github.com/KitiFam/<repo-name>.git ~/swspace
mkvirtualenv --python=/usr/bin/python3.10 swspace
pip install -r ~/swspace/requirements.txt

# สร้าง .env (ดูตัวอย่างด้านล่าง)
# จากนั้น:
cd ~/swspace
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_test_accounts
mkdir -p ~/swspace/media
```

**ตัวอย่าง .env บน server** (`~/swspace/.env`):

```
SECRET_KEY=<สร้างด้วย: python -c "import secrets; print(secrets.token_urlsafe(50))">
DEBUG=False
ALLOWED_HOSTS=<username>.pythonanywhere.com
COMMITTEE_VERIFICATION_CODE=<รหัสที่ต้องการ>
```

จากนั้นตั้งค่า Web App ใน PythonAnywhere Dashboard:

| ส่วน | ค่า |
|------|-----|
| WSGI file | ดู Section C ด้านล่าง |
| Virtualenv | `/home/<username>/.virtualenvs/swspace` |
| Static URL `/static/` | `/home/<username>/swspace/staticfiles` |
| Static URL `/media/` | `/home/<username>/swspace/media` |

**เนื้อหา WSGI file** (`/var/www/<username>_pythonanywhere_com_wsgi.py`):

```python
import os
import sys

path = '/home/<username>/swspace'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

กด **Reload** ใน Web tab — เสร็จสิ้น

---

## ส่วน B: อัพเดตโค้ด (ทำทุกครั้งที่แก้ไข)

### 1. แก้โค้ดและทดสอบบน machine ของคุณ

```bash
python manage.py test
```

ต้องผ่านทุก test ก่อน push

### 2. Commit และ Push ขึ้น GitHub

```bash
git add <ชื่อไฟล์ที่แก้>
git commit -m "อธิบายสิ่งที่แก้ไข"
git push
```

### 3. Pull และ Reload บน PythonAnywhere

เปิด **PythonAnywhere Dashboard** → **Consoles** → **Bash** (เปิดใหม่ได้เสมอ)

```bash
cd ~/swspace
git pull
```

จากนั้น **ดูตารางด้านล่าง** ว่าต้องรันคำสั่งเพิ่มหรือไม่:

| การเปลี่ยนแปลงที่แก้ไข | คำสั่งเพิ่มเติม |
|------------------------|----------------|
| แก้ Python, template, view, form | ไม่ต้องรันอะไรเพิ่ม |
| เพิ่ม/แก้ไข model (มี migration ใหม่) | `python manage.py migrate` |
| แก้ CSS, JS, รูปใน `static/` | `python manage.py collectstatic --noinput` |
| แก้ทั้ง model และ static | รันทั้งสองคำสั่ง |
| แก้ `.env` (ค่า config) | แก้ไฟล์ `~/swspace/.env` ด้วย `nano` |

สุดท้าย: กลับไปที่ **Web** tab → กดปุ่ม **Reload** สีเขียว

---

## ส่วน C: Script อัตโนมัติ (ทางเลือก)

สร้าง script บน PythonAnywhere เพื่อรวมทุกคำสั่งไว้ในที่เดียว

```bash
# สร้างไฟล์ script (ทำครั้งเดียว)
cat > ~/update.sh << 'EOF'
#!/bin/bash
set -e
cd ~/swspace
echo ">>> git pull"
git pull
echo ">>> migrate"
python manage.py migrate
echo ">>> collectstatic"
python manage.py collectstatic --noinput
echo ">>> done — go reload in Web tab"
EOF

chmod +x ~/update.sh
```

หลังจากนั้น ทุกครั้งที่อัพเดตใช้แค่:

```bash
workon swspace && ~/update.sh
```

แล้วกด **Reload** ใน Web tab

> `workon swspace` เปิดใช้ virtualenv ก่อนรัน script

---

## ส่วน D: แก้ไขไฟล์ .env บน server

`.env` บน PythonAnywhere **ไม่ได้มาจาก git** — ต้องแก้บน server โดยตรง

```bash
nano ~/swspace/.env
```

ปุ่มที่ใช้ใน nano:
- แก้ไขได้ปกติ
- `Ctrl+O` → Enter (บันทึก)
- `Ctrl+X` (ออก)

หลังแก้ .env ต้อง **Reload** เสมอเพื่อให้ Django โหลดค่าใหม่

---

## ส่วน E: ตรวจสอบ Error

ถ้าหน้าเว็บพัง หลัง reload:

**Web tab** → ลิงก์ **Error log** ทางขวา → ดูบรรทัดล่างสุด

```bash
# หรือดูผ่าน console
tail -n 50 /var/log/<username>.pythonanywhere.com.error.log
```

---

## สรุปคำสั่งที่ใช้บ่อย

| งาน | คำสั่ง |
|-----|--------|
| ดึงโค้ดใหม่ | `cd ~/swspace && git pull` |
| รัน migration | `python manage.py migrate` |
| Collect static | `python manage.py collectstatic --noinput` |
| ดู error log | `tail -50 /var/log/<username>.pythonanywhere.com.error.log` |
| เปิด virtualenv | `workon swspace` |
| รัน test (local) | `python manage.py test` |
| แก้ .env | `nano ~/swspace/.env` |
