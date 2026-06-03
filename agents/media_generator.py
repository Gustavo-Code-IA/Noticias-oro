from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import os

def create_video(image_paths, audio_path, out_path='media/output.mp4', duration_per_image=4):
    clips = []
    for img in image_paths:
        clip = ImageClip(img).set_duration(duration_per_image)
        clips.append(clip)
    video = concatenate_videoclips(clips, method='compose')
    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    video.write_videofile(out_path, fps=24)

if __name__ == '__main__':
    print('media_generator ready')
