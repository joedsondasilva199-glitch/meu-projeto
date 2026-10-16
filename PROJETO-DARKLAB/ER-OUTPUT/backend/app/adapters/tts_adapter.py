import os
import wave
import struct
import math
from typing import Dict, Any

class BaseTTSAdapter:
    def synthesize_speech(self, text: str, voice_name: str, output_path: str) -> Dict[str, Any]:
        raise NotImplementedError

class MockTTSAdapter(BaseTTSAdapter):
    """Gera arquivos de áudio WAV válidos sintéticos com tom dramático para teste real de reprodução."""

    def synthesize_speech(self, text: str, voice_name: str, output_path: str) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        char_count = len(text)
        # Aproximação de fala realista: ~15 caracteres por segundo
        duration = max(2.0, round(char_count / 15.0, 1))

        # Parâmetros de áudio: 44.1kHz, 16-bit mono
        sample_rate = 44100
        num_samples = int(sample_rate * min(duration, 5.0)) # Gera 5s no arquivo de demonstração para economizar espaço
        frequency = 180.0 # Tom grave e misterioso (narrador dark)

        with wave.open(output_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            # Gera onda senoidal modulada suave
            frames = bytearray()
            for i in range(num_samples):
                t = float(i) / sample_rate
                # Modulação de amplitude para simular pausas de fala humana
                envelope = 0.5 * (1.0 + math.sin(2.0 * math.pi * 1.5 * t))
                sample_val = int(32767.0 * 0.3 * envelope * math.sin(2.0 * math.pi * frequency * t))
                frames.extend(struct.pack("<h", sample_val))

            wav_file.writeframes(frames)

        return {
            "characters_count": char_count,
            "tokens_debited": char_count, # 1 token = 1 caractere
            "duration_seconds": duration,
            "audio_path": output_path
        }
