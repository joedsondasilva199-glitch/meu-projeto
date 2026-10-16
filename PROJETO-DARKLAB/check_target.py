with open(r"D:\Stack de Agentes\PROJETO-DARKLAB\ER-OUTPUT\front-clonado\bundle_darklab.js", "r", encoding="utf-8") as f:
    text = f.read()

target = 'const $t="https://api.darklabapp.com";'
print("Found target:", target in text)
