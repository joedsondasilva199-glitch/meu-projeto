import re

file_path = r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect the API client around position 174000 to 178000
print(text[174000:176500])
