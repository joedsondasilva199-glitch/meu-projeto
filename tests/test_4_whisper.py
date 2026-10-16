#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 4: WHISPER LARGE V3 TURBO - TRANSCRIÇÃO & SINCRONIZAÇÃO DE LEGENDAS
Testa o modelo Whisper Large v3 Turbo transcrevendo o áudio neural com precisão de tempo.
================================================================================
"""

import os
import sys
import time
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def format_timestamp(seconds: float) -> str:
    millis = int((seconds - int(seconds)) * 1000)
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    hours = int(mins // 60)
    mins = int(mins % 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def run_test():
    print("=" * 65)
    print("🧪 INICIANDO TESTE 4: WHISPER LARGE V3 TURBO (OPENAI)")
    print("🎯 Objetivo: Transcrição e Geração de Legendas SRT Sincronizadas")
    print("=" * 65)

    VRAMManager.audit("Pré-Carregamento Whisper")
    model_path = find_model_path("whisper")
    print(f"📦 Caminho do Modelo: {model_path}")

    # Áudio alvo gerado no Teste 2 (ou fallback existente)
    target_audio = os.path.join(OUTPUT_DIR, "test_2_voz_emocao.wav")
    if not os.path.exists(target_audio):
        fallback_audios = [
            "D:/Kaggles/Outputs/miniserie_ia/narracao_20s.wav",
            "assets/speaker_reference_dramatico.wav"
        ]
        for fa in fallback_audios:
            if os.path.exists(fa):
                target_audio = fa
                break

    print(f"🎧 Áudio para Transcrição: {target_audio}")
    if not os.path.exists(target_audio):
        raise FileNotFoundError(f"Nenhum arquivo de áudio encontrado para teste do Whisper: {target_audio}")

    try:
        import whisper
    except ImportError:
        print("⚠️ Instalando openai-whisper...")
        os.system(f"{sys.executable} -m pip install -q --no-warn-script-location openai-whisper")
        import whisper

    start_load = time.time()
    print("⏳ Carregando Whisper Large v3 Turbo na GPU...")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Carrega o modelo
    if os.path.isdir(model_path):
        model = whisper.load_model("large-v3-turbo", device=device, download_root=model_path)
    else:
        model = whisper.load_model("large-v3-turbo", device=device)

    load_time = round(time.time() - start_load, 2)
    print(f"✅ Whisper Carregado em {load_time}s!")
    VRAMManager.audit("Whisper em VRAM")

    print("\n👂 Transcrevendo Áudio com Detecção de Idioma e Timestamps...")
    start_infer = time.time()
    result = model.transcribe(target_audio, language="pt", task="transcribe")
    infer_time = round(time.time() - start_infer, 2)

    detected_text = result.get("text", "").strip()
    segments = result.get("segments", [])

    print(f"✅ Transcrição Concluída em {infer_time}s!")
    print(f"📝 Texto Reconhecido: \"{detected_text}\"")
    print(f"🔢 Total de Segmentos com Timestamps: {len(segments)}")

    # Gera arquivo de legendas .srt formatado
    out_srt = os.path.join(OUTPUT_DIR, "test_4_legendas.srt")
    with open(out_srt, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            s_start = format_timestamp(seg["start"])
            s_end = format_timestamp(seg["end"])
            text_clean = seg["text"].strip()
            f.write(f"{idx}\n{s_start} --> {s_end}\n{text_clean}\n\n")

    print(f"💾 Legendas SRT salvas em: {out_srt}")

    # Liberação de memória
    print("\n🧹 Descarregando modelo Whisper da VRAM...")
    del model
    VRAMManager.purge()
    print("🎉 TESTE 4 (WHISPER LARGE V3) FINALIZADO COM SUCESSO!\n")
    return out_srt

if __name__ == "__main__":
    run_test()
