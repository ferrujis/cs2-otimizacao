from PIL import Image, ImageDraw

# tamanho aproximado usado pela janela
size = (1000, 720)
img = Image.new("RGB", size, (20, 0, 40))  # nome escuro roxo
draw = ImageDraw.Draw(img)

# desenhar linhas amarelas estilo circuito
for i in range(20, size[0], 100):
    draw.line((i, 0, i+200, size[1]), fill=(253,185,39), width=2)
for j in range(20, size[1], 120):
    draw.line((0, j, size[0], j+100), fill=(253,185,39), width=2)

# adicionar alguns círculos como decorações
draw.ellipse((100,100,200,200), outline=(253,185,39), width=3)
draw.ellipse((size[0]-200, size[1]-200, size[0]-100, size[1]-100), outline=(253,185,39), width=3)

img.save("background.png")
print("background.png gerado")
