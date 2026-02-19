# video_merge.py

from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip


def merge_video_audio(clips, audio_path, output_path):
    video_clips = [VideoFileClip(c) for c in clips]
    final_video = concatenate_videoclips(video_clips, method="compose")

    audio = AudioFileClip(audio_path)
    final_video = final_video.set_audio(audio)

    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30
    )

    return output_path
