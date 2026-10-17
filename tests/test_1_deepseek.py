#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TESTE 1: DEEPSEEK-R1 (8B) - ROTEIRISTA & RACIOCÍNIO PROFUNDO
Testa o modelo DeepSeek-R1-Distill-Llama-8B na GPU Dual T4 (32GB VRAM).
================================================================================
"""

import os
import sys
import time
import json
import torch

# Adiciona o diretório atual ao path para importar módulos locais
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_locator import find_model_path
from vram_manager import VRAMManager

OUTPUT_DIR = os.path.abspath("outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test():
    print("=" * 65)
    print("🧪 INICIANDO TESTE 1: DEEPSEEK-R1 (8B)")
    print("🎯 Objetivo: Raciocínio Profundo, Roteiro Sci-Fi de 20s e Cenas JSON")
    print("=" * 65)

    VRAMManager.audit("Pré-Carregamento DeepSeek-R1")
    model_path = find_model_path("deepseek")
    print(f"📦 Caminho do Modelo: {model_path}")

    from transformers import AutoTokenizer, AutoModelForCausalLM

    start_load = time.time()
    print("⏳ Carregando Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    
    print("⏳ Carregando Pesos Neurais em FP16 (device_map='auto')...")
    device_map = "auto" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch_dtype,
        device_map=device_map,
        trust_remote_code=True
    )
    load_time = round(time.time() - start_load, 2)
    print(f"✅ DeepSeek-R1 Carregado em {load_time}s!")
    VRAMManager.audit("DeepSeek-R1 em VRAM")

    prompt = (
        "Você é o diretor e roteirista sênior do Estúdio de IA. "
        "Crie um roteiro cinematográfico sci-fi de exatamente 20 segundos em Português do Brasil com 4 cenas (5s cada). "
        "Estruture a resposta obrigatoriamente no seguinte JSON:\n"
        "{\n"
        '  "titulo": "Nome do Episódio",\n'
        '  "duracao_segundos": 20,\n'
        '  "cenas": [\n'
        '    {"id": 1, "tempo": "00:00 - 00:05", "fala": "...", "prompt_visual_sdxl": "..."},\n'
        '    {"id": 2, "tempo": "00:05 - 00:10", "fala": "...", "prompt_visual_sdxl": "..."},\n'
        '    {"id": 3, "tempo": "00:10 - 00:15", "fala": "...", "prompt_visual_sdxl": "..."},\n'
        '    {"id": 4, "tempo": "00:15 - 00:20", "fala": "...", "prompt_visual_sdxl": "..."}\n'
        "  ]\n"
        "}"
    )

    print("🧠 Executando Inferência com Raciocínio Neural...")
    start_infer = time.time()
    
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.6,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    infer_time = round(time.time() - start_infer, 2)
    print(f"✅ Raciocínio e Geração concluídos em {infer_time}s!")
    print("\n--- RESPOSTA BRUTA GERADA PELO DEEPSEEK-R1 ---")
    print(response_text[:400] + "...\n[Truncado para exibição]")

    # Salva o arquivo de evidência
    out_file = os.path.join(OUTPUT_DIR, "test_1_roteiro.json")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(response_text)
    print(f"💾 Evidência salva em: {out_file}")

    # Liberação cirúrgica de memória
    print("\n🧹 Descarregando modelo DeepSeek-R1 da VRAM...")
    del model
    del tokenizer
    del inputs
    del outputs
    VRAMManager.purge()
    print("🎉 TESTE 1 (DEEPSEEK-R1) FINALIZADO COM SUCESSO!\n")
    return out_file

if __name__ == "__main__":
    run_test()
