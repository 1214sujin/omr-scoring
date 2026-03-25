import cv2
import numpy as np

SID_MARKS = 9
EXTRA_MARKS = 3
ANSWER_MARKS = 10

ANSWER_FIRST_OFFSET = 90
SID_FIRST_OFFSET = 1084
STEP = 49.7
END = 1600
BUBBLE_SIZE = 27

RATIO_THRESHOLD = 0.30


##### 마킹 찾기 #####

def extract_boxes(th):

    h_img, w_img = th.shape

    contours,_ = cv2.findContours(
        th,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    marks = []

    for c in contours:

        x,y,w,h = cv2.boundingRect(c)

        #aspect = w / (h + 1e-5)
        area = w*h

        if (
            x < w_img * 0.05 and   # 왼쪽 영역
            50 < area < 2000       # 적당한 영역
        ):
            marks.append((x,y,w,h))

    marks = sorted(marks, key=lambda m: m[1])

    answer_boxes = []
    extra_boxes = []
    sid_boxes = []

    for i,(mx,my,mw,mh) in enumerate(marks):

        row_center = my + mh//2

        if i < ANSWER_MARKS:
            bx = mx + mw + ANSWER_FIRST_OFFSET
            target = answer_boxes

        elif i < ANSWER_MARKS + EXTRA_MARKS:
            bx = mx + mw + SID_FIRST_OFFSET
            target = extra_boxes

        else:
            bx = mx + mw + SID_FIRST_OFFSET
            target = sid_boxes

        by = row_center - BUBBLE_SIZE // 2

        row_boxes = []

        while bx <= END:
            row_boxes.append((
                int(bx), int(by),
                BUBBLE_SIZE, BUBBLE_SIZE
            ))
            bx += STEP

        target.append(row_boxes)

    return marks, answer_boxes, extra_boxes, sid_boxes


def detect_marks(th, boxes):

    result = []

    for row in boxes:

        row_result = []

        for (x,y,w,h) in row:

            cell = th[y:y+h, x:x+w]
            ratio = np.sum(cell) / 255 / cell.size

            row_result.append(ratio if ratio > RATIO_THRESHOLD else 0)

        result.append(row_result)

    return result


##### 마킹 의미화 #####

def detect_sid(marks):

    sid = []

    for r in range(SID_MARKS-1, -1, -1):
        row = marks[r]

        candidates = [(i, v) for i, v in enumerate(row) if v > 0]
            
        if candidates:
            top = max(candidates, key=lambda x: x[1])
            sid.append(str(top[0]))

        else:
            sid.append('')

    return ''.join(sid)


def detect_extra(marks):

    points = []

    for r in range(EXTRA_MARKS):

        row = marks[r]

        candidates = [(i, v) for i, v in enumerate(row) if v > 0]

        if not candidates:
            points.append(0)
        else:
            # ratio 큰 순 정렬
            top = max(candidates, key=lambda x: x[1])
            points.append(top[0])

    return points[0]*0.1 + points[1] + points[2]*10


def detect_answers(marks):

    answers = []

    for r_start, r_end in [(5,10), (0,5)]:
        for c in range(30):

            col_values = []

            for r in range(r_start, r_end):
                if marks[r][c] > 0:
                    col_values.append(r - r_start)

            answers.append(col_values)
    #print('answers:', answers)

    return answers
