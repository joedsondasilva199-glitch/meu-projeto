import re

file_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

print("File size:", len(text))

# Procurar definicoes de $t ou base url
matches = [m.start() for m in re.finditer(r"\$t\b", text)]
print(f"Total $t matches: {len(matches)}")
for i, pos in enumerate(matches[:8]):
    print(f"\n--- MATCH {i+1} at {pos} ---")
    print(text[max(0, pos-150):pos+150])
