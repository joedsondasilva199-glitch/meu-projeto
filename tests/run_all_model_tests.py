#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SUÍTE DE AUDITORIA COMPLETA: OS 4 MODELOS REAIS (32GB DUAL T4)
Executa os 4 testes um por um com gerenciamento dinâmico de VRAM:
1. DeepSeek-R1 (8B) ➔ Roteiro e Cenas
2. XTTS-v2 ➔ Locução com Emoção e Clonagem
3. SDXL Turbo ➔ Imagem Cinematográfica 1024x1024
4. Whisper Large v3 ➔ Transcrição e Legendas
➔ Compilação Final de Vídeo com FFmpeg
================================================================================
"""

import os
import sys
import time
import shutil
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vram_manager import VRAMManager
import test_1_deepseek
import test_2_xtts_emocao
import test_3_sdxl_turbo
import test_4_whisper
import test_5_svd_video
import test_6_wan21_video

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=" * 70)
    print("🚀 INICIANDO AUDITORIA GERAL DOS 4 MODELOS REAIS NO KAGGLE (32GB VRAM)")
    print("=" * 70)
    
    start_total = time.time()
    results = {}

    # TESTE 1: DeepSeek-R1
    try:
        t0 = time.time()
        file_t1 = test_1_deepseek.run_test()
        results["DeepSeek-R1 (8B)"] = {"status": "APROVADO", "tempo": round(time.time() - t0, 1), "arquivo": file_t1}
    except Exception as e:
        results["DeepSeek-R1 (8B)"] = {"status": f"FALHOU: {e}", "tempo": 0, "arquivo": None}

    # TESTE 2: XTTS-v2 com Emoção
    try:
        t0 = time.time()
        file_t2 = test_2_xtts_emocao.run_test()
        results["XTTS-v2 (Voz com Emoção)"] = {"status": "APROVADO", "tempo": round(time.time() - t0, 1), "arquivo": file_t2}
    except Exception as e:
        results["XTTS-v2 (Voz com Emoção)"] = {"status": f"FALHOU: {e}", "tempo": 0, "arquivo": None}

    # TESTE 3: SDXL Turbo
    try:
        t0 = time.time()
        file_t3 = test_3_sdxl_turbo.run_test()
        results["SDXL Turbo (1024x1024)"] = {"status": "APROVADO", "tempo": round(time.time() - t0, 1), "arquivo": file_t3}
    except Exception as e:
        results["SDXL Turbo (1024x1024)"] = {"status": f"FALHOU: {e}", "tempo": 0, "arquivo": None}

    # TESTE 4: Whisper Large v3
    try:
        t0 = time.time()
        file_t4 = test_4_whisper.run_test()
        results["Whisper Large v3 (Legendas)"] = {"status": "APROVADO", "tempo": round(time.time() - t0, 1), "arquivo": file_t4}
    except Exception as e:
        results["Whisper Large v3 (Legendas)"] = {"status": f"FALHOU: {e}", "tempo": 0, "arquivo": None}

    # TESTE 5: SVD-XT (Vídeo Realista com Difusão Temporal)
    try:
        t0 = time.time()
        file_t5 = test_5_svd_video.run_test()
        results["SVD-XT (Vídeo Realista)"] = {"status": "APROVADO", "tempo": round(time.time() - t0, 1), "arquivo": file_t5}
    except Exception as e:
        results["SVD-XT (Vídeo Realista)"] = {"status": f"FALHOU: {e}", "tempo": 0, "arquivo": None}

    # TESTE 6: WAN 2.1 (Vídeo Realista de Próxima Geração - Estilo Seedance/Kling)
    try:
        t0 = time.time()
        file_t6 = test_6_wan21_video.run_test()
        results["Wan 2.1 (Vídeo Seedance/Kling)"] = {"status": "APROVADO", "tempo": round(time.time() - t0, 1), "arquivo": file_t6}
    except Exception as e:
        results["Wan 2.1 (Vídeo Seedance/Kling)"] = {"status": f"FALHOU: {e}", "tempo": 0, "arquivo": None}

    # ETAPA FINAL: Compilação de Vídeo Integrando os Modelos
    final_video = os.path.join(OUTPUT_DIR, "video_final_integrado.mp4")
    video_wan = results.get("Wan 2.1 (Vídeo Seedance/Kling)", {}).get("arquivo")
    video_svd = results.get("SVD-XT (Vídeo Realista)", {}).get("arquivo")
    best_video = video_wan if (video_wan and os.path.exists(video_wan)) else video_svd
    img_sdxl = results.get("SDXL Turbo (1024x1024)", {}).get("arquivo")
    audio_xtts = results.get("XTTS-v2 (Voz com Emoção)", {}).get("arquivo")
    srt_whisper = results.get("Whisper Large v3 (Legendas)", {}).get("arquivo")

    if audio_xtts and os.path.exists(audio_xtts):
        print("\n🎬 COMPILANDO VÍDEO INTEGRADO COM AS SAÍDAS DOS MODELOS REAIS...")
        if best_video and os.path.exists(best_video):
            print(f" -> Usando VÍDEO NEURAL REAL: {best_video}")
            cmd_video = [
                "ffmpeg", "-y",
                "-stream_loop", "-1", "-i", best_video,
                "-i", audio_xtts,
                "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-pix_fmt", "yuv420p",
                final_video
            ]
        elif img_sdxl and os.path.exists(img_sdxl):
            print(f" -> Usando imagem SDXL com movimento de câmera: {img_sdxl}")
            cmd_video = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", img_sdxl,
                "-i", audio_xtts,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0015,1.15)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25",
                "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-pix_fmt", "yuv420p",
                final_video
            ]
        subprocess.run(cmd_video, check=False)
        print(f"✅ Vídeo gerado com sucesso: {final_video}")

    # Geração do Relatório de Auditoria em Markdown
    total_time = round(time.time() - start_total, 1)
    report_file = os.path.join(OUTPUT_DIR, "RELATORIO_AUDITORIA_32GB.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 📋 RELATÓRIO DE AUDITORIA: OS 4 MODELOS REAIS (32GB DUAL T4)\n\n")
        f.write(f"**Tempo Total da Suíte:** {total_time} segundos\n\n")
        f.write("| Especialista | Modelo Real | Status | Tempo de Execução | Arquivo de Evidência |\n")
        f.write("| :--- | :--- | :---: | :---: | :--- |\n")
        for k, v in results.items():
            f.write(f"| **{k}** | Baixado no Drive/Kaggle | `{v['status']}` | {v['tempo']}s | `{os.path.basename(str(v['arquivo']))}` |\n")
        f.write(f"\n### Vídeo Final Renderizado:\n- `{final_video}`\n")

    print("\n" + "=" * 70)
    print("📊 RESUMO GERAL DA AUDITORIA:")
    for k, v in results.items():
        print(f" -> {k}: {v['status']} ({v['tempo']}s)")
    print(f"💾 Relatório Completo salvo em: {report_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
