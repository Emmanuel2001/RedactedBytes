import torch
import cv2
import numpy as np
from ultralytics import YOLOE


# --- effect helpers ---
def apply_effect(frame, mask, effect="blur", k=201):
    """Apply an effect only where mask==255. k must be odd for Gaussian blur."""
    mask = cv2.dilate(mask, np.ones((7,7), np.uint8), 1)  # reduce leakage
    if effect == "blur":
        mod = cv2.GaussianBlur(frame, (k, k), 0)
    elif effect == "pixelate":
        h, w = frame.shape[:2]
        small = cv2.resize(frame, (max(1, w//24), max(1, h//24)), interpolation=cv2.INTER_LINEAR)
        mod = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
    else:  # black box
        mod = np.zeros_like(frame)
    out = frame.copy()
    out[mask > 0] = mod[mask > 0]
    return out

def build_mask_from_results(r, shape_hw):
    """Return a single 8-bit mask (255 where anything should be redacted)."""
    H, W = shape_hw
    m = np.zeros((H, W), np.uint8)

    # Prefer segmentation polygons if present
    if getattr(r, "masks", None) is not None and getattr(r.masks, "xy", None) is not None:
        for poly in r.masks.xy:                      # list of Nx2 arrays in image coords
            pts = poly.astype(np.int32)
            cv2.fillPoly(m, [pts], 255)

    # Fallback to boxes if no masks
    elif getattr(r, "boxes", None) is not None and getattr(r.boxes, "xyxy", None) is not None:
        for x1, y1, x2, y2 in r.boxes.xyxy.cpu().numpy().astype(int):
            x1 = max(0, x1); y1 = max(0, y1); x2 = min(W-1, x2); y2 = min(H-1, y2)
            if x2 > x1 and y2 > y1:
                m[y1:y2, x1:x2] = 255
    return m

def main():
    SRC = "video.mp4"
    OUT = "output_blurred1.mp4"

    # If your ONNX is segmentation, set task="segment"; else "detect"
    model = YOLOE("model.pt", task="segment")
    DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
    # --- prepare IO ---
    cap = cv2.VideoCapture(SRC)
    assert cap.isOpened(), f"cannot open {SRC}"
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    W  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    writer = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

    # --- stream inference without saving intermediate artifacts ---
    for r in model.predict(
            source=SRC,
            stream=True,          # prevents RAM accumulation
            device=DEVICE,
            imgsz=640,
            save=False,           # we write our own video only
            save_txt=False,
            save_crop=False,
            retina_masks=False,   # speed boost for segmentation
            verbose=False,
            vid_stride=1          # >1 to skip frames if you need more speed
        ):
        # r.orig_img is the original frame; r.plot() draws boxes/masks
        frame = r.orig_img.copy()

        # Build a combined mask and apply blur
        mask = build_mask_from_results(r, (frame.shape[0], frame.shape[1]))
        if mask.any():
            frame = apply_effect(frame, mask, effect="blur", k=201)  # or "pixelate" / "black"

        writer.write(frame)

    writer.release()
    print(f"Saved blurred video to: {OUT}")

if __name__ == "__main__":
    main()