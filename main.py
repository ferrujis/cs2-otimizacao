import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import psutil
import os
import sys
import ctypes
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image


class AlcesBoostApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        # estilo visual (cores, fontes etc.)
        from style import Style

        self.style = Style()


        self.title("alcesboost")
        self.geometry("1000x720")
        self.minsize(900, 600)
        self.configure(fg_color=self.style.colors["bg"])
        self.base_dir = Path(__file__).resolve().parent
        self.header_logo = None
        self._set_app_icon()

        self.check_admin()
        self.tweaks_vars = {}
        self.cleanup_vars = {}
        self.create_widgets()

    @property
    def colors(self):
        return self.style.colors

    @property
    def fonts(self):
        return self.style.fonts

    def _set_app_icon(self):
        ico_path = self.base_dir / "alcesboost.ico"
        png_path = self.base_dir / "logo.png"

        try:
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
        except Exception:
            pass

        try:
            if png_path.exists():
                self._window_icon_photo = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._window_icon_photo)
        except Exception:
            pass

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
        root = ctk.CTkFrame(self, fg_color=self.style.colors["bg"], corner_radius=0)
        root.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_header(root)

        tabview = ctk.CTkTabview(
            root,
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
        tabview.add("Sistema & Tweaks")
        tabview.add("Limpeza")

        self.setup_system_tab(tabview.tab("Sistema & Tweaks"))
        self.setup_cleanup_tab(tabview.tab("Limpeza"))

    def _build_header(self, parent):
        header = ctk.CTkFrame(
            parent,
            fg_color=self.colors["panel"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            corner_radius=10,
            height=68,
        )
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)

        logo_path = self.base_dir / "logo.png"
        if logo_path.exists():
            try:
                logo = Image.open(logo_path)
                self.header_logo = ctk.CTkImage(light_image=logo, dark_image=logo, size=(48, 48))
                logo_label = ctk.CTkLabel(header, text="", image=self.header_logo)
                logo_label.pack(side="left", padx=(16, 6), pady=8)
            except Exception:
                self.header_logo = None

        title = ctk.CTkLabel(
            header,
            text="alcesboost",
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Segoe UI", size=38, weight="bold"),
        )
        title.pack(side="left", padx=10, pady=8)

        subtitle = ctk.CTkLabel(
            header,
            text="Performance Toolkit",
            text_color=self.style.colors["text_soft"],
            font=ctk.CTkFont(family="Segoe UI", size=16),
        )
        subtitle.pack(side="left", pady=12)

    def _styled_panel(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["panel"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            corner_radius=10,
        )

    def _styled_button(self, parent, text, command):
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
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            height=40,
        )

    def _make_scroll_area(self, parent):
        content_frame = self._styled_panel(parent)
        content_frame.pack(fill="both", expand=True, padx=12, pady=12)

        canvas = tk.Canvas(
            content_frame,
            bg=self.style.colors["panel"],
            highlightthickness=0,
            bd=0,
        )
        scroll = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)

        inner = ctk.CTkFrame(canvas, fg_color=self.style.colors["panel"])

        def on_config(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", on_config)

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        scroll.pack(side="right", fill="y", pady=2, padx=(0, 2))

        return inner

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

            cb = ctk.CTkCheckBox(
                row,
                text=name,
                variable=var,
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=6,
                border_width=2,
                border_color=self.colors["gold"],
                fg_color=self.colors["gold"],
                hover_color=self.colors["gold_bright"],
                checkmark_color="#2B183F",
                text_color=self.colors["gold_bright"],
                font=ctk.CTkFont(family="Segoe UI", size=22),
            )
            cb.pack(side="left", padx=8, pady=8, anchor="w")

            desc = ctk.CTkLabel(
                row,
                text=info["desc"],
                text_color=self.colors["text"],
                font=ctk.CTkFont(family="Segoe UI", size=18),
                justify="left",
            )
            desc.pack(side="left", padx=(4, 8), pady=8, anchor="w")

    def setup_system_tab(self, frame):
        info_panel = self._styled_panel(frame)
        info_panel.pack(fill="x", padx=12, pady=(12, 8))

        self.sys_text = ctk.CTkTextbox(
            info_panel,
            wrap="word",
            height=42,
            fg_color=self.colors["bg_alt"],
            border_width=1,
            border_color=self.colors["gold_dark"],
            text_color=self.colors["gold_bright"],
            font=ctk.CTkFont(family="Consolas", size=16),
        )
        self.sys_text.pack(fill="x", padx=10, pady=(10, 8))
        self.sys_text.configure(state="disabled")

        self._styled_button(info_panel, "Atualizar Métricas", self.refresh_system_metrics).pack(
            padx=10, pady=(0, 10), anchor="w"
        )

        self.tweaks_config = {
            "Prioridade Alta": {
                "desc": "Define o processo CS2 como alta prioridade no sistema operacional",
                "func": self.tweak_high_priority,
            },
            "Plano de Energia": {
                "desc": "Alterna para o plano de energia 'Alto Desempenho' do Windows",
                "func": self.tweak_power_plan,
            },
            "Desabilitar Offload": {
                "desc": "Desabilita offloading de rede (LSO, RSC) para menor latência",
                "func": self.tweak_disable_offload,
            },
            "TCP NoDelay": {
                "desc": "Desabilita algoritmo Nagle para reduzir latência na rede",
                "func": self.tweak_tcp_nodelay,
            },
            "Aumentar Buffer UDP": {
                "desc": "Aumenta tamanho dos buffers UDP para melhor recebimento de pacotes",
                "func": self.tweak_udp_buffer,
            },
            "Desabilitar Superfetch": {
                "desc": "Desabilita SysMain para reduzir uso de disco e melhorar frametime",
                "func": self.tweak_disable_superfetch,
            },
            "Desabilitar Aero Theme": {
                "desc": "Desabilita transparência do Windows para melhor performance",
                "func": self.tweak_disable_aero,
            },
            "Desabilitar Hibernação": {
                "desc": "Desabilita hibernação para liberar espaço em disco",
                "func": self.tweak_disable_hibernation,
            },
            "Full Screen Optimization": {
                "desc": "Desabilita otimizações de tela cheia que causam stutter",
                "func": self.tweak_full_screen_opt,
            },
            "Aumentar Virtual Memory": {
                "desc": "Aumenta memória virtual para maior espaço em cache",
                "func": self.tweak_virtual_memory,
            },
        }

        tweaks_area = self._make_scroll_area(frame)
        self._build_option_rows(tweaks_area, self.tweaks_config, self.tweaks_vars)

        self._styled_button(frame, "Aplicar Tweaks Selecionados", self.apply_selected_tweaks).pack(
            padx=12, pady=(0, 12)
        )

        self.refresh_system_metrics()

    def refresh_system_metrics(self):
        """Atualiza métricas de CPU, memória e tempo de boot."""
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            boot = datetime.fromtimestamp(psutil.boot_time())

            info = (
                f"CPU: {cpu:.1f}% | "
                f"Memória: {mem.percent:.1f}% ({mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB) | "
                f"Boot: {boot.strftime('%Y-%m-%d %H:%M:%S')}"
            )

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

    def tweak_high_priority(self):
        """Define processo como alta prioridade."""
        p = psutil.Process(os.getpid())
        if sys.platform.startswith("win"):
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
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
            except Exception:
                raise Exception("Permissão de admin necessária para modificar registro TCP")

    def tweak_udp_buffer(self):
        """Aumenta buffer UDP."""
        if sys.platform.startswith("win"):
            try:
                os.system(
                    'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" '
                    "/v DefaultRcvWindow /t REG_DWORD /d 65536 /f"
                )
            except Exception:
                raise Exception("Permissão de admin necessária para modificar buffers UDP")

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

    def tweak_virtual_memory(self):
        """Aumenta memória virtual para melhor cache."""
        if sys.platform.startswith("win"):
            try:
                os.system('wmic pagefileset where name="C:\\\\pagefile.sys" set InitialSize=12000,MaximumSize=12000')
            except Exception:
                raise Exception("Erro ao ajustar virtual memory")

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
                os.system("del /Q /F C:\\Windows\\Temp\\*.*")
        except Exception:
            raise Exception("Erro ao otimizar memória")

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
