import os
import cv2

def draw_debug(img, timing_marks, boxes, marks, dir_path='결과출력/test', sid='omr'):

    debug = img.copy()
    
    # 원본 이미지 저장
    dir_path = os.path.normpath(dir_path)

    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
        os.makedirs(dir_path+'_debug', exist_ok=True)

    out_name = os.path.join(dir_path, sid+'.jpg')

    source = cv2.rotate(debug, cv2.ROTATE_90_CLOCKWISE)

    source = cv2.resize(source, None, fx=0.5, fy=0.5)
    
    result, encoded = cv2.imencode('.jpg',source,
                                   [cv2.IMWRITE_JPEG_QUALITY, 50])

    if result:
        encoded.tofile(out_name)
    else:
        print("원본 이미지 저장 실패:", out_name)

    # 디버그 이미지 저장
    
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

            color = (255,0,0) if r > 0 else (0,255,0)

            cv2.rectangle(
                debug,
                (bx, by),
                (bx+bw, by+bh),
                color,
                1
            )

    out_name = os.path.join(dir_path+'_debug', sid+'.png')

    debug = cv2.rotate(debug, cv2.ROTATE_90_CLOCKWISE)

    result, encoded = cv2.imencode('.png', debug)

    if result:
        encoded.tofile(out_name)
    else:
        print("디버그 이미지 저장 실패:", out_name)
    
    return;
