import re

file_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'\bqe\(', text)]
print(f"Total qe( calls: {len(matches)}")
for i, pos in enumerate(matches[:30]):
    snippet = text[pos:pos+150].replace('\n', ' ')
    print(f"{i+1:02d}: {snippet}")
