
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

        # fontes reutilizáveis (tamanhos bases, serão escaladas dinamicamente)
        self.fonts = {
            "title": ("Segoe UI", 38, "bold"),
            "subtitle": ("Segoe UI", 16),
            "button": ("Segoe UI", 16, "bold"),
        }

        # Fator de escala (calculado com base na resolução)
        self.scale_factor = 1.0

    def calculate_scale_factor(self, screen_height=None):
        """Calcula fator de escala baseado na altura da tela.

        Ajusta tamanhos de fontes para diferentes resoluções:
        - 768p: 0.85x
        - 1080p: 1.0x
        - 1440p: 1.4x
        - 2160p: 1.8x
        """
        if screen_height is None:
            # Valor padrão: assume 1080p
            self.scale_factor = 1.0
        else:
            # Escala proporcional: 1080 = 1.0
            self.scale_factor = max(0.8, min(2.0, screen_height / 1080.0))

        return self.scale_factor

    def get_scaled_font(self, base_size):
        """Retorna tamanho de fonte escalado baseado no fator de escala."""
        return max(8, int(base_size * self.scale_factor))

    def get_responsive_padding(self, base_padding, window_width=None):
        """Retorna padding escalado responsivamente.

        Se window_width < 1024px, reduz padding.
        Do contrário, mantém proporcional.
        """
        if window_width is None:
            return base_padding

        if window_width < 1024:
            # Em telas pequenas, reduz padding
            return max(4, int(base_padding * (window_width / 1024.0)))

        return base_padding

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

