# alcesboost

Aplicativo desktop para otimização de performance (inspirado em CS2). Interface moderna em roxo/amarelo.

## Features

- Visualização de FPS ao longo do tempo
- Tweaks e ferramentas de limpeza do Windows
- Interface moderna baseada em customtkinter

## Getting Started

1. Crie e ative um ambiente virtual (recomendado).
2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Para executar em desenvolvimento:

```bash
python main.py
```

4. Para gerar um executável Windows (.exe) usando PyInstaller (inclui pedido de permissões de Administrador):

```bash
pyinstaller --noconfirm --onefile --windowed --uac-admin --icon=alcesboost.ico --name alcesboost main.py
```

A opção `--uac-admin` faz com que o Windows solicite ao usuário elevação de privilégios ao abrir o executável, permitindo que tweaks que mexem em registro e serviços sejam aplicados.

Ou use o script `build_alcesboost.bat` no Windows.

## Observações

- Alguns tweaks requerem permissão de Administrador.
- Teste em um ambiente controlado antes de aplicar quaisquer mudanças no sistema.
## Executável

- Um executável Windows já pode ser gerado com PyInstaller; o build gerado localmente está em `dist\alcesboost.exe`.
- O ícone `alcesboost.ico` foi gerado e embutido no executável.

Para executar o `.exe` gerado:

```powershell
.\dist\alcesboost.exe
```

Para recriar o `.exe` (rebuild) a partir do código-fonte:

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --icon=alcesboost.ico --name alcesboost main.py
```

Ou use o script fornecido no repositório:

```powershell
.\build_alcesboost.bat
```

## Observações sobre a interface

- A interface agora contém apenas as abas **Sistema & Tweaks** e **Limpeza** (remoção da aba de métricas em tempo real).
- Foi adicionado um fundo personalizado (`background.png`) e um cabeçalho estilizado para aproximar o visual da imagem de referência.
- É possível usar um logotipo sem fundo (como a imagem do veado) no canto superior: basta colocar um arquivo `deer.png` ou `logo.png` na mesma pasta do executável. O mesmo arquivo será utilizado para gerar o ícone (`alcesboost.ico`) via `generate_icon.py`.
- O visual (cores, fontes, etc.) está centralizado em uma classe `Style` (`style.py`). Se desejar alterar o tema, edite essa classe ou carregue configurações externas com `Style.load_from_json(path)`. Mantém-se o acesso a essas propriedades via `self.colors` e `self.fonts` no código principal.
- Alguns tweaks exigem execução com privilégios de Administrador; execute o `.exe` como Administrador quando necessário.

Se quiser, posso também criar um instalador Windows (Inno Setup) para distribuição.
