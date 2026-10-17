#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from dulwich.repo import Repo
import dulwich.porcelain as git

repo_path = "D:/Stack de Agentes"
repo = Repo(repo_path)

# Arquivos essenciais do pipeline e suite de testes
files_to_track = [
    "Scripts/stage1_seed_audio.py",
    "Scripts/stage2_audio_enhance.py",
    "Scripts/stage3_character_sheets.py",
    "Scripts/stage4_audio_driven_video.py",
    "Scripts/stage5_upscale_project.py",
    "Scripts/pipeline_seedance_master.py",
    "Referencias/vozes/audio_1_p1.wav",
    "Referencias/vozes/audio_2_p2.wav",
    "Referencias/vozes/audio_3_p3.wav",
    "Referencias/rostos/imagem_1.png",
    "Referencias/rostos/imagem_2.png",
    "Referencias/rostos/imagem_3.png",
    "Referencias/rostos/imagem_4_criatura.png",
    "tests/test_1_deepseek.py",
    "tests/test_2_xtts_emocao.py",
    "tests/test_3_sdxl_turbo.py",
    "tests/test_4_whisper.py",
    "tests/test_5_svd_video.py",
    "tests/test_6_wan21_video.py",
    "tests/test_7_lipsync.py",
    "tests/test_7_seedance_audio_video.py",
    "tests/model_locator.py",
    "tests/run_all_model_tests.py",
    "tests/vram_manager.py",
    "download_wan21_and_lipsync.py",
    "run_on_kaggle_cloud.py",
    "build_canonical_32gb_notebook.py",
    "git_commit_and_push.py",
    "KAGGLE_TESTE_MODELOS_32GB.ipynb",
    "Scripts/kaggle_32gb_hot_server.py",
    "Scripts/send_job_to_kaggle_32gb.py",
    "Scripts/dual_t4_parallel_engine.py",
    "Scripts/create_kaggle_model_dataset.py",
    "Scripts/test_xtts_story_20s.py",
    "assets/speaker_reference_dramatico.wav"
]

existing_files = [f.replace("\\", "/") for f in files_to_track if os.path.exists(os.path.join(repo_path, f))]

import subprocess

for s in [sys.stdout, sys.stderr]:
    if hasattr(s, 'reconfigure'):
        s.reconfigure(encoding='utf-8', errors='replace')

# Se HEAD estiver no commit rejeitado, reseta para o commit limpo anterior
current_head = repo.head().decode() if isinstance(repo.head(), bytes) else repo.head()
if current_head == "288c63d20349edbfb4ed0ce3ee9c3b23b08f213c":
    print("Resetando HEAD para o commit limpo 7a4e214f90d769d80ce19c6cdb552ac5f0706e11...")
    repo.refs[b"refs/heads/main"] = b"7a4e214f90d769d80ce19c6cdb552ac5f0706e11"

print(f"Indexando {len(existing_files)} arquivos no Git...")
git.add(repo, existing_files)

# Status
status = git.status(repo)
print(f"Staged Add: {len(status.staged['add'])}, Modify: {len(status.staged['modify'])}, Delete: {len(status.staged['delete'])}")

# Commit
commit_msg = b"feat: Suite Kaggle 32GB Dual-T4 com Hot Server, Cloudflare Tunnel, Paralelismo Real e FP16 Turbo"
author = b"Joedson Silva <joedsondasilva199@gmail.com>"

try:
    c_sha = git.commit(repo, message=commit_msg, author=author, committer=author)
    print(f"Commit realizado com sucesso: {c_sha.decode() if isinstance(c_sha, bytes) else c_sha}")
except Exception as e:
    print(f"Nota de commit: {e}")

# Obtenção dinâmica do token sem hardcode
token = os.environ.get("GITHUB_TOKEN")
if not token:
    try:
        token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception:
        token = ""

remote_url = f"https://{token}@github.com/joedsondasilva199-glitch/meu-projeto.git" if token else "https://github.com/joedsondasilva199-glitch/meu-projeto.git"
print("Realizando push para o GitHub...")
try:
    git.push(repo, remote_location=remote_url, refspecs=["refs/heads/main:refs/heads/main"])
    print("Push concluido com sucesso no GitHub!")
except Exception as e:
    print(f"Erro no push: {e}")
