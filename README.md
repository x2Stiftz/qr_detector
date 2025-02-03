# QR Detector - คู่มือการใช้งาน

## ฟังก์ชันหลัก

| ฟังก์ชัน | คำอธิบาย | ตัวอย่างการใช้งาน |
|----------|------------|-------------------|
| `read_from_file()` | อ่าน QR code จากไฟล์รูปภาพ | ```python
detector = QRDetector()
results = detector.read_from_file('image.jpg')
for result in results:
    print(result.decode())
``` |
| `read_from_bytes()` | อ่าน QR code จากข้อมูลไบต์ | ```python
async def read_qr(image_bytes):
    detector = QRDetector()
    results = await detector.read_from_bytes(image_bytes)
    for result in results:
        print(result.decode())
``` |
| `decode()` | ถอดรหัส QR code จาก numpy array | ```python
import cv2
detector = QRDetector()
img = cv2.imread('image.jpg')
results = detector.decode(img)
``` |

## การติดตั้ง
```bash
pip install qr-detector-th
```
## พารามิเตอร์เพิ่มเติม

| พารามิเตอร์ | คำอธิบาย | ค่าเริ่มต้น |
|-------------|------------|--------------|
| `debug` | เปิดโหมดดีบัก แสดงข้อผิดพลาด | `False` |

## การจัดการข้อผิดพลาด

```python
from qr_detector import QRDetector, QRDetectorError

try:
    detector = QRDetector(debug=True)
    results = detector.read_from_file('image.jpg')
except QRDetectorError as e:
    print(f"เกิดข้อผิดพลาด: {e}")
```

## การแปลงรหัส

```python
results = detector.read_from_file('image.jpg')
for result in results:
    # แปลงรหัสด้วยการเข้ารหัสอื่น
    decoded_text = result.decode(encoding='utf-8')
```

