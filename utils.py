import psutil
from datetime import datetime, timezone

def get_memory_type_name(mem_type):
    """Converte número de tipo de memória WMI para string legível."""
    # Mapeia valores numéricos de Win32_PhysicalMemory.MemoryType para descrições:
    memory_types = {
        20: "DDR", 21: "DDR2", 24: "DDR3", 26: "DDR4", 34: "DDR5"
    }
    return memory_types.get(mem_type, "Desconhecido")

def get_chipset_info(motherboard_name):
    """Extrai informação de chipset do nome da placa mãe ou via WMI."""
    if not motherboard_name: return "Não detectado"

    # Padrões comuns de chipsets Intel e AMD (Manter a lista completa)
    chipset_patterns = {
        "Z890": "Intel Z890", "Z790": "Intel Z790", "H870": "Intel H870",
        "H770": "Intel H770", "B860": "Intel B860", "B760": "Intel B760",
        "Z690": "Intel Z690", "H670": "Intel H670", "B660": "Intel B660",
        "X870": "AMD X870", "X670E": "AMD X670E", "B650E": "AMD B650E",
        "X670": "AMD X670", "B650": "AMD B650",
    }
    mobo_upper = motherboard_name.upper()
    for pattern, chipset in chipset_patterns.items():
        if pattern in mobo_upper: return chipset
    return "Detectado (Desconhecido)"

def get_current_datetime_formatted() -> str:
    """Retorna data e hora formatada para logs."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")