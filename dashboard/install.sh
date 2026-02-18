#!/bin/bash
# สคริปต์สำหรับติดตั้ง Dashboard

echo "=========================================="
echo "AI Camera Services Dashboard - Installation"
echo "=========================================="
echo ""

# ตรวจสอบว่าเป็น root หรือไม่
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  ไม่ควรรันสคริปต์นี้ด้วย sudo"
   exit 1
fi

# 1. ติดตั้ง Python dependencies
echo "[1/4] กำลังติดตั้ง Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ การติดตั้ง dependencies ล้มเหลว"
    exit 1
fi

echo "✅ ติดตั้ง dependencies สำเร็จ"
echo ""

# 2. ตั้งค่า sudoers
echo "[2/4] กำลังตั้งค่า sudoers..."
echo ""
echo "⚠️  ต้องใช้ sudo เพื่อเพิ่มสิทธิ์ systemctl commands"
echo "กรุณารันคำสั่งนี้ด้วย sudo:"
echo ""
echo "sudo visudo -f /etc/sudoers.d/dashboard"
echo ""
echo "แล้วเพิ่มบรรทัดนี้:"
echo "devuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl start *, /usr/bin/systemctl stop *, /usr/bin/systemctl restart *, /usr/bin/systemctl show *, /usr/bin/systemctl daemon-reload, /bin/cp /tmp/service_config_update *, /bin/cp /tmp/service_env_update *"
echo ""
read -p "กด Enter เมื่อตั้งค่า sudoers เสร็จแล้ว..."

# 3. สร้าง systemd service
echo "[3/4] กำลังสร้าง systemd service..."
sudo cp dashboard.service /etc/systemd/system/dashboard.service
sudo systemctl daemon-reload

if [ $? -ne 0 ]; then
    echo "❌ การสร้าง systemd service ล้มเหลว"
    exit 1
fi

echo "✅ สร้าง systemd service สำเร็จ"
echo ""

# 4. Enable และ Start service
echo "[4/4] กำลังเริ่ม dashboard service..."
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service

if [ $? -ne 0 ]; then
    echo "❌ การเริ่ม service ล้มเหลว"
    exit 1
fi

echo "✅ Dashboard service เริ่มทำงานแล้ว"
echo ""

# ตรวจสอบสถานะ
echo "=========================================="
echo "สถานะ Dashboard Service:"
echo "=========================================="
sudo systemctl status dashboard.service --no-pager | head -10

echo ""
echo "=========================================="
echo "✅ การติดตั้งเสร็จสมบูรณ์!"
echo "=========================================="
echo ""
echo "Dashboard ทำงานที่: http://localhost:5000"
echo ""
echo "คำสั่งที่มีประโยชน์:"
echo "  - ดูสถานะ: sudo systemctl status dashboard.service"
echo "  - เริ่ม: sudo systemctl start dashboard.service"
echo "  - หยุด: sudo systemctl stop dashboard.service"
echo "  - ดู logs: sudo journalctl -u dashboard.service -f"
echo ""

