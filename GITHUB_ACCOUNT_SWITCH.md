# วิธี Logout และ Login ใหม่ด้วย Account pwd-vw

## ขั้นตอนที่ 1: Logout จาก GitHub Account ปัจจุบัน (popwandee)

```bash
# Logout จาก GitHub CLI
gh auth logout

# ตรวจสอบสถานะ (ควรแสดงว่าไม่มี account login)
gh auth status
```

## ขั้นตอนที่ 2: Login ใหม่ด้วย Account pwd-vw

### วิธีที่ 1: Login แบบ Interactive (แนะนำ)

```bash
# Login ใหม่ (จะเปิดเบราว์เซอร์ให้ login)
gh auth login

# เมื่อถามคำถาม:
# - What account do you want to log into? → GitHub.com
# - What is your preferred protocol? → HTTPS
# - Authenticate Git with your GitHub credentials? → Yes
# - How would you like to authenticate? → Login with a web browser
# - Enter a code: → จะแสดง code ให้ copy ไปใส่ในเบราว์เซอร์
```

### วิธีที่ 2: Login ด้วย Personal Access Token

```bash
# Login ด้วย token โดยตรง
gh auth login --with-token < token.txt

# หรือใส่ token โดยตรง (ไม่แนะนำ - token จะเห็นใน history)
echo "YOUR_PERSONAL_ACCESS_TOKEN" | gh auth login --with-token
```

### วิธีที่ 3: Login ด้วย Token แบบ Interactive

```bash
# ไปสร้าง Personal Access Token ก่อนที่: https://github.com/settings/tokens
# จากนั้นรันคำสั่งนี้:
gh auth login --web

# หรือ
gh auth login --hostname github.com --git-protocol https --web
```

## ขั้นตอนที่ 3: ตรวจสอบการ Login

```bash
# ตรวจสอบ account ที่ login อยู่
gh auth status

# ตรวจสอบ username
gh api user --jq '.login'

# ตรวจสอบ organizations
gh api user/orgs --jq '.[].login'
```

## ขั้นตอนที่ 4: อัปเดต Git Config (ถ้าจำเป็น)

```bash
# ตั้งค่า user name และ email ใหม่ (ถ้าต้องการ)
git config --global user.name "pwd-vw"
git config --global user.email "admin@pwdvisionworks.com"

# ตรวจสอบ
git config --global user.name
git config --global user.email
```

## ขั้นตอนที่ 5: ทดสอบการ Push

```bash
# ตรวจสอบ remote
git remote -v

# ลอง push อีกครั้ง
git push -u origin main

# หรือสร้าง repository ใหม่ (ถ้ายังไม่มี)
gh repo create pwd-vw/computer-vision --public --source=. --remote=origin --push
```

---

## คำแนะนำเพิ่มเติม

### ถ้า pwd-vw เป็น Organization Account (ไม่ใช่ Personal Account)

ถ้า "pwd-vw" เป็น organization และไม่มี personal account ชื่อ "pwd-vw" คุณต้อง:

1. **ใช้ Personal Account ที่มีสิทธิ์ใน organization pwd-vw**
   - Login ด้วย personal account ที่เป็นสมาชิกของ organization pwd-vw
   - สร้าง repository ใน organization: `gh repo create pwd-vw/computer-vision ...`

2. **ตรวจสอบสิทธิ์ใน Organization**
   ```bash
   # หลัง login แล้ว ตรวจสอบว่าเป็นสมาชิกของ org หรือไม่
   gh api orgs/pwd-vw/members --jq '.[] | select(.login == "YOUR_USERNAME")'
   ```

### ถ้าต้องการ Login หลาย Accounts พร้อมกัน

```bash
# Login account แรก
gh auth login --hostname github.com --git-protocol https

# Login account ที่สอง (ใช้ hostname ต่างกัน หรือใช้ token)
gh auth login --hostname github.com --user pwd-vw --git-protocol https
```

### ถ้าต้องการลบ Credentials ทั้งหมด

```bash
# Logout ทั้งหมด
gh auth logout

# ลบไฟล์ config
rm -rf ~/.config/gh/

# ลบ git credentials cache
git credential-cache exit
# หรือ
rm ~/.git-credentials
```

