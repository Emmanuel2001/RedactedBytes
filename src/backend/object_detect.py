from functools import lru_cache
import numpy as np
import cv2

@lru_cache(maxsize=None)
def _load_yoloe(model_path: str = "model.onnx"):
    # Local import so this module is optional unless the pipeline is used
    try:
        from ultralytics import YOLOE
    except Exception as e:
        raise RuntimeError("Ultralytics/YOLOE is required for the object pipeline") from e
    return YOLOE(model_path, task="segment")

def predict(img: np.ndarray, model_path: str = "model.onnx"):
    """
    Runs YOLOE segmentation/detection and returns a list of polygons (np.ndarray Nx2, int32).
    If only boxes are available, returns 4-point rectangles.
    """
    model = _load_yoloe(model_path)
    results = model.predict(img, save=False, verbose=False)
    res = results[0]

    polys = []
    # Segmentation polygons
    if getattr(res, "masks", None) is not None and res.masks is not None:
        for poly in res.masks.xy:
            poly = np.asarray(poly, dtype=np.int32)
            polys.append(poly)
    # Fallback to boxes
    elif getattr(res, "boxes", None) is not None and res.boxes is not None:
        for x1, y1, x2, y2 in res.boxes.xyxy.cpu().numpy().astype(int):
            polys.append(np.array(
                [[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.int32
            ))
    return polys