from PIL import Image

# convert ico to png 64x64 for header
# prefer deer.png se estiver disponível
import os
if os.path.exists('deer.png'):
    img = Image.open('deer.png').convert('RGBA')
    img = img.resize((48,48))
    img.save('logo.png')
    print('logo.png gerado a partir de deer.png')
else:
    icon = Image.open('alcesboost.ico')
    icon = icon.resize((48,48))
    icon.save('logo.png')
    print('logo.png gerado a partir de alcesboost.ico')
