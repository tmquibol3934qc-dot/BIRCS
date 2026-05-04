import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image


class AdminDashboardWindow:
    def __init__(self, engine, user_data, parent_dashboard=None):
        self.engine = engine
        self.user = user_data
        self.parent_dashboard = parent_dashboard

        self.window = ctk.CTkToplevel()
        self.window.title("BICRS - Kapitan Control Center")
        self.window.state('zoomed')  # Safe against Alt+Tab bug
        self.window.bind("<Key>", self.handle_shortcuts)
        self.window.configure(fg_color="#F4F7F6")

        # Colors
        self.primary = "#27AE60"
        self.dark_green = "#1E8449"
        self.red = "#E74C3C"
        self.text_dark = "#2B2B2B"

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        user_role = self.user.get('role', 'Kapitan')

        if self.user.get('audit_id'):
            self.audit_id = self.user.get('audit_id')
        else:
            self.audit_id = self.engine.log_user_login(user_name, user_role)

        self.window.protocol("WM_DELETE_WINDOW", self.force_logout_on_close)

        self.setup_layout()
        self.show_master_dashboard()

    def setup_layout(self):
        self.sidebar = ctk.CTkFrame(self.window, width=250, corner_radius=0, fg_color="#2C3E50")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 🚀 POGI UPDATE: Logo Integration para kay Kapitan!
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(30, 20), padx=20, fill="x")

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, 'logo.jpg')

            if not os.path.exists(logo_path):
                logo_path = os.path.join(current_dir, 'assets', 'logo.jpg')

            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(80, 80))

                logo_label = ctk.CTkLabel(logo_frame, text="", image=ctk_logo)
                logo_label.pack(anchor="center", pady=(0, 5))
            else:
                ctk.CTkLabel(logo_frame, text="BICRS ADMIN", font=("Arial", 22, "bold"), text_color="white").pack(
                    anchor="center")

        except Exception as e:
            print(f"Error loading logo: {e}")
            ctk.CTkLabel(logo_frame, text="BICRS ADMIN", font=("Arial", 22, "bold"), text_color="white").pack(
                anchor="center")

        ctk.CTkLabel(logo_frame, text="Kapitan Override Active", font=("Arial", 11, "italic"),
                     text_color=self.primary).pack(anchor="center", pady=(5, 0))

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        ctk.CTkLabel(self.sidebar, text=f"Welcome, {user_name}", font=("Arial", 14, "bold"), text_color="white").pack(
            pady=(10, 2))
        ctk.CTkLabel(self.sidebar, text="KAPITAN", font=("Arial", 10, "bold"), text_color=self.primary).pack(
            pady=(0, 30))

        self.btn_master = ctk.CTkButton(self.sidebar, text="📁 Master Dashboard", font=("Arial", 14, "bold"),
                                        fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                        anchor="w", command=self.show_master_dashboard)
        self.btn_master.pack(fill="x", padx=15, pady=5)

        self.btn_team = ctk.CTkButton(self.sidebar, text="👥 Team Management", font=("Arial", 14, "bold"),
                                      fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                      anchor="w", command=self.show_user_management)
        self.btn_team.pack(fill="x", padx=15, pady=5)

        self.btn_logs = ctk.CTkButton(self.sidebar, text="🕒 System Logs", font=("Arial", 14, "bold"),
                                      fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                      anchor="w", command=self.show_login_logs)
        self.btn_logs.pack(fill="x", padx=15, pady=5)

        self.btn_alerts = ctk.CTkButton(self.sidebar, text="🚨 Security Alerts", font=("Arial", 14, "bold"),
                                        fg_color="transparent", text_color=self.red, hover_color=self.dark_green,
                                        anchor="w", command=self.show_security_alerts)
        self.btn_alerts.pack(fill="x", padx=15, pady=5)

        self.btn_maintenance = ctk.CTkButton(self.sidebar, text="⚙️ System Maintenance", font=("Arial", 14, "bold"),
                                             fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                             anchor="w", command=self.show_system_maintenance)
        self.btn_maintenance.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(self.sidebar, text="Lock & Exit Admin", font=("Arial", 12, "bold"), fg_color="transparent",
                      text_color=self.red, hover_color="#34495E", anchor="w", command=self.lock_and_exit).pack(
            side="bottom", fill="x", padx=15, pady=30)

        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def set_active_tab(self, tab_name):
        self.btn_master.configure(fg_color=self.primary if tab_name == "master" else "transparent")
        self.btn_team.configure(fg_color=self.primary if tab_name == "users" else "transparent")
        self.btn_logs.configure(fg_color=self.primary if tab_name == "logs" else "transparent")
        self.btn_alerts.configure(fg_color=self.primary if tab_name == "alerts" else "transparent")
        self.btn_maintenance.configure(fg_color=self.primary if tab_name == "maintenance" else "transparent")

    # ==========================================
    # ROUTING PAGES (MODULARIZED NA LAHAT!)
    # ==========================================
    def show_master_dashboard(self):
        self.clear_main_frame()
        self.set_active_tab("master")
        try:
            from master_dashboard_page import MasterDashboardPage
            MasterDashboardPage(self.main_frame, self.engine, self.window)
        except ImportError:
            try:
                from bircs_package.master_dashboard_page import MasterDashboardPage
                MasterDashboardPage(self.main_frame, self.engine, self.window)
            except ImportError:
                from .master_dashboard_page import MasterDashboardPage
                MasterDashboardPage(self.main_frame, self.engine, self.window)

    def show_user_management(self):
        self.clear_main_frame()
        self.set_active_tab("users")
        try:
            from team_management_page import TeamManagementPage
            TeamManagementPage(self.main_frame, self.engine, self.window)
        except ImportError:
            try:
                from bircs_package.team_management_page import TeamManagementPage
                TeamManagementPage(self.main_frame, self.engine, self.window)
            except ImportError:
                from .team_management_page import TeamManagementPage
                TeamManagementPage(self.main_frame, self.engine, self.window)

    def show_login_logs(self):
        self.clear_main_frame()
        self.set_active_tab("logs")
        try:
            from system_logs_page import SystemLogsPage
            SystemLogsPage(self.main_frame, self.engine)
        except ImportError:
            try:
                from bircs_package.system_logs_page import SystemLogsPage
                SystemLogsPage(self.main_frame, self.engine)
            except ImportError:
                from .system_logs_page import SystemLogsPage
                SystemLogsPage(self.main_frame, self.engine)

    def show_security_alerts(self):
        self.clear_main_frame()
        self.set_active_tab("alerts")
        try:
            from security_alerts_page import SecurityAlertsPage
            SecurityAlertsPage(self.main_frame, self.engine)
        except ImportError:
            try:
                from bircs_package.security_alerts_page import SecurityAlertsPage
                SecurityAlertsPage(self.main_frame, self.engine)
            except ImportError:
                from .security_alerts_page import SecurityAlertsPage
                SecurityAlertsPage(self.main_frame, self.engine)

    def show_system_maintenance(self):
        self.clear_main_frame()
        self.set_active_tab("maintenance")
        try:
            from system_maintenance_page import SystemMaintenancePage
            SystemMaintenancePage(self.main_frame, self.engine, self.window)
        except ImportError:
            try:
                from bircs_package.system_maintenance_page import SystemMaintenancePage
                SystemMaintenancePage(self.main_frame, self.engine, self.window)
            except ImportError:
                from .system_maintenance_page import SystemMaintenancePage
                SystemMaintenancePage(self.main_frame, self.engine, self.window)

    # ==========================================
    # SYSTEM CONTROLS
    # ==========================================
    def lock_and_exit(self):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to lock the Admin Dashboard and log out?"):
            if hasattr(self, 'audit_id'):
                self.engine.log_user_logout(self.audit_id)
            self.window.destroy()
            if self.parent_dashboard:
                self.parent_dashboard.restore_dashboard()

    def force_logout_on_close(self):
        if hasattr(self, 'audit_id'):
            self.engine.log_user_logout(self.audit_id)
        self.window.destroy()
        if self.parent_dashboard:
            self.parent_dashboard.restore_dashboard()

    def handle_shortcuts(self, event):
        focused_widget = self.window.focus_get()
        if focused_widget:
            widget_type = type(focused_widget).__name__
            if widget_type in ['CTkEntry', 'CTkTextbox', 'Entry', 'Text']: return

        key = event.char.lower()
        if key == '1':
            self.show_master_dashboard()
        elif key == '2':
            self.show_user_management()
        elif key == '3':
            self.show_login_logs()
        elif key == '4':
            self.show_security_alerts()
        elif key == 'l':
            self.lock_and_exit()
