import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import math
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
        self.window.overrideredirect(True)
        self.window.state('zoomed')
        self.window.protocol("WM_DELETE_WINDOW", self.force_logout_on_close)
        self.window.bind("<Key>", self.handle_shortcuts)

        # Colors
        self.bg_color = "#F4F7F6"
        self.sidebar_color = "#FFFFFF"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"
        self.primary = "#E79124"
        self.orange = "#F2994A"
        self.green = "#27AE60"
        self.red = "#EB5757"

        # ==========================================
        # TIMER, AUDIT & CACHE INIT LOGIC
        # ==========================================
        self.login_time = datetime.now()
        self.audit_id = self.user.get('audit_id')

        # THE FIX: Dito itatago ni Python yung mga pages para mabilis lumipat!
        self.page_cache = {}

        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}

        self.create_sidebar()

        self.main_frame = ctk.CTkFrame(self.window, fg_color=self.bg_color, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.create_profile_panel()
        self.update_timer()
        self.show_overview_page()

    # ==========================================
    # SIDEBAR SETUP
    # ==========================================
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

        if hasattr(self, 'profile_btn'):
            if active_key == "dashboard":
                self.profile_btn.place(relx=0.98, rely=0.02, anchor="ne")
            else:
                self.profile_btn.place_forget()
                if self.panel_visible:
                    self.account_panel.place_forget()
                    self.panel_visible = False

    def hide_all_pages(self):
        # Imbes na destroy(), itatago lang natin para mabilis lumipat ng tabs!
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()
            widget.grid_forget()

    # ==========================================
    # FLOATING PROFILE PANEL & TIMER LOGIC
    # ==========================================
    def create_profile_panel(self):
        self.profile_btn = ctk.CTkButton(
            self.window, text="👤", width=45, height=45, corner_radius=22,
            fg_color="transparent", text_color=self.primary,
            hover_color="#E0E0E0", font=("Arial", 24),
            command=self.toggle_profile_panel
        )
        self.profile_btn.place(relx=0.98, rely=0.02, anchor="ne")

        self.account_panel = ctk.CTkFrame(self.window, width=250, corner_radius=10, fg_color="white", border_width=1,
                                          border_color="#E0E0E0")
        self.panel_visible = False

        header_frame = ctk.CTkFrame(self.account_panel, fg_color=self.primary, corner_radius=10)
        header_frame.pack(fill="x")
        header_frame.configure(corner_radius=0)
        ctk.CTkLabel(header_frame, text="Account Information", font=("Arial", 14, "bold"), text_color="white").pack(
            pady=10, padx=15, anchor="w")

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        emp_no = self.user.get('employee_id', 'EMP-Default')
        role = self.user_role

        ctk.CTkLabel(self.account_panel, text="Name:", font=("Arial", 10), text_color=self.text_muted).pack(anchor="w",
                                                                                                            padx=15,
                                                                                                            pady=(10,
                                                                                                                  0))
        ctk.CTkLabel(self.account_panel, text=user_name, font=("Arial", 12, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=15)

        ctk.CTkLabel(self.account_panel, text="Employee Number:", font=("Arial", 10), text_color=self.text_muted).pack(
            anchor="w", padx=15, pady=(5, 0))
        ctk.CTkLabel(self.account_panel, text=emp_no, font=("Arial", 12, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=15)

        ctk.CTkLabel(self.account_panel, text="Position:", font=("Arial", 10), text_color=self.text_muted).pack(
            anchor="w", padx=15, pady=(5, 0))
        ctk.CTkLabel(self.account_panel, text=role.upper(), font=("Arial", 12, "bold"), text_color=self.primary).pack(
            anchor="w", padx=15)

        ctk.CTkFrame(self.account_panel, height=1, fg_color="#E0E0E0").pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(self.account_panel, text="Session Started:", font=("Arial", 10), text_color=self.text_muted).pack(
            anchor="w", padx=15)
        self.timer_label = ctk.CTkLabel(self.account_panel, text="Just now", font=("Arial", 12, "bold"),
                                        text_color=self.green)
        self.timer_label.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkFrame(self.account_panel, height=1, fg_color="#E0E0E0").pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(self.account_panel, text="🔑 Kapitan Access", fg_color="transparent", text_color=self.orange,
                      hover_color="#FFF3E0", font=("Arial", 12, "bold"), command=self.prompt_admin_access).pack(
            fill="x", padx=10, pady=5)
        ctk.CTkButton(self.account_panel, text="Log Out", fg_color="transparent", text_color=self.red,
                      hover_color="#FEEEEE", font=("Arial", 12, "bold"), command=self.handle_logout).pack(fill="x",
                                                                                                          padx=10,
                                                                                                          pady=(0, 15))

    def toggle_profile_panel(self):
        if self.panel_visible:
            self.account_panel.place_forget()
            self.panel_visible = False
        else:
            self.account_panel.place(relx=0.98, rely=0.08, anchor="ne")
            self.account_panel.lift()
            self.panel_visible = True

    def update_timer(self):
        diff = datetime.now() - self.login_time
        mins = int(diff.total_seconds() // 60)

        if mins < 1:
            time_text = "Just now"
        elif mins < 60:
            time_text = f"{mins} minute{'s' if mins > 1 else ''} ago"
        else:
            hours = mins // 60
            rem_mins = mins % 60
            time_text = f"{hours} hr {rem_mins} min ago"

        self.timer_label.configure(text=time_text)
        self.window.after(60000, self.update_timer)

    # ==========================================
    # OVERVIEW DASHBOARD
    # ==========================================
    def show_overview_page(self):
        self.hide_all_pages()
        self.set_active_tab("dashboard")

        # Lagi nating ide-destroy ang lumang dashboard cache para mag-update yung "Total Cases" Count!
        if "dashboard" in self.page_cache:
            self.page_cache["dashboard"].destroy()

        dashboard_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        dashboard_container.pack(fill="both", expand=True)
        self.page_cache["dashboard"] = dashboard_container

        db_stats = self.engine.get_dashboard_stats()
        db_analytics = self.engine.get_incident_analytics()

        header_frame = ctk.CTkFrame(dashboard_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Command Center Dashboard", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")

        stats_frame = ctk.CTkFrame(dashboard_container, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25)

        self.create_stat_card(stats_frame, "Total Cases", str(db_stats['Total Cases']), self.primary)
        self.create_stat_card(stats_frame, "Normal", str(db_stats['Pending']), self.orange)
        self.create_stat_card(stats_frame, "Resolved", str(db_stats['Resolved']), self.green)
        self.create_stat_card(stats_frame, "Urgent", str(db_stats['Urgent']), self.red)

        body_frame = ctk.CTkFrame(dashboard_container, fg_color="transparent")
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
    # TABLE, PAGINATION & DEBOUNCED SEARCH
    # ==========================================
    def build_table(self, container):
        self.current_page = 1
        self.items_per_page = 10  # Rows per page

        top_ctrls = ctk.CTkFrame(container, fg_color="transparent")
        top_ctrls.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(top_ctrls, text="Recent Blotter Entries", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(side="left")

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        dropdown = ctk.CTkOptionMenu(top_ctrls, variable=self.filter_category_var, values=cat_list,
                                     fg_color=self.primary, width=140, height=35,
                                     command=lambda e: self.trigger_live_filter(reset_page=True))
        dropdown.pack(side="right", padx=(10, 0))

        self.search_entry = ctk.CTkEntry(top_ctrls, placeholder_text="e.g., Search Case ID, Name, or Zone...",
                                         width=280, height=35, border_color="#E0E0E0")
        self.search_entry.pack(side="right", padx=(10, 0))

        # ANTI-LAG FEATURE: Ginagamit ang delayed_search imbes na trigger agad!
        self.search_entry.bind("<KeyRelease>", self.delayed_search)

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

        self.pagination_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(10, 15))

        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="< Previous", width=100, fg_color="#E0E0E0",
                                      text_color=self.text_dark, hover_color="#D0D0D0", command=self.prev_page)
        self.btn_prev.pack(side="left", padx=10)

        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 12, "bold"),
                                     text_color=self.text_dark)
        self.lbl_page.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >", width=100, fg_color="#E0E0E0",
                                      text_color=self.text_dark, hover_color="#D0D0D0", command=self.next_page)
        self.btn_next.pack(side="right", padx=10)

        self.trigger_live_filter(reset_page=True)

    def delayed_search(self, event):
        # I-cancel ang luma kung nagta-type pa
        if hasattr(self, 'search_timer') and self.search_timer:
            self.window.after_cancel(self.search_timer)
        # Maghintay ng 500ms bago mag-search
        self.search_timer = self.window.after(500, lambda: self.trigger_live_filter(reset_page=True))

    def trigger_live_filter(self, *args, reset_page=True):
        if reset_page:
            self.current_page = 1

        keyword = self.search_entry.get()
        category = self.filter_category_var.get()
        all_data = self.engine.advanced_search_incidents(keyword, category)

        if not all_data:
            self.draw_table_rows([])
            self.lbl_page.configure(text="Page 0 of 0")
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            return

        total_items = len(all_data)
        total_pages = math.ceil(total_items / self.items_per_page)

        if self.current_page > total_pages: self.current_page = total_pages
        if self.current_page < 1: self.current_page = 1

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        cases_to_display = all_data[start_index:end_index]

        self.draw_table_rows(cases_to_display)

        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

    def next_page(self):
        self.current_page += 1
        self.trigger_live_filter(reset_page=False)

    def prev_page(self):
        self.current_page -= 1
        self.trigger_live_filter(reset_page=False)

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

        row.bind("<Button-1>", lambda e=None, c=case: self.show_incident_details(c))

        id_lbl = ctk.CTkLabel(row, text=case.get('case_no'), font=("Arial", 12), text_color=self.primary, width=60,
                              anchor="w", cursor="hand2")
        id_lbl.pack(side="left")
        id_lbl.bind("<Button-1>", lambda e=None, c=case: self.show_incident_details(c))

        type_lbl = ctk.CTkLabel(row, text=type_txt, font=("Arial", 12, "bold"), text_color=self.text_dark, width=180,
                                anchor="w", cursor="hand2")
        type_lbl.pack(side="left", padx=(0, 10))
        type_lbl.bind("<Button-1>", lambda e=None, c=case: self.show_incident_details(c))

        proc_lbl = ctk.CTkLabel(row, text=case.get('processed_by'), font=("Arial", 12), text_color=self.text_muted,
                                width=120, anchor="w", cursor="hand2")
        proc_lbl.pack(side="left")
        proc_lbl.bind("<Button-1>", lambda e=None, c=case: self.show_incident_details(c))

        time_lbl = ctk.CTkLabel(row, text=case.get('exact_time'), font=("Arial", 12), text_color=self.text_muted,
                                width=100, anchor="w", cursor="hand2")
        time_lbl.pack(side="left")
        time_lbl.bind("<Button-1>", lambda e=None, c=case: self.show_incident_details(c))

        raw_status = case.get('status')
        display_status = "Normal" if raw_status == "Pending" else raw_status

        pill = ctk.CTkLabel(row, text=display_status, fg_color=color, text_color="white", width=80, height=24,
                            corner_radius=12, font=("Arial", 11, "bold"), cursor="hand2")
        pill.pack(side="right", padx=10)
        pill.bind("<Button-1>", lambda e=None, c=case: self.show_incident_details(c))

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

        info_frame = ctk.CTkFrame(scroll_area, fg_color="#FFFFFF", corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(info_frame, text="Category:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w",
                                                                                    padx=15, pady=(10, 5))
        ctk.CTkLabel(info_frame, text=row_data.get('category', 'Uncategorized'), text_color=self.orange,
                     font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 5))

        status = row_data.get('status') or 'N/A'
        display_status = "Normal" if status == "Pending" else status
        status_color = self.red if status == 'Urgent' else (self.green if status == 'Resolved' else self.orange)

        ctk.CTkLabel(info_frame, text="Status:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w", padx=15,
                                                                                  pady=(10, 5))
        ctk.CTkLabel(info_frame, text=display_status, text_color=status_color, font=("Arial", 12, "bold")).grid(row=0,
                                                                                                                column=3,
                                                                                                                sticky="w",
                                                                                                                padx=10,
                                                                                                                pady=(
                                                                                                                    10,
                                                                                                                    5))

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

        reopen_stat = row_data.get('reopen_status')

        if row_data.get('narrative_2'):
            if reopen_stat == 'Requested':
                p2_title, title_col = "⏳ Phase 2: Re-open Request (Pending)", self.orange
            elif reopen_stat == 'Denied':
                p2_title, title_col = "❌ Phase 2: Request Denied", self.red
            else:
                p2_title, title_col = "🔄 Phase 2: Case Re-opened", self.green

            ctk.CTkLabel(scroll_area, text=p2_title, font=("Arial", 14, "bold"), text_color=title_col).pack(anchor="w",
                                                                                                            padx=20,
                                                                                                            pady=(15,
                                                                                                                  5))

            n2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                    border_color="#E0E0E0")
            n2_box.pack(fill="x", padx=20, pady=5)
            n2_box.insert("1.0", f"STAFF REASON:\n{row_data.get('narrative_2')}")
            n2_box.configure(state="disabled")

            if row_data.get('settlement_details_2'):
                r2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F0FFF0", text_color="#2B2B2B",
                                        border_width=1, border_color="#E0E0E0")
                r2_box.pack(fill="x", padx=20, pady=5)
                r2_box.insert("1.0", f"NEW SETTLEMENT:\n{row_data.get('settlement_details_2')}")
                r2_box.configure(state="disabled")

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
                self.trigger_live_filter(reset_page=False)
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

        ctk.CTkLabel(card, text="Team Roster & Status", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", padx=20, pady=(20, 10))

        list_frame = ctk.CTkScrollableFrame(card, fg_color="transparent", height=150)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        users = self.engine.get_all_users()

        if not users:
            ctk.CTkLabel(list_frame, text="No personnel found.", text_color="gray", font=("Arial", 11, "italic")).pack(
                pady=10)
            return

        for u in users:
            full_name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
            role = u.get('role', 'Staff')
            acc_status = u.get('status', 'Active')
            self.add_person(list_frame, full_name, role, acc_status)

    def add_person(self, parent, name, role, acc_status):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)

        if acc_status == "Active":
            dot_color = self.green
        elif acc_status == "Suspended":
            dot_color = self.orange
        elif acc_status == "Blocked":
            dot_color = self.red
        else:
            dot_color = "#CCCCCC"

        ctk.CTkLabel(row, text="●", text_color=dot_color, font=("Arial", 14)).pack(side="left", padx=(0, 10))

        txt_frame = ctk.CTkFrame(row, fg_color="transparent")
        txt_frame.pack(side="left")

        ctk.CTkLabel(txt_frame, text=name, font=("Arial", 12, "bold"), text_color=self.text_dark).pack(anchor="w",
                                                                                                       pady=0)
        status_text = f"{role}  |  {acc_status}"
        ctk.CTkLabel(txt_frame, text=status_text, font=("Arial", 10), text_color=self.text_muted).pack(anchor="w",
                                                                                                       pady=0)

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
    # ADMIN ACCESS & LOGOUT
    # ==========================================
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
            if hasattr(self, 'audit_id') and self.audit_id:
                self.engine.log_user_logout(self.audit_id)
            self.window.destroy()
            if self.on_logout:
                self.on_logout()

    def force_logout_on_close(self):
        if hasattr(self, 'audit_id') and self.audit_id:
            self.engine.log_user_logout(self.audit_id)
        self.window.destroy()
        if self.on_logout:
            self.on_logout()

    # ==========================================
    # PAGE NAVIGATION (ANTI-LAG CACHE)
    # ==========================================
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

    def show_analytics_page(self):
        self.hide_all_pages()
        self.set_active_tab("analytics")

        if "analytics" not in self.page_cache:
            container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            ctk.CTkLabel(container, text="📊 Analytics Page (Coming Soon)", font=("Arial", 24),
                         text_color=self.text_muted).pack(pady=100)
            self.page_cache["analytics"] = container

        self.page_cache["analytics"].pack(fill="both", expand=True)

    # ==========================================
    # SMART KEYBOARD SHORTCUTS
    # ==========================================
    def handle_shortcuts(self, event):
        focused_widget = self.window.focus_get()
        if focused_widget:
            widget_type = type(focused_widget).__name__
            if widget_type in ['CTkEntry', 'CTkTextbox', 'Entry', 'Text']: return

        key = event.char.lower()
        if key == '1':
            self.show_overview_page()
        elif key == '2':
            self.show_blotter_page()
        elif key == '3':
            self.show_resolution_page()
        elif key == 'k':
            if hasattr(self, 'toggle_profile_panel'): self.prompt_admin_access()
        elif key == 'l':
            self.handle_logout()
