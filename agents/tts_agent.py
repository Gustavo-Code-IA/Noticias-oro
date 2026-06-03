import os

def synthesize_text(text: str, out_path='media/audio.wav') -> str:
    """Placeholder TTS: integrate provider SDK later."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # For now create a silent placeholder using pydub if available
    try:
        from pydub import AudioSegment
        # create 1 second silence as placeholder, real TTS should replace this
        silent = AudioSegment.silent(duration=1000)
        silent.export(out_path, format='wav')
    except Exception:
        with open(out_path, 'wb') as f:
            f.write(b'')
    return out_path

if __name__ == '__main__':
    synthesize_text('Prueba de síntesis')
