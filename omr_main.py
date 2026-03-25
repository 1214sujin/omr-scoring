import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from tkinter import Tk

from omr_read import *
from omr_draw import *
from omr_excel import *
from omr_ui import OMRApp

QUESTIONS = 60
CHOICES = 5

def start_processing(subject_name, extra_on,
                     pdf_path, students_path, corrects_path,
                     log):

    pdf_name = os.path.basename(pdf_path)

    log('===== 채점 시작 =====')

    log('\nPDF 읽는 중...')

    # 답안지
    pages = convert_from_path(pdf_path)

    results = {}

    for i,page in enumerate(pages):

        log(f'{i+1} 페이지 처리 중')
        
        # 이미지 전처리
        img = np.array(page)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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
            #result = {"학번":sid, "성명":std_list[sid]}

            #for q,a in enumerate(answers):
            #    row[f"{q+1}"] = ','.join(map(str,a))

            #results.append(row)
            
        except Exception as e:
            
            log(f'{i+1} 페이지 처리 실패: {e}')

        finally:
            
            # 디버깅용 이미지 생성
            debug_img_name = f'{subject_name}/{subject_name}-답안지/{i+1}-{sid}.png'

            flat_boxes = [b for row in answer_boxes for b in row]

            boxes = answer_boxes+extra_boxes+sid_boxes
            marks = answer_marks+extra_marks+sid_marks

            debug_img = draw_debug(img, timing_marks, boxes, marks, debug_img_name)

    # 학생 리스트
    std_list = load_students_list(students_path)

    # 정답 및 배점
    answer_key, score_table = load_correct_answer(corrects_path)

    save_result(results, extra, std_list, answer_key, score_table, subject_name)

    log('\n작업 완료\n')


def main():

    window = Tk()

    app = OMRApp(window, start_processing)
    
    window.mainloop()


if __name__ == '__main__':
    main()

#input('종료하려면 Enter를 누르세요.')


