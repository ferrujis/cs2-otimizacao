import ctypes
import os
import subprocess
import sys

class WindowsSystemService:
    """Classe utilitária para encapsular comandos e interações perigosas com o SO (Registro, PowerShell).
    Isola a lógica de baixo nível do sistema operacional.
    """

    @staticmethod
    def requires_admin():
        """Verifica se o processo está rodando com privilégios elevados."""
        if sys.platform != "win32":
            return False # Não aplica em outros SOs
        try:
            # Tenta acessar uma API que requer admin
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return True # Assume true se falhar, para não bloquear o app

    @staticmethod
    def run_command(command: str, description: str) -> tuple[bool, str]:
        """Executa um comando shell e retorna sucesso/falha junto com a saída."""
        if not WindowsSystemService.requires_admin():
            return False, f"Erro de Permissão: Este comando requer permissões de Administrador para rodar."

        try:
            # Usa subprocess.run em vez de os.system para melhor controle e segurança
            process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
            return True, process.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Falha ao executar comando ({description}): {e.stderr}"
        except Exception as e:
            return False, f"Erro geral ao executar o comando ({description}): {str(e)}"

    @staticmethod
    def set_registry_value(hkey: str, subkey: str, value_name: str, data_type: str, data_value: str) -> tuple[bool, str]:
        """Define um valor no Registro do Windows."""
        # Exemplo de comando que usa o REG_* apropriado para cada tipo.
        command = f'reg add "{hkey}\\{subkey}" /v "{value_name}" /t {data_type} /d {data_value} /f'
        success, output = WindowsSystemService.run_command(command, f"Definir Reg: {value_name}")
        return success, output

    @staticmethod
    def open_external_link(url: str) -> tuple[bool, str]:
        """Abre um link externo usando o sistema operacional padrão."""
        try:
            os.system(f'start "{url}"')
            return True, "Link aberto com sucesso."
        except Exception as e:
            return False, f"Falha ao abrir o link: {str(e)}"

# Adiciona alguns métodos utilitários de SO para facilitar o uso em outras classes.
def get_temp_dir() -> str:
    """Retorna o diretório temporário do sistema."""
    return os.environ.get("TEMP", "C:\\Windows\\Temp")

def check_admin_status():
    """Verifica status de administrador sem retornar o valor, apenas uma string para feedback."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        return False

# Funções específicas para limpeza do SO (utilizadas em outro módulo)
def cleanup_temp_files() -> tuple[int, str]:
    """Remove arquivos temporários do sistema."""
    import shutil
    temp_path = get_temp_dir()
    deleted_count = 0
    try:
        for filename in os.listdir(temp_path):
            file_path = os.path.join(temp_path, filename)
            if os.path.isfile(file_path) or os.path.isdir(file_path):
                shutil.rmtree(file_path)
                deleted_count += 1
        return deleted_count, f"Arquivos temporários em '{temp_path}' limpos com sucesso."
    except Exception as e:
        return -1, f"Erro ao limpar arquivos temporários: {str(e)}"

def cleanup_prefetch() -> tuple[int, str]:
    """Remove arquivos de prefetch do Windows."""
    prefetch_path = "C:\\Windows\\Prefetch"
    deleted_count = 0
    try:
        for filename in os.listdir(prefetch_path):
            file_path = os.path.join(prefetch_path, filename)
            if filename.endswith(".pf"):
                os.unlink(file_path)
                deleted_count += 1
        return deleted_count, f"Arquivos pré-fetch removidos com sucesso em {prefetch_path}."
    except Exception as e:
        return -1, f"Erro ao limpar arquivos prefetch: {str(e)}"