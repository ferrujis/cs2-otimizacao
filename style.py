
class Style:
    """Encapsula cores, fontes e outras propriedades visuais.

    A ideia é centralizar todas as definições de tema em um único lugar,
    facilitando a alteração futura ou mesmo a leitura de um arquivo
    de configuração (JSON/INI) para temas diferentes.
    """

    def __init__(self):
        # esquema de cores padrão (roxo / dourado)
        self.colors = {
            "bg": "#2A1A45",
            "bg_alt": "#342055",
            "panel": "#3E2864",
            "panel_soft": "#4B3277",
            "gold": "#DAB670",
            "gold_bright": "#F7D899",
            "gold_dark": "#86653A",
            "text": "#F3E7CB",
            "text_soft": "#D2C4A4",
        }

        # fontes reutilizáveis
        self.fonts = {
            "title": ("Segoe UI", 38, "bold"),
            "subtitle": ("Segoe UI", 16),
            "button": ("Segoe UI", 16, "bold"),
        }

    def load_from_json(self, path):
        """Carrega cores/fontes de um arquivo JSON externo.

        Exemplo de estrutura:
        {
            "colors": { "bg": "#ffffff", ... },
            "fonts": { "title": ["Arial", 24, "bold"], ... }
        }
        """
        import json

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.colors.update(data.get("colors", {}))
            self.fonts.update(data.get("fonts", {}))
        except Exception:
            # falha silenciosa, mantém padrões
            pass
