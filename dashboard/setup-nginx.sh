#!/bin/bash
# สคริปต์สำหรับตั้งค่า nginx สำหรับ dashboard

echo "=========================================="
echo "AI Camera Services Dashboard - Nginx Setup"
echo "=========================================="
echo ""

# 1. ทดสอบ nginx config
echo "[1/3] กำลังทดสอบ nginx configuration..."
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "❌ nginx configuration มีข้อผิดพลาด กรุณาตรวจสอบ"
    exit 1
fi

echo "✅ nginx configuration ถูกต้อง"
echo ""

# 2. Reload nginx
echo "[2/3] กำลัง reload nginx..."
sudo systemctl reload nginx

if [ $? -ne 0 ]; then
    echo "❌ ไม่สามารถ reload nginx ได้"
    exit 1
fi

echo "✅ nginx reloaded สำเร็จ"
echo ""

# 3. ตรวจสอบสถานะ
echo "[3/3] กำลังตรวจสอบสถานะ nginx..."
sudo systemctl status nginx.service --no-pager | head -10

echo ""
echo "=========================================="
echo "✅ การตั้งค่าเสร็จสมบูรณ์!"
echo "=========================================="
echo ""
echo "Dashboard สามารถเข้าถึงได้ที่:"
echo "  - ผ่าน nginx: http://YOUR_SERVER_IP/dashboard/"
echo "  - โดยตรง: http://YOUR_SERVER_IP:5000/"
echo ""
echo "หมายเหตุ:"
echo "  - ตรวจสอบว่า dashboard service ทำงานอยู่: systemctl status dashboard.service"
echo "  - ตรวจสอบว่า port 5000 เปิดอยู่: ss -tulpn | grep 5000"
echo ""

