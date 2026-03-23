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

        self.nav_buttons["dashboard"] = self.create_nav_btn(sidebar, "📁 Dashboard", self.show_overview_page)
        self.nav_buttons["blotter"] = self.create_nav_btn(sidebar, "📄 Incident Blotter", self.show_blotter_page)
        self.nav_buttons["resolution"] = self.create_nav_btn(sidebar, "⚖️ Resolution", self.show_resolution_page)
        self.nav_buttons["analytics"] = self.create_nav_btn(sidebar, "📊 Analytics", self.show_analytics_page)

        ctk.CTkFrame(sidebar, height=150, fg_color="transparent").pack()

        admin_btn = ctk.CTkButton(sidebar, text="🔑 Kapitan Access", fg_color="transparent", text_color=self.green,
                                  hover_color="#E8F5E9", font=("Arial", 13, "bold"), command=self.prompt_admin_access)
        admin_btn.pack(side="bottom", pady=(0, 5))

        logout_btn = ctk.CTkButton(sidebar, text="Log Out", fg_color="transparent", text_color=self.red,
                                   hover_color="#FEEEEE", font=("Arial", 13, "bold"), command=self.handle_logout)
        logout_btn.pack(side="bottom", pady=20)

    def prompt_admin_access(self):
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
            self.window.withdraw()
            from .admin_dashboard import AdminDashboardWindow
            AdminDashboardWindow(self.engine, kapitan_data, parent_dashboard=self)
        except Exception as e:
            self.window.deiconify()
            messagebox.showerror("System Error", f"Could not launch Admin Dashboard:\n{e}")

    def restore_dashboard(self):
        self.window.deiconify()
        self.window.state('zoomed')

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the Command Center?"):
            self.window.destroy()
            if self.on_logout:
                self.on_logout()

    def create_nav_btn(self, parent, text, command=None):
        btn = ctk.CTkButton(parent, text=f"  {text}", fg_color="transparent", text_color=self.text_muted,
                            hover_color="#F0F0F0", anchor="w", height=45, corner_radius=8, font=("Arial", 13, "bold"),
                            command=command)
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

    # ==========================================
    # OVERVIEW DASHBOARD
    # ==========================================
    def show_overview_page(self):
        self.clear_main_frame()
        self.set_active_tab("dashboard")

        db_stats = self.engine.get_dashboard_stats()
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

        self.build_table(table_container)

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

    # ==========================================
    # TABLE & LIVE FILTERING
    # ==========================================
    def build_table(self, container):
        top_ctrls = ctk.CTkFrame(container, fg_color="transparent")
        top_ctrls.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(top_ctrls, text="Recent Blotter Entries", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(side="left")

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        dropdown = ctk.CTkOptionMenu(top_ctrls, variable=self.filter_category_var, values=cat_list,
                                     fg_color=self.primary, width=140, height=35, command=self.trigger_live_filter)
        dropdown.pack(side="right", padx=(10, 0))

        self.search_entry = ctk.CTkEntry(top_ctrls, placeholder_text="e.g., Search Case ID, Name, or Zone...",
                                         width=280, height=35, border_color="#E0E0E0")
        self.search_entry.pack(side="right", padx=(10, 0))
        self.search_entry.bind("<KeyRelease>", self.trigger_live_filter)

        header_row = ctk.CTkFrame(container, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(header_row, text="ID", font=("Arial", 12, "bold"), text_color=self.text_muted, width=60,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Category & Zone", font=("Arial", 12, "bold"), text_color=self.text_muted,
                     width=180, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_row, text="Processed By", font=("Arial", 12, "bold"), text_color=self.primary, width=120,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Time", font=("Arial", 12, "bold"), text_color=self.text_muted, width=100,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Status", font=("Arial", 12, "bold"), text_color=self.text_muted, width=80,
                     anchor="e").pack(side="right", padx=10)

        ctk.CTkFrame(container, height=1, fg_color="#E0E0E0").pack(fill="x", padx=20, pady=5)

        self.table_rows_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.table_rows_frame.pack(fill="both", expand=True)

        self.trigger_live_filter()

    def trigger_live_filter(self, *args):
        keyword = self.search_entry.get()
        category = self.filter_category_var.get()
        filtered_data = self.engine.advanced_search_incidents(keyword, category)
        self.draw_table_rows(filtered_data)

    def draw_table_rows(self, data_to_draw):
        for widget in self.table_rows_frame.winfo_children():
            widget.destroy()

        if not data_to_draw:
            ctk.CTkLabel(self.table_rows_frame, text="No matching records found.", text_color=self.text_muted).pack(
                pady=20)
            return

        for case in data_to_draw:
            status = case.get('status')
            color = self.green if status == 'Resolved' else (self.red if status == 'Urgent' else self.orange)

            cat = case.get('category', 'Uncategorized')
            zone = case.get('zone', 'N/A')
            type_txt = f"{cat} ({zone})"

            self.add_table_row(self.table_rows_frame, case, type_txt, color)

    def add_table_row(self, parent, case, type_txt, color):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=40, cursor="hand2")
        row.pack(fill="x", padx=20, pady=5)
        row.pack_propagate(False)

        row.bind("<Button-1>", lambda e, c=case: self.show_incident_details(c))

        id_lbl = ctk.CTkLabel(row, text=case.get('case_no'), font=("Arial", 12), text_color=self.primary, width=60,
                              anchor="w", cursor="hand2")
        id_lbl.pack(side="left")
        id_lbl.bind("<Button-1>", lambda e, c=case: self.show_incident_details(c))

        type_lbl = ctk.CTkLabel(row, text=type_txt, font=("Arial", 12, "bold"), text_color=self.text_dark, width=180,
                                anchor="w", cursor="hand2")
        type_lbl.pack(side="left", padx=(0, 10))
        type_lbl.bind("<Button-1>", lambda e, c=case: self.show_incident_details(c))

        proc_lbl = ctk.CTkLabel(row, text=case.get('processed_by'), font=("Arial", 12), text_color=self.text_muted,
                                width=120, anchor="w", cursor="hand2")
        proc_lbl.pack(side="left")
        proc_lbl.bind("<Button-1>", lambda e, c=case: self.show_incident_details(c))

        time_lbl = ctk.CTkLabel(row, text=case.get('exact_time'), font=("Arial", 12), text_color=self.text_muted,
                                width=100, anchor="w", cursor="hand2")
        time_lbl.pack(side="left")
        time_lbl.bind("<Button-1>", lambda e, c=case: self.show_incident_details(c))

        pill = ctk.CTkLabel(row, text=case.get('status'), fg_color=color, text_color="white", width=80, height=24,
                            corner_radius=12, font=("Arial", 11, "bold"), cursor="hand2")
        pill.pack(side="right", padx=10)
        pill.bind("<Button-1>", lambda e, c=case: self.show_incident_details(c))

        ctk.CTkFrame(parent, height=1, fg_color="#F0F0F0").pack(fill="x", padx=20)

    # ==========================================
    # POPUP: INCIDENT DETAILS & KAPITAN REQUEST
    # ==========================================
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

        # --- SECTION 1: GENERAL INFO ---
        info_frame = ctk.CTkFrame(scroll_area, fg_color="#FFFFFF", corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(info_frame, text="Category:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w",
                                                                                    padx=15, pady=(10, 5))
        ctk.CTkLabel(info_frame, text=row_data.get('category', 'Uncategorized'), text_color=self.orange,
                     font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 5))

        status = row_data.get('status') or 'N/A'
        status_color = self.red if status == 'Urgent' else (self.green if status == 'Resolved' else self.orange)
        ctk.CTkLabel(info_frame, text="Status:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w", padx=15,
                                                                                  pady=(10, 5))
        ctk.CTkLabel(info_frame, text=status, text_color=status_color, font=("Arial", 12, "bold")).grid(row=0, column=3,
                                                                                                        sticky="w",
                                                                                                        padx=10,
                                                                                                        pady=(10, 5))

        # --- SECTION 2: PARTIES ---
        parties_frame = ctk.CTkFrame(scroll_area, fg_color="#F8F9FA", corner_radius=8)
        parties_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(parties_frame, text="Complainant:", font=("Arial", 12, "bold"), text_color=self.primary).grid(
            row=0, column=0, sticky="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(parties_frame,
                     text=f"{row_data.get('complainant_name')} (Contact: {row_data.get('complainant_contact') or 'N/A'})",
                     font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))

        ctk.CTkLabel(parties_frame, text="Respondent:", font=("Arial", 12, "bold"), text_color=self.red).grid(row=1,
                                                                                                              column=0,
                                                                                                              sticky="w",
                                                                                                              padx=15,
                                                                                                              pady=(2,
                                                                                                                    10))
        ctk.CTkLabel(parties_frame,
                     text=f"{row_data.get('respondent_name')} (Contact: {row_data.get('respondent_contact') or 'N/A'})",
                     font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=10, pady=(2, 10))

        # --- PHASE 1: NARRATIVE & RESOLUTION ---
        ctk.CTkLabel(scroll_area, text="📝 Phase 1: Original Report & Settlement", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)

        n1_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                border_color="#E0E0E0")
        n1_box.pack(fill="x", padx=20, pady=5)
        n1_box.insert("1.0", f"NARRATIVE:\n{row_data.get('narrative') or 'N/A'}")
        n1_box.configure(state="disabled")

        r1_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F0FFF0", text_color="#2B2B2B", border_width=1,
                                border_color="#E0E0E0")
        r1_box.pack(fill="x", padx=20, pady=5)
        r1_box.insert("1.0", f"SETTLEMENT:\n{row_data.get('settlement_details') or 'Case still pending.'}")
        r1_box.configure(state="disabled")

        # --- PHASE 2: DYNAMIC "DENIED" UX HANDLING ---
        reopen_stat = row_data.get('reopen_status')

        if row_data.get('narrative_2'):
            # Determine the title and color based on if it was denied!
            if reopen_stat == 'Requested':
                p2_title = "⏳ Phase 2: Re-open Request (Pending Approval)"
                title_col = self.orange
            elif reopen_stat == 'Denied':
                p2_title = "❌ Phase 2: Re-open Request (Denied by Kapitan)"
                title_col = self.red
            else:
                p2_title = "🔄 Phase 2: Case Re-opened"
                title_col = self.green

            ctk.CTkLabel(scroll_area, text=p2_title, font=("Arial", 14, "bold"), text_color=title_col).pack(anchor="w",
                                                                                                            padx=20,
                                                                                                            pady=(15,
                                                                                                                  5))

            n2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                    border_color="#E0E0E0")
            n2_box.pack(fill="x", padx=20, pady=5)
            n2_box.insert("1.0", f"STAFF REASON FOR RE-OPEN:\n{row_data.get('narrative_2')}")
            n2_box.configure(state="disabled")

            if row_data.get('settlement_details_2'):
                r2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F0FFF0", text_color="#2B2B2B",
                                        border_width=1, border_color="#E0E0E0")
                r2_box.pack(fill="x", padx=20, pady=5)
                r2_box.insert("1.0", f"NEW SETTLEMENT:\n{row_data.get('settlement_details_2')}")
                r2_box.configure(state="disabled")

        # --- THE BUTTON ROW (WITH KAPITAN REQUEST) ---
        btn_frame = ctk.CTkFrame(scroll_area, fg_color="transparent")
        btn_frame.pack(pady=(20, 20))

        if status == 'Resolved':
            if reopen_stat == 'Requested':
                ctk.CTkLabel(btn_frame, text="⏳ Pending Kapitan's Approval", text_color=self.orange,
                             font=("Arial", 12, "bold")).pack(side="left", padx=10)
            elif reopen_stat == 'Approved':
                ctk.CTkLabel(btn_frame, text="✅ Case Re-opened", text_color=self.green,
                             font=("Arial", 12, "bold")).pack(side="left", padx=10)
            elif reopen_stat == 'Denied':
                # If denied, show the badge AND give them the button back to try again!
                ctk.CTkLabel(btn_frame, text="❌ Request Denied", text_color=self.red, font=("Arial", 12, "bold")).pack(
                    side="left", padx=10)
                ctk.CTkButton(btn_frame, text="Submit New Request", fg_color=self.orange, hover_color="#C67B1D",
                              font=("Arial", 12, "bold"),
                              command=lambda: self.prompt_reopen_request(row_data.get('case_no'), popup)).pack(
                    side="left", padx=10)
            else:
                ctk.CTkButton(btn_frame, text="Request Re-open", fg_color=self.orange, hover_color="#C67B1D",
                              font=("Arial", 12, "bold"),
                              command=lambda: self.prompt_reopen_request(row_data.get('case_no'), popup)).pack(
                    side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Close Report", command=popup.destroy, fg_color="#E0E0E0",
                      text_color=self.text_dark, hover_color="#CCCCCC", font=("Arial", 12, "bold")).pack(side="left",
                                                                                                         padx=10)

    def prompt_reopen_request(self, case_no, parent_popup):
        req_window = ctk.CTkToplevel(self.window)
        req_window.title(f"Request Re-open: Case #{case_no}")
        req_window.geometry("500x350")
        req_window.transient(parent_popup)
        req_window.grab_set()

        ctk.CTkLabel(req_window, text="Reason for Re-opening (Sent to Kapitan)", font=("Arial", 14, "bold"),
                     text_color=self.primary).pack(pady=(20, 10))

        reason_box = ctk.CTkTextbox(req_window, height=150, fg_color="#F9F9F9", text_color="black", border_width=1,
                                    border_color="#E0E0E0")
        reason_box.pack(fill="x", padx=20, pady=(0, 20))

        def submit_request():
            reason = reason_box.get("1.0", "end-1c").strip()
            if not reason:
                messagebox.showwarning("Missing Info", "Please enter a reason to send to the Kapitan.")
                return

            if self.engine.request_case_reopen(case_no, reason):
                messagebox.showinfo("Success", "Request sent to Kapitan's Dashboard!")
                req_window.destroy()
                parent_popup.destroy()
                self.trigger_live_filter()
            else:
                messagebox.showerror("Error", "Failed to send request.")

        ctk.CTkButton(req_window, text="Send Request to Kapitan", fg_color=self.orange, hover_color="#C67B1D",
                      font=("Arial", 12, "bold"), command=submit_request).pack(pady=10)

    # ==========================================
    # RIGHT SIDE PANEL (Personnel & Analytics)
    # ==========================================
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

    # ==========================================
    # PAGE NAVIGATION
    # ==========================================
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
