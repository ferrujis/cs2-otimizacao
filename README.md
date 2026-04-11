# alcesboost

Aplicativo desktop para otimização de performance focado em CS2 (Counter-Strike 2). Interface moderna em roxo/amarelo com detecção automática de hardware e otimizações personalizadas.

## Features

- **Detecção Completa de Hardware**: Identifica automaticamente CPU, GPU, RAM, placa mãe e chipset
- **Verificação de Drivers**: Analisa versões de drivers de GPU, rede, áudio e dá recomendações de atualização
- **Otimização CS2 Inteligente**: Recomendações e tweaks específicos baseados no hardware detectado
- **5 Categorias de Otimização**:
  - **CPU**: Ajusta afinidade, prioridade e desabilita core parking
  - **GPU**: Configura perfis de jogo, desabilita V-sync global
  - **RAM**: Otimiza cache do sistema e gerenciamento de memória
  - **Rede**: TCP NoDelay, desabilita offloading, baixa latência
  - **Sistema**: Modo zero input lag, Game Mode, desabilita DVR
- **Recomendações Automáticas**: Análise do hardware e sugestões para melhor frametime
- Interface moderna baseada em customtkinter

## Novas Funcionalidades (v2.0)

### Detecção de Hardware
- **CPU**: Nome, cores físicos/lógicos, frequência atual/máxima
- **RAM**: Capacidade total, tipo (DDR4/DDR5) e velocidade
- **GPU**: Modelo, memória dedicada (suporte NVIDIA, AMD, Intel)
- **Placa Mãe**: Fabricante e modelo
- **Chipset**: Identificação do chipset da placa mãe

### Verificação de Drivers
- **GPU Drivers**: Versão e data dos drivers de vídeo (NVIDIA, AMD, Intel)
- **Rede Drivers**: Drivers de placa de rede Ethernet/Wi-Fi
- **Áudio Drivers**: Drivers de dispositivos de áudio
- **Análise Inteligente**: Recomendações para atualização de drivers desatualizados
- **Compatibilidade CS2**: Verificação específica para drivers de jogos
- **Atualização Automática**: Botão para abrir links oficiais de atualização de drivers

### Otimizações CS2 Inteligentes
- **Otimização de CPU**: Ajusta afinidade, prioridade e desabilita core parking
- **Otimização de GPU**: Configura perfis de jogo, desabilita V-sync global
- **Otimização de RAM**: Ajusta cache do sistema e gerenciamento de memória
- **Configurações de Rede**: TCP NoDelay, desabilita offloading, baixa latência
- **Tweaks de Sistema**: Modo zero input lag, Game Mode, desabilita DVR

### Recomendações Automáticas
Baseadas no hardware detectado, o app gera recomendações específicas para CS2:
- Análise de RAM suficiente para o jogo
- Avaliação de capacidade multicore da CPU
- Sugestões para melhor frametime e redução de stuttering

## Como Usar

### 1. Detecção de Hardware
- Clique em "Detectar Hardware" para identificar automaticamente todos os componentes
- Visualize informações detalhadas sobre CPU, GPU, RAM, placa mãe e chipset

### 2. Verificação de Drivers
- Clique em "Verificar Drivers" para analisar o status atual dos drivers
- O app mostra versões instaladas e indica se estão atualizados
- Use "Atualizar Drivers" para acessar links oficiais de download

### 3. Otimização CS2
- Selecione as categorias de otimização desejadas (CPU, GPU, RAM, Rede, Sistema)
- Clique em "Aplicar Otimizações CS2" para implementar as mudanças
- Reinicie o computador para que todas as alterações tenham efeito

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

- **Drivers Atualizados**: Mantenha drivers de GPU sempre atualizados para melhor performance no CS2
- **Permissões**: Alguns tweaks requerem permissão de Administrador
- **Backup**: Recomenda-se fazer backup do sistema antes de aplicar otimizações
- **Testes**: Teste as configurações em jogos para verificar melhorias
- **Reversão**: Algumas otimizações podem ser revertidas reiniciando o PC
- **Hardware**: Funciona com qualquer hardware, mas otimizações são otimizadas para CS2

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
