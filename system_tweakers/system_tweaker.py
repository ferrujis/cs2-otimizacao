import psutil
import os
import subprocess
from typing import Dict, Any

# Assume that system_tweaks.py exists and contains WindowsSystemService
# from .system_tweaks import WindowsSystemService

class SystemTweaker:
    """Gerencia todas as otimizações de baixo nível do sistema operacional (SO) para jogos."""

    def __init__(self):
        self.success_count = 0
        self.fail_count = 0

    def apply_all_optimizations(self, selected_tweaks: list[str]) -> tuple[list[str], int]:
        """Aplica uma lista de otimizações selecionadas e retorna o status."""
        results = []
        for tweak_name in selected_tweaks:
            try:
                if hasattr(self, f"_{tweak_name.lower().replace(' ', '')}"):
                    method = getattr(self, f"_{tweak_name.lower().replace(' ', '')}")
                    method() # Executa o método como função
                    results.append(f"✅ {tweak_name}: Sucesso")
                else:
                    results.append(f"❓ {tweak_name}: Método não implementado ou removido.")
            except Exception as e:
                results.append(f"✗ {tweak_name}: Falha - {str(e)}")

        self.success_count = len([r for r in results if "Sucesso" in r])
        self.fail_count = len([r for r in results if "Falha" in r or "Erro" in r])
        return results, self.success_count + self.fail_count

    def _optimize_cpu(self):
        """Otimiza configurações de CPU para CS2."""
        if not WindowsSystemService.requires_admin():
             raise PermissionError("Administrador necessário para otimizar o CPU.")

        # 1. Afinidade de CPU (melhor prática)
        cs2_processes = self._find_process(b"cs2.exe")
        if cs2_processes:
            cpu_count = psutil.cpu_count(logical=True)
            try:
                for process in cs2_processes:
                    # Tenta limitar a afinidade aos cores disponíveis (melhor que o original de range)
                    process.cpu_affinity(list(range(psutil.cpu_count(logical=True))))
                print("CPU Affinity set.") # Feedback interno para debugging
            except Exception as e:
                 raise RuntimeError(f"Falha ao ajustar afinidade de CPU (pode ser por permissão): {str(e)}")

        # 2. Tweaks do Registro (manter a lógica original, mas encapsulada)
        WindowsSystemService.set_registry_value("HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl", "Win32PrioritySeparation", "Win32PrioritySeparation", "REG_DWORD", "38")

    def _optimize_gpu(self):
        """Otimiza configurações de GPU para CS2."""
        if not WindowsSystemService.requires_admin():
             raise PermissionError("Administrador necessário para otimizar a GPU.")

        # Lógica encapsulada aqui, usando apenas comandos do sistema e o serviço.
        print("GPU optimization logic placeholder executed.")
        WindowsSystemService.set_registry_value(
            "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers",
            None, "HwSchMode", "REG_DWORD", "2"
        )
        # Adicionar mais comandos de registro aqui...

    def _optimize_ram(self):
        """Otimiza gerenciamento de RAM para jogos."""
        if not WindowsSystemService.requires_admin():
             raise PermissionError("Administrador necessário para otimizar a memória.")

        WindowsSystemService.set_registry_value("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management", "LargeSystemCache", "LargeSystemCache", "REG_DWORD", "1")
        # Mais ajustes...

    def _optimize_network(self):
        """Otimiza rede para baixa latência."""
        if not WindowsSystemService.requires_admin():
             raise PermissionError("Administrador necessário para otimizar a rede.")

        # Chamadas de registro encapsuladas
        WindowsSystemService.set_registry_value("HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", "TcpNoDelay", "TCPNoDelay", "REG_DWORD", "1")


    def _apply_all_optimizations(self):
        """Função wrapper para aplicar todas as otimizações."""
        try:
            self._optimize_cpu()
            # self._optimize_gpu() # Descomentar se a lógica for completa e testada
            self._optimize_ram()
            self._optimize_network()
            return True, "Todas as otimizações aplicadas com sucesso (Verificar reinicialização)."
        except PermissionError as e:
             return False, str(e)
        except Exception as e:
             return False, f"Erro geral de otimização: {str(e)}"

    # --- Funções auxiliares internas ---

    def _find_process(self, process_name: bytes | str) -> list[psutil.Process]:
        """Encontra processos pelo nome."""
        processes = []
        for p in psutil.process_iter(['name']):
            try:
                name = p.info['name']
                if name == process_name or name.lower() == str(process_name).lower():
                    processes.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def cleanup_temp_files(self) -> tuple[int, str]:
        """Executa limpeza de arquivos temporários usando o serviço."""
        deleted_count, message = WindowsSystemService.cleanup_temp_files()
        return deleted_count, f"{message} {', '.join([f'{c} ({count} files)' for c in ['Windows\\Temp'] if count > 0])}"

    def cleanup_prefetch(self) -> tuple[int, str]:
        """Executa limpeza de arquivos prefetch."""
        return WindowsSystemService.cleanup_prefetch()

# Este módulo centraliza a lógica complexa de modificação do SO e deve ser chamado pela UI.