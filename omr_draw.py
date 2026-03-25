import os
import cv2

def draw_debug(img, timing_marks, boxes, marks, out_name="omr_debug.png"):

    debug = img.copy()

    # timing mark
    for i,(mx,my,mw,mh) in enumerate(timing_marks):

        cv2.rectangle(
            debug,
            (mx,my),
            (mx+mw,my+mh),
            (0,255,0),
            1
        )

    # answers
    for row_boxes, row_marks in zip(boxes, marks):
        for (bx, by, bw, bh), r in zip(row_boxes, row_marks):

            color = (0,0,255) if r > 0 else (255,0,0)

            cv2.rectangle(
                debug,
                (bx, by),
                (bx+bw, by+bh),
                color,
                1
            )

    dir_path = os.path.dirname(out_name)

    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    result, encoded = cv2.imencode('.png', debug)

    if result:
        encoded.tofile(out_name)
        #print("디버그 이미지 저장:", out_name)
    else:
        print("디버그 이미지 저장 실패:", out_name)
    
    return;

'''
    for i,(bx,by,bw,bh) in enumerate(boxes):

        # answer box 표시
        cv2.rectangle(
            debug,
            (bx,by),
            (bx+bw,by+bh),
            (0,255,0),
            1
        )
            
    cv2.imwrite(out_name, debug)
    
    return
'''
