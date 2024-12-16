import cv2
import numpy as np
import pytesseract

# 이미지 업로드
img = cv2.imread('keyimages/82_5feea617-099c-47e9-9781-e3f01cb59da2.jpg')

# 마우스로 ROI 영역 선택
x, y, w, h = cv2.selectROI('img', img, False)

# ROI가 유효하면 처리 진행
if w and h:
    roi = img[y:y+h, x:x+w]  # 선택한 영역 자르기
    cv2.imshow('Cropped', roi)  # 잘린 이미지 표시
    cv2.imwrite('test/cropped.jpg', roi)  # 잘린 이미지를 파일로 저장

    # Tesseract OCR 실행
    ocr = pytesseract.image_to_string('test/cropped.jpg', lang='kor+eng')
    print("OCR 결과:")
    print(ocr)

cv2.waitKey(0)
cv2.destroyAllWindows()

