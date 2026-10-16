import re

file_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

for term in ['20128', 'balance', 'synthes', 'kanban']:
    print(f"\n=================== TERM: {term} ===================")
    for m in re.finditer(re.escape(term), text, re.IGNORECASE):
        pos = m.start()
        print("---")
        print(text[max(0, pos-150):pos+200].replace('\n', ' '))
