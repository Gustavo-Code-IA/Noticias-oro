import os

def synthesize_text(text: str, out_path='media/audio.wav') -> str:
    """Placeholder TTS: integrate provider SDK later."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # For now create a silent placeholder using pydub if available
    try:
        from pydub import AudioSegment
        # create 1 second silence as placeholder, real TTS should replace this
        silent = AudioSegment.silent(duration=1000)
        import os
        import requests
        from typing import Optional


        def _pitch_shift_wav(path: str, semitones: float) -> str:
            """Shift pitch by semitones using pydub (no external heavy deps).

            Returns path to the new file (overwrites original if needed).
            """
            try:
                from pydub import AudioSegment
                sound = AudioSegment.from_file(path)
                new_sample_rate = int(sound.frame_rate * (2.0 ** (semitones / 12.0)))
                pitched = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
                pitched = pitched.set_frame_rate(sound.frame_rate)
                out_path = path
                pitched.export(out_path, format='wav')
                return out_path
            except Exception:
                return path


        def synthesize_text(text: str, out_path: str = 'media/audio.wav') -> str:
            """Synthesize `text` to `out_path` using ElevenLabs if configured.

            Env vars:
            - `ELEVENLABS_API_KEY` required to use ElevenLabs REST API.
            - `ELEVEN_VOICE_ID` optional: voice id from ElevenLabs dashboard. If not set,
               attempts to use SDK when available.
            - `ELEVEN_PITCH_SEMITONES` optional: number of semitones to raise pitch (float).

            Falls back to a 1s silent WAV if TTS fails or not configured.
            """
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            key = os.getenv('ELEVENLABS_API_KEY')
            voice_id = os.getenv('ELEVEN_VOICE_ID')
            pitch = float(os.getenv('ELEVEN_PITCH_SEMITONES', '2'))

            if key:
                # Prefer REST API (works without SDK)
                if voice_id:
                    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
                    headers = {
                        'Accept': 'audio/wav',
                        'Content-Type': 'application/json',
                        'xi-api-key': key,
                    }
                    payload = {
                        'text': text,
                        'voice_settings': {'stability': 0.4, 'similarity_boost': 0.6}
                    }
                    try:
                        r = requests.post(url, json=payload, headers=headers, timeout=30)
                        if r.status_code == 200:
                            with open(out_path, 'wb') as f:
                                f.write(r.content)
                            # apply pitch if requested
                            if pitch and pitch != 0:
                                _pitch_shift_wav(out_path, pitch)
                            return out_path
                        else:
                            # try SDK fallback below
                            pass
                    except Exception:
                        pass

                # Try SDK if REST failed or no voice_id provided
                try:
                    from elevenlabs import set_api_key, generate, save
                    set_api_key(key)
                    voice = os.getenv('ELEVEN_VOICE', 'alloy')
                    model = os.getenv('ELEVEN_MODEL', 'eleven_multilingual_v1')
                    audio = generate(text=text, voice=voice, model=model)
                    # `save` will write the file
                    save(audio, out_path)
                    if pitch and pitch != 0:
                        _pitch_shift_wav(out_path, pitch)
                    return out_path
                except Exception:
                    pass

            # Fallback: placeholder silent wav
            try:
                from pydub import AudioSegment
                silent = AudioSegment.silent(duration=1000)
                silent.export(out_path, format='wav')
            except Exception:
                with open(out_path, 'wb') as f:
                    f.write(b'')
            return out_path
