from functools import lru_cache
import cv2
import numpy as np
from paddleocr import PaddleOCR

@lru_cache(maxsize=1)
def get_ocr():
    return PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        text_det_limit_type="max",
        text_det_limit_side_len=1024,
    )

def predict(img: np.ndarray, merge_dist: int = 12):
    ocr = get_ocr()  # reused, not rebuilt per call
    result = ocr.predict(img)[0]
    rec_texts = result["rec_texts"]
    rec_polys = result["rec_polys"]
    rec_texts, rec_polys = merge_boxes_and_texts(rec_polys, rec_texts, merge_dist)
    return rec_texts, rec_polys

def merge_boxes_and_texts(rec_polys, rec_texts, merge_dist):
    """
    Merge nearby OCR boxes and concatenate their texts based on a pixel distance.
    Returns (merged_texts, merged_polys).
    """
    if not rec_polys or not rec_texts or merge_dist is None or merge_dist <= 0:
        return rec_texts, rec_polys

    n = len(rec_polys)
    if n == 0:
        return [], []

    # Build bounding rects (x1,y1,x2,y2) for each polygon
    rects = []
    polys_pts = []
    for p in rec_polys:
        pts = np.asarray(p, dtype=np.int32).reshape(-1, 2)
        polys_pts.append(pts)
        x, y, w, h = cv2.boundingRect(pts)
        rects.append((x, y, x + w, y + h))

    # Disjoint-set union (union-find) to group close rects
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Expand rects by merge_dist and intersect to decide merging
    d = merge_dist
    def expanded(r):
        return (r[0] - d, r[1] - d, r[2] + d, r[3] + d)
    def intersects(r1, r2):
        return not (r1[2] < r2[0] or r2[2] < r1[0] or r1[3] < r2[1] or r2[3] < r1[1])

    for i in range(n):
        ri = expanded(rects[i])
        for j in range(i + 1, n):
            rj = expanded(rects[j])
            if intersects(ri, rj):
                union(i, j)

    # Collect components
    groups = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(i)

    merged_texts, merged_polys = [], []
    for idxs in groups.values():
        # Reading order: top-to-bottom, then left-to-right
        idxs_sorted = sorted(idxs, key=lambda k: (rects[k][1], rects[k][0]))
        merged_texts.append(" ".join(rec_texts[k] for k in idxs_sorted).strip())

        # Merge polygons via convex hull of all points in the group
        pts = np.vstack([polys_pts[k] for k in idxs])
        hull = cv2.convexHull(pts).reshape(-1, 2)
        merged_polys.append(hull.tolist())

    return merged_texts, merged_polys