from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, TextClip, CompositeVideoClip
import os
from typing import List


def create_video(image_paths: List[str], audio_path: str, out_path: str = 'media/videos/output.mp4', duration_per_image: int = 4, title: str = '') -> str:
    """Genera un video a partir de imágenes y un audio.

    Añade un título como texto superpuesto en la primera imagen.
    Devuelve la ruta del archivo generado.
    """
    clips = []
    for idx, img in enumerate(image_paths):
        clip = ImageClip(img).set_duration(duration_per_image).resize(width=1280)
        # añadir texto en la primera imagen
        if idx == 0 and title:
            txt = TextClip(title, fontsize=48, color='white', bg_color='black').set_duration(3).set_position(('center', 'bottom'))
            comp = CompositeVideoClip([clip, txt.set_start(0)])
            clips.append(comp)
        else:
            clips.append(clip)

    if not clips:
        raise ValueError('No image clips to build video')

    video = concatenate_videoclips(clips, method='compose')
    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    video.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac')
    return out_path


def generate_media_for_text(title: str, text: str, images: List[str], out_path: str, tts_func) -> str:
    """Helper que sintetiza audio con `tts_func`(text)->audio_path y llama a create_video."""
    audio_path = tts_func(f"{title}. {text}", out_path='media/audio/tmp.wav')
    return create_video(images, audio_path, out_path=out_path, title=title)


if __name__ == '__main__':
    print('media_generator ready')
