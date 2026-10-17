#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE DE MODELO DE VOZ NEURAL (XTTS-v2): HISTÓRIA DRAMÁTICA DE 20 SEGUNDOS
Gera áudio com clonagem vocal, entonação cinematográfica e cadência de 20s em PT-BR
================================================================================
"""

import os
import sys
import time
import wave
import subprocess

for s in [sys.stdout, sys.stderr]:
    if hasattr(s, 'reconfigure'):
        s.reconfigure(encoding='utf-8', errors='replace')

# 1. Instalação e importação do Coqui TTS
print("=" * 70)
print("🎙️ INICIANDO TESTE DO MODELO DE VOZ NEURAL (XTTS-v2)")
print("🎯 Narrativa: História Dramática de 20 Segundos em Português do Brasil")
print("=" * 70)

try:
    from TTS.api import TTS
except ImportError:
    print("⏳ Instalando biblioteca Coqui TTS...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "TTS", "soundfile"], check=True)
    from TTS.api import TTS

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"⚡ Dispositivo de Inferência: {device.upper()}")
if torch.cuda.is_available():
    print(f"   🔹 GPU: {torch.cuda.get_device_name(0)} (VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB)")

# 2. Localização do Modelo XTTS-v2
DATASET_XTTS = "/kaggle/input/kaggles-32gb-models/xtts"
GDRIVE_XTTS = "G:/Meu Drive/Kaggles/Modelos/xtts"
CACHE_DIR = "/tmp/tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

model_source = None
if os.path.exists(DATASET_XTTS) and os.path.exists(os.path.join(DATASET_XTTS, "config.json")):
    model_source = DATASET_XTTS
    print(f"📦 Usando pesos montados do Dataset Kaggle: {DATASET_XTTS}")
elif os.path.exists(GDRIVE_XTTS) and os.path.exists(os.path.join(GDRIVE_XTTS, "config.json")):
    model_source = GDRIVE_XTTS
    print(f"📦 Usando pesos do Google Drive: {GDRIVE_XTTS}")

t0 = time.time()
print("⏳ Carregando XTTS-v2 na VRAM...")
if model_source:
    tts = TTS(
        model_path=model_source,
        config_path=os.path.join(model_source, "config.json")
    ).to(device)
else:
    print("🌐 Carregando modelo oficial multilingue XTTS-v2...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

print(f"✅ Modelo XTTS-v2 Carregado com Sucesso em {round(time.time() - t0, 1)}s!")

# 3. Referência Vocal para Clonagem Emocional
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
candidates_ref = [
    os.path.join(BASE_DIR, "assets", "speaker_reference_dramatico.wav"),
    os.path.join(BASE_DIR, "Referencias", "vozes", "audio_1_p1.wav"),
    "/tmp/meu-projeto/assets/speaker_reference_dramatico.wav",
    "/tmp/meu-projeto/Referencias/vozes/audio_1_p1.wav",
    "assets/speaker_reference_dramatico.wav",
    "Referencias/vozes/audio_1_p1.wav"
]

ref_audio = None
for c in candidates_ref:
    if os.path.exists(c):
        ref_audio = os.path.abspath(c)
        break

print(f"🎭 Âncora de Voz (Clonagem): {ref_audio if ref_audio else 'Voz nativa do modelo'}")

# 4. Roteiro Narrativo Calibrado para ~20 Segundos
# 50 palavras com pausas expressivas geram exatamente 19s a 22s de áudio
historia_20s = (
    "Na escuridão daquela noite sem estrelas, uma presença invisível despertou no coração da cidade. "
    "Marcos sabia que o segredo não poderia mais ser escondido. "
    "Quando a porta se abriu lentamente, ele olhou nos olhos de Helena e compreendeu: "
    "o destino de todos nós estava prestes a mudar para sempre."
)

OUTPUT_DIR = "/kaggle/working" if os.path.exists("/kaggle") else os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_wav = os.path.join(OUTPUT_DIR, "historia_voz_20s.wav")

print("\n" + "=" * 70)
print("📖 TEXTO DA HISTÓRIA (CADÊNCIA DE 20 SEGUNDOS):")
print(f'"{historia_20s}"')
print("=" * 70)

print("\n🎙️ Sintetizando locução neural cinematográfica em Português (PT-BR)...")
t_synth = time.time()

if ref_audio and os.path.exists(ref_audio):
    tts.tts_to_file(
        text=historia_20s,
        speaker_wav=ref_audio,
        language="pt",
        file_path=output_wav,
        temperature=0.72,
        repetition_penalty=2.0
    )
else:
    speaker_name = tts.speakers[0] if hasattr(tts, 'speakers') and tts.speakers else None
    tts.tts_to_file(
        text=historia_20s,
        speaker=speaker_name,
        language="pt",
        file_path=output_wav
    )

tempo_inferencia = round(time.time() - t_synth, 2)
print(f"✅ Síntese neural concluída em {tempo_inferencia}s!")

# 5. Medição Exata de Duração do Áudio Gerado
duracao_segundos = 0.0
with wave.open(output_wav, "rb") as wf:
    frames = wf.getnframes()
    rate = wf.getframerate()
    duracao_segundos = round(frames / float(rate), 2)

tamanho_mb = round(os.path.getsize(output_wav) / (1024 * 1024), 2)

print("\n" + "=" * 70)
print("📊 RESULTADO DO TESTE DE VOZ XTTS-v2:")
print(f"📁 Arquivo: {output_wav}")
print(f"⏱️ Duração do Áudio: {duracao_segundos} segundos (Meta: ~20s)")
print(f"💾 Tamanho do Arquivo: {tamanho_mb} MB")
print(f"⚡ Tempo de Processamento: {tempo_inferencia}s na GPU")
print("=" * 70)

# 6. Player de Áudio Inline para Jupyter / Kaggle
try:
    from IPython.display import Audio, display
    print("\n▶️ Reproduza a história diretamente abaixo:")
    display(Audio(output_wav, autoplay=False))
except Exception:
    pass
