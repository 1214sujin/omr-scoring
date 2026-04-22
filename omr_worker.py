import sys
import cv2
import numpy as np
from pdf2image import convert_from_path

from omr_read import *
from omr_draw import *
from omr_excel import *

QUESTIONS = 60
CHOICES = 5

def log(*msg):
    print(*msg, flush=True)

def main():
    subject_name, extra_on, pdf_path, students_path, corrects_path = sys.argv[1:]

    extra_on = bool(extra_on)

    log('===== 채점 시작 =====')

    log('PDF 읽는 중...')

    # 답안지
    pages = convert_from_path(pdf_path)
    TOTAL_PAGES = len(pages)
    log(f'답안지 수: {TOTAL_PAGES}')
    log('채점 중...')

    results = {}

    for i,page in enumerate(pages):
        
        img = np.array(page)
        
        # 이미지 전처리
        # openCV 색상체계(BGR)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # 빨간색 필터링 (빨강 -> 하양)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 100, 70])
        upper_red = np.array([10, 255, 255])

        red_mask = cv2.inRange(hsv, lower_red, upper_red)
        
        mask_img = img.copy()
        mask_img[red_mask > 0] = (255,255,255)

        gray = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)

        th = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        try :

            # OMR 카드 형식 식별
            timing_marks, answer_boxes, extra_boxes, sid_boxes = extract_boxes(th)

            # 마킹 인식
            answer_marks = detect_marks(th, answer_boxes)
            extra_marks = detect_marks(th, extra_boxes)
            sid_marks = detect_marks(th, sid_boxes)

            answers = detect_answers(answer_marks)
            sid = detect_sid(sid_marks)
            if extra_on:
                extra = detect_extra(extra_marks)
            else:
                extra=0

            # 엑셀 답안
            results[sid] = answers
            
        except Exception as e:
            
            log(f'{i+1} 페이지 처리 실패:', e)

        finally:

            # 디버깅용 이미지 생성
            debug_img_name = f'{subject_name}/{subject_name}-답안지/{sid}.png'

            flat_boxes = [b for row in answer_boxes for b in row]

            boxes = answer_boxes+extra_boxes+sid_boxes
            marks = answer_marks+extra_marks+sid_marks

            debug_img = draw_debug(img, timing_marks, boxes, marks, debug_img_name)

    log('결과 저장 중...')
    
    # 학생 리스트
    std_list = load_students_list(students_path)

    # 정답 및 배점
    answer_key, score_table = load_correct_answer(corrects_path)

    save_result(results, extra, std_list, answer_key, score_table, subject_name)

    log('===== 작업 완료 =====\n')


if __name__ == '__main__':
    main()
