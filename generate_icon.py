from PIL import Image, ImageDraw
import os

# Se existir uma imagem chamada deer.png ou logo.png, use-a como fonte do ícone
src = None
for name in ("deer.png", "logo.png"):
    if os.path.exists(name):
        src = name
        break

if src:
    # converter imagem existente para ícone
    base = Image.open(src).convert("RGBA")
    base = base.resize((256, 256))
    base.save("alcesboost.ico", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
    print(f'Ícone gerado a partir de {src}: alcesboost.ico')
else:
    # fallback para desenho simples custom
    # Cores (roxo / amarelo Lakers)
    PURPLE = (85, 37, 131, 255)  # #552583
    YELLOW = (253, 185, 39, 255)  # #FDB927

    # Criar base 256x256
    size = (256, 256)
    img = Image.new("RGBA", size, PURPLE)
    draw = ImageDraw.Draw(img)

    # Desenhar círculo amarelo central
    draw.ellipse((40, 40, 216, 216), fill=YELLOW)

    # Desenhar um 'A' estilizado (triângulo) em roxo sobre o círculo
    triangle = [(128, 64), (92, 176), (164, 176)]
    draw.polygon(triangle, fill=PURPLE)

    # Pequeno recorte no topo para formar o A
    draw.rectangle((118, 96, 138, 116), fill=PURPLE)

    # Salvar como .ico com múltiplos tamanhos
    img.save("alcesboost.ico", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
    print('Ícone padrão gerado: alcesboost.ico')
