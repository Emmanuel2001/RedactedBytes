import cv2
import zxingcpp
import numpy as np
from functools import lru_cache


@lru_cache(maxsize=1)
def get_detector():
    # Replace with your actual construction if different
    return cv2.QRCodeDetector()


def predict(img: np.ndarray):
    det = get_detector()
    results = zxingcpp.read_barcodes(img)

    pt_array = []

    for barcode in results:
        pts = np.array([
            [barcode.position.top_left.x, barcode.position.top_left.y],
            [barcode.position.top_right.x, barcode.position.top_right.y],
            [barcode.position.bottom_right.x, barcode.position.bottom_right.y],
            [barcode.position.bottom_left.x, barcode.position.bottom_left.y]
        ], dtype=np.int32)

        pt_array.append(pts)

    if pt_array:
        all_pts = np.stack(pt_array)
    else:
        all_pts = np.empty((0, 4, 2), dtype=np.int32)
    return all_pts
