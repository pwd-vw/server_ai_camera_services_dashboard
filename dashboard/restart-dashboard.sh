#!/bin/bash
# สคริปต์สำหรับ restart dashboard service หลังจากแก้ไขโค้ด

echo "=========================================="
echo "Restart Dashboard Service"
echo "=========================================="
echo ""

# 1. หยุด process ที่รันอยู่ (ถ้ามี)
echo "[1/3] กำลังหยุด dashboard process..."
pkill -f "python3 app.py" 2>/dev/null
sleep 1

# 2. Restart service
echo "[2/3] กำลัง restart dashboard service..."
sudo systemctl restart dashboard.service

if [ $? -ne 0 ]; then
    echo "❌ ไม่สามารถ restart dashboard service ได้"
    exit 1
fi

echo "✅ restart dashboard service สำเร็จ"
echo ""

# 3. ตรวจสอบสถานะ
echo "[3/3] กำลังตรวจสอบสถานะ..."
sleep 2

echo ""
echo "สถานะ Dashboard Service:"
sudo systemctl status dashboard.service --no-pager | head -15

echo ""
echo "Port 5000:"
ss -tulpn | grep 5000 || echo "  → Port 5000 ยังไม่เปิด"

echo ""
echo "ทดสอบ Static Files:"
curl -I http://localhost:5000/static/style.css 2>&1 | grep -E "(HTTP|Content-Type)" | head -2

echo ""
echo "=========================================="
echo "✅ เสร็จสมบูรณ์!"
echo "=========================================="
echo ""
echo "Dashboard:"
echo "  - Local: http://localhost:5000/"
echo "  - Nginx: http://YOUR_SERVER_IP/dashboard/"
echo ""

