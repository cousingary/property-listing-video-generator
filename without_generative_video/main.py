# main.py

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("service_account.json")
from config_loader import load_config
from drive_client import download_property_folder, upload_video
from tts_engine import generate_tts
from video_engine import generate_micro_clips


PROPERTY_DEFAULTS = {
    "voice": "Kore",
    "tts_speed_factor": 1.3,
    "prompt_style": "",
    "model_tts": "gemini-2.5-flash-tts",
}


def normalize_property_config(cfg: dict) -> dict:
    if not cfg.get("thai_text", "").strip():
        raise ValueError("thai_text is mandatory")

    for k, v in PROPERTY_DEFAULTS.items():
        cfg.setdefault(k, v)

    return cfg


def main():
    pipeline_cfg = load_config("pipeline_config.json")

    workdir = "workdir"
    os.makedirs(workdir, exist_ok=True)

    assets, property_cfg_path = download_property_folder(
        folder_id=pipeline_cfg["drive_input_folder"],
        output_dir=workdir
    )

    property_cfg = load_config(property_cfg_path)
    property_cfg = normalize_property_config(property_cfg)

    clips = generate_micro_clips(
        property_cfg,
        assets,
        workdir,
        clip_duration=pipeline_cfg.get("clip_duration", 3)
    )

    audio_path = generate_tts(
        text=property_cfg["thai_text"],
        voice=property_cfg["voice"],
        speed_factor=property_cfg["tts_speed_factor"],
        output_path=os.path.join(workdir, "voice.mp3"),
        model=property_cfg["model_tts"],
        prompt_style=property_cfg["prompt_style"],
        api_key=pipeline_cfg["gemini_api_key"],
    )


    final_video_path = os.path.join(workdir, "final.mp4")

    from video_merge import merge_video_audio
    merge_video_audio(clips, audio_path, final_video_path)

    upload_video(
        file_path=final_video_path,
        folder_id=pipeline_cfg["drive_output_folder"],
    )

    print("Pipeline complete.")


if __name__ == "__main__":
    main()
