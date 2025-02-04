# 📌 **QR Detector 1.2 - คู่มือการใช้งาน**

## 🚀 **ฟังก์ชันหลัก**

| ฟังก์ชัน | คำอธิบาย |
|----------|------------|
| **`read_from_file()`** | อ่าน QR Code จากไฟล์รูปภาพ |
| **`read_from_bytes()`** | อ่าน QR Code จากข้อมูลไบต์ |
| **`decode()`** | ถอดรหัส QR Code จากรูปภาพ (numpy array) |

### 🔹 **ตัวอย่างการใช้งาน**
#### 📂 อ่าน QR Code จากไฟล์รูปภาพ
```python
from qr_detector import QRDetector

detector = QRDetector()
results = detector.read_from_file('image.jpg')
for result in results:
    print(result.decode())
```

#### 🔄 อ่าน QR Code จากข้อมูลไบต์
```python
async def read_qr(image_bytes):
    detector = QRDetector()
    results = await detector.read_from_bytes(image_bytes)
    for result in results:
        print(result.decode())
```

#### 🖼️ ถอดรหัส QR Code จาก `numpy array`
```python
import cv2
from qr_detector import QRDetector

detector = QRDetector()
img = cv2.imread('image.jpg')
results = detector.decode(img)
```

---

## 📥 **การติดตั้ง**
```bash
pip install qr-detector-th
```
## ⌛ **การอัพเดต**
```bash
pip install --upgrade qr-detector-th
```
---

## ⚙️ **พารามิเตอร์เพิ่มเติม**
| พารามิเตอร์ | คำอธิบาย | ค่าเริ่มต้น |
|-------------|------------|--------------|
| `debug` | เปิดโหมดดีบัก แสดงข้อผิดพลาด | `False` |

---

## ⚠️ **การจัดการข้อผิดพลาด**
```python
from qr_detector import QRDetector, QRDetectorError

try:
    detector = QRDetector(debug=True)
    results = detector.read_from_file('image.jpg')
except QRDetectorError as e:
    print(f"เกิดข้อผิดพลาด: {e}")
```

---

## 🔄 **การแปลงรหัสผลลัพธ์**
```python
from qr_detector import QRDetector, QRDetectorError

try:
    detector = QRDetector(debug=True)
    results = detector.read_from_file('image.jpg')
    for result in results:
        decoded_text = result.decode(encoding='utf-8')
        print(f"รหัสที่แปลงแล้ว {decoded_text}")
except QRDetectorError as e:
    print(f"เกิดข้อผิดพลาด: {e}")
```

📌 **หมายเหตุ:** สามารถเปลี่ยน `encoding='utf-8'` เป็น `shift_jis` หรือ `iso-8859-1` ได้ตามข้อมูล QR Code ที่ใช้! 🎯
⛔ **ข้อผิดพลาดที่ยยังอาจจะพบเจอ** `ไม่สามารถตรวจสอบqrที่เล็กเกินได้` บาง qr ก็อาจไม่ตรวจสอบขออภัยสำหรับข้อผิดพลาดที่เกิดขึ้น🙏🙏
