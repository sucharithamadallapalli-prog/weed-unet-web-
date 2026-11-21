import os, uuid
import numpy as np
import cv2
from flask import current_app
from werkzeug.utils import secure_filename
from app.services.unet_service import predict_mask

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXT"]

def severity_for(pct):
    return "Low" if pct < 5 else "Moderate" if pct < 20 else "High"

def process_upload(file):
    """Save upload, run U-Net, write mask + overlay, return dict for Analysis."""
    cfg = current_app.config
    size, up = cfg["IMG_SIZE"], cfg["UPLOAD_DIR"]
    name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    orig_path = os.path.join(up, "originals", name)
    file.save(orig_path)

    bgr = cv2.imread(orig_path)
    if bgr is None:
        os.remove(orig_path)
        raise ValueError(f"Cannot read image: {file.filename}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    inp = cv2.resize(rgb, (size, size)).astype("float32") / 255.0
    prob = predict_mask(inp[None])[0]
    mask = (prob > cfg["THRESHOLD"]).astype("uint8")

    h, w = bgr.shape[:2]
    mask_full = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
    overlay = bgr.copy()
    overlay[mask_full == 1] = (0.5 * overlay[mask_full == 1] + 0.5 * np.array([0, 0, 255])).astype("uint8")

    stem = os.path.splitext(name)[0] + ".png"
    cv2.imwrite(os.path.join(up, "masks", stem), mask_full * 255)
    cv2.imwrite(os.path.join(up, "results", stem), overlay)
    pct = float(mask.mean() * 100)
    return dict(original=name, mask=stem, overlay=stem, weed_percent=round(pct, 2), severity=severity_for(pct))
