#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 2: XTTS-v2 - LOCUÇÃO NEURAL COM EMOÇÃO E CLONAGEM DE VOZ
Testa o modelo XTTS-v2 gerando fala em Português com dinâmica emocional real.
================================================================================
"""

import os
import sys
import time
import wave
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test():
    print("=" * 65)
    print("🧪 INICIANDO TESTE 2: XTTS-v2 COM EMOÇÃO PERFEITA")
    print("🎯 Objetivo: Voz Neural Realista em PT-BR com Dinâmica Emocional")
    print("=" * 65)

    VRAMManager.audit("Pré-Carregamento XTTS-v2")
    model_path = find_model_path("xtts")
    print(f"📦 Caminho do Modelo: {model_path}")

    # Localiza o arquivo de referência vocal dramática
    possible_refs = [
        "assets/speaker_reference_dramatico.wav",
        "../assets/speaker_reference_dramatico.wav",
        "/kaggle/working/meu-projeto/assets/speaker_reference_dramatico.wav",
        "D:/Kaggles/assets/speaker_reference_dramatico.wav",
        "G:/Meu Drive/Kaggles/assets/speaker_reference_dramatico.wav"
    ]
    ref_audio = None
    for r in possible_refs:
        if os.path.exists(r):
            ref_audio = os.path.abspath(r)
            break

    print(f"🎙️ Âncora de Emoção (Speaker Reference): {ref_audio if ref_audio else 'Usando voz nativa'}")

    try:
        from TTS.api import TTS
    except ImportError:
        print("⚠️ Instalando biblioteca TTS oficial (Coqui)...")
        os.system(f"{sys.executable} -m pip install -q --no-warn-script-location TTS")
        from TTS.api import TTS

    start_load = time.time()
    print("⏳ Carregando Modelo XTTS-v2 na GPU...")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Carrega via diretório local se config.json existir, senão via identifier
    if os.path.isdir(model_path) and os.path.exists(os.path.join(model_path, "config.json")):
        tts = TTS(
            model_path=model_path,
            config_path=os.path.join(model_path, "config.json")
        ).to(device)
    else:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    load_time = round(time.time() - start_load, 2)
    print(f"✅ XTTS-v2 Carregado em {load_time}s!")
    VRAMManager.audit("XTTS-v2 em VRAM")

    # Texto dramático com marcações de pausa e entonação para expressar emoção real
    emotional_script = (
        "Nas profundezas do silêncio... algo começou a se mover. "
        "Não eram simples códigos de máquina! Era uma nova consciência... que acaba de acordar."
    )

    out_wav = os.path.join(OUTPUT_DIR, "test_2_voz_emocao.wav")
    print("\n🎭 Sintetizando Narração com Carga Emocional em Português...")
    print(f"Texto: \"{emotional_script}\"")
    start_infer = time.time()

    if ref_audio and os.path.exists(ref_audio):
        tts.tts_to_file(
            text=emotional_script,
            speaker_wav=ref_audio,
            language="pt",
            file_path=out_wav,
            temperature=0.75,
            repetition_penalty=2.0
        )
    else:
        # Usa um dos speakers disponíveis no modelo
        speaker_name = tts.speakers[0] if hasattr(tts, 'speakers') and tts.speakers else None
        tts.tts_to_file(
            text=emotional_script,
            speaker=speaker_name,
            language="pt",
            file_path=out_wav
        )

    infer_time = round(time.time() - start_infer, 2)
    print(f"✅ Áudio Sintetizado com Sucesso em {infer_time}s!")

    # Verificação de integridade do áudio
    if os.path.exists(out_wav):
        with wave.open(out_wav, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = round(frames / float(rate), 2)
            channels = wf.getnchannels()
            print(f"📊 Métricas do Áudio: Duração: {duration}s | Amostragem: {rate}Hz | Canais: {channels} | Tamanho: {os.path.getsize(out_wav)} bytes")
        print(f"💾 Evidência salva em: {out_wav}")
    else:
        raise RuntimeError("Arquivo de áudio não foi gerado!")

    # Liberação de memória
    print("\n🧹 Descarregando modelo XTTS-v2 da VRAM...")
    del tts
    VRAMManager.purge()
    print("🎉 TESTE 2 (XTTS-v2 COM EMOÇÃO) FINALIZADO COM SUCESSO!\n")
    return out_wav

if __name__ == "__main__":
    run_test()
