import cv2
import numpy as np
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

class OCR:
    @staticmethod
    def clahe(img, clip_limit = 2.0, grid_size = (8,8)):
        clahe = cv2.createCLAHE(clipLimit = clip_limit, tileGridSize = grid_size)
        return clahe.apply(img)

    @staticmethod
    def getFilteredImage(imgPath):
        src = cv2.imread(imgPath)
        srcH, srcW = src.shape[:2]
        src = cv2.resize(src, (int(srcW * 1.5), int(srcH * 1.5)))

        # HSV thresholding to get rid of as much background as possible
        hsv = cv2.cvtColor(src.copy(), cv2.COLOR_BGR2HSV)
        lower_blue = np.array([0, 0, 180])
        upper_blue = np.array([180, 38, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        result = cv2.bitwise_and(src, src, mask = mask)
        b, g, r = cv2.split(result)
        g = OCR.clahe(g, 5, (5, 5))
        inverse = cv2.bitwise_not(g)

        return inverse

    @staticmethod
    def imageToStringArray(img):
        t = pytesseract.image_to_string(img, lang='eng', \
            config='--oem 3 --psm 12 poe')
        t = t.replace("\n\n", "\n")
        lines = t.split("\n")

        return lines
