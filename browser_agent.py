#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BROWSER AGENT: SUPERPODERES DE NAVEGAÇÃO E AUTOMAÇÃO PARA ANTIGRAVITY
Permite ao Antigravity:
1. Abrir URLs e renderizar SPAs (React, Vue, Colab, Kaggle, Dashboards)
2. Fazer Login autônomo (digitar usuário, senha e submeter formulários)
3. Clicar em botões, links e menus pelo texto ou seletores CSS
4. Tirar capturas de tela (screenshots) para auditoria visual
5. Persistir sessões e cookies para manter logins salvos
================================================================================
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright, Page, BrowserContext

USER_DATA_DIR = os.path.abspath("browser_profile")

class BrowserAgent:
    def __init__(self, headless: bool = True, user_data_dir: str = USER_DATA_DIR):
        self.headless = headless
        self.user_data_dir = user_data_dir
        os.makedirs(self.user_data_dir, exist_ok=True)

    def run_actions(self, actions: List[Dict[str, Any]], screenshot_path: Optional[str] = "browser_action.png") -> Dict[str, Any]:
        """
        Executa uma sequência determinística de ações de navegação.
        Exemplo de ações:
        - {"type": "goto", "url": "https://..."}
        - {"type": "fill", "selector": "#email", "value": "user@example.com"}
        - {"type": "fill", "selector": "#password", "value": "segredo123"}
        - {"type": "click", "selector": "button[type='submit']"}
        - {"type": "wait", "milliseconds": 3000}
        - {"type": "screenshot", "path": "evidencia.png"}
        - {"type": "extract_text", "selector": "h1"}
        """
        results = {"success": True, "steps": [], "errors": []}
        
        with sync_playwright() as p:
            # Lança com contexto persistente para manter cookies e logins salvos
            context: BrowserContext = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                viewport={"width": 1280, "height": 800},
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
            )
            
            page: Page = context.pages[0] if context.pages else context.new_page()
            
            for idx, action in enumerate(actions):
                act_type = action.get("type")
                step_log = {"step": idx + 1, "action": act_type}
                
                try:
                    if act_type == "goto":
                        url = action["url"]
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        step_log["url"] = page.url
                        step_log["title"] = page.title()
                        
                    elif act_type == "click":
                        selector = action["selector"]
                        # Tenta clicar pelo seletor CSS ou texto
                        if action.get("by_text"):
                            page.get_by_text(selector).first.click(timeout=15000)
                        else:
                            page.click(selector, timeout=15000)
                        step_log["clicked"] = selector
                        
                    elif act_type == "fill":
                        selector = action["selector"]
                        val = action["value"]
                        page.fill(selector, val, timeout=15000)
                        step_log["filled"] = selector
                        
                    elif act_type == "wait":
                        ms = action.get("milliseconds", 2000)
                        page.wait_for_timeout(ms)
                        step_log["waited_ms"] = ms
                        
                    elif act_type == "wait_for_selector":
                        selector = action["selector"]
                        page.wait_for_selector(selector, timeout=20000)
                        step_log["found_selector"] = selector

                    elif act_type == "screenshot":
                        path = action.get("path", screenshot_path)
                        page.screenshot(path=path, full_page=action.get("full_page", False))
                        step_log["screenshot_saved"] = os.path.abspath(path)

                    elif act_type == "extract_text":
                        selector = action.get("selector", "body")
                        text_val = page.locator(selector).first.inner_text(timeout=10000)
                        step_log["extracted_text"] = text_val[:500]

                    results["steps"].append(step_log)

                except Exception as e:
                    step_log["error"] = str(e)
                    results["errors"].append(step_log)
                    results["success"] = False
                    # Salva screenshot do erro para depuração
                    err_img = f"error_step_{idx + 1}.png"
                    try:
                        page.screenshot(path=err_img)
                        step_log["error_screenshot"] = os.path.abspath(err_img)
                    except Exception:
                        pass
                    break

            if screenshot_path and results["success"]:
                try:
                    page.screenshot(path=screenshot_path)
                    results["final_screenshot"] = os.path.abspath(screenshot_path)
                except Exception:
                    pass

            context.close()

        return results

def main():
    parser = argparse.ArgumentParser(description="Browser Agent CLI para Antigravity")
    parser.add_argument("--url", help="URL inicial para navegar")
    parser.add_argument("--actions-file", help="Caminho para arquivo JSON contendo a lista de ações")
    parser.add_argument("--screenshot", default="browser_capture.png", help="Caminho do screenshot final")
    parser.add_argument("--visible", action="store_true", help="Abrir navegador visível na tela (não-headless)")
    parser.add_argument("--quick-open", help="Abre uma URL, tira screenshot e extrai o título")

    parser.add_argument("--interactive", action="store_true", help="Abre o navegador visível para login interativo e salva a sessão")

    args = parser.parse_args()

    if args.interactive:
        url = args.url or "https://www.kaggle.com/account/login"
        print(f"🚀 Abrindo navegador interativo em: {url}")
        print("💡 Faça seu login na janela do navegador. Quando terminar, feche a janela ou aperte Enter aqui no terminal.")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                viewport=None,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url)
            try:
                # Mantém aberto até o usuário fechar ou dar timeout de 120s
                page.wait_for_event("close", timeout=120000)
            except Exception:
                pass
            context.close()
            print("✅ Sessão e cookies salvos com sucesso no perfil persistente!")
        return

    agent = BrowserAgent(headless=not args.visible)

    if args.quick_open:
        actions = [
            {"type": "goto", "url": args.quick_open},
            {"type": "wait", "milliseconds": 3000},
            {"type": "screenshot", "path": args.screenshot}
        ]
        res = agent.run_actions(actions, screenshot_path=args.screenshot)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.actions_file:
        with open(args.actions_file, "r", encoding="utf-8-sig") as f:
            actions = json.load(f)
        res = agent.run_actions(actions, screenshot_path=args.screenshot)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.url:
        actions = [
            {"type": "goto", "url": args.url},
            {"type": "wait", "milliseconds": 2000},
            {"type": "screenshot", "path": args.screenshot}
        ]
        res = agent.run_actions(actions, screenshot_path=args.screenshot)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
