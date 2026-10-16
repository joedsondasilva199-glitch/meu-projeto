import re

# 1. Atualizar bundle_darklab.js
bundle_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js"
with open(bundle_path, "r", encoding="utf-8") as f:
    bundle_content = f.read()

old_bundle_target = 'const $t="https://api.darklabapp.com";'
new_bundle_target = 'const API_BASE_URL=window.API_BASE_URL||"";const $t=API_BASE_URL;'

if old_bundle_target in bundle_content:
    bundle_content = bundle_content.replace(old_bundle_target, new_bundle_target)
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(bundle_content)
    print("bundle_darklab.js: API_BASE_URL centralizada com sucesso!")
else:
    print("bundle_darklab.js: Padrão já substituído ou não encontrado.")

# 2. Atualizar darklab_engine.js
engine_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\darklab_engine.js"
with open(engine_path, "r", encoding="utf-8") as f:
    engine_content = f.read()

if "window.API_BASE_URL" not in engine_content:
    engine_content = 'const API_BASE_URL = window.API_BASE_URL || "";\n' + engine_content
    # Substituir fetch("/api/ por fetch(API_BASE_URL + "/api/
    engine_content = engine_content.replace('fetch("/api/', 'fetch(API_BASE_URL + "/api/')
    engine_content = engine_content.replace('fetch(`/api/', 'fetch(`${API_BASE_URL}/api/')
    with open(engine_path, "w", encoding="utf-8") as f:
        f.write(engine_content)
    print("darklab_engine.js: API_BASE_URL centralizada com sucesso!")
else:
    print("darklab_engine.js: Já configurado.")

# 3. Atualizar dashboard.js
dash_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\dashboard.js"
with open(dash_path, "r", encoding="utf-8") as f:
    dash_content = f.read()

if "window.API_BASE_URL" not in dash_content:
    dash_content = 'const API_BASE_URL = window.API_BASE_URL || "";\n' + dash_content
    dash_content = dash_content.replace("fetch('/api/", "fetch(API_BASE_URL + '/api/")
    dash_content = dash_content.replace("fetch(`/api/", "fetch(`${API_BASE_URL}/api/")
    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(dash_content)
    print("dashboard.js: API_BASE_URL centralizada com sucesso!")
else:
    print("dashboard.js: Já configurado.")
