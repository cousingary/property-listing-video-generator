# video_engine.py

import os
from motion_engine import render_kenburns_clip


def generate_micro_clips(
    property_cfg,
    assets,
    workdir,
    clip_duration=2
):
    clips = []

    for idx, asset_path in enumerate(assets):
        clip_path = os.path.join(workdir, f"clip_{idx:02d}.mp4")

        try:
            render_kenburns_clip(
                image_path=asset_path,
                output_path=clip_path,
                duration_seconds=clip_duration
            )
            clips.append(clip_path)

        except Exception as e:
            print(f"[WARN] Skipping asset {asset_path}: {e}")

    if not clips:
        raise RuntimeError("No clips generated.")

    return clips
