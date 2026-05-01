import customtkinter as ctk
import math
from .pdf_generator import PDFGenerator
from .modals import IncidentDetailsModal


class OverviewPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        self.sidebar_color, self.text_dark, self.text_muted = "#1D2153", "#2B2B2B", "#7A7A7A"
        self.primary, self.orange, self.red, self.green = "#2980B9", "#F39C12", "#E74C3C", "#27AE60"

        self.container = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        db_stats = self.engine.get_dashboard_stats()
        db_analytics = self.engine.get_incident_analytics()

        header_frame = ctk.CTkFrame(self.container, fg_color="white", corner_radius=8)
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Dashboard Overview", font=("Arial", 28, "bold"),
                     text_color=self.sidebar_color).pack(side="left", padx=20, pady=15)

        stats_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25)
        self.create_stat_card(stats_frame, "Total Cases", str(db_stats['Total Cases']), self.red)
        self.create_stat_card(stats_frame, "Normal", str(db_stats['Pending']), self.orange)
        self.create_stat_card(stats_frame, "Resolved", str(db_stats['Resolved']), self.green)
        self.create_stat_card(stats_frame, "Urgent", str(db_stats['Urgent']), self.red)

        body_frame = ctk.CTkFrame(self.container, fg_color="transparent")
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

        self.build_bottom_analytics()

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color="white", border_color=color, border_width=1, corner_radius=8, height=100)
        card.pack(side="left", fill="x", expand=True, padx=5)
        card.pack_propagate(False)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text=title, font=("Arial", 14, "bold"), text_color=color).pack(pady=(0, 5))
        ctk.CTkLabel(content, text=value, font=("Arial", 28, "bold"), text_color=color).pack()

    def build_table(self, container):
        self.current_page, self.items_per_page = 1, 10
        top_ctrls = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
        top_ctrls.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(top_ctrls, text="Filter Cases", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            side="left")

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        ctk.CTkOptionMenu(top_ctrls, variable=self.filter_category_var, values=cat_list, fg_color="white",
                          text_color=self.text_dark, button_color="#F0F0F0", button_hover_color="#E0E0E0", width=140,
                          height=35, command=lambda e: self.trigger_live_filter(reset_page=True)).pack(side="left",
                                                                                                       padx=(15, 0))

        self.search_entry = ctk.CTkEntry(top_ctrls, placeholder_text="Search Case ID or Name...", width=280, height=35,
                                         text_color=self.text_dark)
        self.search_entry.pack(side="right", padx=(10, 0))
        self.search_entry.bind("<KeyRelease>", self.delayed_search)

        title_row = ctk.CTkFrame(container, fg_color="#A3AEB5", corner_radius=0, height=45)
        title_row.pack(fill="x")
        title_row.pack_propagate(False)
        ctk.CTkLabel(title_row, text="Recent Blotter Entries", font=("Arial", 16, "bold"), text_color="white").pack(
            side="left", padx=20)

        self.table_rows_frame = ctk.CTkFrame(container, fg_color="white")
        self.table_rows_frame.pack(fill="both", expand=True)

        self.pagination_frame = ctk.CTkFrame(container, fg_color="white")
        self.pagination_frame.pack(fill="x", padx=20, pady=(10, 15))
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="< Previous", width=100, fg_color="#F0F0F0",
                                      text_color=self.text_dark, hover_color="#E0E0E0",
                                      command=lambda: self.change_page(-1))
        self.btn_prev.pack(side="left", padx=10)
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 12, "bold"),
                                     text_color=self.text_dark)
        self.lbl_page.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >", width=100, fg_color="#F0F0F0",
                                      text_color=self.text_dark, hover_color="#E0E0E0",
                                      command=lambda: self.change_page(1))
        self.btn_next.pack(side="right", padx=10)

        self.trigger_live_filter(reset_page=True)

    def delayed_search(self, event):
        if hasattr(self, 'search_timer') and self.search_timer: self.container.after_cancel(self.search_timer)
        self.search_timer = self.container.after(500, lambda: self.trigger_live_filter(reset_page=True))

    def trigger_live_filter(self, reset_page=True):
        if reset_page: self.current_page = 1
        all_data = self.engine.advanced_search_incidents(self.search_entry.get(), self.filter_category_var.get())
        if not all_data:
            self.draw_table_rows([])
            self.lbl_page.configure(text="Page 0 of 0")
            self.btn_prev.configure(state="disabled");
            self.btn_next.configure(state="disabled")
            return

        total_pages = math.ceil(len(all_data) / self.items_per_page)
        if self.current_page > total_pages: self.current_page = total_pages
        if self.current_page < 1: self.current_page = 1

        self.draw_table_rows(
            all_data[(self.current_page - 1) * self.items_per_page: self.current_page * self.items_per_page])
        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

    def change_page(self, direction):
        self.current_page += direction
        self.trigger_live_filter(reset_page=False)

    def draw_table_rows(self, data_to_draw):
        for widget in self.table_rows_frame.winfo_children(): widget.destroy()
        if not data_to_draw:
            return ctk.CTkLabel(self.table_rows_frame, text="No records found.", text_color=self.text_muted).pack(
                pady=20)

        for case in data_to_draw:
            row = ctk.CTkFrame(self.table_rows_frame, fg_color="white", height=45, cursor="hand2")
            row.pack(fill="x");
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=case.get('case_no'), font=("Arial", 12, "bold"), text_color=self.text_dark, width=60,
                         anchor="w", cursor="hand2").pack(side="left", padx=(20, 0))
            ctk.CTkLabel(row, text=f"{case.get('category', 'Uncategorized')} (Zone {case.get('zone', 'N/A')})",
                         font=("Arial", 12), text_color=self.text_dark, width=180, anchor="w", cursor="hand2").pack(
                side="left", padx=(0, 10))
            ctk.CTkLabel(row, text=case.get('processed_by'), font=("Arial", 12), text_color=self.text_muted, width=120,
                         anchor="w", cursor="hand2").pack(side="left")
            ctk.CTkLabel(row, text=case.get('exact_time'), font=("Arial", 12), text_color=self.text_muted, width=100,
                         anchor="w", cursor="hand2").pack(side="left")

            status = case.get('status')
            color = self.green if status == 'Resolved' else (self.red if status == 'Urgent' else self.orange)
            ctk.CTkLabel(row, text="Pending" if status == "Pending" else status, text_color=color,
                         font=("Arial", 12, "bold"), width=80, anchor="e", cursor="hand2").pack(side="right", padx=20)

            click_command = lambda e, c=case: IncidentDetailsModal(self.container.winfo_toplevel(), c, self.engine,
                                                                   self.user, self.trigger_live_filter)
            row.bind("<Button-1>", click_command)
            for child in row.winfo_children():
                child.bind("<Button-1>", click_command)

            ctk.CTkFrame(self.table_rows_frame, height=1, fg_color="#F0F0F0").pack(fill="x")

    def build_active_personnel(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E0E0E0", border_width=1, corner_radius=8)
        card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(card, text="Team Roster & Status", font=("Arial", 14, "bold"), text_color=self.sidebar_color).pack(
            anchor="w", padx=20, pady=(20, 10))
        list_frame = ctk.CTkScrollableFrame(card, fg_color="transparent", height=150)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for u in self.engine.get_all_users() or []:
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            color = self.green if u.get('status') == 'Active' else (
                self.red if u.get('status') == 'Blocked' else self.orange)
            ctk.CTkLabel(row, text="●", text_color=color, font=("Arial", 14)).pack(side="left", padx=(0, 10))
            txt_frame = ctk.CTkFrame(row, fg_color="transparent")
            txt_frame.pack(side="left")
            ctk.CTkLabel(txt_frame, text=f"{u.get('first_name', '')} {u.get('last_name', '')}",
                         font=("Arial", 12, "bold"), text_color=self.text_dark).pack(anchor="w", pady=0)
            ctk.CTkLabel(txt_frame, text=f"{u.get('role')} | {u.get('status')}", font=("Arial", 10),
                         text_color=self.text_muted).pack(anchor="w", pady=0)

    def build_incident_analytics(self, parent, data):
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#E0E0E0", border_width=1, corner_radius=8)
        card.pack(fill="x")
        ctk.CTkLabel(card, text="Incident Analytics", font=("Arial", 14, "bold"), text_color=self.sidebar_color).pack(
            anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(card, text=f"🔥 Hotspot: {data.get('hotspot', 'N/A')}", font=("Arial", 12, "bold"),
                     text_color=self.red).pack(anchor="w", padx=20, pady=(5, 5))
        ctk.CTkLabel(card, text=f"🕒 Peak: {data.get('peak_hours', 'N/A')}", font=("Arial", 12, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20, pady=(5, 20))

    def build_bottom_analytics(self):
        report_frame = ctk.CTkFrame(self.container, fg_color="white", corner_radius=15, border_color="#E0E0E0",
                                    border_width=1)
        report_frame.pack(fill="x", padx=30, pady=(0, 30))

        top_ctrl = ctk.CTkFrame(report_frame, fg_color="transparent")
        top_ctrl.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(top_ctrl, text="📊 Comprehensive Analytics Report", font=("Arial", 20, "bold"),
                     text_color=self.sidebar_color).pack(side="left")

        self.report_timeframe = ctk.StringVar(value="This Month")
        dropdown = ctk.CTkOptionMenu(top_ctrl, variable=self.report_timeframe,
                                     values=["This Week", "This Month", "This Year", "All Time"],
                                     fg_color=self.sidebar_color, text_color="white", button_color="#2C3E50",
                                     command=lambda e: self.update_report_ui())
        dropdown.pack(side="left", padx=20)

        ctk.CTkButton(top_ctrl, text="🖨️ Generate PDF Report", fg_color=self.green, hover_color="#1E8449",
                      font=("Arial", 12, "bold"), height=35,
                      command=lambda: PDFGenerator.export_analytics(
                          self.engine.get_timeframe_analytics(self.report_timeframe.get()),
                          self.report_timeframe.get())).pack(side="right")

        self.info_cards_container = ctk.CTkFrame(report_frame, fg_color="transparent")
        self.info_cards_container.pack(fill="x", padx=20, pady=(0, 25))
        self.info_cards_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_total = self.create_infograph_card(self.info_cards_container, 0, "Total Files", "0", "📁", "#34495E")
        self.card_resolved = self.create_infograph_card(self.info_cards_container, 1, "Resolved", "0", "✅", self.green,
                                                        has_progress=True)
        self.card_top = self.create_infograph_card(self.info_cards_container, 2, "Top Issue", "N/A", "🔥", self.red)

        self.update_report_ui()

    def create_infograph_card(self, parent, col, title, val, icon, color, has_progress=False):
        card = ctk.CTkFrame(parent, fg_color="#F8F9FA", corner_radius=12, height=120)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.pack_propagate(False)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 0))

        ctk.CTkLabel(header, text=icon, font=("Arial", 20)).pack(side="left")
        ctk.CTkLabel(header, text=title, font=("Arial", 13, "bold"), text_color=self.text_muted).pack(side="left",
                                                                                                      padx=10)

        val_lbl = ctk.CTkLabel(card, text=val, font=("Arial", 22, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=20, pady=(5, 0))

        progress = None
        if has_progress:
            progress = ctk.CTkProgressBar(card, height=8, progress_color=color, fg_color="#E0E0E0")
            progress.pack(fill="x", padx=20, pady=(10, 0))
            progress.set(0)

        return {"val_lbl": val_lbl, "progress": progress}

    def update_report_ui(self):
        data = self.engine.get_timeframe_analytics(self.report_timeframe.get())

        self.card_total["val_lbl"].configure(text=str(data['total']))

        self.card_resolved["val_lbl"].configure(text=str(data['resolved']))
        if data['total'] > 0:
            rate = data['resolved'] / data['total']
            self.card_resolved["progress"].set(rate)
        else:
            self.card_resolved["progress"].set(0)

        top_text = data['top_category']
        if len(top_text) > 18: top_text = top_text[:15] + "..."
        self.card_top["val_lbl"].configure(text=top_text)