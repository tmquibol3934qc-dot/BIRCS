import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
from PIL import Image

# THE NEW CLEAN IMPORTS!
from .overview_page import OverviewPage
from .incident_blotter import IncidentBlotterPage
from .resolution_page import ResolutionPage
from .archive_page import ArchivesPage  # 🚀 POGI UPDATE: Bagong import para sa Archives!


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

        self.bg_color, self.sidebar_color = "#F8F9F5", "#1D2153"
        self.primary, self.orange, self.green, self.red = "#2980B9", "#F39C12", "#27AE60", "#E74C3C"
        self.text_dark, self.text_muted = "#2B2B2B", "#7A7A7A"

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

        self.main_frame = ctk.CTkFrame(self.window, fg_color=self.bg_color, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.create_profile_panel()
        self.update_timer()

        # MATIC LOAD ANG OVERVIEW!
        self.show_overview_page()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.window, width=220, corner_radius=0, fg_color=self.sidebar_color)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
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
                ctk.CTkLabel(logo_frame, text="BICRS", font=("Arial", 28, "bold"), text_color="#F1C40F").pack(
                    anchor="center")

        except Exception as e:
            print(f"Error loading logo: {e}")
            ctk.CTkLabel(logo_frame, text="BICRS", font=("Arial", 28, "bold"), text_color="#F1C40F").pack(
                anchor="center")

        ctk.CTkLabel(logo_frame, text="Brgy. 176-B Bagong Silang", font=("Arial", 11), text_color="#BDC3C7").pack(
            anchor="center")

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        ctk.CTkLabel(sidebar, text=f"Welcome, {user_name}", font=("Arial", 12, "bold"), text_color="white").pack(
            pady=(0, 5))
        ctk.CTkLabel(sidebar, text=self.user_role.upper(), font=("Arial", 10), text_color=self.green).pack(pady=(0, 20))

        # 🚀 POGI UPDATE: Idinagdag ang Archives at inayos ang labels!
        self.nav_buttons["dashboard"] = self.create_nav_btn(sidebar, "📊 Analytics", self.show_overview_page)
        self.nav_buttons["blotter"] = self.create_nav_btn(sidebar, "📄 Incident Blotter", self.show_blotter_page)
        self.nav_buttons["resolution"] = self.create_nav_btn(sidebar, "⚖️ Resolution", self.show_resolution_page)
        self.nav_buttons["archives"] = self.create_nav_btn(sidebar, "🗄️ Archives", self.show_archives_page)

    def create_nav_btn(self, parent, text, command=None):
        btn = ctk.CTkButton(parent, text=f"  {text}", fg_color="transparent", text_color="white", hover_color="#2C3E50",
                            anchor="w", height=45, corner_radius=0, font=("Arial", 13, "bold"), command=command)
        btn.pack(fill="x", pady=2)
        return btn

    def set_active_tab(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color="white", text_color=self.sidebar_color, hover_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="white", hover_color="#2C3E50")
        if hasattr(self, 'profile_btn'):
            if active_key == "dashboard":
                self.profile_btn.place(relx=0.98, rely=0.02, anchor="ne")
            else:
                self.profile_btn.place_forget()
                if self.panel_visible: self.toggle_profile_panel()

    def hide_all_pages(self):
        for widget in self.main_frame.winfo_children(): widget.pack_forget()

    # --- PROFILE PANEL ---
    def create_profile_panel(self):
        img_path = self.user.get('profile_pic', '')
        has_image = False

        if img_path and os.path.exists(img_path):
            try:
                pil_image = Image.open(img_path)
                self.btn_img = ctk.CTkImage(pil_image, size=(30, 30))
                self.panel_img = ctk.CTkImage(pil_image, size=(100, 100))
                has_image = True
            except Exception as e:
                print(f"Error loading image: {e}")

        btn_text = "" if has_image else "👤"
        btn_image = self.btn_img if has_image else None

        self.profile_btn = ctk.CTkButton(
            self.window, text=btn_text, image=btn_image, width=45, height=45, corner_radius=22,
            fg_color="white", text_color=self.sidebar_color, border_width=1, border_color="#E0E0E0",
            hover_color="#F0F0F0", font=("Arial", 24),
            command=self.toggle_profile_panel
        )
        self.profile_btn.place(relx=0.98, rely=0.02, anchor="ne")

        self.account_panel = ctk.CTkFrame(self.window, width=250, corner_radius=10, fg_color="white", border_width=1,
                                          border_color="#E0E0E0")
        self.panel_visible = False

        header_frame = ctk.CTkFrame(self.account_panel, fg_color=self.sidebar_color, corner_radius=0)
        header_frame.pack(fill="x")

        ctk.CTkLabel(header_frame, text="Account Information", font=("Arial", 12, "bold"), text_color="white").pack(
            pady=(10, 5))

        pic_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        pic_frame.pack(pady=(0, 20))

        if has_image:
            ctk.CTkLabel(pic_frame, text="", image=self.panel_img).pack()
        else:
            fallback = ctk.CTkFrame(pic_frame, width=80, height=80, corner_radius=40, fg_color="#E0E0E0")
            fallback.pack()
            fallback.pack_propagate(False)
            ctk.CTkLabel(fallback, text="👤", font=("Arial", 40), text_color=self.sidebar_color).place(relx=0.5,
                                                                                                      rely=0.5,
                                                                                                      anchor="center")

        details_frame = ctk.CTkFrame(self.account_panel, fg_color="transparent")
        details_frame.pack(fill="x", pady=10)

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        role = self.user_role

        ctk.CTkLabel(details_frame, text="Name:", font=("Arial", 10), text_color=self.text_muted).pack(anchor="w",
                                                                                                       padx=15)
        ctk.CTkLabel(details_frame, text=user_name, font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=15, pady=(0, 5))

        ctk.CTkLabel(details_frame, text="Role:", font=("Arial", 10), text_color=self.text_muted).pack(anchor="w",
                                                                                                       padx=15)
        ctk.CTkLabel(details_frame, text=role.upper(), font=("Arial", 12, "bold"), text_color=self.primary).pack(
            anchor="w", padx=15, pady=(0, 10))

        ctk.CTkFrame(self.account_panel, height=1, fg_color="#E0E0E0").pack(fill="x", padx=15)

        self.timer_label = ctk.CTkLabel(self.account_panel, text="Just now", font=("Arial", 11, "bold"),
                                        text_color=self.green)
        self.timer_label.pack(pady=10)

        ctk.CTkButton(self.account_panel, text="🔑 Kapitan Access", fg_color="transparent", text_color=self.orange,
                      hover_color="#FFF3E0", font=("Arial", 12, "bold"), command=self.prompt_admin_access).pack(
            fill="x", padx=10, pady=2)
        ctk.CTkButton(self.account_panel, text="Log Out", fg_color="transparent", text_color=self.red,
                      hover_color="#FEEEEE", font=("Arial", 12, "bold"), command=self.handle_logout).pack(fill="x",
                                                                                                          padx=10,
                                                                                                          pady=(2, 15))

    def toggle_profile_panel(self):
        if self.panel_visible:
            self.account_panel.place_forget()
            self.panel_visible = False
        else:
            self.account_panel.place(relx=0.98, rely=0.08, anchor="ne")
            self.account_panel.lift()
            self.panel_visible = True

    def update_timer(self):
        mins = int((datetime.now() - self.login_time).total_seconds() // 60)
        time_text = "Just now" if mins < 1 else (
            f"{mins} min ago" if mins < 60 else f"{mins // 60} hr {mins % 60} min ago")
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

    # 🚀 POGI UPDATE: Bagong logic para ipakita ang Archives
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
        scanned_rfid = ctk.CTkInputDialog(text="Scan Kapitan RFID:", title="Auth").get_input()
        if scanned_rfid:
            success, kapitan_data = self.engine.verify_kapitan_access(scanned_rfid)
            if success:
                self.window.withdraw()
                from .admin_dashboard import AdminDashboardWindow
                AdminDashboardWindow(self.engine, kapitan_data, parent_dashboard=self)
            else:
                messagebox.showerror("Access Denied", "Invalid RFID.")

    def restore_dashboard(self):
        self.window.deiconify()
        self.window.state('zoomed')

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?"):
            self.force_logout_on_close()

    def force_logout_on_close(self):
        if hasattr(self, 'audit_id') and self.audit_id: self.engine.log_user_logout(self.audit_id)
        self.window.destroy()
        if self.on_logout: self.on_logout()

    def handle_shortcuts(self, event):
        focused_widget = self.window.focus_get()
        if focused_widget and type(focused_widget).__name__ in ['CTkEntry', 'CTkTextbox', 'Entry', 'Text']: return
        key = event.char.lower()
        if key == '1':
            self.show_overview_page()
        elif key == '2':
            self.show_blotter_page()
        elif key == '3':
            self.show_resolution_page()
        elif key == '4':
            self.show_archives_page()  # 🚀 Added Shortcut for Archives!
        elif key == 'k' and hasattr(self, 'toggle_profile_panel'):
            self.prompt_admin_access()
        elif key == 'l':
            self.handle_logout()
