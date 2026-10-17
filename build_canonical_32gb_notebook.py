#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o notebook canônico KAGGLE_TESTE_MODELOS_32GB.ipynb com:
- Zero Fila QUEUED (Hot Server + Cloudflare Tunnel)
- Paralelismo Real Dual-GPU Tesla T4 (cuda:0 + cuda:1)
- Otimização FP16 Tensor Cores Turing + NVENC
- Standalone Batch Runner
"""

import json
import os
import sys

for s in [sys.stdout, sys.stderr]:
    if hasattr(s, 'reconfigure'):
        s.reconfigure(encoding='utf-8', errors='replace')

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 🚀 KAGGLE 32GB (2x TESLA T4) - SUÍTE DE ALTA PERFORMANCE\n",
                "### Geração Neural Wan 2.1 FP16 | Servidor Quente Zero-Queue | Paralelismo Dual GPU\n",
                "---\n",
                "Este notebook oferece 3 modos operacionais para extrair 100% dos 32 GB de VRAM (2x Tesla T4):\n",
                "1. **Modo Servidor Quente (Recomendado):** Mantém as GPUs ativas em sessão interativa (boot em 15s) e expõe uma URL Cloudflared segura. Você dispara jobs do seu Windows sem esperar 1 segundo em fila `QUEUED`!\n",
                "2. **Modo Motor Paralelo Dual-GPU:** Renderiza cenas pares na GPU 0 (`cuda:0`) e ímpares na GPU 1 (`cuda:1`) simultaneamente com exportação por hardware `h264_nvenc`.\n",
                "3. **Modo Standalone Batch:** Renderiza os 4 takes sequenciais diretamente no Kaggle gerando o vídeo final e o relatório de telemetria."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# [1] DIAGNÓSTICO DE HARDWARE: 2x TESLA T4 (32 GB VRAM)\n",
                "import subprocess, sys, os\n",
                "print('=== VERIFICAÇÃO NVIDIA-SMI ===')\n",
                "subprocess.run(['nvidia-smi'], check=True)\n",
                "\n",
                "import torch\n",
                "print(f'\\nCUDA Disponível: {torch.cuda.is_available()}')\n",
                "num_gpus = torch.cuda.device_count()\n",
                "print(f'Total de GPUs: {num_gpus}')\n",
                "for i in range(num_gpus):\n",
                "    props = torch.cuda.get_device_properties(i)\n",
                "    total_gb = (props.total_mem if hasattr(props, 'total_mem') else props.total_memory) / (1024**3)\n",
                "    print(f'  🔹 GPU [{i}]: {props.name} | VRAM: {total_gb:.2f} GB | Compute: {props.major}.{props.minor}')\n",
                "\n",
                "assert torch.cuda.is_available(), 'ABORTANDO: Nenhuma GPU NVIDIA detectada no Kaggle!'"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# [2] INSTALAÇÃO DE DEPENDÊNCIAS DE PRODUÇÃO (FASTAPI, CLOUDFLARE, DIFFUSERS FP16)\n",
                "import subprocess, sys\n",
                "print('Instalando pacotes essenciais...')\n",
                "subprocess.run([\n",
                "    sys.executable, '-m', 'pip', 'install', '-q',\n",
                "    'fastapi>=0.110.0', 'uvicorn[standard]>=0.28.0', 'pydantic>=2.0',\n",
                "    'diffusers[torch]>=0.30.0', 'transformers>=4.44.0', 'accelerate>=0.33.0',\n",
                "    'sentencepiece', 'protobuf', 'requests', 'pillow'\n",
                "], check=True)\n",
                "print('✅ Dependências instaladas com sucesso!')"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# [3] SINCRONIZAR REPOSITÓRIO COM OS SCRIPTS DO PROJETO\n",
                "import os, subprocess\n",
                "REPO_DIR = '/tmp/meu-projeto'\n",
                "if not os.path.exists(REPO_DIR):\n",
                "    print('Clonando repositório meu-projeto...')\n",
                "    subprocess.run(['git', 'clone', 'https://github.com/joedsondasilva199-glitch/meu-projeto.git', REPO_DIR], check=True)\n",
                "else:\n",
                "    print('Atualizando repositório meu-projeto...')\n",
                "    subprocess.run(['git', '-C', REPO_DIR, 'pull'], check=True)\n",
                "\n",
                "print('✅ Scripts de renderização prontos em:', REPO_DIR)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# ============================================================================\n",
                "# [TESTE DE VOZ XTTS-v2] HISTÓRIA DRAMÁTICA DE 20 SEGUNDOS (PT-BR)\n",
                "# ============================================================================\n",
                "import os, subprocess, sys\n",
                "subprocess.run(['git', '-C', '/tmp/meu-projeto', 'pull'], check=False)\n",
                "voice_script = '/tmp/meu-projeto/Scripts/test_xtts_story_20s.py'\n",
                "print('🎙️ Executando teste de voz neural XTTS-v2 (História 20s)...')\n",
                "subprocess.run([sys.executable, voice_script], check=True)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# ============================================================================\n",
                "# [OPÇÃO 1] INICIAR SERVIDOR QUENTE (FASTAPI + TÚNEL CLOUDFLARE PÚBLICO)\n",
                "# Mantém 2x Tesla T4 prontas e ativas sem fila QUEUED\n",
                "# ============================================================================\n",
                "import subprocess, sys\n",
                "server_script = '/tmp/meu-projeto/Scripts/kaggle_32gb_hot_server.py'\n",
                "if os.path.exists(server_script):\n",
                "    print('🚀 Iniciando Kaggle 32GB Hot Server...')\n",
                "    # O servidor roda e expõe a URL trycloudflare.com no stdout e no GitHub\n",
                "    subprocess.run([sys.executable, server_script])\n",
                "else:\n",
                "    print('⚠️ Script do servidor não encontrado em:', server_script)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# ============================================================================\n",
                "# [OPÇÃO 2] TESTE DO MOTOR PARALELO DUAL T4 (cuda:0 + cuda:1 + NVENC)\n",
                "# ============================================================================\n",
                "import subprocess, sys\n",
                "parallel_script = '/tmp/meu-projeto/Scripts/dual_t4_parallel_engine.py'\n",
                "if os.path.exists(parallel_script):\n",
                "    print('🚀 Executando Motor Paralelo Dual-GPU...')\n",
                "    subprocess.run([sys.executable, parallel_script])\n",
                "else:\n",
                "    print('⚠️ Script do motor paralelo não encontrado em:', parallel_script)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# ============================================================================\n",
                "# [OPÇÃO 3] BATCH STANDALONE: 4 TAKES WAN 2.1 FP16 (EXECUÇÃO LOCAL DIRETA)\n",
                "# ============================================================================\n",
                "import os, gc, json, time, subprocess\n",
                "import torch\n",
                "from diffusers import DiffusionPipeline, UniPCMultistepScheduler\n",
                "from diffusers.utils import export_to_video\n",
                "\n",
                "CACHE_DIR = '/tmp/hf_cache'\n",
                "WORK_DIR = '/tmp/workspace'\n",
                "OUTPUT_DIR = '/kaggle/working'\n",
                "os.makedirs(CACHE_DIR, exist_ok=True)\n",
                "os.makedirs(WORK_DIR, exist_ok=True)\n",
                "\n",
                "print('=' * 70)\n",
                "print('CARREGANDO WAN 2.1 T2V EM FP16 NATIVO (TENSOR CORES T4)')\n",
                "print('=' * 70)\n",
                "\n",
                "pipe = DiffusionPipeline.from_pretrained(\n",
                "    'Wan-AI/Wan2.1-T2V-1.3B-Diffusers',\n",
                "    torch_dtype=torch.float16,\n",
                "    cache_dir=CACHE_DIR\n",
                ")\n",
                "pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)\n",
                "if hasattr(pipe, 'text_encoder') and pipe.text_encoder is not None:\n",
                "    pipe.text_encoder.to(torch.float32)\n",
                "pipe.enable_model_cpu_offload()\n",
                "\n",
                "PROMPTS = [\n",
                "    {'pers': 'Helena', 'prompt': 'Cinematic close-up of a beautiful Brazilian woman in her 30s, tears streaming down face, intense heartbreak and rage, luxury penthouse at night, warm lamp bokeh, dramatic 35mm lighting, photorealistic, 1080p'},\n",
                "    {'pers': 'Marcos', 'prompt': 'Cinematic close-up of a handsome Brazilian man late 30s in dark suit, frozen in shock and guilt, dim moody penthouse, warm rim lighting, dramatic shadows, 35mm anamorphic lens, photorealistic, 1080p'},\n",
                "    {'pers': 'Helena', 'prompt': 'Medium shot glamorous Brazilian woman turning away in contempt, tears on cheeks, hand on door handle, luxury hallway, dramatic backlighting, cinematic grain, photorealistic, 1080p'},\n",
                "    {'pers': 'Marcos', 'prompt': 'Dramatic shot distressed Brazilian man in dark suit reaching forward desperately, pleading expression, luxury penthouse at night, dramatic shadows, cinematic 35mm, photorealistic, 1080p'},\n",
                "]\n",
                "\n",
                "clips = []\n",
                "for idx, item in enumerate(PROMPTS):\n",
                "    take = idx + 1\n",
                "    print(f'\\nGerando Take {take}/4: {item[\"pers\"]} (49 frames, 12 steps)...')\n",
                "    torch.cuda.reset_peak_memory_stats(0)\n",
                "    t_gen = time.time()\n",
                "    output = pipe(\n",
                "        prompt=item['prompt'],\n",
                "        num_frames=49,\n",
                "        height=480,\n",
                "        width=832,\n",
                "        num_inference_steps=12,\n",
                "        guidance_scale=1.0,\n",
                "        generator=torch.Generator(device='cpu').manual_seed(42 + idx)\n",
                "    )\n",
                "    gen_time = round(time.time() - t_gen, 1)\n",
                "    clip_path = os.path.join(WORK_DIR, f'take_{take}_{item[\"pers\"].lower()}.mp4')\n",
                "    export_to_video(output.frames[0], clip_path, fps=16)\n",
                "    clips.append(clip_path)\n",
                "    print(f'  Take {take} concluído em {gen_time}s')\n",
                "\n",
                "del pipe\n",
                "gc.collect()\n",
                "torch.cuda.empty_cache()\n",
                "\n",
                "# Montagem com aceleração por Hardware NVENC\n",
                "concat_list = os.path.join(WORK_DIR, 'concat_list.txt')\n",
                "with open(concat_list, 'w') as f:\n",
                "    for c in clips:\n",
                "        f.write(f\"file '{c}'\\n\")\n",
                "\n",
                "final_path = os.path.join(OUTPUT_DIR, 'video_wan21_real_22s.mp4')\n",
                "cmd_nvenc = [\n",
                "    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,\n",
                "    '-vf', 'setpts=1.8*PTS,minterpolate=fps=25:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1920:1080:flags=lanczos',\n",
                "    '-c:v', 'h264_nvenc', '-preset', 'p4', '-cq', '19',\n",
                "    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',\n",
                "    final_path\n",
                "]\n",
                "res = subprocess.run(cmd_nvenc, capture_output=True, text=True)\n",
                "if res.returncode != 0:\n",
                "    cmd_cpu = [\n",
                "        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,\n",
                "        '-vf', 'setpts=1.8*PTS,minterpolate=fps=25:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1920:1080:flags=lanczos',\n",
                "        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',\n",
                "        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',\n",
                "        final_path\n",
                "    ]\n",
                "    subprocess.run(cmd_cpu, check=True)\n",
                "\n",
                "final_sz = round(os.path.getsize(final_path) / (1024*1024), 2)\n",
                "print(f'\\n✅ Vídeo Final Gerado: {final_path} ({final_sz} MB)')"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

target_paths = [
    r"D:\Stack de Agentes\KAGGLE_TESTE_MODELOS_32GB.ipynb",
    r"D:\Kaggles\KAGGLE_TESTE_MODELOS_32GB.ipynb",
    r"D:\Kaggles\kaggle_push\KAGGLE_TESTE_MODELOS_32GB.ipynb"
]

for p in target_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"✅ Notebook gerado: {p}")
