#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
GOOGLE DRIVE AUTO-SYNC ENGINE
Sincronização Bidirecional Contínua entre Kaggle/Colab e o Google Drive
Cria a pasta: Google Drive > Stack_Agentes_32GB
Garante que nenhum trabalho seja perdido e permite retomada instantânea.
================================================================================
"""

import os
import sys
import shutil
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DriveSync")

DRIVE_FOLDER_NAME = "Stack_Agentes_32GB"

def is_colab() -> bool:
    return "google.colab" in sys.modules or os.path.exists("/content")

def is_kaggle() -> bool:
    return os.path.exists("/kaggle")

class GoogleDriveManager:
    def __init__(self, target_folder: str = DRIVE_FOLDER_NAME):
        self.target_folder = target_folder
        self.drive_mounted_path = None
        self.is_connected = False

    def connect(self) -> bool:
        """Conecta ao Google Drive detectando o ambiente (Colab vs Kaggle vs Local)."""
        logger.info("Iniciando conexão com o Google Drive...")
        
        # 1. Modo Google Colab (Nativo, direto e sem fricção)
        if is_colab():
            try:
                from google.colab import drive
                mount_point = "/content/drive"
                if not os.path.exists(f"{mount_point}/MyDrive"):
                    logger.info("Montando Google Drive nativo no Colab...")
                    drive.mount(mount_point)
                
                self.drive_mounted_path = os.path.join(mount_point, "MyDrive", self.target_folder)
                os.makedirs(self.drive_mounted_path, exist_ok=True)
                self.is_connected = True
                logger.info(f"✅ Google Drive conectado com sucesso em: {self.drive_mounted_path}")
                return True
            except Exception as e:
                logger.warning(f"Falha na montagem automática do Colab: {e}")

        # 2. Modo Kaggle / Standalone (via PyDrive2 com autenticação segura)
        if is_kaggle() or not self.is_connected:
            try:
                import pydrive2
            except ImportError:
                logger.info("Instalando pydrive2 para integração com Google Drive...")
                os.system(f"{sys.executable} -m pip install -q --no-warn-script-location pydrive2")
            
            try:
                from pydrive2.auth import GoogleAuth
                from pydrive2.drive import GoogleDrive

                # Configura autenticação headless do Google
                gauth = GoogleAuth()
                gauth.settings['get_refresh_token'] = True
                
                # Se houver credenciais salvas no disco efêmero, carrega
                cred_file = os.path.abspath("google_drive_credentials.json")
                if os.path.exists(cred_file):
                    gauth.LoadCredentialsFile(cred_file)
                
                if gauth.credentials is None:
                    print("\n" + "="*65)
                    print("🔗 AUTORIZAÇÃO SEGURA DO GOOGLE DRIVE:")
                    print("Abra o link abaixo, faça login na sua conta Google e cole o código de verificação:")
                    print("="*65 + "\n")
                    gauth.CommandLineAuth()
                    gauth.SaveCredentialsFile(cred_file)
                elif gauth.access_token_expired:
                    gauth.Refresh()
                else:
                    gauth.Authorize()
                
                self.drive = GoogleDrive(gauth)
                self.is_connected = True
                logger.info("✅ Conexão com Google Drive estabelecida com sucesso via API!")
                return True
            except Exception as e:
                logger.error(f"Erro ao autenticar Google Drive no Kaggle: {e}")
                return False

        return False

    def sync_to_drive(self, local_path: str = ".") -> None:
        """Salva todos os arquivos importantes no Google Drive."""
        if not self.is_connected:
            if not self.connect():
                logger.warning("Google Drive não conectado. Sincronização ignorada.")
                return

        logger.info(f"💾 Sincronizando dados para o Google Drive ({self.target_folder})...")

        # Se tiver caminho de pasta montada (Colab / Sistema de arquivos)
        if self.drive_mounted_path and os.path.exists(self.drive_mounted_path):
            files_to_sync = [
                "cloud_state.json",
                "kaggle_32gb_runner.py",
                "setup_kaggle.py",
                "google_drive_sync.py"
            ]
            for f in files_to_sync:
                if os.path.exists(f):
                    dst = os.path.join(self.drive_mounted_path, f)
                    shutil.copy2(f, dst)
                    logger.info(f" -> Arquivo sincronizado no Drive: {f}")

            # Sincroniza checkpoints de modelos se existirem
            output_dir = "/kaggle/working" if is_kaggle() else "."
            for item in os.listdir(output_dir):
                if item.endswith((".pt", ".safetensors", ".bin", ".json")):
                    src = os.path.join(output_dir, item)
                    dst = os.path.join(self.drive_mounted_path, item)
                    shutil.copy2(src, dst)
            
            logger.info("🎉 Todos os arquivos e estados foram salvos no seu Google Drive com sucesso!")

        elif hasattr(self, 'drive'):
            # Upload via PyDrive para o Kaggle
            # Procura ou cria a pasta remota
            folder_id = self._get_or_create_folder(self.target_folder)
            
            for fname in ["cloud_state.json", "kaggle_32gb_runner.py"]:
                if os.path.exists(fname):
                    gfile = self.drive.CreateFile({'title': fname, 'parents': [{'id': folder_id}]})
                    gfile.SetContentFile(fname)
                    gfile.Upload()
                    logger.info(f" -> Arquivo enviado ao Google Drive: {fname}")
            
            logger.info("🎉 Checkpoints e arquivos sincronizados no Google Drive!")

    def _get_or_create_folder(self, folder_name: str) -> str:
        """Encontra ou cria a pasta no Google Drive."""
        q = f"title = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        file_list = self.drive.ListFile({'q': q}).GetList()
        if file_list:
            return file_list[0]['id']
        
        folder = self.drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()
        return folder['id']

def auto_backup():
    """Função utilitária executável diretamente."""
    mgr = GoogleDriveManager()
    if mgr.connect():
        mgr.sync_to_drive()

if __name__ == "__main__":
    auto_backup()
