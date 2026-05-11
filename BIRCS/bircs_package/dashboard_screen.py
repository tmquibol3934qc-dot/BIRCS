import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
from PIL import Image

from .overview_page import OverviewPage
from .incident_blotter import IncidentBlotterPage
from .resolution_page import ResolutionPage
from .archive_page import ArchivesPage


class DashboardWindow:
    def __init__(self, engine, user_data, on_logout=None):
        self.engine = engine
        self.user = user_data
        self.on_logout = on_logout
        self.user_role = user_data.get('role', 'Staff') if user_data else 'Staff'

        self.window = ctk.CTkToplevel()
        self.window.title("BICRS - Command Center Dashboard")
        self.window.state('zoomed')
        self.window.protocol("WM_DELETE_WINDOW", self.force_logout_on_close)
        self.window.bind("<Key>", self.handle_shortcuts)

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"
        self.color_bg = "#F4F6F7"
        self.color_card = "#FFFFFF"
        self.color_border = "#EAECEE"
        self.primary = "#27AE60"
        self.orange = "#E05D3A"
        self.red = "#E74C3C"
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE FONT STANDARD
        self.ui_font = "Poppins"

        self.login_time = datetime.now()
        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()

        if not self.user.get('audit_id'):
            self.audit_id = self.engine.log_user_login(user_name, self.user_role)
            self.user['audit_id'] = self.audit_id
        else:
            self.audit_id = self.user.get('audit_id')

        self.page_cache = {}
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.nav_buttons = {}

        self.create_sidebar()

        self.main_frame = ctk.CTkFrame(self.window, fg_color=self.color_bg, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.create_profile_panel()
        self.update_timer()

        self.show_overview_page()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.window, width=260, corner_radius=0, fg_color=self.color_sidebar)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)
        sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(35, 10), fill="x")

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
                ctk.CTkLabel(logo_frame, text="BICRS", font=(self.ui_font, 28, "bold"), text_color="white").pack(anchor="center")

        except Exception:
            ctk.CTkLabel(logo_frame, text="BICRS", font=(self.ui_font, 28, "bold"), text_color="white").pack(anchor="center")

        ctk.CTkLabel(logo_frame, text="Brgy. 176-B Bagong Silang", font=(self.ui_font, 11), text_color="#BDC3C7").pack(anchor="center")

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        ctk.CTkLabel(sidebar, text=user_name, font=(self.ui_font, 14, "bold"), text_color="white").pack(pady=(15, 2))

        role_badge = ctk.CTkFrame(sidebar, fg_color="#2A2F6C", corner_radius=10, height=22)
        role_badge.pack(pady=(0, 20))
        role_badge.pack_propagate(False)
        ctk.CTkLabel(role_badge, text=f" {self.user_role.upper()} ", font=(self.ui_font, 10, "bold"),
                     text_color=self.primary).pack(expand=True)

        ctk.CTkFrame(sidebar, height=1, fg_color="#2A2F6C").pack(fill="x", padx=20, pady=(0, 20))

        self.nav_buttons["dashboard"] = self.create_nav_btn(sidebar, "   📊   Analytics Dashboard", self.show_overview_page)
        self.nav_buttons["blotter"] = self.create_nav_btn(sidebar, "   📄   Incident Blotter", self.show_blotter_page)
        self.nav_buttons["resolution"] = self.create_nav_btn(sidebar, "   ⚖️   Resolution", self.show_resolution_page)
        self.nav_buttons["archives"] = self.create_nav_btn(sidebar, "   🗄️   Case Archives", self.show_archives_page)

    def create_nav_btn(self, parent, text, command=None):
        btn = ctk.CTkButton(parent, text=text, fg_color="transparent", text_color="white", hover_color="#2A2F6C",
                            anchor="w", height=42, corner_radius=8, font=(self.ui_font, 13, "bold"), command=command)
        btn.pack(fill="x", padx=20, pady=4)
        return btn

    def set_active_tab(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=self.primary, text_color="white", hover_color="#1E8449")
            else:
                btn.configure(fg_color="transparent", text_color="white", hover_color="#2A2F6C")

        if hasattr(self, 'profile_btn'):
            if active_key == "dashboard":
                self.profile_btn.place(relx=0.97, rely=0.03, anchor="ne")
            else:
                self.profile_btn.place_forget()
                if self.panel_visible: self.toggle_profile_panel()

    def hide_all_pages(self):
        for widget in self.main_frame.winfo_children(): widget.pack_forget()

    # --- PROFILE PANEL WIDGET ---
    def create_profile_panel(self):
        img_path = self.user.get('profile_pic', '')
        has_image = False

        if img_path and os.path.exists(img_path):
            try:
                pil_image = Image.open(img_path)
                self.btn_img = ctk.CTkImage(pil_image, size=(34, 34))
                self.panel_img = ctk.CTkImage(pil_image, size=(90, 90))
                has_image = True
            except Exception:
                pass

        btn_text = "" if has_image else "👤"
        btn_image = self.btn_img if has_image else None

        self.profile_btn = ctk.CTkButton(
            self.window, text=btn_text, image=btn_image, width=48, height=48, corner_radius=24,
            fg_color=self.color_card, text_color=self.color_sidebar, border_width=1, border_color=self.color_border,
            hover_color="#F8F9FA", font=(self.ui_font, 20), command=self.toggle_profile_panel
        )
        self.profile_btn.place(relx=0.97, rely=0.03, anchor="ne")

        self.account_panel = ctk.CTkFrame(self.window, width=280, corner_radius=12, fg_color=self.color_card,
                                          border_width=1, border_color=self.color_border)
        self.panel_visible = False

        header_frame = ctk.CTkFrame(self.account_panel, fg_color=self.color_sidebar, corner_radius=0)
        header_frame.pack(fill="x", pady=(2, 0), padx=2)
        ctk.CTkLabel(header_frame, text="Active Session", font=(self.ui_font, 12, "bold"), text_color="white").pack(pady=(15, 5))

        pic_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        pic_frame.pack(pady=(0, 20))

        if has_image:
            ctk.CTkLabel(pic_frame, text="", image=self.panel_img).pack()
        else:
            fallback = ctk.CTkFrame(pic_frame, width=80, height=80, corner_radius=40, fg_color="#EBF5FB")
            fallback.pack()
            fallback.pack_propagate(False)
            ctk.CTkLabel(fallback, text="👤", font=(self.ui_font, 36), text_color=self.color_sidebar).place(relx=0.5, rely=0.5, anchor="center")

        details_frame = ctk.CTkFrame(self.account_panel, fg_color="transparent")
        details_frame.pack(fill="x", pady=15)

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"

        ctk.CTkLabel(details_frame, text="Account Name", font=(self.ui_font, 10, "bold"),
                     text_color=self.text_muted).pack(anchor="w", padx=20)
        ctk.CTkLabel(details_frame, text=user_name, font=(self.ui_font, 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(details_frame, text="Authorization Level", font=(self.ui_font, 10, "bold"),
                     text_color=self.text_muted).pack(anchor="w", padx=20)
        ctk.CTkLabel(details_frame, text=self.user_role.upper(), font=(self.ui_font, 12, "bold"),
                     text_color=self.primary).pack(anchor="w", padx=20, pady=(0, 5))

        ctk.CTkFrame(self.account_panel, height=1, fg_color=self.color_border).pack(fill="x", padx=20)

        footer_frame = ctk.CTkFrame(self.account_panel, fg_color="transparent")
        footer_frame.pack(fill="x", pady=15)

        self.timer_label = ctk.CTkLabel(footer_frame, text="🟢 Online: Just now", font=(self.ui_font, 11, "bold"), text_color=self.primary)
        self.timer_label.pack(pady=(0, 15))

        ctk.CTkButton(footer_frame, text="🔑 Kapitan Override", fg_color="transparent", border_width=1, border_color=self.orange,
                      text_color=self.orange, hover_color="#FDEDEC", font=(self.ui_font, 12, "bold"), height=35, corner_radius=8,
                      command=self.prompt_admin_access).pack(fill="x", padx=20, pady=4)

        ctk.CTkButton(footer_frame, text="🚪 Secure Log Out", fg_color="transparent", border_width=1, border_color=self.red,
                      text_color=self.red, hover_color="#FDEDEC", font=(self.ui_font, 12, "bold"), height=35, corner_radius=8,
                      command=self.handle_logout).pack(fill="x", padx=20, pady=4)

    def toggle_profile_panel(self):
        if self.panel_visible:
            self.account_panel.place_forget()
            self.panel_visible = False
        else:
            self.account_panel.place(relx=0.97, rely=0.10, anchor="ne")
            self.account_panel.lift()
            self.panel_visible = True

    def update_timer(self):
        mins = int((datetime.now() - self.login_time).total_seconds() // 60)
        time_text = "🟢 Online: Just now" if mins < 1 else (
            f"🟢 Online: {mins} min ago" if mins < 60 else f"🟢 Online: {mins // 60} hr {mins % 60} min")
        self.timer_label.configure(text=time_text)
        self.window.after(60000, self.update_timer)

    # --- NAVIGATION LOGIC ---
    def show_overview_page(self):
        self.hide_all_pages()
        self.set_active_tab("dashboard")
        if "dashboard" in self.page_cache: self.page_cache["dashboard"].destroy()
        self.page_cache["dashboard"] = OverviewPage(self.main_frame, self.engine, self.user).container

    def show_blotter_page(self):
        self.hide_all_pages()
        self.set_active_tab("blotter")
        if "blotter" not in self.page_cache:
            container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            IncidentBlotterPage(container, self.engine, self.user)
            self.page_cache["blotter"] = container
        self.page_cache["blotter"].pack(fill="both", expand=True)

    def show_resolution_page(self):
        self.hide_all_pages()
        self.set_active_tab("resolution")
        if "resolution" not in self.page_cache:
            container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            ResolutionPage(container, self.engine, self.user)
            self.page_cache["resolution"] = container
        self.page_cache["resolution"].pack(fill="both", expand=True)

    def show_archives_page(self):
        self.hide_all_pages()
        self.set_active_tab("archives")
        if "archives" not in self.page_cache:
            container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            ArchivesPage(container, self.engine, self.user)
            self.page_cache["archives"] = container
        self.page_cache["archives"].pack(fill="both", expand=True)

    # --- ADMIN / LOGOUT ---
    def prompt_admin_access(self):
        scanned_rfid = ctk.CTkInputDialog(text="Scan Kapitan RFID:", title="Authorization").get_input()
        if scanned_rfid:
            success, kapitan_data = self.engine.verify_kapitan_access(scanned_rfid)
            if success:
                self.window.withdraw()
                from .admin_dashboard import AdminDashboardWindow
                AdminDashboardWindow(self.engine, kapitan_data, parent_dashboard=self)
            else:
                messagebox.showerror("Access Denied", "Invalid or unauthorized RFID.", parent=self.window)

    def restore_dashboard(self):
        self.window.deiconify()
        self.window.state('zoomed')

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to securely log out of the system?", parent=self.window):
            self.force_logout_on_close()

    def force_logout_on_close(self):
        if hasattr(self, 'audit_id') and self.audit_id: self.engine.log_user_logout(self.audit_id)
        self.window.destroy()
        if self.on_logout: self.on_logout()

    def handle_shortcuts(self, event):
        focused_widget = self.window.focus_get()
        if focused_widget and type(focused_widget).__name__ in ['CTkEntry', 'CTkTextbox', 'Entry', 'Text']: return
        key = event.char.lower()
        if key == '1': self.show_overview_page()
        elif key == '2': self.show_blotter_page()
        elif key == '3': self.show_resolution_page()
        elif key == '4': self.show_archives_page()
        elif key == 'k' and hasattr(self, 'toggle_profile_panel'): self.prompt_admin_access()
        elif key == 'l': self.handle_logout()
