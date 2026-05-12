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
        self.window.state('zoomed')
        self.window.bind("<Key>", self.handle_shortcuts)

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy para sa Authority
        self.color_bg = "#F4F6F7"  # Very light gray/cream para lumutang ang mga white cards sa loob
        self.color_hover = "#2A2F6C"  # Slightly lighter navy for hover effect
        self.color_accent = "#E05D3A"  # Web Orange for highlights/alerts
        self.text_dark = "#2C3E50"

        # 🚀 SINGLE FONT STANDARD
        self.ui_font = "Poppins"

        self.window.configure(fg_color=self.color_bg)

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        user_role = self.user.get('role', 'Kapitan')

        if self.user.get('audit_id'):
            self.audit_id = self.user.get('audit_id')
        else:
            self.audit_id = self.engine.log_user_login(user_name, user_role)

        self.window.protocol("WM_DELETE_WINDOW", self.force_logout_on_close)

        self.setup_layout()
        self.show_analytics_dashboard()

    def setup_layout(self):
        # 🚀 POGI UPDATE: The Modern Web Sidebar
        self.sidebar = ctk.CTkFrame(self.window, width=260, corner_radius=0, fg_color=self.color_sidebar)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # --- LOGO & BRANDING AREA ---
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(30, 10), fill="x")

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, 'logo-removebg-preview.png')

            if not os.path.exists(logo_path):
                logo_path = os.path.join(current_dir, 'assets', 'logo-removebg-preview.png')

            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(70, 70))
                ctk.CTkLabel(logo_frame, text="", image=ctk_logo).pack(anchor="center", pady=(0, 5))
            else:
                ctk.CTkLabel(logo_frame, text="BICRS", font=(self.ui_font, 28, "bold"), text_color="white").pack(
                    anchor="center")
        except Exception:
            ctk.CTkLabel(logo_frame, text="BICRS", font=(self.ui_font, 28, "bold"), text_color="white").pack(
                anchor="center")

        # --- USER PROFILE AREA ---
        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        ctk.CTkLabel(self.sidebar, text=user_name, font=(self.ui_font, 14, "bold"), text_color="white").pack(
            pady=(5, 0))

        # Subtle Role Badge
        role_badge = ctk.CTkFrame(self.sidebar, fg_color="#2A2F6C", corner_radius=10, height=20)
        role_badge.pack(pady=(2, 20))
        role_badge.pack_propagate(False)
        ctk.CTkLabel(role_badge, text=" KAPITAN OVERRIDE ", font=(self.ui_font, 9, "bold"), text_color="#A9CCE3").pack(
            expand=True)

        # Thin Separator Line
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2A2F6C").pack(fill="x", padx=20, pady=(0, 20))

        # --- NAVIGATION PILLS ---
        btn_args = {
            "font": (self.ui_font, 13, "bold"),
            "fg_color": "transparent",
            "text_color": "white",
            "hover_color": self.color_hover,
            "anchor": "w",
            "corner_radius": 8,
            "height": 42
        }

        self.btn_analytics = ctk.CTkButton(self.sidebar, text="   📊   Analytics", command=self.show_analytics_dashboard,
                                           **btn_args)
        self.btn_analytics.pack(fill="x", padx=20, pady=4)

        self.btn_archives = ctk.CTkButton(self.sidebar, text="   🗄️   Case Archives", command=self.show_archives_page,
                                          **btn_args)
        self.btn_archives.pack(fill="x", padx=20, pady=4)

        self.btn_team = ctk.CTkButton(self.sidebar, text="   👥   Team Management", command=self.show_user_management,
                                      **btn_args)
        self.btn_team.pack(fill="x", padx=20, pady=4)

        self.btn_logs = ctk.CTkButton(self.sidebar, text="   🕒   System Logs", command=self.show_login_logs, **btn_args)
        self.btn_logs.pack(fill="x", padx=20, pady=4)

        self.btn_alerts = ctk.CTkButton(self.sidebar, text="   🚨   Security Alerts", command=self.show_security_alerts,
                                        **btn_args)
        self.btn_alerts.configure(text_color=self.color_accent)  # Orange accent
        self.btn_alerts.pack(fill="x", padx=20, pady=4)

        self.btn_maintenance = ctk.CTkButton(self.sidebar, text="   ⚙️   Maintenance",
                                             command=self.show_system_maintenance, **btn_args)
        self.btn_maintenance.pack(fill="x", padx=20, pady=4)

        # --- BOTTOM SECTION ---
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2A2F6C").pack(side="bottom", fill="x", padx=20, pady=(0, 70))

        ctk.CTkButton(self.sidebar, text="   🚪   Lock & Exit Admin", font=(self.ui_font, 12, "bold"),
                      fg_color="transparent", border_width=1, border_color="#E74C3C", text_color="#E74C3C",
                      hover_color="#FDEDEC",
                      anchor="center", corner_radius=8, height=40, command=self.lock_and_exit).pack(side="bottom",
                                                                                                    fill="x", padx=20,
                                                                                                    pady=15)

        # --- MAIN CANVAS ---
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def set_active_tab(self, tab_name):
        # 🚀 POGI UPDATE: Active state turns WHITE, text turns NAVY BLUE! (Except Alerts)
        default_fg = "transparent"
        default_tc = "white"
        active_fg = "white"
        active_tc = self.color_sidebar

        self.btn_analytics.configure(
            fg_color=active_fg if tab_name == "analytics" else default_fg,
            text_color=active_tc if tab_name == "analytics" else default_tc,
            hover_color="#F8F9FA" if tab_name == "analytics" else self.color_hover
        )
        self.btn_archives.configure(
            fg_color=active_fg if tab_name == "archives" else default_fg,
            text_color=active_tc if tab_name == "archives" else default_tc,
            hover_color="#F8F9FA" if tab_name == "archives" else self.color_hover
        )
        self.btn_team.configure(
            fg_color=active_fg if tab_name == "users" else default_fg,
            text_color=active_tc if tab_name == "users" else default_tc,
            hover_color="#F8F9FA" if tab_name == "users" else self.color_hover
        )
        self.btn_logs.configure(
            fg_color=active_fg if tab_name == "logs" else default_fg,
            text_color=active_tc if tab_name == "logs" else default_tc,
            hover_color="#F8F9FA" if tab_name == "logs" else self.color_hover
        )
        self.btn_maintenance.configure(
            fg_color=active_fg if tab_name == "maintenance" else default_fg,
            text_color=active_tc if tab_name == "maintenance" else default_tc,
            hover_color="#F8F9FA" if tab_name == "maintenance" else self.color_hover
        )

        # Alerts has a special Orange/White theme
        self.btn_alerts.configure(
            fg_color=active_fg if tab_name == "alerts" else default_fg,
            text_color=self.color_accent,  # Always keep it orange to show urgency
            hover_color="#F8F9FA" if tab_name == "alerts" else self.color_hover
        )

    # ==========================================
    # ROUTING PAGES
    # ==========================================
    def show_analytics_dashboard(self):
        self.clear_main_frame()
        self.set_active_tab("analytics")
        try:
            from overview_page import OverviewPage
            OverviewPage(self.main_frame, self.engine, self.user)
        except ImportError:
            try:
                from bircs_package.overview_page import OverviewPage
                OverviewPage(self.main_frame, self.engine, self.user)
            except ImportError:
                from .overview_page import OverviewPage
                OverviewPage(self.main_frame, self.engine, self.user)

    def show_archives_page(self):
        self.clear_main_frame()
        self.set_active_tab("archives")
        try:
            from kapitan_archives_page import KapitanArchivesPage
            KapitanArchivesPage(self.main_frame, self.engine, self.user)
        except ImportError:
            try:
                from bircs_package.kapitan_archives_page import KapitanArchivesPage
                KapitanArchivesPage(self.main_frame, self.engine, self.user)
            except ImportError:
                from .kapitan_archives_page import KapitanArchivesPage
                KapitanArchivesPage(self.main_frame, self.engine, self.user)

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
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to lock the Admin Dashboard and log out?",
                               parent=self.window):
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
            self.show_analytics_dashboard()
        elif key == '2':
            self.show_archives_page()
        elif key == '3':
            self.show_user_management()
        elif key == '4':
            self.show_login_logs()
        elif key == '5':
            self.show_security_alerts()
        elif key == '6':
            self.show_system_maintenance()
        elif key == 'l':
            self.lock_and_exit()
