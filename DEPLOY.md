# Deploy & Update Guide — PythonAnywhere

---

## ภาพรวม Workflow

```
แก้โค้ด (local) → บอก Claude "อัปเดตโค้ดขึ้น GitHub" → รัน 1 คำสั่งบน PA → Reload
```

ทุกอย่างวนซ้ำขั้นตอนนี้ทุกครั้งที่อัพเดต — รายละเอียดดู **ส่วน B**

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
| WSGI file | ดูเนื้อหาด้านล่าง |
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

## ส่วน B: อัพเดตโค้ด (ทำทุกครั้งที่แก้ไข) — ทำแค่ 2 ขั้นตอน

### ขั้นตอนที่ 1 — บอก Claude Code

พิมพ์สั้นๆ ว่า:

> อัปเดตโค้ดขึ้น GitHub ให้หน่อย

Claude จะรัน test → commit → push ให้อัตโนมัติ (ถ้า test ไม่ผ่าน จะหยุดแจ้งก่อน ไม่ push ของเสียขึ้นไป)

### ขั้นตอนที่ 2 — วางคำสั่งนี้ใน PythonAnywhere

เปิด **PythonAnywhere Dashboard** → **Consoles** → **Bash** (เปิดใหม่ได้เสมอ) แล้ววาง:

```bash
workon swspace && cd ~/swspace && git pull && python manage.py migrate && python manage.py collectstatic --noinput
```

### ขั้นตอนที่ 3 — กด Reload

ไปแท็บ **Web** → กดปุ่ม **Reload** สีเขียว — เสร็จ

> คำสั่งเดียวด้านบนรัน `migrate` และ `collectstatic` ทุกครั้งไปเลยแม้บางครั้งไม่จำเป็น (ไม่มีผลเสีย แค่เผื่อไว้ไม่ต้องมานั่งคิดว่ารอบนี้ต้องรันอะไรบ้าง) ถ้าอยากคุมละเอียดว่ารอบนี้จำเป็นต้องรันคำสั่งไหน ดูตารางนี้:

| การเปลี่ยนแปลงที่แก้ไข | คำสั่งที่จำเป็นจริงๆ |
|------------------------|----------------|
| แก้ Python, template, view, form | `workon swspace && cd ~/swspace && git pull` (ไม่ต้องรันอะไรเพิ่ม) |
| เพิ่ม/แก้ไข model (มี migration ใหม่) | เพิ่ม `python manage.py migrate` |
| แก้ CSS, JS, รูปใน `static/` | เพิ่ม `python manage.py collectstatic --noinput` |
| แก้ `.env` (ค่า config) | แก้ไฟล์ `~/swspace/.env` ด้วย `nano` แทน (ดูส่วน C) |

---

## ส่วน C: แก้ไขไฟล์ .env บน server

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

## ส่วน D: ตรวจสอบ Error

ถ้าหน้าเว็บพัง หลัง reload:

**Web tab** → ลิงก์ **Error log** ทางขวา → ดูบรรทัดล่างสุด

```bash
# หรือดูผ่าน console
tail -n 50 /var/log/<username>.pythonanywhere.com.error.log
```

---

## สรุปคำสั่งที่ใช้บ่อย

**อัปเดตโค้ด (ใช้บ่อยที่สุด — ก็อปวางบน PA ได้เลย):**

```bash
workon swspace && cd ~/swspace && git pull && python manage.py migrate && python manage.py collectstatic --noinput
```

| งาน | คำสั่ง |
|-----|--------|
| ดู error log | `tail -50 /var/log/<username>.pythonanywhere.com.error.log` |
| รัน test (local) | `python manage.py test` |
| แก้ .env | `nano ~/swspace/.env` |
