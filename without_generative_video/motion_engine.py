# motion_engine.py

import os
import cv2
import numpy as np


def ease_in_out(t):
    return 3*t**2 - 2*t**3


def render_kenburns_clip(
    image_path,
    output_path,
    duration_seconds=2,
    fps=30,
    zoom_start=1.0,
    zoom_end=1.08
):
    img = cv2.imread(image_path)

    if img is None:
        raise RuntimeError(f"Could not load image: {image_path}")

    h, w, _ = img.shape

    target_w = 1080
    target_h = 1920

    # Resize to fill 9:16
    scale = max(target_w / w, target_h / h)
    resized = cv2.resize(img, (int(w * scale), int(h * scale)))

    rh, rw, _ = resized.shape

    total_frames = int(duration_seconds * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    for frame_idx in range(total_frames):
        t = frame_idx / (total_frames - 1)
        eased = ease_in_out(t)

        zoom = zoom_start + (zoom_end - zoom_start) * eased

        crop_w = int(target_w / zoom)
        crop_h = int(target_h / zoom)

        x = int((rw - crop_w) / 2)
        y = int((rh - crop_h) / 2)

        cropped = resized[y:y+crop_h, x:x+crop_w]
        frame = cv2.resize(cropped, (target_w, target_h))

        out.write(frame)

    out.release()
