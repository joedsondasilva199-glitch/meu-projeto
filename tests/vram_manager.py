#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de VRAM e Auditoria de Memória para Kaggle Dual GPU (32GB Total).
"""

import os
import gc
import sys
import torch
import logging

logger = logging.getLogger("VRAMManager")

class VRAMManager:
    @staticmethod
    def audit(stage_name: str = ""):
        print("\n" + "=" * 60)
        print(f"📊 AUDITORIA DE VRAM: {stage_name}")
        print("=" * 60)
        if not torch.cuda.is_available():
            print("⚠️ CUDA não disponível neste nó.")
            return

        num_gpus = torch.cuda.device_count()
        total_alloc = 0.0
        total_res = 0.0
        
        for i in range(num_gpus):
            alloc = torch.cuda.memory_allocated(i) / (1024 ** 2)
            res = torch.cuda.memory_reserved(i) / (1024 ** 2)
            total = torch.cuda.get_device_properties(i).total_memory / (1024 ** 2)
            total_alloc += alloc
            total_res += res
            print(f"🔹 GPU [{i}] ({torch.cuda.get_device_name(i)}): Alocada: {alloc:.1f} MB | Reservada: {res:.1f} MB | Total: {total:.1f} MB")
            
        print(f"📈 TOTAL VRAM EM USO: {total_alloc:.1f} MB | RESERVADO: {total_res:.1f} MB")
        print("=" * 60 + "\n")

    @staticmethod
    def purge():
        """Esvazia tensores, invoca GC e limpa o cache de ambas as GPUs."""
        print("🧹 [VRAMManager] Purgando tensores e liberando memória VRAM...")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            try:
                torch.cuda.ipc_collect()
            except Exception:
                pass
        VRAMManager.audit("Pós-Purga (VRAM Livre)")
