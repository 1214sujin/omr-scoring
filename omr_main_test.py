import sys
import cv2
import numpy as np
from pdf2image import convert_from_path

from omr_read import *
from omr_draw import *

def log(*msg):
    print(*msg, flush=True)

def main():
    
    log('sys.argv:', sys.argv)
    subject_name, extra_on, pdf_path, students_path, corrects_path = sys.argv[1:]

    log("\n===== OMR 화면 인식 디버깅 =====")

    #pdf_name = input("PDF 파일명을 입력하세요: ").strip()
    pdf_name = 'omr_test'

    log("\nPDF 읽는 중...")

    page = convert_from_path(pdf_name + '.pdf')[6]

    # 이미지 전처리
    img = np.array(page)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    th = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    try:

        # OMR 카드 형식 식별
        timing_marks, answer_boxes, extra_boxes, sid_boxes = extract_boxes(th)

        # 채점
        answer_marks = detect_marks(th, answer_boxes)
        extra_marks = detect_marks(th, extra_boxes)
        sid_marks = detect_marks(th, sid_boxes)

        answers = detect_answers(answer_marks)
        sid = detect_sid(sid_marks)
        extra = detect_extra(extra_marks)

        row = {}
        
        for q,a in enumerate(answers):
            row[f"{q+1}"] = a
            
        log('===== answers ======')
        log('학번: ' + sid)
        log(row)

    finally:

        # 디버깅

        flat_boxes = [b for row in answer_boxes for b in row]

        boxes = answer_boxes+extra_boxes+sid_boxes
        marks = answer_marks+extra_marks+sid_marks
                
        debug_img = draw_debug(img, timing_marks, boxes, marks)

if __name__ == "__main__":
    main()
