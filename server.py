from fastapi import FastAPI, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from io import BytesIO
from main import redact_image, redact_video
import ocr_detect, barcode_detect, pii_detect
import tempfile, os

app = FastAPI(title="RedactedByte API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def warmup():
    ocr_detect.get_ocr()
    barcode_detect.get_detector()
    pii_detect.get_model()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/redact/")  # allow trailing slash too
@app.post("/redact")
async def redact(
    file: UploadFile = File(...),
    blur_ksize: int = Query(101, ge=1),
    blur_sigma: float = Query(0.0),
    merge_dist: int = Query(20, ge=0),
    meta: bool = Query(False, description="Return JSON metadata instead of an image"),
):
    data = await file.read()
    npbuf = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(npbuf, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse({"error": "Invalid image"}, status_code=400)

    out_img, info = redact_image(img, blur_ksize=blur_ksize, blur_sigma=blur_sigma, merge_dist=merge_dist)

    if meta:
        h, w = out_img.shape[:2]
        info.update({"width": int(w), "height": int(h)})
        return JSONResponse(info)

    ok, enc = cv2.imencode(".png", out_img)
    if not ok:
        return JSONResponse({"error": "Failed to encode image"}, status_code=500)
    return StreamingResponse(BytesIO(enc.tobytes()), media_type="image/png")

@app.post("/redact-video/")  # allow trailing slash too
@app.post("/redact-video")
async def redact_video_api(
    file: UploadFile = File(...),
    yolo_model: str = Query("model.pt"),
    effect: str = Query("blur"),          # "blur" | "pixelate" | "black" (see video_obj.apply_effect)
    blur_k: int = Query(51, ge=1),
    vid_stride: int = Query(1, ge=1),
    return_meta: bool = Query(False),
    background_tasks: BackgroundTasks = None,
):
    # Save upload to a temp file
    suffix = os.path.splitext(file.filename or ".mp4")[1] or ".mp4"
    in_fd, in_path = tempfile.mkstemp(suffix=suffix)
    out_fd, out_path = tempfile.mkstemp(suffix=".mp4")
    os.close(in_fd); os.close(out_fd)
    try:
        with open(in_path, "wb") as f:
            f.write(await file.read())

        meta = redact_video(
            src_path=in_path,
            out_path=out_path,
            yolo_model=yolo_model,
            effect=effect,
            blur_k=blur_k,
            vid_stride=vid_stride,
        )

        if return_meta:
            # Serve metadata and keep file path for reference
            return JSONResponse(meta)

        # Stream the produced MP4 and clean up afterward
        if background_tasks is not None:
            background_tasks.add_task(lambda: (os.remove(in_path), os.remove(out_path)))
        return FileResponse(
            out_path,
            media_type="video/mp4",
            filename=os.path.basename(file.filename or "redacted.mp4"),
            background=background_tasks,
        )
    except Exception as e:
        # Cleanup on error
        try:
            os.remove(in_path)
        except Exception:
            pass
        try:
            os.remove(out_path)
        except Exception:
            pass
        return JSONResponse({"error": str(e)}, status_code=500)