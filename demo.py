import os
import cv2

import pcn


def step_by_step(imgpath):
    img = cv2.imread(imgpath)
    winlist = pcn.detect(img)
    pcn.draw(img, winlist)
    cv2.imshow("Image", img)


def one_line_show(imgpath):
    pcn.show(imgpath)

def one_line_show_crop(imgpath):
    pcn.show(imgpath, is_crop=True)


if __name__ == '__main__':
    # usage settings
    import sys
    #if len(sys.argv) != 2:
        #print("Usage: python3 pcn.py path/to/img")
        #sys.exit()
    #else:
        #imgpath = sys.argv[1]
        
    imgpath = "D:\girl1.jpg"

    one_line_show(imgpath)
    one_line_show_crop(imgpath)
    step_by_step(imgpath)