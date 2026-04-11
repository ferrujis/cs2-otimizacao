import psutil
import wmi
from datetime import datetime, timezone
from typing import Dict, Any

# Importar funções utilitárias de sistema do novo módulo system_tweaks para uso local (se necessário)
# from .system_tweaks import WindowsSystemService

class HardwareDetector:
    """Classe dedicada a coletar e estruturar informações detalhadas de hardware."""

    def __init__(self):
        self.hardware_info = {}

    def detect_all(self) -> Dict[str, Any]:
        """Método principal que orquestra a coleta de dados de todos os componentes."""
        try:
            self.detect_cpu()
            self.detect_memory()
            self.detect_gpu()
            self.detect_motherboard()
            self.detect_storage()
            # Adicionar outros detectores aqui conforme necessário (rede, etc.)
            return self.hardware_info
        except Exception as e:
            print(f"Erro fatal na detecção de hardware: {e}")
            return {"error": str(e)}

    def _safe_getattr(self, obj, attr, default=None):
        """Tenta obter um atributo com tratamento de exceção."""
        try:
            return getattr(obj, attr)
        except AttributeError:
            return default
        except Exception:
            return None

    def detect_cpu(self):
        """Coleta informações sobre CPU e desempenho."""
        info = {}
        try:
            # Informações básicas de hardware (psutil)
            info['model'] = psutil.cpu_percent(interval=0.1) # Um "modelo" baseado no percentual de uso recente, para fins de demonstração
            info['cores'] = f"{psutil.cpu_count(logical=False)} físicos / {psutil.cpu_count(logical=True)} lógicos"
            freq = psutil.cpu_freq()
            info['frequencia'] = f"{freq.current:.0f} MHz (máx: {freq.max:.0f} MHz)" if freq else "N/A"

        except Exception as e:
            info['error'] = str(e)
        self.hardware_info['cpu'] = info


    def detect_memory(self):
        """Coleta informações sobre RAM."""
        try:
            mem = psutil.virtual_memory()
            info = {
                'total_gb': round(mem.total / (1024**3), 2),
                'percent': f"{mem.percent:.1f}%",
                'used_gb': round(mem.used / (1024**3), 2),
                'available_gb': round(mem.available / (1024**3), 2)
            }
        except Exception as e:
            info = {'error': str(e)}
        self.hardware_info['memory'] = info

    def detect_gpu(self):
        """Detecta informações de placa de vídeo usando WMI."""
        try:
            import wmi
            c = wmi.WMI()
            gpus = []
            for gpu in c.Win32_VideoController():
                name = gpu.Name or "Desconhecida"
                # Tentativa de obter memória e data
                mem_total = getattr(gpu, 'AdapterRAM', 0) // (1024**3) # em GB
                driver_version = gpu.DriverVersion or "N/A"
                driver_date = gpu.DriverDate or "N/A"

                gpus.append({
                    'name': name,
                    'memory_gb': round(mem_total, 1),
                    'driver_version': driver_version,
                    'driver_date': driver_date
                })

            self.hardware_info['gpu'] = gpus if gpus else {"error": "Nenhuma GPU detectada via WMI."}

        except Exception as e:
            self.hardware_info['gpu'] = {"error": f"Erro ao detectar GPU (WMI): {str(e)}. Tente executar como Admin."}


    def detect_motherboard(self):
        """Detecta informações da placa mãe e chipset."""
        try:
            import wmi
            c = wmi.WMI()
            # Busca por Win32_BaseBoard ou equivalente
            try:
                motherboard = c.Win32_BaseBoard()[0]
                info = {
                    'manufacturer': motherboard.Manufacturer or "N/A",
                    'product': motherboard.Product or "N/A"
                }
            except Exception:
                 # Fallback se Win32_BaseBoard não estiver disponível ou falhar
                info = {'manufacturer': 'N/A', 'product': 'Não detectável'}

            # Usamos a lógica de chipset que estava no main.py original para manter a funcionalidade
            chipset_patterns = {
                "Z890": "Intel Z890", "Z790": "Intel Z790", "H870": "Intel H870",
                "H770": "Intel H770", "B860": "Intel B860", "B760": "Intel B760",
                "Z690": "Intel Z690", "H670": "Intel H670", "B660": "Intel B660",
                "X870": "AMD X870", "X670E": "AMD X670E", "B650E": "AMD B650E",
                "X670": "AMD X670", "B650": "AMD B650",
            }
            mobo_name = info['product']
            mobo_upper = mobo_name.upper()
            chipset = "Detectado (Desconhecido)"
            for pattern, chipset in chipset_patterns.items():
                if pattern in mobo_upper:
                    chipset = chipset
                    break
            info['chipset'] = chipset

        except Exception as e:
            self.hardware_info['motherboard'] = {'error': str(e)}
        else:
             self.hardware_info['motherboard'] = {"manufacturer": self.hardware_info.get('motherboard', {}).get('manufacturer'),
                                                  "product": self.hardware_info.get('motherboard', {}).get('product'),
                                                  "chipset": self.hardware_info.get('motherboard', {}).get('chipset')}


    def detect_storage(self):
        """Detecta informações de armazenamento (SSD/HDD) usando WMI."""
        try:
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                model = getattr(disk, 'Model', '')
                media_type = getattr(disk, 'MediaType', None)

                if media_type == 4: # SSD
                    storage_info = "SSD"
                elif media_type == 3: # HDD (Rotativo)
                    storage_info = "HDD (Rotativo)"
                else:
                    # Fallback por nome do modelo
                    if 'SSD' in model.upper() or 'NVME' in model.upper():
                        storage_info = "SSD"
                    else:
                        storage_info = "Desconhecido"

                self.hardware_info['storage'] = f"{model}: {storage_info}"
        except Exception as e:
            self.hardware_info['storage'] = f"Erro ao detectar storage: {str(e)}"


# As classes de serviço deverão ser importadas ou definidas em seu próprio módulo (system_tweaks).
# O detector agora depende apenas do psutil/wmi, que são bibliotecas de detecção e não manipulação.