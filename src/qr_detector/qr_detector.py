import cv2
import numpy as np
from typing import List, Optional, Union
from dataclasses import dataclass
import os, time

@dataclass
class QRResult:
    """คลาสสำหรับเก็บผลลัพธ์จากการอ่าน QR code"""
    data: bytes
    def decode(self, encoding: str = 'utf-8') -> Optional[str]:
        """แปลงข้อมูลไบต์เป็นสตริง"""
        try:
            return self.data.decode(encoding)
        except UnicodeDecodeError:
            return None

class QRDetectorError(Exception):
    """คลาสสำหรับข้อผิดพลาดที่เกิดในโมดูล QR Detector"""
    pass

class QRDetector:
    def __init__(self, debug: bool = False):
        self.qr_detector = cv2.QRCodeDetector()
        self.debug = debug

    def preprocess_image(self, img: np.ndarray, scale: float = 2.0) -> np.ndarray:
        """ขยายและปรับแต่งภาพเพื่อเพิ่มประสิทธิภาพการตรวจจับ QR Code"""
        # แปลงเป็นภาพขาวดำ
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # ปรับความคมชัด
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # ลดสัญญาณรบกวน
        gray = cv2.medianBlur(gray, 3)
        
        # แปลงเป็นภาพขาวดำแบบไบนารี
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # ขยายภาพ
        height, width = binary.shape[:2]
        resized = cv2.resize(binary, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_LINEAR)
        
        return resized

    def rotate_image(self, img: np.ndarray, angle: float) -> np.ndarray:
        """หมุนภาพเพื่อแก้ไข QR Code ที่เอียง"""
        height, width = img.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)
        return cv2.warpAffine(img, rotation_matrix, (width, height))

    def decode(self, img: np.ndarray) -> List[QRResult]:
        """ถอดรหัส QR Code จากภาพ พร้อมการตรวจสอบหลายมุม"""
        try:
            if img is None or img.size == 0:
                raise QRDetectorError("รูปภาพไม่ถูกต้อง")
            
            # มุมที่จะลองหมุน
            rotation_angles = [0, 45, -45, 90, -90]
            all_results = []

            for angle in rotation_angles:
                # หมุนภาพ
                rotated_img = self.rotate_image(img, angle)
                
                # เตรียมภาพ
                preprocessed_img = self.preprocess_image(rotated_img, scale=2.0)
                
                # ตรวจจับและถอดรหัส QR Code
                retval, decoded_info, points, _ = self.qr_detector.detectAndDecodeMulti(preprocessed_img)
                
                # เก็บผลลัพธ์
                results = [QRResult(data.encode('utf-8')) for data in decoded_info if data]
                all_results.extend(results)

                # หากพบ QR Code แล้ว จะไม่ลองมุมอื่นต่อ
                if results:
                    break

            return all_results
        except Exception as e:
            if self.debug:
                print(f"เกิดข้อผิดพลาดในการถอดรหัส: {str(e)}")
            raise QRDetectorError(f"เกิดข้อผิดพลาดในการถอดรหัส: {str(e)}")

    def read_from_file(self, file_path: str) -> List[QRResult]:
        """อ่าน QR code จากไฟล์รูปภาพ"""
        try:
            if not os.path.exists(file_path):
                raise QRDetectorError(f"ไม่พบไฟล์: {file_path}")
            
            img = cv2.imread(file_path)
            if img is None:
                raise QRDetectorError(f"ไม่สามารถอ่านไฟล์รูปภาพได้: {file_path}")
            
            return self.decode(img)
        except QRDetectorError:
            raise
        except Exception as e:
            if self.debug:
                print(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")
            raise QRDetectorError(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")

    async def read_from_bytes(self, img_bytes: bytes) -> List[QRResult]:
        """อ่าน QR code จากข้อมูลไบต์ของรูปภาพ"""
        try:
            if not img_bytes:
                raise QRDetectorError("ไม่พบข้อมูลรูปภาพ")
            
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise QRDetectorError("ไม่สามารถแปลงข้อมูลไบต์เป็นรูปภาพได้")
            
            return self.decode(img)
        except QRDetectorError:
            raise
        except Exception as e:
            if self.debug:
                print(f"เกิดข้อผิดพลาดในการอ่านข้อมูลไบต์: {str(e)}")
            raise QRDetectorError(f"เกิดข้อผิดพลาดในการอ่านข้อมูลไบต์: {str(e)}")

    def decode_results(self, img: np.ndarray) -> Optional[List[str]]:
        """ถอดรหัส QR Code และคืนค่าเป็น List ของสตริง โดยลบค่า [''] ออก"""
        results = self.decode(img)
        decoded = list(filter(None, [result.decode() for result in results]))
        return decoded[0] if decoded else None

    async def read_from_bytes_decoded(self, img_bytes: bytes) -> Optional[List[str]]:
        """อ่าน QR code จากข้อมูลไบต์ และคืนค่า list ของสตริง โดยลบค่า [''] ออก"""
        results = await self.read_from_bytes(img_bytes)
        decoded = list(filter(None, [result.decode() for result in results]))
        return decoded[0] if decoded else None
        
    def scan_qr(self, camera_id: int = 0, window_width: int = 800, window_height: int = 600):
        """
        สแกน QR code และหยุดเมื่อได้ผลลัพธ์ พร้อมความสามารถในการขยายหน้าต่างและเพิ่มประสิทธิภาพการสแกนระยะไกล
        
        Args:
            camera_id: ID ของกล้องที่ต้องการใช้ (default: 0)
            window_width: ความกว้างของหน้าต่างที่ต้องการ (default: 800)
            window_height: ความสูงของหน้าต่างที่ต้องการ (default: 600)
        """
        # ตั้งค่ากล้อง
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("❌ ไม่สามารถเปิดกล้องได้")
            return
    
        
        # สร้างหน้าต่างที่สามารถปรับขนาดได้
        cv2.namedWindow("QR Scanner (press 'q' to exit)", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("QR Scanner (press 'q' to exit)", window_width, window_height)
        
        print("✅ เปิดกล้องสำเร็จ - กำลังเริ่มสแกน")
        
        # ตัวแปรเพื่อเก็บเวลาและควบคุมความถี่ในการสแกน
        last_scan_time = time.time()
        scan_interval = 0.1  # ตรวจสอบทุก 100 มิลลิวินาที (เร็วกว่าการสแกนทุกเฟรม)
        
        # ตัวแปรเก็บค่า QR Code ที่ตรวจพบล่าสุด
        last_detected_qr = None
        confirmation_count = 0  # จำนวนครั้งที่ต้องการให้ตรวจพบซ้ำก่อนยืนยันผล
        
        # ตัวแปรสำหรับการประมวลผลแบบขนาน
        process_this_frame = True  # สลับไปมาระหว่างเฟรมเพื่อลดการประมวลผล
        
        try:
            while True:
                # อ่านเฟรมจากกล้อง
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("❌ ไม่สามารถอ่านภาพจากกล้องได้")
                    break

                # แสดงขนาดเฟรม
                height, width = frame.shape[:2]
                
                # สร้าง copy สำหรับการแสดงผล
                display_frame = frame.copy()
                
                # สร้างกรอบตรงกลางหน้าจอสำหรับบอกตำแหน่งการสแกน
                center_x, center_y = width // 2, height // 2
                
                # ปรับขนาดกรอบสแกนให้ใหญ่ขึ้นเพื่อรองรับการสแกนระยะไกล
                scan_box_size = min(width, height) * 0.7  # เพิ่มขนาดเป็น 70% ของหน้าจอ
                
                top_left = (int(center_x - scan_box_size // 2), int(center_y - scan_box_size // 2))
                bottom_right = (int(center_x + scan_box_size // 2), int(center_y + scan_box_size // 2))
                
                # วาดกรอบสแกนตรงกลางจอ
                cv2.rectangle(display_frame, top_left, bottom_right, (0, 255, 0), 2)
                
                # วาดเส้นตัดกลางกรอบ
                cv2.line(display_frame, 
                    (center_x, top_left[1]), 
                    (center_x, bottom_right[1]), 
                    (0, 255, 0), 1)
                cv2.line(display_frame, 
                    (top_left[0], center_y), 
                    (bottom_right[0], center_y), 
                    (0, 255, 0), 1)
                
                # เพิ่มข้อความลงในเฟรม
                status_text = f"Scanning... ({width}x{height})"
                cv2.putText(display_frame, status_text, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                guide_text = "วางรหัส QR ในกรอบสีเขียว"
                cv2.putText(display_frame, guide_text, (width // 2 - 150, height - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                # ตรวจสอบว่าถึงเวลาสแกนหรือยัง (ไม่สแกนทุกเฟรม)
                current_time = time.time()
                if current_time - last_scan_time > scan_interval and process_this_frame:
                    # ตั้งเวลาสแกนใหม่
                    last_scan_time = current_time
                    
                    try:
                        # ตัดเฉพาะส่วนในกรอบสแกนเพื่อลดพื้นที่การประมวลผล
                        roi = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                        
                        if roi.size > 0:  # ตรวจสอบว่า ROI ไม่ว่างเปล่า
                            # สร้างภาพแบบต่างๆ เพื่อเพิ่มโอกาสในการตรวจจับ
                            
                            # ภาพต้นฉบับปรับปรุงคุณภาพเล็กน้อย
                            enhanced_roi = cv2.detailEnhance(roi, sigma_s=10, sigma_r=0.15)
                            
                            # ภาพขาวดำแบบปรับปรุง
                            gray_roi = cv2.cvtColor(enhanced_roi, cv2.COLOR_BGR2GRAY)
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                            enhanced_gray = clahe.apply(gray_roi)
                            
                            # ภาพไบนารีแบบปรับความสว่าง
                            _, binary_roi = cv2.threshold(enhanced_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                            
                            # ลองสแกนในแต่ละรูปแบบของภาพ
                            results = None
                            
                            # 1. ลองตรวจจับใน ROI ที่ปรับปรุงแล้ว
                            try:
                                results = self.decode(enhanced_roi)
                            except Exception as e:
                                if self.debug:
                                    print(f"Error in enhanced detection: {e}")
                            
                            # 2. ถ้ายังไม่พบ ลองใช้ภาพขาวดำที่ปรับปรุงแล้ว (แปลงเป็น 3 channel)
                            if not results:
                                try:
                                    enhanced_gray_3ch = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
                                    results = self.decode(enhanced_gray_3ch)
                                except Exception as e:
                                    if self.debug:
                                        print(f"Error in gray detection: {e}")
                            
                            # 3. ถ้ายังไม่พบ ลองใช้ภาพไบนารี (แปลงเป็น 3 channel)
                            if not results:
                                try:
                                    binary_3ch = cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2BGR)
                                    results = self.decode(binary_3ch)
                                except Exception as e:
                                    if self.debug:
                                        print(f"Error in binary detection: {e}")
                            
                            # 4. หากยังไม่พบ ลองกับภาพเต็ม (ในกรณีที่ QR อยู่นอกกรอบหรือใหญ่เกินกรอบ)
                            if not results:
                                try:
                                    gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    _, binary_full = cv2.threshold(gray_full, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                                    binary_full_3ch = cv2.cvtColor(binary_full, cv2.COLOR_GRAY2BGR)
                                    results = self.decode(binary_full_3ch)
                                except Exception as e:
                                    if self.debug:
                                        print(f"Error in full frame detection: {e}")
                            
                            # ถ้าพบ QR Code
                            if results:
                                for result in results:
                                    decoded = result.decode()
                                    if decoded:
                                        # ตรวจสอบว่าเป็น QR Code เดิมหรือไม่
                                        if decoded == last_detected_qr:
                                            confirmation_count += 1
                                        else:
                                            # พบ QR Code ใหม่ เริ่มนับใหม่
                                            last_detected_qr = decoded
                                            confirmation_count = 1
                                        
                                        # แสดงข้อความว่าตรวจพบ QR Code
                                        cv2.putText(display_frame, f"QR Code detected! ({confirmation_count}/3)", (10, 60),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                        cv2.putText(display_frame, decoded, (10, 90),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                        
                                        # ถ้าตรวจพบ QR เดิมซ้ำครบ 3 ครั้ง ถือว่ายืนยันผล
                                        if confirmation_count >= 3:
                                            # แสดงข้อความยืนยันการตรวจพบ
                                            result_overlay = display_frame.copy()
                                            cv2.rectangle(result_overlay, (0, 0), (width, height), (0, 200, 0), -1)
                                            alpha = 0.3
                                            cv2.addWeighted(result_overlay, alpha, display_frame, 1 - alpha, 0, display_frame)
                                            
                                            cv2.putText(display_frame, "QR CODE CONFIRMED!", (center_x - 180, center_y - 50),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                                            cv2.putText(display_frame, decoded, (center_x - 180, center_y + 50),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                                                    
                                            cv2.imshow("QR Scanner (press 'q' to exit)", display_frame)
                                            cv2.waitKey(1500)  # แสดงเฟรมสุดท้าย 1.5 วินาที
                                            print(f"\n🎯 ผลการสแกน: {decoded}")
                                            print("✅ สแกนสำเร็จ - กำลังปิดโปรแกรม")
                                            return decoded

                    except Exception as e:
                        if self.debug:
                            print(f"\n⚠️ เกิดข้อผิดพลาดในการสแกน: {str(e)}")
                
                # สลับตัวแปรสำหรับการประมวลผลเฟรมถัดไป (สแกนเฟรมเว้นเฟรม)
                process_this_frame = not process_this_frame
                
                # แสดงภาพจากกล้อง
                cv2.imshow("QR Scanner (press 'q' to exit)", display_frame)

                # กด 'q' เพื่อออกก่อนเจอ QR Code
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 ยกเลิกการสแกน")
                    break
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()
