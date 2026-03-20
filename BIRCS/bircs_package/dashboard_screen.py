import customtkinter as ctk
from tkinter import messagebox
from .incident_blotter import IncidentBlotterPage
from .resolution_page import ResolutionPage


class DashboardWindow:
    def __init__(self, engine, user_data, on_logout=None):
        self.engine = engine
        self.user = user_data
        self.on_logout = on_logout
        self.user_role = user_data.get('role', 'Staff') if user_data else 'Staff'

        self.window = ctk.CTkToplevel()
        self.window.title("BICRS - Command Center Dashboard")
        self.window.state('zoomed')

        self.bg_color = "#F4F7F6"
        self.sidebar_color = "#FFFFFF"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"

        self.primary = "#E79124"
        self.orange = "#F2994A"
        self.green = "#27AE60"
        self.red = "#EB5757"

        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.create_sidebar()

        self.main_frame = ctk.CTkFrame(self.window, fg_color=self.bg_color, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.show_overview_page()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.window, width=220, corner_radius=0, fg_color=self.sidebar_color)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(30, 20), padx=20, fill="x")
        ctk.CTkLabel(logo_frame, text="BICRS", font=("Arial", 28, "bold"), text_color=self.primary).pack(
            anchor="center")
        ctk.CTkLabel(logo_frame, text="Brgy. 176-B Bagong Silang", font=("Arial", 11), text_color=self.text_muted).pack(
            anchor="center")

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        ctk.CTkLabel(sidebar, text=f"Welcome, {user_name}", font=("Arial", 12, "bold"), text_color=self.text_dark).pack(
            pady=(0, 5))
        ctk.CTkLabel(sidebar, text=self.user_role.upper(), font=("Arial", 10), text_color=self.green).pack(pady=(0, 20))

        # Standard navigation buttons
        self.nav_buttons["dashboard"] = self.create_nav_btn(sidebar, "📁 Dashboard", self.show_overview_page)
        self.nav_buttons["blotter"] = self.create_nav_btn(sidebar, "📄 Incident Blotter", self.show_blotter_page)
        self.nav_buttons["resolution"] = self.create_nav_btn(sidebar, "⚖️ Resolution", self.show_resolution_page)
        self.nav_buttons["analytics"] = self.create_nav_btn(sidebar, "📊 Analytics", self.show_analytics_page)

        ctk.CTkFrame(sidebar, height=150, fg_color="transparent").pack()

        # --- THE NEW ADMIN ACCESS BUTTON ---
        admin_btn = ctk.CTkButton(sidebar, text="🔑 Kapitan Access", fg_color="transparent",
                                  text_color=self.green, hover_color="#E8F5E9",
                                  font=("Arial", 13, "bold"), command=self.prompt_admin_access)
        admin_btn.pack(side="bottom", pady=(0, 5))

        logout_btn = ctk.CTkButton(sidebar, text="Log Out", fg_color="transparent",
                                   text_color=self.red, hover_color="#FEEEEE",
                                   font=("Arial", 13, "bold"), command=self.handle_logout)
        logout_btn.pack(side="bottom", pady=20)

    # --- THE OVERRIDE POPUP ---
    def prompt_admin_access(self):
        # Creates a popup asking for the RFID scan
        dialog = ctk.CTkInputDialog(text="Please scan Kapitan RFID to proceed:", title="Authorization Required")
        scanned_rfid = dialog.get_input()

        if scanned_rfid:
            success, kapitan_data = self.engine.verify_kapitan_access(scanned_rfid)
            if success:
                messagebox.showinfo("Access Granted", "Kapitan verified. Opening Secure Dashboard.")
                self.launch_admin_dashboard(kapitan_data)
            else:
                messagebox.showerror("Access Denied", "Invalid RFID or insufficient permissions.")

    def launch_admin_dashboard(self, kapitan_data):
        try:
            # 1. Hide the staff dashboard completely
            self.window.withdraw()

            # 2. Pass 'self' so the Admin window knows who to unhide later!
            from .admin_dashboard import AdminDashboardWindow
            AdminDashboardWindow(self.engine, kapitan_data, parent_dashboard=self)

        except Exception as e:
            self.window.deiconify()  # If it crashes, bring the dashboard back!
            messagebox.showerror("System Error", f"Could not launch Admin Dashboard:\n{e}")

    def restore_dashboard(self):
        """Called by the Admin dashboard when it closes to unhide the staff screen"""
        self.window.deiconify()
        self.window.state('zoomed')  # Add this line to force it back to full screen!

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the Command Center?"):
            self.window.destroy()
            if self.on_logout:
                self.on_logout()

    def create_nav_btn(self, parent, text, command=None):
        btn = ctk.CTkButton(parent, text=f"  {text}", fg_color="transparent", text_color=self.text_muted,
                            hover_color="#F0F0F0", anchor="w", height=45, corner_radius=8,
                            font=("Arial", 13, "bold"), command=command)
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def set_active_tab(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=self.primary, text_color="white", hover_color=self.primary)
            else:
                btn.configure(fg_color="transparent", text_color=self.text_muted, hover_color="#F0F0F0")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_overview_page(self):
        self.clear_main_frame()
        self.set_active_tab("dashboard")

        db_stats = self.engine.get_dashboard_stats()
        db_incidents = self.engine.get_all_incidents()
        db_analytics = self.engine.get_incident_analytics()

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Command Center Dashboard", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")

        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25)

        self.create_stat_card(stats_frame, "Total Cases", str(db_stats['Total Cases']), self.primary)
        self.create_stat_card(stats_frame, "Pending", str(db_stats['Pending']), self.orange)
        self.create_stat_card(stats_frame, "Resolved", str(db_stats['Resolved']), self.green)
        self.create_stat_card(stats_frame, "Urgent", str(db_stats['Urgent']), self.red)

        body_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=30, pady=20)

        body_frame.grid_columnconfigure(0, weight=3)
        body_frame.grid_columnconfigure(1, weight=1)

        table_container = ctk.CTkFrame(body_frame, fg_color="white", corner_radius=10)
        table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.build_table(table_container, db_incidents)

        right_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")

        self.build_active_personnel(right_panel)
        self.build_incident_analytics(right_panel, db_analytics)

    def create_stat_card(self, parent, title, value, border_color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=110)
        card.pack(side="left", fill="x", expand=True, padx=5)
        card.pack_propagate(False)

        top_line = ctk.CTkFrame(card, height=4, fg_color=border_color, corner_radius=0)
        top_line.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(card, text=value, font=("Arial", 32, "bold"), text_color=self.text_dark).pack(pady=(10, 0))
        ctk.CTkLabel(card, text=title, font=("Arial", 12), text_color=self.text_muted).pack()

    def build_table(self, container, incidents):
        self.all_incidents = incidents

        top_ctrls = ctk.CTkFrame(container, fg_color="transparent")
        top_ctrls.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(top_ctrls, text="Recent Blotter Entries", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_table)

        search = ctk.CTkEntry(top_ctrls, textvariable=self.search_var, placeholder_text="Search ID or Zone...",
                              width=150, height=30, border_color="#E0E0E0")
        search.pack(side="right", padx=(10, 0))

        dropdown = ctk.CTkOptionMenu(top_ctrls, values=["All Categories", "Incidents", "Complaints"],
                                     fg_color=self.primary, width=120, height=30)
        dropdown.pack(side="right")

        header_row = ctk.CTkFrame(container, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(header_row, text="ID", font=("Arial", 12, "bold"), text_color=self.text_muted, width=60,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Type/Zone", font=("Arial", 12, "bold"), text_color=self.text_muted, width=150,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Processed By", font=("Arial", 12, "bold"), text_color=self.primary, width=120,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Time", font=("Arial", 12, "bold"), text_color=self.text_muted, width=100,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Status", font=("Arial", 12, "bold"), text_color=self.text_muted, width=80,
                     anchor="e").pack(side="right", padx=10)

        ctk.CTkFrame(container, height=1, fg_color="#E0E0E0").pack(fill="x", padx=20, pady=5)

        self.table_rows_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.table_rows_frame.pack(fill="both", expand=True)

        self.draw_table_rows(self.all_incidents)

    def filter_table(self, *args):
        query = self.search_var.get().lower()
        if not query:
            self.draw_table_rows(self.all_incidents)
            return

        filtered_data = []
        for row in self.all_incidents:
            case_id = str(row.get('case_no', '')).lower()
            zone = str(row.get('zone', '')).lower()
            officer = str(row.get('processed_by', '')).lower()
            if query in case_id or query in zone or query in officer:
                filtered_data.append(row)

        self.draw_table_rows(filtered_data)

    def draw_table_rows(self, data_to_draw):
        for widget in self.table_rows_frame.winfo_children():
            widget.destroy()

        if not data_to_draw:
            ctk.CTkLabel(self.table_rows_frame, text="No matching records found.", text_color=self.text_muted).pack(
                pady=20)
            return

        for row in data_to_draw:
            if row['status'] == 'Resolved':
                color = self.green
            elif row['status'] == 'Urgent':
                color = self.red
            else:
                color = self.orange

            self.add_table_row(self.table_rows_frame, row['case_no'], f"Zone: {row['zone']}", row['processed_by'],
                               row['exact_time'], row['status'], color)

    def add_table_row(self, parent, case_id, type_txt, proc_by, time_txt, status, color):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        row.pack(fill="x", padx=20, pady=5)
        row.pack_propagate(False)

        ctk.CTkLabel(row, text=case_id, font=("Arial", 12), text_color=self.primary, width=60, anchor="w").pack(
            side="left")
        ctk.CTkLabel(row, text=type_txt, font=("Arial", 12), text_color=self.text_dark, width=150, anchor="w").pack(
            side="left")
        ctk.CTkLabel(row, text=proc_by, font=("Arial", 12), text_color=self.text_muted, width=120, anchor="w").pack(
            side="left")
        ctk.CTkLabel(row, text=time_txt, font=("Arial", 12), text_color=self.text_muted, width=100, anchor="w").pack(
            side="left")

        pill = ctk.CTkLabel(row, text=status, fg_color=color, text_color="white", width=80, height=24, corner_radius=12,
                            font=("Arial", 11, "bold"))
        pill.pack(side="right", padx=10)

        ctk.CTkFrame(parent, height=1, fg_color="#F0F0F0").pack(fill="x", padx=20)

    def build_active_personnel(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card, text="Active Personnel (LAN)", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=20, pady=(20, 15))
        self.add_person(card, "Krizzy Balogo", "Desk Officer", True)
        self.add_person(card, "Kristan Ariate", "Investigator", True)
        self.add_person(card, "Ayumi Melchor", "Brgy. Captain", False)
        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

    def add_person(self, parent, name, role, is_online):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)

        dot_color = self.green if is_online else "#CCCCCC"
        ctk.CTkLabel(row, text="●", text_color=dot_color, font=("Arial", 14)).pack(side="left", padx=(0, 10))

        txt_frame = ctk.CTkFrame(row, fg_color="transparent")
        txt_frame.pack(side="left")
        ctk.CTkLabel(txt_frame, text=name, font=("Arial", 12, "bold"), text_color=self.text_dark).pack(anchor="w",
                                                                                                       pady=0)
        ctk.CTkLabel(txt_frame, text=role, font=("Arial", 10), text_color=self.text_muted).pack(anchor="w", pady=0)

    def build_incident_analytics(self, parent, analytics_data):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x")

        ctk.CTkLabel(card, text="Incident Analytics", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=20, pady=(20, 10))

        hotspot = analytics_data.get("hotspot", "N/A")
        peak = analytics_data.get("peak_hours", "N/A")
        pct_float = analytics_data.get("hotspot_pct", 0.0)
        pct_display = int(pct_float * 100)

        ctk.CTkLabel(card, text=f"🔥 Top Hotspot: {hotspot}", font=("Arial", 12, "bold"), text_color=self.red).pack(
            anchor="w", padx=20, pady=(5, 5))
        ctk.CTkLabel(card, text=f"{hotspot} Incidents ({pct_display}% of Total)", font=("Arial", 11),
                     text_color=self.text_muted).pack(anchor="w", padx=20)

        bar = ctk.CTkProgressBar(card, fg_color="#F0F0F0", progress_color=self.red, height=8)
        bar.pack(fill="x", padx=20, pady=(5, 15))
        bar.set(pct_float)

        ctk.CTkLabel(card, text=f"🕒 Peak Hours: {peak}", font=("Arial", 12, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=20, pady=(5, 20))

    def show_blotter_page(self):
        self.clear_main_frame()
        self.set_active_tab("blotter")
        IncidentBlotterPage(self.main_frame, self.engine, self.user)

    def show_resolution_page(self):
        self.clear_main_frame()
        self.set_active_tab("resolution")
        ResolutionPage(self.main_frame, self.engine, self.user)

    def show_analytics_page(self):
        self.clear_main_frame()
        self.set_active_tab("analytics")
        ctk.CTkLabel(self.main_frame, text="📊 Analytics Page (Coming Soon)", font=("Arial", 24),
                     text_color=self.text_muted).pack(pady=100)
