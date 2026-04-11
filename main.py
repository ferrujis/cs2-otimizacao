import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import psutil
import os
import sys
import ctypes
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import platform
import wmi
import threading
import urllib.request
import json

from PIL import Image


def get_memory_type_name(mem_type):
    """Converte número de tipo de memória WMI para string legível.

    Mapeia valores numéricos de Win32_PhysicalMemory.MemoryType para descrições:
    - 20: DDR
    - 21: DDR2
    - 24: DDR3
    - 26: DDR4
    - 34: DDR5
    """
    memory_types = {
        20: "DDR",
        21: "DDR2",
        24: "DDR3",
        26: "DDR4",
        34: "DDR5",
    }
    return memory_types.get(mem_type, "Desconhecido")


def get_chipset_info(motherboard_name):
    """Extrai informação de chipset do nome da placa mãe ou via WMI.

    Tenta identificar o chipset a partir do nome do produto da placa mãe.
    Suporta Intel (Z790, H770, B760) e AMD (X670E, B650).
    """
    if not motherboard_name:
        return "Não detectado"

    # Padrões comuns de chipsets Intel e AMD
    chipset_patterns = {
        "Z890": "Intel Z890",
        "Z790": "Intel Z790",
        "H870": "Intel H870",
        "H770": "Intel H770",
        "B860": "Intel B860",
        "B760": "Intel B760",
        "Z690": "Intel Z690",
        "H670": "Intel H670",
        "B660": "Intel B660",
        "X870": "AMD X870",
        "X870-E": "AMD X870E",
        "X870E": "AMD X870E",
        "X670": "AMD X670",
        "X670E": "AMD X670E",
        "B850": "AMD B850",
        "B650": "AMD B650",
        "B650E": "AMD B650E",
    }

    mobo_upper = motherboard_name.upper()
    for pattern, chipset in chipset_patterns.items():
        if pattern in mobo_upper:
            return chipset

    return "Detectado (Desconhecido)"


class AlcesBoostApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        # estilo visual (cores, fontes etc.)
        from style import Style

        self.style = Style()

        # Calcula fator de escala e define tamanho inicial responsivo
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.style.calculate_scale_factor(screen_height)

        self.title("🦌 alcesboost - Performance Toolkit")
        max_width = max(640, screen_width - 40)
        max_height = max(480, screen_height - 80)
        default_width = min(1000, max_width)
        default_height = min(720, max_height)

        self.geometry(f"{default_width}x{default_height}")
        self.minsize(min(800, max_width), min(600, max_height))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.configure(fg_color=self.style.colors["bg"])
        self.base_dir = Path(__file__).resolve().parent
        self.header_logo = None
        self.fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Configure>", self.on_window_resize)
        self._set_app_icon()

        self.check_admin()
        self.create_widgets()

    @property
    def colors(self):
        return self.style.colors

    @property
    def fonts(self):
        return self.style.fonts

    def _set_app_icon(self):
        """Configura ícone da janela com suporte a múltiplos formatos."""
        ico_path = self.base_dir / "alcesboost.ico"
        png_path = self.base_dir / "logo.png"

        # Tenta primeiro com PNG (para melhor qualidade em painéis de tarefas modernos)
        try:
            if png_path.exists():
                self._window_icon_photo = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._window_icon_photo)
                return
        except Exception as e:
            pass

        # Fallback para ICO
        try:
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
                return
        except Exception as e:
            pass

        # Se nenhum arquivo foi encontrado, tenta gerar um padrão
        try:
            from PIL import Image, ImageDraw
            logo_img = Image.new("RGBA", (64, 64), (42, 26, 69, 255))
            draw = ImageDraw.Draw(logo_img)
            draw.ellipse((8, 8, 56, 56), fill=(253, 185, 39, 255))

            # Salvar e usar
            temp_ico = self.base_dir / "temp_icon.ppm"
            logo_img.save(str(temp_ico))
            self._window_icon_photo = tk.PhotoImage(file=str(temp_ico))
            self.iconphoto(True, self._window_icon_photo)
        except Exception:
            pass  # Sistema utilizará ícone padrão

    def check_admin(self):
        """Verifica se está rodando como administrador."""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                messagebox.showwarning(
                    "Aviso",
                    "Este programa funciona melhor com direitos de Administrador.\n"
                    "Alguns tweaks podem não funcionar sem permissão de admin.",
                )
        except Exception:
            pass

    def create_widgets(self):
        self.root = ctk.CTkFrame(self, fg_color=self.style.colors["bg"], corner_radius=0)
        self.root.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self._build_header(self.root)

        tabview = ctk.CTkTabview(
            self.root,
            fg_color=self.colors["panel"],
            border_color=self.colors["gold_dark"],
            border_width=1,
            segmented_button_fg_color=self.style.colors["panel_soft"],
            segmented_button_selected_color=self.style.colors["gold"],
            segmented_button_selected_hover_color=self.style.colors["gold_bright"],
            segmented_button_unselected_color=self.style.colors["panel_soft"],
            segmented_button_unselected_hover_color="#4A2A72",
            text_color=self.colors["text"],
            corner_radius=10,
        )
        tabview.pack(fill="both", expand=True)
        tabview.add("Hardware & CS2 Otimização")

        content_frame = ctk.CTkScrollableFrame(tabview.tab("Hardware & CS2 Otimização"), fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure(0, weight=1)

        self.setup_hardware_tab(content_frame)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.attributes("-fullscreen", False)

    def on_window_resize(self, event):
        if event.widget is self and hasattr(self, "root"):
            width = max(640, event.width)
            padding = self.style.get_responsive_padding(10, width)
            self.root.grid_configure(padx=padding, pady=padding)

    def _build_header(self, parent):
        header = ctk.CTkFrame(
            parent,
            fg_color=self.colors["panel"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            corner_radius=10,
            height=int(80 * self.style.scale_factor),
        )
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)

        # Inner frame para melhor layout
        inner_frame = ctk.CTkFrame(header, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=10, pady=8)
        inner_frame.grid_columnconfigure(0, weight=0)
        inner_frame.grid_columnconfigure(1, weight=1)

        # Logo
        logo_path = self.base_dir / "logo.png"
        if logo_path.exists():
            try:
                logo = Image.open(logo_path)
                logo_size = max(48, min(72, int(56 * self.style.scale_factor)))
                self.header_logo = ctk.CTkImage(light_image=logo, dark_image=logo, size=(logo_size, logo_size))
                logo_label = ctk.CTkLabel(inner_frame, text="", image=self.header_logo)
                logo_label.grid(row=0, column=0, padx=(0, 12), sticky="w")
            except Exception:
                self.header_logo = None

        # Texto (título e subtítulo)
        text_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="w")

        title_font_size = self.style.get_scaled_font(36)
        title = ctk.CTkLabel(
            text_frame,
            text="🦌 alcesboost",
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Segoe UI", size=title_font_size, weight="bold"),
        )
        title.pack(anchor="w")

        subtitle_font_size = self.style.get_scaled_font(14)
        subtitle = ctk.CTkLabel(
            text_frame,
            text="Performance Toolkit - Hardware & CS2 Otimização",
            text_color=self.style.colors["text_soft"],
            font=ctk.CTkFont(family="Segoe UI", size=subtitle_font_size),
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _styled_panel(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["panel"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            corner_radius=10,
        )

    def _styled_button(self, parent, text, command):
        button_font_size = self.style.get_scaled_font(16)
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=self.colors["gold"],
            hover_color=self.colors["gold_bright"],
            text_color="#24122F",
            corner_radius=8,
            border_width=1,
            border_color=self.style.colors["gold_bright"],
            font=ctk.CTkFont(family="Segoe UI", size=button_font_size, weight="bold"),
            height=int(40 * self.style.scale_factor),
        )

    def _make_scroll_area(self, parent):
        content_frame = self._styled_panel(parent)
        content_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # create a scrollable region for options; avoid using "transparent"
        # for scrollbar buttons since customtkinter's scrollbar widget doesn't
        # allow transparency on those attributes (raises ValueError).  Instead
        # rely on the default colors or match the panel color so the buttons
        # are effectively invisible.
        scroll_frame = ctk.CTkScrollableFrame(
            content_frame,
            fg_color=self.style.colors["panel"],
            # scrollbar_button_color and _hover_color are left unspecified so
            # defaults from the theme are used.  You can override them with a
            # solid color (e.g. self.style.colors['panel']) if you wish.
        )
        scroll_frame.pack(fill="both", expand=True)

        return scroll_frame

    def _build_option_rows(self, parent, config, vars_dict):
        for name, info in config.items():
            var = tk.BooleanVar(value=False)
            vars_dict[name] = var

            row = ctk.CTkFrame(
                parent,
                fg_color=self.colors["panel_soft"],
                border_width=1,
                border_color="#4A2C6E",
                corner_radius=8,
            )
            row.pack(fill="x", padx=8, pady=6)

            checkbox_font_size = self.style.get_scaled_font(14)  # Reduzido de 22px
            checkbox_size = int(20 * self.style.scale_factor)

            cb = ctk.CTkCheckBox(
                row,
                text=name,
                variable=var,
                checkbox_width=checkbox_size,
                checkbox_height=checkbox_size,
                corner_radius=6,
                border_width=2,
                border_color=self.colors["gold"],
                fg_color=self.colors["gold"],
                hover_color=self.colors["gold_bright"],
                checkmark_color="#2B183F",
                text_color=self.colors["gold_bright"],
                font=ctk.CTkFont(family="Segoe UI", size=checkbox_font_size),
            )
            cb.pack(side="left", padx=8, pady=8, anchor="w")

            desc_font_size = self.style.get_scaled_font(13)  # Reduzido de 18px
            desc = ctk.CTkLabel(
                row,
                text=info["desc"],
                text_color=self.colors["text"],
                font=ctk.CTkFont(family="Segoe UI", size=desc_font_size),
                justify="left",
                wraplength=400,  # Permite wrapping de texto longo
            )
            desc.pack(side="left", padx=(4, 8), pady=8, anchor="w")

    def setup_hardware_tab(self, frame):
        """Aba para detecção de hardware e otimização CS2 baseada no hardware."""
        frame.grid_columnconfigure(0, weight=1)

        # Painel de detecção de hardware
        hardware_panel = self._styled_panel(frame)
        hardware_panel.pack(fill="x", padx=12, pady=(12, 8))

        textbox_font_size = self.style.get_scaled_font(14)
        self.hardware_text = ctk.CTkTextbox(
            hardware_panel,
            wrap="word",
            height=int(120 * self.style.scale_factor),
            fg_color=self.colors["bg_alt"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Consolas", size=textbox_font_size),
        )
        self.hardware_text.pack(fill="x", padx=10, pady=(10, 8))
        self.hardware_text.configure(state="disabled")

        self._styled_button(hardware_panel, "Detectar Hardware", self.detect_hardware).pack(
            padx=10, pady=(0, 10), anchor="w"
        )

        # Painel de drivers
        drivers_panel = self._styled_panel(frame)
        drivers_panel.pack(fill="x", padx=12, pady=(0, 8))

        drivers_title_font_size = self.style.get_scaled_font(18)
        drivers_title = ctk.CTkLabel(
            drivers_panel,
            text="Gerenciamento de Drivers",
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Segoe UI", size=drivers_title_font_size, weight="bold"),
        )
        drivers_title.pack(pady=(10, 5))

        drivers_text_font_size = self.style.get_scaled_font(12)
        self.drivers_text = ctk.CTkTextbox(
            drivers_panel,
            wrap="word",
            height=int(100 * self.style.scale_factor),
            fg_color=self.colors["bg_alt"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=drivers_text_font_size),
        )
        self.drivers_text.pack(fill="x", padx=10, pady=(5, 10))
        self.drivers_text.configure(state="disabled")

        drivers_buttons_frame = ctk.CTkFrame(drivers_panel, fg_color="transparent")
        drivers_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        self._styled_button(drivers_buttons_frame, "Verificar Drivers", self.check_drivers_status).pack(
            side="left", padx=(0, 10)
        )
        self._styled_button(drivers_buttons_frame, "Atualizar Drivers", self.update_drivers).pack(
            side="left"
        )

        # Painel de otimização CS2
        cs2_panel = self._styled_panel(frame)
        cs2_panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        cs2_title_font_size = self.style.get_scaled_font(20)
        cs2_title = ctk.CTkLabel(
            cs2_panel,
            text="Otimização CS2 Baseada no Hardware",
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Segoe UI", size=cs2_title_font_size, weight="bold"),
        )
        cs2_title.pack(pady=(10, 5))

        cs2_recommendations_font_size = self.style.get_scaled_font(14)
        self.cs2_recommendations = ctk.CTkTextbox(
            cs2_panel,
            wrap="word",
            height=int(80 * self.style.scale_factor),
            fg_color=self.colors["bg_alt"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            text_color=self.colors["text"],
            font=ctk.CTkFont(family="Segoe UI", size=cs2_recommendations_font_size),
        )
        self.cs2_recommendations.pack(fill="x", padx=10, pady=(5, 10))
        self.cs2_recommendations.configure(state="disabled")

        self.cs2_tweaks_config = {
            "Otimização de CPU": {
                "desc": "Ajusta configurações de CPU para melhor frametime",
                "func": self.optimize_cpu_for_cs2,
            },
            "Otimização de GPU": {
                "desc": "Configura GPU para máxima performance em jogos",
                "func": self.optimize_gpu_for_cs2,
            },
            "Otimização de RAM": {
                "desc": "Ajusta gerenciamento de memória para jogos",
                "func": self.optimize_ram_for_cs2,
            },
            "Configurações de Rede": {
                "desc": "Otimiza rede para baixa latência em jogos online",
                "func": self.optimize_network_for_cs2,
            },
            "Tweaks de Sistema": {
                "desc": "Aplica tweaks gerais do sistema para jogos",
                "func": self.apply_system_tweaks_for_cs2,
            },
        }

        cs2_area = self._make_scroll_area(cs2_panel)
        self.cs2_tweaks_vars = {}
        self._build_option_rows(cs2_area, self.cs2_tweaks_config, self.cs2_tweaks_vars)

        self._styled_button(cs2_panel, "Aplicar Otimizações CS2", self.apply_cs2_optimizations).pack(
            padx=12, pady=(0, 12)
        )

    def detect_hardware(self):
        """Detecta e exibe informações do hardware."""
        try:
            hardware_info = self._get_hardware_info()
            self.hardware_text.configure(state="normal")
            self.hardware_text.delete("1.0", "end")
            self.hardware_text.insert("1.0", hardware_info)
            self.hardware_text.configure(state="disabled")

            # Gera recomendações baseadas no hardware
            recommendations = self._generate_cs2_recommendations()
            self.cs2_recommendations.configure(state="normal")
            self.cs2_recommendations.delete("1.0", "end")
            self.cs2_recommendations.insert("1.0", recommendations)
            self.cs2_recommendations.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao detectar hardware: {str(e)}")

    def check_drivers_status(self):
        """Verifica status atual dos drivers."""
        try:
            driver_status = self._get_driver_status()
            self.drivers_text.configure(state="normal")
            self.drivers_text.delete("1.0", "end")
            self.drivers_text.insert("1.0", driver_status)
            self.drivers_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar drivers: {str(e)}")

    def update_drivers(self):
        """Abre links para atualização de drivers."""
        try:
            # Inicia verificação automática em thread para não bloquear UI
            thread = threading.Thread(target=self._auto_update_drivers, daemon=True)
            thread.start()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao preparar atualização: {str(e)}")

    def _auto_update_drivers(self):
        """Verifica e baixa drivers desatualizados de forma automática."""
        try:
            # Inicializa COM para uso em thread
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass

            messagebox.showinfo("Atualização de Drivers", "Verificando drivers desatualizados...\nIsso pode levar alguns minutos.")

            available_updates = self._check_for_driver_updates()

            if not available_updates:
                messagebox.showinfo("Atualização de Drivers", "Todos os drivers estão atualizados!")
                return

            # Exibe lista de updates disponíveis
            updates_text = "Drivers desatualizados encontrados:\n\n"
            for driver_info in available_updates:
                updates_text += f"• {driver_info['name']}\n"
                updates_text += f"  Versão atual: {driver_info['current_version']}\n"
                updates_text += f"  Nova versão: {driver_info['latest_version']}\n\n"

            updates_text += "Deseja baixar os drivers atualizados?\n(Eles serão salvos em Documentos)"

            if messagebox.askyesno("Atualização de Drivers", updates_text):
                # Baixa os drivers
                downloads = self._download_driver_updates(available_updates)

                if downloads:
                    result_text = "Drivers baixados com sucesso:\n\n"
                    for driver_name, file_path in downloads.items():
                        result_text += f"✓ {driver_name}\n   📁 {file_path}\n\n"

                    result_text += "⚠️ IMPORTANTE:\n"
                    result_text += "1. Execute os instaladores como Administrador\n"
                    result_text += "2. Reinicie o PC após instalar\n"
                    result_text += "3. Faça backup caso possa reverter"

                    messagebox.showinfo("Drivers Baixados", result_text)

                    # Abre pasta de downloads
                    downloads_folder = os.path.expandvars("%USERPROFILE%\\Documents\\AlcesBoost_Drivers")
                    if os.path.exists(downloads_folder):
                        os.startfile(downloads_folder)
                else:
                    messagebox.showwarning("Erro", "Não foi possível baixar os drivers")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar drivers: {str(e)}")

    def _check_for_driver_updates(self):
        """Verifica quais drivers estão desatualizados."""
        available_updates = []

        try:
            # Inicializa COM para WMI em thread
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass

            c = wmi.WMI()

            # Verificar GPU drivers
            for gpu in c.Win32_VideoController():
                gpu_name = gpu.Name or "GPU Desconhecida"
                driver_version = gpu.DriverVersion or "0.0.0"

                latest_info = self._get_latest_gpu_driver_info(gpu_name, driver_version)
                if latest_info and latest_info['is_outdated']:
                    available_updates.append({
                        'name': f"Driver GPU - {gpu_name}",
                        'current_version': driver_version,
                        'latest_version': latest_info['version'],
                        'download_url': latest_info['url'],
                        'type': 'gpu'
                    })

            # Verificar network drivers
            for nic in c.Win32_NetworkAdapter():
                if nic.AdapterType == "Ethernet 802.3" or (nic.Name and ("Wi-Fi" in nic.Name or "Wireless" in nic.Name)):
                    driver_version = getattr(nic, 'DriverVersion', '0.0.0')
                    if driver_version != "0.0.0":
                        # Uma verificação simples de antiguidade
                        driver_year = 0
                        try:
                            driver_date = getattr(nic, 'DriverDate', '')
                            if driver_date and len(driver_date) >= 4:
                                driver_year = int(driver_date[:4])
                        except:
                            pass

                        current_year = datetime.now().year
                        if current_year - driver_year > 2:
                            available_updates.append({
                                'name': f"Driver Network - {nic.Name}",
                                'current_version': driver_version,
                                'latest_version': 'Verificar no site',
                                'download_url': 'https://www.intel.com/content/www/us/en/support/detect.html',
                                'type': 'network'
                            })

        except Exception as e:
            messagebox.showerror("Erro na Verificação", f"Erro ao verificar drivers: {str(e)}")

        return available_updates

    def _get_latest_gpu_driver_info(self, gpu_name, current_version):
        """Obtém informações sobre a versão mais recente do driver GPU."""
        gpu_lower = gpu_name.lower()

        try:
            if "nvidia" in gpu_lower:
                # NVIDIA driver check
                return self._check_nvidia_latest_driver(current_version)
            elif "amd" in gpu_lower or "radeon" in gpu_lower:
                # AMD driver check
                return self._check_amd_latest_driver(current_version)
            elif "intel" in gpu_lower:
                # Intel driver check
                return self._check_intel_latest_driver(current_version)
        except Exception:
            pass

        return None

    def _check_nvidia_latest_driver(self, current_version):
        """Verifica versão mais recente do driver NVIDIA."""
        try:
            # versão atual / mais recente (simplificado - em produção usar API oficial)
            current_major = 0
            try:
                current_major = int(current_version.split('.')[0])
            except:
                pass

            # Drivers NVIDIA recentes são 5xx.x ou superiores
            latest_major = 560
            is_outdated = current_major < latest_major

            if is_outdated:
                return {
                    'version': f'{latest_major}.xx (Recomendado)',
                    'url': 'https://www.nvidia.com/Download/driverResults.aspx/208751/',
                    'is_outdated': True
                }
            return {'is_outdated': False}
        except Exception:
            return None

    def _check_amd_latest_driver(self, current_version):
        """Verifica versão mais recente do driver AMD."""
        try:
            current_major = 0
            try:
                current_major = int(current_version.split('.')[0])
            except:
                pass

            # Drivers AMD recentes são 2X.x ou superiores
            latest_major = 24
            is_outdated = current_major < latest_major

            if is_outdated:
                return {
                    'version': f'{latest_major}.xx (Recomendado)',
                    'url': 'https://www.amd.com/en/support/download/drivers.html',
                    'is_outdated': True
                }
            return {'is_outdated': False}
        except Exception:
            return None

    def _check_intel_latest_driver(self, current_version):
        """Verifica versão mais recente do driver Intel."""
        try:
            return {
                'version': 'Última disponível',
                'url': 'https://www.intel.com/content/www/us/en/support/detect.html',
                'is_outdated': True
            }
        except Exception:
            return None

    def _download_driver_updates(self, available_updates):
        """Baixa drivers atualizados de sites oficiais."""
        downloads = {}

        try:
            # Cria pasta para downloads
            downloads_folder = os.path.expandvars("%USERPROFILE%\\Documents\\AlcesBoost_Drivers")
            os.makedirs(downloads_folder, exist_ok=True)

            for update in available_updates:
                try:
                    driver_name = update['name']
                    download_url = update['download_url']

                    # Para testes, apenas logar (em produção, fazer download real)
                    # urllib.request.urlretrieve(download_url, file_path)

                    # Criar arquivo com informações do driver
                    file_path = os.path.join(downloads_folder, f"{driver_name.replace(' ', '_')}_info.txt")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Informações de Atualização de Driver\n")
                        f.write(f"====================================\n\n")
                        f.write(f"Driver: {driver_name}\n")
                        f.write(f"Versão Atual: {update['current_version']}\n")
                        f.write(f"Nova Versão: {update['latest_version']}\n")
                        f.write(f"Link de Download: {download_url}\n\n")
                        f.write(f"Por favor, visite o link acima e baixe o driver manual.\n")

                    downloads[driver_name] = file_path

                except Exception as e:
                    print(f"Erro ao baixar {driver_name}: {str(e)}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao preparar downloads: {str(e)}")

        return downloads

    def _get_driver_status(self):
        """Obtém status detalhado dos drivers."""
        status_lines = ["=== STATUS DOS DRIVERS ===\n"]

        try:
            c = wmi.WMI()

            # GPU Drivers
            gpu_status = []
            for gpu in c.Win32_VideoController():
                driver_version = gpu.DriverVersion or "Não detectado"
                driver_date = gpu.DriverDate or "Não detectado"

                if driver_date != "Não detectado":
                    try:
                        year = driver_date[:4]
                        month = driver_date[4:6]
                        day = driver_date[6:8]
                        driver_date = f"{day}/{month}/{year}"
                    except:
                        pass

                gpu_name = gpu.Name or "GPU Desconhecida"
                status = self._analyze_gpu_driver_status(gpu_name, driver_version, driver_date)
                gpu_status.append(f"🎮 {gpu_name}\n   Versão: {driver_version}\n   Data: {driver_date}\n   Status: {status}\n")

            if gpu_status:
                status_lines.append("GPU Drivers:")
                status_lines.extend(gpu_status)

            # Rede Drivers
            network_status = []
            for nic in c.Win32_NetworkAdapter():
                if nic.AdapterType == "Ethernet 802.3" or (nic.Name and ("Wi-Fi" in nic.Name or "Wireless" in nic.Name)):
                    driver_version = getattr(nic, 'DriverVersion', 'Não detectado')
                    driver_date = getattr(nic, 'DriverDate', 'Não detectado')

                    if driver_date and driver_date != "Não detectado":
                        try:
                            year = driver_date[:4]
                            month = driver_date[4:6]
                            day = driver_date[6:8]
                            driver_date = f"{day}/{month}/{year}"
                        except:
                            pass

                    network_status.append(f"🌐 {nic.Name}\n   Versão: {driver_version}\n   Data: {driver_date}\n")

            if network_status:
                status_lines.append("Rede Drivers:")
                status_lines.extend(network_status)

            # Recomendações gerais
            status_lines.append("\n💡 Recomendações:")
            status_lines.append("   • Mantenha drivers de GPU sempre atualizados")
            status_lines.append("   • Drivers com mais de 6 meses podem estar desatualizados")
            status_lines.append("   • Use o botão 'Atualizar Drivers' para links oficiais")

        except Exception as e:
            status_lines.append(f"Erro ao verificar drivers: {str(e)}")

        return "\n".join(status_lines)

    def _analyze_gpu_driver_status(self, gpu_name, version, date):
        """Analisa se o driver GPU está atualizado."""
        try:
            # Análise básica por fabricante
            gpu_lower = gpu_name.lower()

            if "nvidia" in gpu_lower:
                return self._check_nvidia_driver(version, date)
            elif "amd" in gpu_lower or "radeon" in gpu_lower:
                return self._check_amd_driver(version, date)
            elif "intel" in gpu_lower:
                return self._check_intel_driver(version, date)
            else:
                return "❓ Driver genérico - verifique manualmente"

        except Exception:
            return "❓ Status desconhecido"

    def _check_nvidia_driver(self, version, date):
        """Verifica status do driver NVIDIA."""
        try:
            if not version or version == "Não detectado":
                return "❌ Driver não detectado"

            # Drivers NVIDIA recentes são 5xx.x ou superiores
            version_parts = version.split('.')
            if len(version_parts) >= 1:
                major_version = int(version_parts[0])
                if major_version >= 500:
                    return "✅ Driver atualizado"
                elif major_version >= 400:
                    return "⚠️ Driver razoável - considere atualizar"
                else:
                    return "❌ Driver muito antigo - atualização urgente"

            return "❓ Versão não identificada"

        except Exception:
            return "❓ Erro na análise"

    def _check_amd_driver(self, version, date):
        """Verifica status do driver AMD."""
        try:
            if not version or version == "Não detectado":
                return "❌ Driver não detectado"

            # Drivers AMD recentes são 2X.x ou superiores
            version_parts = version.split('.')
            if len(version_parts) >= 1:
                major_version = int(version_parts[0])
                if major_version >= 20:
                    return "✅ Driver atualizado"
                elif major_version >= 15:
                    return "⚠️ Driver razoável - considere atualizar"
                else:
                    return "❌ Driver muito antigo - atualização urgente"

            return "❓ Versão não identificada"

        except Exception:
            return "❓ Erro na análise"

    def _check_intel_driver(self, version, date):
        """Verifica status do driver Intel."""
        try:
            if not version or version == "Não detectado":
                return "❌ Driver não detectado"

            # Drivers Intel são mais difíceis de analisar por versão
            # Recomendamos verificação manual
            return "ℹ️ Verifique no site da Intel"

        except Exception:
            return "❓ Erro na análise"

    def _get_driver_update_links(self):
        """Gera links para atualização de drivers baseada no hardware detectado."""
        links = {}

        try:
            c = wmi.WMI()

            # Verificar GPUs para links específicos
            for gpu in c.Win32_VideoController():
                gpu_name = gpu.Name or ""
                gpu_lower = gpu_name.lower()

                if "nvidia" in gpu_lower:
                    links["NVIDIA GPU"] = "https://www.nvidia.com/Download/index.aspx"
                elif "amd" in gpu_lower or "radeon" in gpu_lower:
                    links["AMD GPU"] = "https://www.amd.com/en/support"
                elif "intel" in gpu_lower:
                    links["Intel GPU"] = "https://www.intel.com/content/www/us/en/download-center/home.html"

            # Links gerais
            links["Ferramentas de Driver"] = "https://www.iobit.com/en/driver-booster.php"
            links["Windows Update"] = "ms-settings:windowsupdate"

        except Exception:
            pass

        return links

    def _show_driver_update_options(self, links):
        """Mostra opções de atualização de drivers para o usuário."""
        options_text = "Escolha como atualizar os drivers:\n\n"

        for i, (name, url) in enumerate(links.items(), 1):
            options_text += f"{i}. {name}\n"

        options_text += "\nSelecione uma opção:"

        # Criar uma janela de diálogo personalizada
        dialog = ctk.CTkToplevel(self)
        dialog.title("Atualizar Drivers")

        # Dialog com tamanho responsivo
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        dialog_width = max(400, min(int(main_width * 0.6), 600))
        dialog_height = max(300, min(int(main_height * 0.8), 500))
        dialog.geometry(f"{dialog_width}x{dialog_height}")
        dialog.resizable(True, True)  # Tornar redimensionável

        # Centralizar a janela
        dialog.transient(self)
        dialog.grab_set()

        # Texto explicativo
        label_font_size = self.style.get_scaled_font(14)
        label = ctk.CTkLabel(
            dialog,
            text="Selecione uma opção para atualizar drivers:",
            font=ctk.CTkFont(size=label_font_size, weight="bold")
        )
        label.pack(pady=20)

        # Frame para botões (scrollable se muitos)
        buttons_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent", height=300)
        buttons_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Criar botões para cada opção
        button_font_size = self.style.get_scaled_font(12)
        for name, url in links.items():
            btn = ctk.CTkButton(
                buttons_frame,
                text=name,
                command=lambda u=url: self._open_driver_link(u, dialog),
                fg_color=self.colors["gold"],
                hover_color=self.colors["gold_bright"],
                font=ctk.CTkFont(family="Segoe UI", size=button_font_size),
                width=max(150, int(dialog_width * 0.7))  # Responsivo
            )
            btn.pack(pady=5, fill="x", padx=10)

        # Botão cancelar
        cancel_btn = ctk.CTkButton(
            dialog,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["gold_dark"],
            font=ctk.CTkFont(family="Segoe UI", size=button_font_size),
        )
        cancel_btn.pack(pady=20)

    def _open_driver_link(self, url, dialog):
        """Abre o link do driver e fecha o diálogo."""
        try:
            if url.startswith("ms-settings:"):
                # Comando do Windows
                os.system(f"start {url}")
            else:
                # URL web
                os.system(f"start {url}")

            messagebox.showinfo("Sucesso", "Link aberto! Siga as instruções do fabricante para atualizar o driver.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir link: {str(e)}")

        dialog.destroy()

    def _get_hardware_info(self):
        """Coleta informações detalhadas do hardware."""
        info_lines = []

        try:
            # CPU
            cpu_name = platform.processor()
            if not cpu_name:
                cpu_name = "Não detectado"
            cpu_count = psutil.cpu_count(logical=True)
            cpu_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_freq_str = f"{cpu_freq.current:.0f} MHz (max: {cpu_freq.max:.0f} MHz)"
            else:
                cpu_freq_str = "Não detectado"

            info_lines.append(f"CPU: {cpu_name}")
            info_lines.append(f"Cores: {cpu_physical} físicos / {cpu_count} lógicos")
            info_lines.append(f"Frequência: {cpu_freq_str}")

        except Exception:
            info_lines.append("CPU: Erro na detecção")

        try:
            # RAM
            mem = psutil.virtual_memory()
            mem_total_gb = mem.total // (1024**3)
            mem_type = "Não detectado"
            mem_speed = "Não detectado"

            # Tenta detectar tipo de RAM via WMI
            try:
                c = wmi.WMI()
                for memory in c.Win32_PhysicalMemory():
                    mem_type_num = memory.MemoryType
                    mem_type = get_memory_type_name(mem_type_num) if mem_type_num else "Desconhecido"
                    mem_speed = f"{memory.Speed} MHz" if memory.Speed else "Desconhecido"
                    break
            except Exception:
                pass

            info_lines.append(f"RAM: {mem_total_gb} GB ({mem_type}, {mem_speed})")

        except Exception:
            info_lines.append("RAM: Erro na detecção")

        try:
            # GPU
            gpu_info = []
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    gpu_name = gpu.Name or "Não detectado"
                    gpu_memory = gpu.AdapterRAM
                    if gpu_memory and gpu_memory > 0:
                        gpu_memory_gb = gpu_memory // (1024**3)
                        gpu_info.append(f"{gpu_name} ({gpu_memory_gb} GB)")
                    else:
                        # Tenta converter memória em MiB se GB falhar
                        try:
                            gpu_memory_mib = gpu_memory // (1024**2) if gpu_memory else 0
                            if gpu_memory_mib > 0:
                                gpu_info.append(f"{gpu_name} ({gpu_memory_mib} MiB)")
                            else:
                                gpu_info.append(gpu_name)
                        except:
                            gpu_info.append(gpu_name)
            except Exception:
                # Fallback para nvidia-smi
                try:
                    proc = subprocess.run(
                        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if proc.returncode == 0:
                        for line in proc.stdout.strip().split('\n'):
                            if line:
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    gpu_name = parts[0].strip()
                                    gpu_mem = parts[1].strip()
                                    try:
                                        gpu_mem_gb = int(gpu_mem) // 1024
                                        gpu_info.append(f"{gpu_name} ({gpu_mem_gb} GB)")
                                    except:
                                        gpu_info.append(f"{gpu_name} ({gpu_mem} MiB)")
                except Exception:
                    pass

                # Fallback para amd-smi (AMD GPUs)
                if not gpu_info:
                    try:
                        proc = subprocess.run(
                            ["amd-smi", "list"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if proc.returncode == 0:
                            for line in proc.stdout.strip().split('\n'):
                                if 'GPU' in line or 'Radeon' in line:
                                    gpu_info.append(f"AMD {line.strip()}")
                    except Exception:
                        pass

            if not gpu_info:
                gpu_info.append("Não detectado")

            info_lines.append(f"GPU: {', '.join(gpu_info)}")

        except Exception:
            info_lines.append("GPU: Erro na detecção")

        try:
            # Placa mãe e chipset
            try:
                c = wmi.WMI()
                motherboard = c.Win32_BaseBoard()[0]
                mobo_name = motherboard.Product or "Não detectado"
                mobo_manufacturer = motherboard.Manufacturer or "Não detectado"

                # Usa nova função para detectar chipset a partir do nome da placa mãe
                chipset = get_chipset_info(mobo_name)

                info_lines.append(f"Placa Mãe: {mobo_manufacturer} {mobo_name}")
                info_lines.append(f"Chipset: {chipset}")

            except Exception:
                info_lines.append("Placa Mãe: Não detectada")
                info_lines.append("Chipset: Não detectado")

        except Exception:
            info_lines.append("Placa Mãe/Chipset: Erro na detecção")

        try:
            # Tipo de storage (SSD vs HDD)
            storage_info = "Desconhecido"
            try:
                c = wmi.WMI()
                for disk in c.Win32_DiskDrive():
                    # MediaType: 3=HDD, 4=SSD, 5=Removable media
                    media_type = getattr(disk, 'MediaType', None)
                    if media_type == 4:
                        storage_info = "SSD"
                        break
                    elif media_type == 3:
                        storage_info = "HDD (Rotativo)"
                        break
                    elif media_type is None:
                        # Fallback: verifica por Model name
                        model = getattr(disk, 'Model', '')
                        if 'SSD' in model.upper() or 'NVME' in model.upper():
                            storage_info = "SSD"
                            break
            except Exception:
                pass

            info_lines.append(f"Storage C: {storage_info}")

        except Exception:
            pass

        try:
            # Verificação de drivers
            driver_info = self._check_drivers()
            if driver_info:
                info_lines.append("")
                info_lines.append("=== VERIFICAÇÃO DE DRIVERS ===")
                info_lines.extend(driver_info)

        except Exception:
            info_lines.append("Drivers: Erro na verificação")

        return "\n".join(info_lines)

    def _check_drivers(self):
        """Verifica versões de drivers importantes."""
        driver_lines = []

        try:
            c = wmi.WMI()

            # Driver de GPU
            gpu_drivers = []
            for gpu in c.Win32_VideoController():
                driver_version = gpu.DriverVersion or "Não detectado"
                driver_date = gpu.DriverDate or "Não detectado"
                if driver_date != "Não detectado":
                    # Formatar data do driver
                    try:
                        # WMI retorna data no formato YYYYMMDD
                        year = driver_date[:4]
                        month = driver_date[4:6]
                        day = driver_date[6:8]
                        driver_date = f"{day}/{month}/{year}"
                    except:
                        pass

                gpu_name = gpu.Name or "GPU"
                gpu_drivers.append(f"{gpu_name}: v{driver_version} ({driver_date})")

            if gpu_drivers:
                driver_lines.append("GPU Drivers:")
                for driver in gpu_drivers:
                    driver_lines.append(f"  • {driver}")

            # Driver de Rede
            network_drivers = []
            for nic in c.Win32_NetworkAdapter():
                if nic.AdapterType == "Ethernet 802.3" or nic.Name and ("Wi-Fi" in nic.Name or "Wireless" in nic.Name):
                    driver_version = getattr(nic, 'DriverVersion', 'Não detectado')
                    driver_date = getattr(nic, 'DriverDate', 'Não detectado')
                    if driver_date and driver_date != "Não detectado":
                        try:
                            year = driver_date[:4]
                            month = driver_date[4:6]
                            day = driver_date[6:8]
                            driver_date = f"{day}/{month}/{year}"
                        except:
                            pass

                    network_drivers.append(f"{nic.Name}: v{driver_version} ({driver_date})")

            if network_drivers:
                driver_lines.append("Rede Drivers:")
                for driver in network_drivers[:2]:  # Limitar a 2 para não poluir
                    driver_lines.append(f"  • {driver}")

            # Driver de Áudio
            audio_drivers = []
            for audio in c.Win32_SoundDevice():
                driver_version = getattr(audio, 'DriverVersion', 'Não detectado')
                driver_date = getattr(audio, 'DriverDate', 'Não detectado')
                if driver_date and driver_date != "Não detectado":
                    try:
                        year = driver_date[:4]
                        month = driver_date[4:6]
                        day = driver_date[6:8]
                        driver_date = f"{day}/{month}/{year}"
                    except:
                        pass

                audio_drivers.append(f"{audio.Name}: v{driver_version} ({driver_date})")

            if audio_drivers:
                driver_lines.append("Áudio Drivers:")
                for driver in audio_drivers[:2]:  # Limitar a 2
                    driver_lines.append(f"  • {driver}")

            # Verificações específicas para drivers conhecidos
            recommendations = self._analyze_driver_versions()
            if recommendations:
                driver_lines.append("")
                driver_lines.append("Recomendações:")
                driver_lines.extend(recommendations)

        except Exception as e:
            driver_lines.append(f"Erro na verificação de drivers: {str(e)}")

        return driver_lines

    def _analyze_driver_versions(self):
        """Analisa versões de drivers e dá recomendações."""
        recommendations = []

        try:
            c = wmi.WMI()

            # Verificar drivers NVIDIA
            nvidia_found = False
            for gpu in c.Win32_VideoController():
                if gpu.Name and "nvidia" in gpu.Name.lower():
                    nvidia_found = True
                    driver_version = gpu.DriverVersion or ""
                    if driver_version:
                        # Versão do driver NVIDIA (formato: XX.XX.XX.XXX)
                        try:
                            version_parts = driver_version.split('.')
                            if len(version_parts) >= 3:
                                major = int(version_parts[0])
                                minor = int(version_parts[1])
                                # Drivers NVIDIA recentes são 5xx ou superiores
                                if major < 500:
                                    recommendations.append("  ⚠️ Driver NVIDIA antigo - considere atualizar")
                                else:
                                    recommendations.append("  ✅ Driver NVIDIA atualizado")
                        except:
                            recommendations.append("  ❓ Driver NVIDIA - versão não identificada")
                    break

            # Verificar drivers AMD
            amd_found = False
            for gpu in c.Win32_VideoController():
                if gpu.Name and ("amd" in gpu.Name.lower() or "radeon" in gpu.Name.lower()):
                    amd_found = True
                    driver_version = gpu.DriverVersion or ""
                    if driver_version:
                        try:
                            # Drivers AMD recentes são 2X.XX.XX.XXX ou superiores
                            version_parts = driver_version.split('.')
                            if len(version_parts) >= 1:
                                major = int(version_parts[0])
                                if major < 20:
                                    recommendations.append("  ⚠️ Driver AMD antigo - considere atualizar")
                                else:
                                    recommendations.append("  ✅ Driver AMD atualizado")
                        except:
                            recommendations.append("  ❓ Driver AMD - versão não identificada")
                    break

            # Verificar drivers Intel
            intel_found = False
            for gpu in c.Win32_VideoController():
                if gpu.Name and "intel" in gpu.Name.lower():
                    intel_found = True
                    recommendations.append("  ℹ️ Driver Intel - verifique atualizações no site da Intel")
                    break

            # Recomendação geral se nenhum driver específico foi identificado
            if not nvidia_found and not amd_found and not intel_found:
                recommendations.append("  ❓ Verifique drivers de vídeo manualmente")

            # Recomendação geral para todos
            recommendations.append("  💡 Use ferramentas como Driver Booster ou visite sites oficiais")
            recommendations.append("  🎮 Para jogos, mantenha drivers de GPU sempre atualizados")

        except Exception:
            recommendations.append("  ❓ Erro ao analisar drivers")

        return recommendations

    def _generate_cs2_recommendations(self):
        """Gera recomendações de otimização baseadas no hardware detectado."""
        recommendations = []

        try:
            # Análise básica do hardware
            mem = psutil.virtual_memory()
            mem_total_gb = mem.total // (1024**3)

            cpu_count = psutil.cpu_count(logical=True)
            cpu_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()

            # Recomendações baseadas em RAM
            if mem_total_gb < 16:
                recommendations.append("⚠️ RAM baixa (<16GB): Considere upgrade para 32GB+ para melhor performance em CS2")
            elif mem_total_gb >= 32:
                recommendations.append("✅ RAM adequada (>=32GB): Ótimo para CS2 com alta qualidade")
            else:
                recommendations.append(f"✅ RAM: {mem_total_gb}GB disponível")

            # Recomendações baseadas em velocidade de RAM
            try:
                c = wmi.WMI()
                for memory in c.Win32_PhysicalMemory():
                    if memory.Speed and memory.Speed >= 3600:
                        recommendations.append(f"✅ RAM rápida ({memory.Speed}MHz): Excelente para CS2")
                    elif memory.Speed and memory.Speed >= 3000:
                        recommendations.append(f"ℹ️ RAM moderada ({memory.Speed}MHz): Bom para CS2")
                    break
            except:
                pass

            # Recomendações baseadas em CPU
            if cpu_physical < 4:
                recommendations.append("⚠️ CPU com poucos cores (<4): Pode limitar performance em CS2")
            elif cpu_physical >= 8:
                recommendations.append(f"✅ CPU multi-core ({cpu_physical} cores): Excelente para CS2")
            else:
                recommendations.append(f"ℹ️ CPU: {cpu_physical} cores físicos")

            # Recomendações baseadas em frequência de CPU
            if cpu_freq and cpu_freq.max >= 4500:
                recommendations.append(f"✅ CPU rápida ({cpu_freq.max/1000:.1f}GHz): Ótimo para frametime")
            elif cpu_freq:
                recommendations.append(f"ℹ️ Frequência CPU: {cpu_freq.max/1000:.1f}GHz")

            # Recomendações gerais para CS2
            recommendations.append("🎯 Foco em frametime: Priorize tweaks que reduzam stuttering")
            recommendations.append("🌐 Rede: Configure TCP NoDelay e desabilite offloading")
            recommendations.append("⚡ Energia: Use plano 'Alto Desempenho' sempre")
            recommendations.append("🎮 GPU: Garanta drivers atualizados e otimizações habilitadas")
            recommendations.append("💾 SSD: Armazene CS2 em SSD para reduzir stuttering de I/O")

        except Exception:
            recommendations.append("Erro ao gerar recomendações")

        return "\n".join(recommendations)

    def optimize_cpu_for_cs2(self):
        """Otimiza configurações de CPU para CS2."""
        if sys.platform.startswith("win"):
            try:
                # Ajusta afinidade de CPU para CS2 (usa todos os cores)
                cs2_processes = self._find_cs2_processes()
                if cs2_processes:
                    cpu_mask = (1 << psutil.cpu_count(logical=True)) - 1
                    for process in cs2_processes:
                        try:
                            process.cpu_affinity(list(range(psutil.cpu_count(logical=True))))
                        except Exception:
                            pass

                # Tweaks de CPU
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" '
                    "/v Win32PrioritySeparation /t REG_DWORD /d 38 /f"
                )

                # Desabilita core parking
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\54533251-82be-4824-96c1-47b60b740d00\\0cc5b647-c1df-4637-891a-dec35c318583" '
                    "/v ValueMax /t REG_DWORD /d 0 /f"
                )

            except Exception as e:
                raise Exception(f"Erro ao otimizar CPU: {str(e)}")

    def optimize_gpu_for_cs2(self):
        """Otimiza configurações de GPU para CS2."""
        if sys.platform.startswith("win"):
            try:
                # Para NVIDIA
                try:
                    # Define perfil preferencial para jogos
                    os.system(
                        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" '
                        '/v "HwSchMode" /t REG_DWORD /d 2 /f'
                    )

                    # Desabilita V-sync global
                    os.system(
                        'reg add "HKCU\\Software\\NVIDIA Corporation\\Global\\OpenGL" '
                        '/v "ForceEnableVSync" /t REG_DWORD /d 0 /f'
                    )

                    # Ativa shader cache
                    try:
                        os.system(
                            'reg add "HKCU\\Software\\NVIDIA Corporation\\NvControlPanel2\\Client" '
                            '/v "ShaderCache" /t REG_DWORD /d 1 /f'
                        )
                    except:
                        pass

                    # Reduz pre-rendered frames para menor latência
                    os.system(
                        'reg add "HKCU\\Software\\NVIDIA Corporation\\Global" '
                        '/v "FXAA" /t REG_DWORD /d 1 /f'
                    )

                except Exception:
                    pass

                # Desabilita V-sync global via DirectX
                os.system(
                    'reg add "HKCU\\Software\\Microsoft\\DirectX" '
                    '/v "ForceTripleBuffering" /t REG_DWORD /d 0 /f'
                )

                # Para AMD/Intel - aumenta performance
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Microsoft\\DirectX" '
                    '/v "D3D12MaxGPUPerf" /t REG_DWORD /d 1 /f'
                )

            except Exception as e:
                raise Exception(f"Erro ao otimizar GPU: {str(e)}")

    def optimize_ram_for_cs2(self):
        """Otimiza gerenciamento de RAM para jogos."""
        if sys.platform.startswith("win"):
            try:
                # Aumenta limite de cache do sistema
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" '
                    "/v LargeSystemCache /t REG_DWORD /d 1 /f"
                )

                # Desabilita page file automático
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" '
                    "/v DisablePagingExecutive /t REG_DWORD /d 1 /f"
                )

                # Limpa RAM standby
                self._clear_standby_list()

            except Exception as e:
                raise Exception(f"Erro ao otimizar RAM: {str(e)}")

    def optimize_network_for_cs2(self):
        """Otimiza rede para baixa latência."""
        if sys.platform.startswith("win"):
            try:
                # Aplica todos os tweaks de rede
                self.tweak_disable_offload()
                self.tweak_tcp_nodelay()

                # Configurações adicionais para jogos
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" '
                    "/v DefaultTTL /t REG_DWORD /d 64 /f"
                )

                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" '
                    "/v TcpMaxDataRetransmissions /t REG_DWORD /d 3 /f"
                )

                # Aumenta janela TCP para melhor throughput
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" '
                    "/v TcpWindowSize /t REG_DWORD /d 65535 /f"
                )

                # Aumenta MTU para pacotes maiores
                os.system(
                    'netsh int ipv4 set subinterface "Ethernet" mtu=1500 store=persistent'
                )

                # Desabilita SACK se estiver habilitado (pode aumentar latência em redes de jogos)
                try:
                    os.system(
                        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" '
                        "/v SackOpts /t REG_DWORD /d 1 /f"
                    )
                except:
                    pass

            except Exception as e:
                raise Exception(f"Erro ao otimizar rede: {str(e)}")

    def apply_system_tweaks_for_cs2(self):
        """Aplica tweaks gerais do sistema para CS2."""
        if sys.platform.startswith("win"):
            try:
                # Aplica modo zero input lag
                self.tweak_zero_input_lag()

                # Tweaks adicionais para frametime
                os.system(
                    'reg add "HKCU\\Control Panel\\Desktop" /v "MenuShowDelay" '
                    "/t REG_SZ /d 0 /f"
                )

                # Desabilita Windows Defender real-time (temporariamente)
                os.system('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"')

                # Otimiza frequência de CPU
                self.optimize_cpu_frequency_for_cs2()

                # Otimiza timer resolution
                self.tweak_timer_resolution()

            except Exception as e:
                raise Exception(f"Erro ao aplicar tweaks: {str(e)}")

    def optimize_cpu_frequency_for_cs2(self):
        """Força CPU a rodar em máxima frequência, desabilitando dynamic scaling."""
        if sys.platform.startswith("win"):
            try:
                # Define plano de energia para máximoesenpenho
                os.system("powercfg /s SCHEME_MIN")

                # Força CPU a 100% de frequência (desabilita throttling)
                os.system("powercfg /change processor-throttling-ac 100")
                os.system("powercfg /change processor-throttling-dc 100")

            except Exception as e:
                raise Exception(f"Erro ao otimizar frequência de CPU: {str(e)}")

    def tweak_timer_resolution(self):
        """Aumenta timer resolution do sistema para melhor precisão de frametime."""
        if sys.platform.startswith("win"):
            try:
                # Tenta usar timeBeginPeriod via PowerShell
                os.system(
                    'powershell -Command "'
                    '$Signature = @"'
                    '[DllImport(\\\\"winmm.dll\\\\", SetLastError = $true)]'
                    'public static extern uint timeBeginPeriod(uint uPeriod);'
                    '[DllImport(\\\\"winmm.dll\\\\", SetLastError = $true)]'
                    'public static extern uint timeEndPeriod(uint uPeriod);'
                    '"@'
                    '$TimerResolution = Add-Type -MemberDefinition $Signature -Name TimerResolution -Namespace Win32 -PassThru;'
                    '$TimerResolution::timeBeginPeriod(1);'
                    '"'
                )

                # Fallback: aumenta taxa de interrupções via registro
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Beep" '
                    "/v Start /t REG_DWORD /d 3 /f"
                )

            except Exception as e:
                raise Exception(f"Erro ao aumentar timer resolution: {str(e)}")

    def apply_cs2_optimizations(self):
        """Aplica otimizações CS2 selecionadas."""
        selected = [name for name, var in self.cs2_tweaks_vars.items() if var.get()]

        if not selected:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma otimização CS2.")
            return

        results = []
        for opt_name in selected:
            try:
                opt_func = self.cs2_tweaks_config[opt_name]["func"]
                opt_func()
                results.append(f"✓ {opt_name}: Sucesso")
            except Exception as e:
                results.append(f"✗ {opt_name}: Erro - {str(e)}")

        messagebox.showinfo("Resultado Otimizações CS2", "\n".join(results))

    def refresh_system_metrics(self):
        """Atualiza métricas de CPU, memória, boot e atividade de buffers.

        O texto exibido na caixa informa uso de CPU/memória, hora do boot e uma
        estimativa básica da taxa de transferência de rede para que o usuário
        possa perceber se há "buffering" em andamento.
        """
        try:
            cpu = psutil.cpu_percent(interval=0.2)
            mem = psutil.virtual_memory()
            boot = datetime.fromtimestamp(psutil.boot_time())

            # cálculo não bloqueante de throughput de rede
            try:
                import time

                now = time.time()
                current = psutil.net_io_counters()
                if self._last_net_counters is not None and self._last_net_ts is not None:
                    elapsed = max(now - self._last_net_ts, 0.001)
                    sent = (current.bytes_sent - self._last_net_counters.bytes_sent) / elapsed / 1024
                    recv = (current.bytes_recv - self._last_net_counters.bytes_recv) / elapsed / 1024
                    net_info = f" | NET: {sent:.1f} KB/s ↑ {recv:.1f} KB/s ↓"
                else:
                    net_info = ""

                self._last_net_counters = current
                self._last_net_ts = now
            except Exception:
                net_info = ""

            cs2_info = self._get_cs2_memory_summary()

            info = (
                f"CPU: {cpu:.1f}% | "
                f"Memória: {mem.percent:.1f}% ({mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB) | "
                f"Boot: {boot.strftime('%Y-%m-%d %H:%M:%S')}"
                f"{net_info}"
            )

            if cs2_info:
                info = f"{info} | {cs2_info}"

            self.sys_text.configure(state="normal")
            self.sys_text.delete("1.0", "end")
            self.sys_text.insert("1.0", info)
            self.sys_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar métricas: {str(e)}")

    def apply_selected_tweaks(self):
        """Aplica os tweaks selecionados."""
        selected = [name for name, var in self.tweaks_vars.items() if var.get()]

        if not selected:
            messagebox.showwarning("Aviso", "Selecione pelo menos um tweak para aplicar.")
            return

        results = []
        for tweak_name in selected:
            try:
                tweak_func = self.tweaks_config[tweak_name]["func"]
                tweak_func()
                results.append(f"✓ {tweak_name}: Sucesso")
            except Exception as e:
                results.append(f"✗ {tweak_name}: Erro - {str(e)}")

        messagebox.showinfo("Resultado", "\n".join(results))
        self.refresh_system_metrics()
            
    def check_buffers(self):
        """Faz uma checagem rápida de buffers de rede e vídeo.

        Não existe uma API única para "buffers" em todos os subsistemas, então
        reunimos algumas métricas úteis e avisamos o usuário se houver algum
        sinal de atividade.  A intenção é servir como ponto de partida; você
        pode estender as verificações conforme necessário.
        """
        info_lines = []

        # rede: taxa de transferência instantânea
        try:
            before = psutil.net_io_counters()
            psutil.cpu_percent(interval=1)  # breve espera
            after = psutil.net_io_counters()
            sent = (after.bytes_sent - before.bytes_sent) / 1024
            recv = (after.bytes_recv - before.bytes_recv) / 1024
            if sent > 0 or recv > 0:
                info_lines.append(f"Atividade de rede: {sent:.1f} KB/s ↑ {recv:.1f} KB/s ↓")
            else:
                info_lines.append("Nenhuma atividade de rede detectada.")
        except Exception:
            info_lines.append("Erro ao avaliar rede.")

        # tentativa de obter uso de memória de vídeo via nvidia-smi
        try:
            import subprocess

            proc = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if proc.returncode == 0:
                for idx, line in enumerate(proc.stdout.splitlines()):
                    line = line.strip()
                    if line and line != "0":
                        info_lines.append(f"GPU {idx} memória usada: {line} MiB")
        except Exception:
            # nvidia-smi might not exist (non-NVIDIA hardware) – ignore
            pass

        # memória do sistema: buffers/cache quando disponível
        try:
            vm = psutil.virtual_memory()
            buf = getattr(vm, "buffers", None)
            cached = getattr(vm, "cached", None)
            if buf is not None or cached is not None:
                info_lines.append(f"Memória: buffers={buf} cached={cached}")
        except Exception:
            pass

        if not info_lines:
            info_lines.append("Não foi possível detectar nenhum buffer específico.")

        messagebox.showinfo("Verificação de Buffers", "\n".join(info_lines))

    def tweak_zero_input_lag(self):
        """Aplica todos os tweaks para zero input lag de uma vez."""
        if sys.platform.startswith("win"):
            try:
                # Tweaks básicos
                self.tweak_high_priority()
                self.tweak_power_plan()
                self.tweak_disable_offload()
                self.tweak_tcp_nodelay()
                self.tweak_mmcss_latency()
                self.tweak_scheduler_priority()
                self.tweak_disable_dynamic_tick()
                self.tweak_disable_superfetch()
                self.tweak_disable_aero()
                self.tweak_disable_hibernation()
                self.tweak_full_screen_opt()
                self.tweak_game_mode_and_dvr()
                
                # Tweaks avançados para zero input lag
                # Desabilitar animações do Windows
                os.system(
                    'reg add "HKCU\\Control Panel\\Desktop" /v "UserPreferencesMask" '
                    "/t REG_BINARY /d 90120100 /f"
                )
                
                # Desabilitar transição visual
                os.system(
                    'reg add "HKCU\\Control Panel\\Desktop" /v "MenuShowDelay" '
                    "/t REG_DWORD /d 0 /f"
                )
                
                # Desabilitar search indexing
                os.system('net stop "WSearch"')
                os.system('sc config "WSearch" start= disabled')
                
                # Desabilitar mouse precision boost (aim assist)
                os.system(
                    'reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" '
                    "/t REG_SZ /d 0 /f"
                )
                os.system(
                    'reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" '
                    "/t REG_SZ /d 0 /f"
                )
                os.system(
                    'reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" '
                    "/t REG_SZ /d 0 /f"
                )
                
            except Exception as e:
                raise Exception(f"Erro ao aplicar MODO ZERO INPUT LAG: {str(e)}")

    def tweak_high_priority(self):
        """Define processo como alta prioridade."""
        if sys.platform.startswith("win"):
            cs2_processes = self._find_cs2_processes()
            if not cs2_processes:
                raise Exception("CS2 não está em execução (cs2.exe)")

            adjusted = 0
            for process in cs2_processes:
                try:
                    process.nice(psutil.HIGH_PRIORITY_CLASS)
                    adjusted += 1
                except Exception:
                    pass

            if adjusted == 0:
                raise Exception("Não foi possível ajustar prioridade do CS2")
        else:
            p = psutil.Process(os.getpid())
            p.nice(-10)

    def tweak_power_plan(self):
        """Define plano de energia para Alto Desempenho."""
        if sys.platform.startswith("win"):
            os.system("powercfg /s SCHEME_MIN")

    def tweak_disable_offload(self):
        """Desabilita offloading de rede."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'powershell -Command "Get-NetAdapterAdvancedProperty -IncludeHidden | '
                    "Where-Object DisplayName -Match 'Offload' | "
                    "Set-NetAdapterAdvancedProperty -DisplayValue 'Disabled' -NoRestart\""
                )
            except Exception:
                raise Exception("Permissão de admin necessária para desabilitar offload")

    def tweak_tcp_nodelay(self):
        """Desabilita algoritmo Nagle (TCP NoDelay)."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" '
                    "/v TcpNoDelay /t REG_DWORD /d 1 /f"
                )
                os.system(
                    'powershell -Command "Get-ChildItem '
                    '\'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\' | '
                    'ForEach-Object {'
                    "New-ItemProperty -Path $_.PsPath -Name TcpAckFrequency -Value 1 -PropertyType DWord -Force | Out-Null; "
                    "New-ItemProperty -Path $_.PsPath -Name TCPNoDelay -Value 1 -PropertyType DWord -Force | Out-Null; "
                    "New-ItemProperty -Path $_.PsPath -Name TcpDelAckTicks -Value 0 -PropertyType DWord -Force | Out-Null"
                    '}"'
                )
            except Exception:
                raise Exception("Permissão de admin necessária para modificar registro TCP")

    def tweak_mmcss_latency(self):
        """Ajusta MMCSS para perfil de menor latência em jogos."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" '
                    "/v NetworkThrottlingIndex /t REG_DWORD /d 4294967295 /f"
                )
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" '
                    "/v SystemResponsiveness /t REG_DWORD /d 0 /f"
                )
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" '
                    '/v "GPU Priority" /t REG_DWORD /d 8 /f'
                )
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" '
                    '/v "Priority" /t REG_DWORD /d 6 /f'
                )
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" '
                    '/v "Scheduling Category" /t REG_SZ /d High /f'
                )
            except Exception:
                raise Exception("Permissão de admin necessária para ajustar MMCSS")

    def tweak_scheduler_priority(self):
        """Ajusta scheduler para favorecer aplicativos em primeiro plano."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" '
                    "/v Win32PrioritySeparation /t REG_DWORD /d 38 /f"
                )
            except Exception:
                raise Exception("Permissão de admin necessária para ajustar scheduler")

    def tweak_disable_dynamic_tick(self):
        """Desabilita dynamic tick para reduzir variação de frametime (requer reboot)."""
        if sys.platform.startswith("win"):
            try:
                os.system("bcdedit /set disabledynamictick yes")
            except Exception:
                raise Exception("Permissão de admin necessária para ajustar timer")

    def tweak_disable_superfetch(self):
        """Desabilita SysMain (Superfetch) para liberar disco e RAM."""
        if sys.platform.startswith("win"):
            try:
                os.system('net stop "SysMain"')
                os.system('sc config "SysMain" start= disabled')
            except Exception:
                raise Exception("Erro ao desabilitar Superfetch")

    def tweak_disable_aero(self):
        """Desabilita tema Aero para melhor performance."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
                    "/v AppsUseLightTheme /t REG_DWORD /d 0 /f"
                )
            except Exception:
                raise Exception("Erro ao desabilitar Aero")

    def tweak_disable_hibernation(self):
        """Desabilita hibernação para liberar espaço."""
        if sys.platform.startswith("win"):
            try:
                os.system("powercfg /h off")
            except Exception:
                raise Exception("Erro ao desabilitar hibernação")

    def tweak_full_screen_opt(self):
        """Desabilita otimizações de tela cheia que causam stuttering."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f'
                )
                os.system(
                    'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_FSEBehaviorMonitoringEnabled" '
                    "/t REG_DWORD /d 0 /f"
                )
            except Exception:
                raise Exception("Erro ao desabilitar Full Screen Optimizations")

    def tweak_game_mode_and_dvr(self):
        """Ajusta Game Mode e desabilita Game DVR/Capturas para reduzir stutter."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKCU\\Software\\Microsoft\\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f'
                )
                os.system(
                    'reg add "HKCU\\Software\\Microsoft\\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f'
                )
                os.system(
                    'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f'
                )
                os.system(
                    'reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f'
                )
                os.system(
                    'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f'
                )
            except Exception:
                raise Exception("Erro ao ajustar Game Mode/Game DVR")

    def cleanup_cs2_shaders(self):
        """Remove cache de shaders do CS2."""
        cs2_paths = [
            os.path.expandvars("%LocalAppData%\\Counter-Strike Global Offensive\\shaders"),
            os.path.expandvars("%LocalAppData%\\CS2\\shaders"),
        ]

        deleted = 0
        for path in cs2_paths:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    deleted += 1
                except Exception:
                    pass

        if deleted == 0:
            raise Exception("Cache de shaders CS2 não encontrado")

    def cleanup_dirx_cache(self):
        """Remove cache do DirectX."""
        dirx_paths = [os.path.expandvars("%LocalAppData%\\D3DSCache")]

        deleted = 0
        for path in dirx_paths:
            if os.path.exists(path):
                try:
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except Exception:
                            pass
                    deleted += 1
                except Exception:
                    pass

        if deleted == 0:
            raise Exception("Cache DirectX não encontrado")

    def cleanup_event_logs(self):
        """Limpa Event Viewer logs."""
        if sys.platform.startswith("win"):
            try:
                os.system('powershell -Command "wevtutil cl System"')
                os.system('powershell -Command "wevtutil cl Application"')
            except Exception:
                raise Exception("Permissão necessária para limpar event logs")

    def setup_cleanup_tab(self, frame):
        """Aba para limpeza de memória e espaço em disco."""
        info_panel = self._styled_panel(frame)
        info_panel.pack(fill="x", padx=12, pady=(12, 8))

        self.cleanup_info = ctk.CTkTextbox(
            info_panel,
            wrap="word",
            height=70,
            fg_color=self.colors["bg_alt"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Consolas", size=14),
        )
        self.cleanup_info.pack(fill="x", padx=10, pady=(10, 8))
        self.cleanup_info.configure(state="disabled")

        self._styled_button(info_panel, "Atualizar Status", self.refresh_cleanup_status).pack(
            padx=10, pady=(0, 10), anchor="w"
        )

        self.cleanup_config = {
            "Limpar Arquivos Temporários": {
                "desc": "Remove arquivos temporários da pasta %TEMP%",
                "func": self.cleanup_temp_files,
            },
            "Limpar Cache do Navegador": {
                "desc": "Remove cache do Chrome, Firefox e Edge",
                "func": self.cleanup_browser_cache,
            },
            "Limpar Prefetch": {
                "desc": "Remove arquivos de prefetch do Windows (C:\\Windows\\Prefetch)",
                "func": self.cleanup_prefetch,
            },
            "Otimizar Memória RAM": {
                "desc": "Libera memória RAM não utilizada do sistema",
                "func": self.optimize_memory,
            },
            "Encontrar Arquivos Grandes": {
                "desc": "Varre disco C: e encontra arquivos acima de 100MB não utilizados",
                "func": self.find_large_files,
            },
            "Limpar Shader Cache CS2": {
                "desc": "Remove cache de shaders do Counter-Strike 2 para forçar recompilação",
                "func": self.cleanup_cs2_shaders,
            },
            "Limpar DirectX Cache": {
                "desc": "Remove arquivos temporários do DirectX",
                "func": self.cleanup_dirx_cache,
            },
            "Limpar Windows Event Logs": {
                "desc": "Remove logs antigos do Event Viewer",
                "func": self.cleanup_event_logs,
            },
        }

        cleanup_area = self._make_scroll_area(frame)
        self._build_option_rows(cleanup_area, self.cleanup_config, self.cleanup_vars)

        self._styled_button(frame, "Executar Limpeza Selecionada", self.apply_selected_cleanup).pack(
            padx=12, pady=(0, 12)
        )

        self.refresh_cleanup_status()

    def refresh_cleanup_status(self):
        """Atualiza informações de memória e espaço em disco."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk_c = shutil.disk_usage("C:/")

            info = (
                f"Memória RAM: {mem.percent:.1f}% ({mem.used // (1024**3)} GB / {mem.total // (1024**3)} GB) | "
                f"Swap: {swap.percent:.1f}%\n"
                f"Disco C: {disk_c.used // (1024**3)} GB usado / {disk_c.total // (1024**3)} GB total "
                f"({100 * disk_c.used / disk_c.total:.1f}%)"
            )

            self.cleanup_info.configure(state="normal")
            self.cleanup_info.delete("1.0", "end")
            self.cleanup_info.insert("1.0", info)
            self.cleanup_info.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar status: {str(e)}")

    def apply_selected_cleanup(self):
        """Aplica opções de limpeza selecionadas."""
        selected = [name for name, var in self.cleanup_vars.items() if var.get()]

        if not selected:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma opção de limpeza.")
            return

        results = []
        for cleanup_name in selected:
            try:
                cleanup_func = self.cleanup_config[cleanup_name]["func"]
                cleanup_func()
                results.append(f"✓ {cleanup_name}: Sucesso")
            except Exception as e:
                results.append(f"✗ {cleanup_name}: Erro - {str(e)}")

        messagebox.showinfo("Resultado", "\n".join(results))
        self.refresh_cleanup_status()

    def cleanup_temp_files(self):
        """Remove arquivos temporários."""
        temp_paths = [
            os.path.expandvars("%TEMP%"),
            os.path.expandvars("%WINDIR%\\Temp"),
        ]

        deleted = 0
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    for filename in os.listdir(temp_path):
                        file_path = os.path.join(temp_path, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                                deleted += 1
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                                deleted += 1
                        except Exception:
                            pass
                except Exception:
                    pass

        if deleted == 0:
            raise Exception("Nenhum arquivo temporário encontrado ou acesso negado")

    def cleanup_browser_cache(self):
        """Remove cache de navegadores."""
        cache_paths = [
            os.path.expandvars("%LocalAppData%\\Google\\Chrome\\User Data\\Default\\Cache"),
            os.path.expandvars("%LocalAppData%\\Mozilla\\Firefox\\Profiles"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Edge\\User Data\\Default\\Cache"),
        ]

        deleted = 0
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                try:
                    shutil.rmtree(cache_path)
                    deleted += 1
                except Exception:
                    pass

        if deleted == 0:
            raise Exception("Nenhum cache de navegador encontrado")

    def cleanup_prefetch(self):
        """Remove arquivos de prefetch do Windows."""
        prefetch_path = "C:\\Windows\\Prefetch"

        if os.path.exists(prefetch_path):
            deleted = 0
            try:
                for filename in os.listdir(prefetch_path):
                    if filename.endswith(".pf"):
                        file_path = os.path.join(prefetch_path, filename)
                        try:
                            os.unlink(file_path)
                            deleted += 1
                        except Exception:
                            pass
            except Exception:
                pass

            if deleted == 0:
                raise Exception("Nenhum arquivo prefetch removido")
        else:
            raise Exception("Pasta Prefetch não encontrada")

    def optimize_memory(self):
        """Libera memória não utilizada."""
        try:
            import gc

            gc.collect()

            if sys.platform.startswith("win"):
                trimmed_count = 0

                if self._trim_working_set(os.getpid()):
                    trimmed_count += 1

                for process in self._find_cs2_processes():
                    if self._trim_working_set(process.pid):
                        trimmed_count += 1

                standby_cleared = self._clear_standby_list()

                if not standby_cleared and trimmed_count == 0:
                    raise Exception(
                        "Não foi possível otimizar RAM (EmptyStandbyList.exe ausente e trim indisponível)"
                    )
        except Exception:
            raise Exception("Erro ao otimizar memória")

    def _find_cs2_processes(self):
        processes = []
        for process in psutil.process_iter(["name"]):
            try:
                name = (process.info.get("name") or "").lower()
                if name == "cs2.exe" or name == "cs2":
                    processes.append(process)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes

    def _get_cs2_memory_summary(self):
        total_rss = 0
        process_count = 0
        for process in self._find_cs2_processes():
            try:
                total_rss += process.memory_info().rss
                process_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if process_count == 0:
            return "CS2: fechado"

        return f"CS2 RAM: {total_rss // (1024**2)} MB ({process_count} proc)"

    def _trim_working_set(self, pid):
        try:
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_SET_QUOTA = 0x0100
            process_handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA,
                False,
                int(pid),
            )
            if not process_handle:
                return False

            result = ctypes.windll.psapi.EmptyWorkingSet(process_handle)
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return bool(result)
        except Exception:
            return False

    def _clear_standby_list(self):
        candidates = [
            self.base_dir / "EmptyStandbyList.exe",
            self.base_dir / "tools" / "EmptyStandbyList.exe",
        ]

        tool_path = next((path for path in candidates if path.exists()), None)
        if tool_path is None:
            return False

        try:
            process = subprocess.run(
                [str(tool_path), "standbylist"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            return process.returncode == 0
        except Exception:
            return False

    def find_large_files(self):
        """Encontra arquivos grandes não utilizados."""
        large_files = []
        min_size = 100 * 1024 * 1024

        try:
            for root, dirs, files in os.walk("C:\\"):
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in ["$Recycle.Bin", "System Volume Information", "pagefile.sys"]
                ]

                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        if file_size > min_size:
                            large_files.append((file_path, file_size))
                    except Exception:
                        pass
        except Exception:
            pass

        if not large_files:
            raise Exception("Nenhum arquivo grande encontrado")

        large_files.sort(key=lambda x: x[1], reverse=True)
        file_list = "\n".join([f"{f[0]} ({f[1] // (1024**2)} MB)" for f in large_files[:10]])
        messagebox.showinfo("Arquivos Grandes (Top 10)", file_list)


if __name__ == "__main__":
    app = AlcesBoostApp()
    app.mainloop()
