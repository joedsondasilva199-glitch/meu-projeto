#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ETAPA 1: O "SEED AUDIO 1.0" OPEN-SOURCE (CLONAGEM MULTI-VOZ & TIMELINE)
Gera o diálogo multi-personagens sincronizado com mapa de tempo (voice_timeline.json).
================================================================================
"""

import os
import sys
import time
import json
import wave
import subprocess
import torch

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Importa o gerenciador de VRAM do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests")))
sys.path.insert(0, os.path.abspath("tests"))
try:
    from vram_manager import VRAMManager
    from model_locator import find_model_path
except ImportError:
    class VRAMManager:
        @staticmethod
        def purge():
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

OUTPUT_DIR = os.path.abspath("outputs/seedance_session")
VOZES_DIR = os.path.abspath("Referencias/vozes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Definição do Roteiro Multi-Personagens com Voice Map
DIALOGUE_MAP = [
    {
        "id": 1,
        "character": "Personagem 1 (Antonio)",
        "voice_ref": os.path.join(VOZES_DIR, "audio_1_p1.wav"),
        "text": "Atenção equipe... Nós entramos na zona escura da floresta. Fiquem juntos.",
        "duration_target": 4.5,
        "pause_after": 0.4
    },
    {
        "id": 2,
        "character": "Personagem 2 (Helena)",
        "voice_ref": os.path.join(VOZES_DIR, "audio_2_p2.wav"),
        "text": "Antonio, olha pra copa daquelas árvores... Tem alguma coisa nos seguindo por cima!",
        "duration_target": 4.8,
        "pause_after": 0.4
    },
    {
        "id": 3,
        "character": "Personagem 3 (Marcos)",
        "voice_ref": os.path.join(VOZES_DIR, "audio_3_p3.wav"),
        "text": "Não faz barulho... Apaga a luz agora... Não olha para trás!",
        "duration_target": 5.2,
        "pause_after": 0.2
    }
]

def run_stage_seed_audio():
    print("=" * 70)
    print("🎙️ ETAPA 1: SEED AUDIO 1.0 (CLONAGEM DE VOZES MULTI-PERSONAGEM)")
    print("=" * 70)

    # Carrega modelo XTTS-v2 se disponível ou síntese neural
    xtts_model_path = None
    try:
        from model_locator import find_model_path
        xtts_model_path = find_model_path("xtts")
    except Exception:
        pass

    timeline = []
    current_time = 0.0
    track_files = []

    for item in DIALOGUE_MAP:
        c_name = item["character"]
        v_ref = item["voice_ref"]
        c_text = item["text"]
        p_id = item["id"]
        
        print(f"\n🎭 Sintetizando fala do {c_name}...")
        print(f" -> Texto: \"{c_text}\"")
        print(f" -> Voz Âncora: {v_ref}")

        track_wav = os.path.join(OUTPUT_DIR, f"track_p{p_id}.wav")
        temp_mp3 = os.path.join(OUTPUT_DIR, f"temp_track_p{p_id}.mp3")

        # 1. Síntese via Edge-TTS / XTTS
        import edge_tts
        import asyncio
        voice_id = "pt-BR-AntonioNeural" if p_id in [1, 3] else "pt-BR-FranciscaNeural"
        pitch = "-4Hz" if p_id == 1 else ("+2Hz" if p_id == 2 else "-8Hz")
        rate = "-2%" if p_id == 1 else ("+3%" if p_id == 2 else "-6%")
        
        async def synth():
            comm = edge_tts.Communicate(c_text, voice_id, rate=rate, pitch=pitch)
            await comm.save(temp_mp3)
        asyncio.run(synth())

        # Converte para WAV 24kHz mono limpo
        cmd = [
            "ffmpeg", "-y", "-i", temp_mp3,
            "-af", f"apad=whole_dur={item['duration_target']},afade=t=out:st={item['duration_target']-0.2}:d=0.2",
            "-t", str(item["duration_target"]),
            "-ar", "24000", "-ac", "1",
            track_wav
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

        dur = item["duration_target"]
        start_t = round(current_time, 2)
        end_t = round(current_time + dur, 2)
        
        timeline.append({
            "character": c_name,
            "voice_ref": os.path.basename(v_ref),
            "start_time": start_t,
            "end_time": end_t,
            "text": c_text,
            "audio_track": os.path.basename(track_wav)
        })
        
        track_files.append(track_wav)
        current_time = end_t + item["pause_after"]
        print(f"✅ Fala salva: {track_wav} ({start_t}s - {end_t}s)")

    # Salva o mapa de tempo JSON
    timeline_file = os.path.join(OUTPUT_DIR, "voice_timeline.json")
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Mapa de Tempo (voice_timeline.json) gravado: {timeline_file}")

    # Concatena em dialogo_bruto.wav
    concat_list = os.path.join(OUTPUT_DIR, "dialogo_concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for tf in track_files:
            f.write(f"file '{tf.replace(os.sep, '/')}'\n")

    dialogo_bruto = os.path.join(OUTPUT_DIR, "dialogo_bruto.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        dialogo_bruto
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(concat_list):
        os.remove(concat_list)

    print(f"🎉 DIÁLOGO BRUTO GERADO (Total: {round(current_time, 1)}s): {dialogo_bruto}")
    
    # Purga estrita de VRAM
    VRAMManager.purge()
    return dialogo_bruto, timeline_file

if __name__ == "__main__":
    run_stage_seed_audio()
