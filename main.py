import os
import sys
import argparse
import cv2
import torch
import numpy as np
import ocr_detect
import pii_detect
import barcode_detect
import object_detect
import video_object_detect
from ultralytics import YOLOE
from functools import lru_cache

def get_torch_device():
    if torch.cuda.is_available():
        # e.g., 'cuda:0' for first GPU
        return "cuda:0"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

@lru_cache(maxsize=1)
def _get_yolo_video(model_path: str = "model.pt"):
    # Lazy load; used only for video processing
    from ultralytics import YOLO
    return YOLOE(model_path, task="segment")

def redact_video(
    src_path: str,
    out_path: str,
    yolo_model: str = "model.pt",
    effect: str = "blur",
    blur_k: int = 201,
    vid_stride: int = 1,
) -> dict:
    """
    Process a video using the segmentation/detection model and redact per-frame.
    Uses video_obj.build_mask_from_results and video_obj.apply_effect.
    Returns metadata dict.
    """
    cap = cv2.VideoCapture(src_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {src_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    model = _get_yolo_video(yolo_model)
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    DEVICE = get_torch_device()

    frames_in, frames_out = 0, 0
    for r in model.predict(
        source=src_path,
        stream=True,
        device=DEVICE,
        imgsz=640,
        save=False,
        save_txt=False,
        save_crop=False,
        retina_masks=False,
        verbose=False,
        vid_stride=max(1, int(vid_stride)),
    ):
        frames_in += 1
        frame = r.orig_img.copy()
        mask = video_object_detect.build_mask_from_results(r, (frame.shape[0], frame.shape[1]))
        if mask.any():
            frame = video_object_detect.apply_effect(frame, mask, effect=effect, k=blur_k)
        writer.write(frame)
        frames_out += 1

    writer.release()
    return {
        "width": W,
        "height": H,
        "fps": float(fps),
        "frames_in": frames_in,
        "frames_out": frames_out,
        "output": out_path,
        "effect": effect,
        "model": yolo_model,
    }


def redact_image(img: np.ndarray,
                 blur_ksize: int = 201,
                 blur_sigma: float = 0.0,
                 merge_dist: int = 12,
                 pipeline: str = "all",
                 yoloe_model: str = "model.pt"):
    """
    Pipelines:
      - 'ocr'   : OCR + PII + barcodes
      - 'object': Object segmentation/detection only
      - 'all'   : union of OCR+PII+barcodes and objects
    """
    if img is None:
        raise ValueError("img is None")

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    redacted_items, barcode_items, object_items = [], [], []

    if pipeline in ("ocr", "all"):
        rec_texts, rec_polys = ocr_detect.predict(img, merge_dist=merge_dist)
        for text, box in zip(rec_texts, rec_polys):
            redacted_text = pii_detect.predict(text)
            if redacted_text != text:
                pts = np.asarray(box, dtype=np.int32).reshape(-1, 1, 2)
                cv2.fillPoly(mask, [pts], 255)
                redacted_items.append({"type": "text", "text": text, "poly": np.asarray(box).reshape(-1, 2).tolist()})
        # barcodes
        barcode_boxes = barcode_detect.predict(img)
        for pts in barcode_boxes:
            cv2.fillPoly(mask, [pts.reshape(-1, 1, 2)], 255)
            barcode_items.append({"type": "barcode", "poly": pts.reshape(-1, 2).tolist()})

    if pipeline in ("object", "all"):
        try:
            obj_polys = object_detect.predict(img, model_path=yoloe_model)
            for poly in obj_polys:
                cv2.fillPoly(mask, [poly.reshape(-1, 1, 2)], 255)
                object_items.append({"type": "object", "poly": poly.reshape(-1, 2).tolist()})
        except Exception as e:
            print(f"[object_detect] skipped: {e}")

    # apply Gaussian blur only inside masked regions
    out = img.copy()
    if np.any(mask):
        ks = blur_ksize if blur_ksize % 2 == 1 else blur_ksize + 1
        blurred = cv2.GaussianBlur(out, (ks, ks), blur_sigma)
        out[mask == 255] = blurred[mask == 255]

    meta = {
        "pipeline": pipeline,
        "mask_applied": bool(np.any(mask)),
        "redactions": redacted_items,
        "barcodes": barcode_items,
        "objects": object_items,
    }
    return out, meta

def main():
    parser = argparse.ArgumentParser(description="Redact PII from images")
    parser.add_argument("--input", "-i", default="images/in/license.jpeg", help="Path to input image")
    parser.add_argument("--outdir", "-o", default="output", help="Directory to save outputs")
    parser.add_argument("--pipeline", choices=["ocr", "object", "all"], default="ocr", help="Which pipeline to run")
    parser.add_argument("--yoloe-model", default="model.onnx", help="Path to YOLOE ONNX model")
    parser.add_argument("--blur-ksize", type=int, default=101, help="Odd kernel size; larger = stronger blur")
    parser.add_argument("--blur-sigma", type=float, default=0.0, help="Sigma; 0 lets OpenCV choose from ksize")
    parser.add_argument("--merge-dist", type=int, default=12, help="Merge boxes within this pixel distance (0 disables)")
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        sys.exit(1)

    # set up paths and create output dir
    image_path = args.input
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to read image: {image_path}")
        sys.exit(1)

    out_img, meta = redact_image(
        img,
        blur_ksize=args.blur_ksize,
        blur_sigma=args.blur_sigma,
        merge_dist=args.merge_dist,
        pipeline=args.pipeline,
        yoloe_model=args.yoloe_model,
    )

    # save output
    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_image_path = os.path.join(outdir, f"{base}_redacted.png")
    cv2.imwrite(out_image_path, out_img)
    print(f"Saved redacted image: {out_image_path}")
    

if __name__ == "__main__":
    main()