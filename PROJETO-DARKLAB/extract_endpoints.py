import re

file_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Procura chamadas a qe, zC, Ax com caminhos
calls = []

# Pattern 1: qe("...", ...) ou qe(`...`, ...)
p1 = re.findall(r'\bqe\(\s*["`](/[^"`]+)["`]', text)
calls.extend(p1)

# Pattern 2: zC("...", ...) ou zC(`...`, ...)
p2 = re.findall(r'\bzC\(\s*["`](/[^"`]+)["`]', text)
calls.extend(p2)

# Pattern 3: Ax("...", ...)
p3 = re.findall(r'\bAx\(\s*["`](/[^"`]+)["`]', text)
calls.extend(p3)

# Pattern 4: fetch(`${$t}...`)
p4 = re.findall(r'fetch\(`\${\$t}(/[^`]+)`', text)
calls.extend(p4)

# Pattern 5: fetch("/api/..." ou similar)
p5 = re.findall(r'["`](/api/[^"`]+)["`]', text)
calls.extend(p5)

# Pattern 6: rotas em geral como "/auth/...", "/users/...", etc
p6 = re.findall(r'["`](/(?:auth|user|workspace|admin|public|billing|subscriptions|tokens|projects|scripts|storyboard|tts|viral-lab|voices|media|folders|analytics|export|render|jobs|notifications)[^"`]*)["`]', text)
calls.extend(p6)

unique_endpoints = sorted(list(set(calls)))
print(f"Total de endpoints identificados: {len(unique_endpoints)}")
for ep in unique_endpoints:
    print(ep)
