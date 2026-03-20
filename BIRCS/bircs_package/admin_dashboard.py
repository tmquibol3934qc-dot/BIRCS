import customtkinter as ctk
from tkinter import messagebox


class AdminDashboardWindow:
    def __init__(self, engine, kapitan_data, parent_dashboard=None):
        self.engine = engine
        self.kapitan = kapitan_data
        self.parent_dashboard = parent_dashboard

        self.window = ctk.CTkToplevel()
        self.window.title("BICRS - Kapitan Control Center")
        self.window.state('zoomed')

        # Admin Theme Colors
        self.bg_color = "#F4F7F6"
        self.sidebar_color = "#1E392A"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"

        self.primary = "#27AE60"
        self.orange = "#F2994A"
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
        ctk.CTkLabel(logo_frame, text="BICRS ADMIN", font=("Arial", 24, "bold"), text_color="white").pack(
            anchor="center")
        ctk.CTkLabel(logo_frame, text="Kapitan Override Active", font=("Arial", 11), text_color=self.primary).pack(
            anchor="center")

        user_name = f"{self.kapitan.get('first_name', '')} {self.kapitan.get('last_name', '')}"
        ctk.CTkLabel(sidebar, text=f"Welcome, {user_name}", font=("Arial", 12, "bold"), text_color="white").pack(
            pady=(0, 5))
        ctk.CTkLabel(sidebar, text="KAPITAN", font=("Arial", 10), text_color=self.primary).pack(pady=(0, 20))

        # --- THE NAVIGATION MENU ---
        self.nav_buttons["dashboard"] = self.create_nav_btn(sidebar, "📁 Master Dashboard", self.show_overview_page)
        self.nav_buttons["users"] = self.create_nav_btn(sidebar, "👥 Team Management", self.show_user_management)
        self.nav_buttons["analytics"] = self.create_nav_btn(sidebar, "📊 Deep Analytics", self.show_analytics_page)

        ctk.CTkFrame(sidebar, height=150, fg_color="transparent").pack()

        close_btn = ctk.CTkButton(sidebar, text="Lock & Exit Admin", fg_color="transparent",
                                  text_color=self.red, hover_color="#3A1E1E",
                                  font=("Arial", 13, "bold"), command=self.close_admin)
        close_btn.pack(side="bottom", pady=20)

    def close_admin(self):
        self.window.destroy()
        if self.parent_dashboard:
            self.parent_dashboard.restore_dashboard()

    def create_nav_btn(self, parent, text, command=None):
        btn = ctk.CTkButton(parent, text=f"  {text}", fg_color="transparent", text_color="#CCCCCC",
                            hover_color="#2C4C3B", anchor="w", height=45, corner_radius=8,
                            font=("Arial", 13, "bold"), command=command)
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def set_active_tab(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=self.primary, text_color="white", hover_color=self.primary)
            else:
                btn.configure(fg_color="transparent", text_color="#CCCCCC", hover_color="#2C4C3B")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # =========================================================
    # 1. MASTER OVERVIEW PAGE & INCIDENT TABLE
    # =========================================================
    def show_overview_page(self):
        self.clear_main_frame()
        self.set_active_tab("dashboard")

        db_stats = self.engine.get_dashboard_stats()
        db_incidents = self.engine.get_all_incidents()
        db_analytics = self.engine.get_incident_analytics()

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Master Overview", font=("Arial", 24, "bold"), text_color=self.text_dark).pack(
            side="left")

        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25)

        self.create_stat_card(stats_frame, "Total Cases", str(db_stats.get('Total Cases', 0)), self.primary)
        self.create_stat_card(stats_frame, "Pending", str(db_stats.get('Pending', 0)), self.orange)
        self.create_stat_card(stats_frame, "Resolved", str(db_stats.get('Resolved', 0)), self.primary)
        self.create_stat_card(stats_frame, "Urgent", str(db_stats.get('Urgent', 0)), self.red)

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

        ctk.CTkLabel(top_ctrls, text="Master Incident Log (Click to view details)", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_table)

        search = ctk.CTkEntry(top_ctrls, textvariable=self.search_var, placeholder_text="Search Global Database...",
                              width=180, height=30, border_color="#E0E0E0")
        search.pack(side="right", padx=(10, 0))

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

        self.table_rows_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
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
            if row.get('status') == 'Resolved':
                color = self.primary
            elif row.get('status') == 'Urgent':
                color = self.red
            else:
                color = self.orange

            self.add_table_row(self.table_rows_frame, row, color)

    def add_table_row(self, parent, row_data, color):
        row_frame = ctk.CTkFrame(parent, fg_color="transparent", height=40, cursor="hand2")
        row_frame.pack(fill="x", padx=20, pady=5)
        row_frame.pack_propagate(False)

        def on_enter(e): row_frame.configure(fg_color="#E8F5E9")

        def on_leave(e): row_frame.configure(fg_color="transparent")

        click_cmd = lambda e, r=row_data: self.show_incident_details(r)

        case_id = str(row_data.get('case_no', ''))
        type_txt = f"Zone: {row_data.get('zone', '')}"
        proc_by = row_data.get('processed_by', '')
        time_txt = row_data.get('exact_time', '')
        status = row_data.get('status', '')

        l1 = ctk.CTkLabel(row_frame, text=case_id, font=("Arial", 12), text_color=self.primary, width=60, anchor="w")
        l1.pack(side="left")
        l2 = ctk.CTkLabel(row_frame, text=type_txt, font=("Arial", 12), text_color=self.text_dark, width=150,
                          anchor="w")
        l2.pack(side="left")
        l3 = ctk.CTkLabel(row_frame, text=proc_by, font=("Arial", 12), text_color=self.text_muted, width=120,
                          anchor="w")
        l3.pack(side="left")
        l4 = ctk.CTkLabel(row_frame, text=time_txt, font=("Arial", 12), text_color=self.text_muted, width=100,
                          anchor="w")
        l4.pack(side="left")

        pill = ctk.CTkLabel(row_frame, text=status, fg_color=color, text_color="white", width=80, height=24,
                            corner_radius=12, font=("Arial", 11, "bold"))
        pill.pack(side="right", padx=10)

        row_frame.bind("<Button-1>", click_cmd)
        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)

        for widget in row_frame.winfo_children():
            widget.bind("<Button-1>", click_cmd)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        ctk.CTkFrame(parent, height=1, fg_color="#F0F0F0").pack(fill="x", padx=20)

    def show_incident_details(self, row_data):
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Incident Details - Case #{row_data.get('case_no')}")
        popup.geometry("700x750")
        popup.transient(self.window)
        popup.grab_set()

        scroll_area = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll_area.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_area, text=f"Case #{row_data.get('case_no')} Comprehensive Report",
                     font=("Arial", 22, "bold"), text_color=self.primary).pack(pady=(10, 15))

        # --- SECTION 1: GENERAL INFORMATION ---
        ctk.CTkLabel(scroll_area, text="📋 General Information", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)
        info_frame = ctk.CTkFrame(scroll_area, fg_color="#FFFFFF", corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(info_frame, text="Zone Level:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w",
                                                                                      padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=row_data.get('zone', 'N/A')).grid(row=0, column=1, sticky="w", padx=(0, 40))

        exact_date = row_data.get('date_of_incident') or 'N/A'
        exact_time = row_data.get('exact_time') or ''
        ctk.CTkLabel(info_frame, text="Logged Date/Time:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w",
                                                                                            padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=f"{exact_date} {exact_time}").grid(row=1, column=1, sticky="w", padx=(0, 40))

        processed_by = row_data.get('processed_by') or 'Not Recorded'
        ctk.CTkLabel(info_frame, text="Handling Officer:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w",
                                                                                            pady=5)
        ctk.CTkLabel(info_frame, text=processed_by, text_color=self.primary, font=("Arial", 12, "bold")).grid(row=0,
                                                                                                              column=3,
                                                                                                              sticky="w",
                                                                                                              padx=10)

        status = row_data.get('status') or 'N/A'
        ctk.CTkLabel(info_frame, text="Current Status:", font=("Arial", 12, "bold")).grid(row=1, column=2, sticky="w",
                                                                                          pady=5)
        status_color = self.red if status == 'Urgent' else (self.primary if status == 'Resolved' else self.orange)
        ctk.CTkLabel(info_frame, text=status, text_color=status_color, font=("Arial", 12, "bold")).grid(row=1, column=3,
                                                                                                        sticky="w",
                                                                                                        padx=10)

        # --- SECTION 2: INVOLVED PARTIES ---
        ctk.CTkLabel(scroll_area, text="👥 Involved Parties", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)
        parties_frame = ctk.CTkFrame(scroll_area, fg_color="#F8F9FA", corner_radius=8)
        parties_frame.pack(fill="x", padx=20, pady=(5, 15))

        complainant = row_data.get('complainant_name')
        if not complainant: complainant = "Not Recorded"

        defendant = row_data.get('respondent_name')
        if not defendant: defendant = "Not Recorded"

        ctk.CTkLabel(parties_frame, text="Complainant:", font=("Arial", 12, "bold"), text_color=self.primary).grid(
            row=0, column=0, sticky="w", padx=15, pady=8)
        ctk.CTkLabel(parties_frame, text=complainant, font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(parties_frame, text="Defendant/Respondent:", font=("Arial", 12, "bold"), text_color=self.red).grid(
            row=1, column=0, sticky="w", padx=15, pady=(0, 8))
        ctk.CTkLabel(parties_frame, text=defendant, font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=10)

        # --- SECTION 3: NARRATIVE ---
        ctk.CTkLabel(scroll_area, text="📝 Officer's Narrative", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)
        nar_box = ctk.CTkTextbox(scroll_area, height=130, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                 border_color="#E0E0E0")
        nar_box.pack(fill="x", padx=20, pady=(5, 2))  # Shrunk bottom padding for the stamp

        narrative = row_data.get('narrative')
        if not narrative: narrative = "No narrative provided for this case."
        nar_box.insert("1.0", narrative)
        nar_box.configure(state="disabled")

        # --- ADDED: NARRATIVE AUDIT STAMP ---
        log_stamp = f"Initial report filed by: {processed_by} | {exact_date} {exact_time}".strip()
        ctk.CTkLabel(scroll_area, text=log_stamp, font=("Arial", 11, "italic"), text_color=self.text_muted).pack(
            anchor="e", padx=25, pady=(0, 15))

        # --- SECTION 4: RESOLUTION & COMPLIANCE ---
        ctk.CTkLabel(scroll_area, text="⚖️ Settlement & Resolution Terms", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)

        stage = row_data.get('hearing_stage') or 'N/A'
        deadline = row_data.get('compliance_deadline') or 'N/A'

        if stage != 'N/A' or deadline != 'N/A':
            details_txt = f"Stage: {stage}   |   Deadline: {deadline}"
            ctk.CTkLabel(scroll_area, text=details_txt, font=("Arial", 11, "italic"), text_color=self.text_muted).pack(
                anchor="w", padx=20, pady=(0, 5))

        res_box = ctk.CTkTextbox(scroll_area, height=130, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                 border_color="#E0E0E0")
        res_box.pack(fill="x", padx=20, pady=(0, 2))  # Shrunk bottom padding for the stamp

        res_text = row_data.get('settlement_details')
        if not res_text:
            res_text = "Case is still pending. No settlement agreement has been recorded yet."

        res_box.insert("1.0", res_text)
        res_box.configure(state="disabled")

        # --- ADDED: RESOLUTION AUDIT STAMP ---
        if status == 'Resolved':
            ctk.CTkLabel(scroll_area, text=f"Resolution finalized & authorized by: {processed_by}",
                         font=("Arial", 11, "italic"), text_color=self.text_muted).pack(anchor="e", padx=25,
                                                                                        pady=(0, 10))

        ctk.CTkButton(scroll_area, text="Close Report", command=popup.destroy, fg_color="#E0E0E0",
                      text_color=self.text_dark, hover_color="#CCCCCC").pack(pady=(10, 20))

    # =========================================================
    # 2. RIGHT PANEL WIDGETS
    # =========================================================
    def build_active_personnel(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card, text="Active Personnel (LAN)", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=20, pady=(20, 15))
        self.add_person(card, "Krizzy Balogo", "Desk Officer", True)
        self.add_person(card, "Kristan Ariate", "Investigator", True)
        self.add_person(card, "Ayumi Melchor", "Brgy. Captain", True)
        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

    def add_person(self, parent, name, role, is_online):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)

        dot_color = self.primary if is_online else "#CCCCCC"
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

    def show_analytics_page(self):
        self.clear_main_frame()
        self.set_active_tab("analytics")
        ctk.CTkLabel(self.main_frame, text="📊 Deep Analytics (Coming Soon)", font=("Arial", 24),
                     text_color=self.text_muted).pack(pady=100)

    # =========================================================
    # 3. TEAM MANAGEMENT PAGE (THE NEW ADDITION!)
    # =========================================================
    def show_user_management(self):
        self.clear_main_frame()
        self.set_active_tab("users")

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Team Management", font=("Arial", 24, "bold"), text_color=self.text_dark).pack(
            side="left")

        # --- THE NEW ADD ACCOUNT BUTTON ---
        add_btn = ctk.CTkButton(header_frame, text="+ Add Account", fg_color=self.primary, hover_color="#1E8449",
                                font=("Arial", 12, "bold"), height=35, command=self.launch_add_account)
        add_btn.pack(side="right")

        self.user_list_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.user_list_container.pack(fill="both", expand=True, padx=20, pady=10)

        users = self.engine.get_all_users()
        for user in users:
            self.build_user_card(self.user_list_container, user)

    # --- THE FUNCTION THAT LAUNCHES THE FORM ---
    def launch_add_account(self):
        try:
            from bircs_package.signup_screen import SignupWindow
            # We pass is_admin_mode=True, and tell it to refresh this page when it's done!
            SignupWindow(self.window, self.engine, is_admin_mode=True, on_refresh=self.show_user_management)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch Account Creator: {e}")

    def build_user_card(self, parent, user):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=75)
        card.pack(fill="x", pady=5, padx=10)
        card.pack_propagate(False)

        initial = user.get('first_name', 'U')[0].upper()
        avatar = ctk.CTkFrame(card, width=45, height=45, corner_radius=22, fg_color="#E8EAF6")
        avatar.pack(side="left", padx=20, pady=15)
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=initial, font=("Arial", 16, "bold"), text_color="#3F51B5").pack(expand=True)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", pady=15)
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
        ctk.CTkLabel(info_frame, text=name, font=("Arial", 14, "bold"), text_color=self.text_dark).pack(anchor="w")

        is_active = user.get('status', 'Active').lower() == 'active'
        status_color = self.primary if is_active else self.red
        ctk.CTkLabel(info_frame, text=f"● {user.get('role', 'Staff').title()} ({user.get('status', 'Active')})",
                     font=("Arial", 11), text_color=status_color).pack(anchor="w")

        btn = ctk.CTkButton(card, text="View Details", fg_color="transparent", border_width=1, border_color="#D0D4DB",
                            text_color="#3F51B5", hover_color="#F0F2F5", width=100,
                            command=lambda u=user: self.show_user_details_popup(u))
        btn.pack(side="right", padx=20)

    def show_user_details_popup(self, user):
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Manage User - {user.get('username')}")
        popup.geometry("500x750")  # Made it slightly taller for the timer menu
        popup.transient(self.window)
        popup.grab_set()

        officer_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        stats = self.engine.get_user_performance_stats(officer_name)

        stat_frame = ctk.CTkFrame(popup, fg_color="#3F51B5", corner_radius=0)
        stat_frame.pack(fill="x")
        ctk.CTkLabel(stat_frame, text=f"Performance: {officer_name}", font=("Arial", 16, "bold"),
                     text_color="white").pack(pady=(20, 5))

        stat_text = f"Total Cases Handled: {stats.get('handled', 0)}   |   Successfully Resolved: {stats.get('resolved', 0)}"
        ctk.CTkLabel(stat_frame, text=stat_text, font=("Arial", 12), text_color="#E8EAF6").pack(pady=(0, 20))

        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40, pady=20)

        def create_field(parent, label_text, default_val):
            ctk.CTkLabel(parent, text=label_text, font=("Arial", 12, "bold"), text_color=self.text_dark).pack(
                anchor="w", pady=(5, 2))
            entry = ctk.CTkEntry(parent, width=400)
            entry.pack(fill="x")
            entry.insert(0, str(default_val))
            return entry

        fn_entry = create_field(form, "First Name", user.get('first_name', ''))
        ln_entry = create_field(form, "Last Name", user.get('last_name', ''))
        un_entry = create_field(form, "Username", user.get('username', ''))
        pw_entry = create_field(form, "Password", user.get('password', ''))

        # --- THE SECURITY LOCKDOWN FOR ROLES ---
        ctk.CTkLabel(form, text="System Role (Privilege Level)", font=("Arial", 12, "bold"),
                     text_color=self.text_dark).pack(anchor="w", pady=(10, 2))

        current_role = user.get('role', 'Staff')
        role_var = ctk.StringVar(value=current_role)

        if current_role.lower() == 'kapitan' or current_role.lower() == 'admin':
            # If this is the Kapitan, lock the box. They cannot be demoted, and nobody else can take this role.
            locked_box = ctk.CTkEntry(form, textvariable=role_var, state="disabled", fg_color="#E8EAF6",
                                      text_color="#3F51B5")
            locked_box.pack(fill="x")
        else:
            # If it's normal staff, ONLY show non-admin roles. "Kapitan" is completely removed.
            ctk.CTkOptionMenu(form, variable=role_var, values=["Desk Officer", "Investigator", "Staff"]).pack(fill="x")

        # --- THE DYNAMIC SUSPENSION TIMER ---
        ctk.CTkLabel(form, text="Account Status", font=("Arial", 12, "bold"), text_color=self.text_dark).pack(
            anchor="w", pady=(10, 2))
        status_var = ctk.StringVar(value=user.get('status', 'Active'))

        # This hidden frame holds the timer inputs
        suspend_frame = ctk.CTkFrame(form, fg_color="#FFF3E0", corner_radius=5)
        suspend_val_var = ctk.StringVar(value="24")
        suspend_type_var = ctk.StringVar(value="Hours")

        ctk.CTkLabel(suspend_frame, text="Suspend For:", font=("Arial", 11, "bold"), text_color="#E65100").pack(
            side="left", padx=(10, 5), pady=10)
        ctk.CTkEntry(suspend_frame, textvariable=suspend_val_var, width=50, height=25).pack(side="left", padx=5)
        ctk.CTkOptionMenu(suspend_frame, variable=suspend_type_var, values=["Hours", "Days"], width=80, height=25,
                          fg_color="#F57C00").pack(side="left", padx=5)

        # This function hides or shows the timer based on the dropdown choice
        def on_status_change(new_status):
            if new_status == "Suspended":
                suspend_frame.pack(fill="x", pady=(5, 0))
            else:
                suspend_frame.pack_forget()  # Hides the frame completely

        # Attach the function to the status dropdown
        status_dropdown = ctk.CTkOptionMenu(form, variable=status_var, values=["Active", "Blocked", "Suspended"],
                                            command=on_status_change)
        status_dropdown.pack(fill="x")

        # Run it once immediately just in case the user is ALREADY suspended when you open the popup
        on_status_change(status_var.get())

        # --- SAVE FUNCTION ---
        def save_changes():
            # Pass the new suspend values to the engine!
            success = self.engine.update_user_account(
                user.get('id'), fn_entry.get(), ln_entry.get(), un_entry.get(),
                pw_entry.get(), role_var.get(), status_var.get(),
                suspend_val_var.get(), suspend_type_var.get()
            )
            if success:
                messagebox.showinfo("Success", "User details updated securely!")
                popup.destroy()
                self.show_user_management()
            else:
                messagebox.showerror("Error", "Failed to update user. Check database connection.")

        ctk.CTkButton(popup, text="Save Changes", fg_color=self.primary, hover_color="#1E8449",
                      font=("Arial", 14, "bold"), height=40, command=save_changes).pack(pady=30, padx=40, fill="x")