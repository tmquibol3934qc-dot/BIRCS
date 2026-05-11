import customtkinter as ctk
from tkinter import messagebox
import math
import random  # 🚀 Added for dynamic chart data generation

try:
    from .pdf_generator import PDFGenerator
except ImportError:
    pass


class MasterDashboardPage:
    def __init__(self, parent_frame, engine, root_window):
        self.parent_frame = parent_frame
        self.engine = engine
        self.root_window = root_window

        self.current_page = 1
        self.items_per_page = 10
        self.all_filtered_cases = []

        # 🎨 THE PREMIUM WEB PALETTE
        self.primary = "#27AE60"  # Emerald Green
        self.dark_green = "#1E8449"
        self.red = "#E74C3C"  # Urgent Red
        self.orange = "#E05D3A"  # Web Orange (Updated from previous theme)
        self.sidebar_color = "#1D2153"  # Deep Navy
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"

        self.ui_font = "Poppins"
        self.header_font = "Young Serif"

        # 🚀 STICKY STRUCTURE
        self.main_wrapper = ctk.CTkFrame(self.parent_frame, fg_color="#F4F6F7")  # Light gray web background
        self.main_wrapper.pack(fill="both", expand=True)

        self.sticky_top = ctk.CTkFrame(self.main_wrapper, fg_color="transparent")
        self.sticky_top.pack(fill="x", side="top")

        self.scroll_container = ctk.CTkScrollableFrame(self.main_wrapper, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        db_stats = self.engine.get_dashboard_stats()
        db_analytics = self.engine.get_incident_analytics()

        # ==========================================
        # 📌 1. STICKY TOP SECTION
        # ==========================================
        header_frame = ctk.CTkFrame(self.sticky_top, fg_color="white", corner_radius=12, border_width=1,
                                    border_color="#EAECEE")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Master Database & Analytics", font=(self.header_font, 26, "bold"),
                     text_color=self.sidebar_color).pack(side="left", padx=25, pady=20)

        stats_frame = ctk.CTkFrame(self.sticky_top, fg_color="transparent")
        stats_frame.pack(fill="x", padx=25, pady=(0, 10))

        self.create_stat_card(stats_frame, "Total Cases", str(db_stats.get('Total Cases', 0)), self.sidebar_color)
        self.create_stat_card(stats_frame, "Routine", str(db_stats.get('Pending', 0)), self.orange)
        self.create_stat_card(stats_frame, "Resolved", str(db_stats.get('Resolved', 0)), self.primary)
        self.create_stat_card(stats_frame, "High Priority", str(db_stats.get('Urgent', 0)), self.red)

        # ==========================================
        # 📜 2. SCROLLABLE BODY SECTION
        # ==========================================
        body_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        body_frame.grid_columnconfigure(0, weight=3)
        body_frame.grid_columnconfigure(1, weight=1)

        table_container = ctk.CTkFrame(body_frame, fg_color="white", corner_radius=12, border_width=1,
                                       border_color="#EAECEE")
        table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.build_table(table_container)

        right_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")
        self.build_active_personnel(right_panel)
        self.build_incident_analytics(right_panel, db_analytics, db_stats)

        # 🚀 THE NEW ANALYTICS SECTION WITH GRAPH
        self.build_bottom_analytics()

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color="white", border_color=color, border_width=2, corner_radius=12, height=110)
        card.pack(side="left", fill="x", expand=True, padx=5)
        card.pack_propagate(False)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text=title, font=(self.ui_font, 13, "bold"), text_color="gray").pack(pady=(0, 5))
        ctk.CTkLabel(content, text=value, font=(self.header_font, 32, "bold"), text_color=color).pack()

    def build_table(self, container):
        top_ctrls = ctk.CTkFrame(container, fg_color="transparent")
        top_ctrls.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(top_ctrls, text="Filter Records", font=(self.ui_font, 16, "bold"),
                     text_color=self.sidebar_color).pack(side="left")

        status_list = ["All Status", "Re-open Requests", "Routine", "High Priority", "Resolved"]
        self.filter_status_var = ctk.StringVar(value="All Status")
        ctk.CTkOptionMenu(top_ctrls, variable=self.filter_status_var, values=status_list, fg_color="#F8F9FA",
                          text_color=self.red, button_color="#EAECEE", button_hover_color="#D5D8DC", width=140,
                          height=35, font=(self.ui_font, 12, "bold"), command=lambda e: self.reset_and_refresh()).pack(
            side="left", padx=(20, 5))

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        ctk.CTkOptionMenu(top_ctrls, variable=self.filter_category_var, values=cat_list, fg_color="#F8F9FA",
                          text_color=self.text_dark, button_color="#EAECEE", button_hover_color="#D5D8DC", width=140,
                          height=35, font=(self.ui_font, 12), command=lambda e: self.reset_and_refresh()).pack(
            side="left", padx=(5, 0))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(top_ctrls, textvariable=self.search_var, fg_color="#F8F9FA", border_width=1,
                                         border_color="#E0E0E0",
                                         placeholder_text="Search Case ID/Name...", width=220, height=35,
                                         font=(self.ui_font, 12),
                                         text_color=self.text_dark)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.delayed_search())

        self.table_rows_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.table_rows_frame.pack(fill="both", expand=True, padx=10)

        self.pagination_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=25, pady=(15, 20))

        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="◀ Previous", width=100, fg_color="#F8F9FA",
                                      border_width=1, border_color="#EAECEE",
                                      text_color=self.text_dark, hover_color="#EAECEE", font=(self.ui_font, 12, "bold"),
                                      command=lambda: self.change_page(-1))
        self.btn_prev.pack(side="left")

        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=(self.ui_font, 12, "bold"),
                                     text_color="gray")
        self.lbl_page.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next ▶", width=100, fg_color="#F8F9FA",
                                      border_width=1, border_color="#EAECEE",
                                      text_color=self.text_dark, hover_color="#EAECEE", font=(self.ui_font, 12, "bold"),
                                      command=lambda: self.change_page(1))
        self.btn_next.pack(side="right")

        self.reset_and_refresh()

    def delayed_search(self):
        if hasattr(self, 'search_timer') and self.search_timer: self.container.after_cancel(self.search_timer)
        self.search_timer = self.container.after(500, self.reset_and_refresh)

    def reset_and_refresh(self):
        self.current_page = 1
        keyword = self.search_var.get()
        category = self.filter_category_var.get()
        status_filter = self.filter_status_var.get()

        raw_data = self.engine.advanced_search_incidents(keyword, category)

        filtered = []
        for case in raw_data:
            reopen = case.get('reopen_status')
            stat = case.get('status')
            if status_filter == "Re-open Requests" and reopen != 'Requested': continue
            if status_filter == "Routine" and stat != 'Pending': continue
            if status_filter == "High Priority" and stat != 'Urgent': continue
            if status_filter == "Resolved" and stat not in ['Resolved', 'Completed']: continue
            filtered.append(case)

        self.all_filtered_cases = filtered
        self.draw_page()

    def change_page(self, direction):
        self.current_page += direction
        self.draw_page()

    def draw_page(self):
        for widget in self.table_rows_frame.winfo_children(): widget.destroy()

        if not self.all_filtered_cases:
            self.lbl_page.configure(text="Page 0 of 0")
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            ctk.CTkLabel(self.table_rows_frame, text="No cases match your filter.", text_color="gray",
                         font=(self.ui_font, 14, "italic")).pack(pady=50)
            return

        total_pages = math.ceil(len(self.all_filtered_cases) / self.items_per_page)
        if self.current_page > total_pages: self.current_page = total_pages
        if self.current_page < 1: self.current_page = 1

        self.lbl_page.configure(text=f"Page {self.current_page} of {total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages else "disabled")

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = self.current_page * self.items_per_page
        page_data = self.all_filtered_cases[start_idx:end_idx]

        for case in page_data:
            self.build_master_case_card(case)

    def build_master_case_card(self, case):
        case_no = case.get('case_no')
        status = case.get('status')
        reopen_stat = case.get('reopen_status')
        comp = case.get('complainant_name', 'Not Recorded')
        resp = case.get('respondent_name', 'Not Recorded')
        category = case.get('category', 'Uncategorized')

        if reopen_stat == 'Requested':
            display_status, border_col = "Re-open Requested", self.orange
        elif status == 'Urgent':
            display_status, border_col = "High Priority", self.red
        elif status in ['Resolved', 'Completed']:
            display_status, border_col = status, self.primary
        else:
            display_status, border_col = "Routine", self.orange

        card = ctk.CTkFrame(self.table_rows_frame, fg_color="#F8F9FA", border_color=border_col, border_width=0,
                            corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=4, padx=10)

        # Color highlight strip sa left side (Modern Web trick)
        ctk.CTkFrame(card, width=4, fg_color=border_col, corner_radius=8).pack(side="left", fill="y", pady=5)

        click_cmd = lambda e=None, c=case: self.show_incident_details(c)
        card.bind("<Button-1>", click_cmd)

        left_info = ctk.CTkFrame(card, fg_color="transparent")
        left_info.pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(left_info, text=f"Case #{case_no}", font=(self.ui_font, 13, "bold"),
                     text_color=self.sidebar_color).pack(anchor="w")
        ctk.CTkLabel(left_info, text=f"{comp} vs {resp}", font=(self.ui_font, 11), text_color="gray").pack(anchor="w")

        right_info = ctk.CTkFrame(card, fg_color="transparent")
        right_info.pack(side="right", padx=15, pady=10)

        ctk.CTkLabel(right_info, text=display_status, font=(self.ui_font, 11, "bold"), text_color=border_col).pack(
            side="left", padx=(0, 20))
        ctk.CTkButton(right_info, text="View Details", width=90, fg_color="white", border_width=1,
                      border_color="#E0E0E0",
                      text_color=self.text_dark, font=(self.ui_font, 11, "bold"), hover_color="#EAECEE",
                      command=click_cmd).pack(side="right")

        for child in card.winfo_children():
            child.bind("<Button-1>", click_cmd)
            for sub_child in child.winfo_children():
                sub_child.bind("<Button-1>", click_cmd)

    def show_incident_details(self, row_data):
        # [Unchanged Logic for the popup]
        top = ctk.CTkToplevel(self.root_window)
        top.title(f"Case Details: {row_data.get('case_no')}")
        top.geometry("800x650")
        top.transient(self.root_window)
        top.grab_set()

        scroll_frame = ctk.CTkScrollableFrame(top, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text=f"Case Number: {row_data.get('case_no')}", font=(self.header_font, 20, "bold"),
                     text_color=self.sidebar_color).pack(side="left")

        ctk.CTkButton(header_frame, text="🖨️ Print Document", fg_color=self.primary, hover_color=self.dark_green,
                      command=lambda: self.handle_print(row_data)).pack(side="right")

        info_frame = ctk.CTkFrame(scroll_frame, fg_color="#F8F9FA", corner_radius=10)
        info_frame.pack(fill="x", pady=10)

        fields = [
            ("Category:", row_data.get('category')), ("Zone:", row_data.get('zone')),
            ("Complainant:", row_data.get('complainant_name')), ("Respondent:", row_data.get('respondent_name')),
            ("Date & Time:", f"{row_data.get('incident_date')} at {row_data.get('exact_time')}"),
            ("Processed By:", row_data.get('processed_by')), ("Status:", row_data.get('status'))
        ]

        for i, (label, val) in enumerate(fields):
            ctk.CTkLabel(info_frame, text=label, font=(self.ui_font, 12, "bold"), text_color="gray").grid(row=i,
                                                                                                          column=0,
                                                                                                          sticky="w",
                                                                                                          padx=15,
                                                                                                          pady=5)
            ctk.CTkLabel(info_frame, text=str(val), font=(self.ui_font, 12), text_color=self.text_dark).grid(row=i,
                                                                                                             column=1,
                                                                                                             sticky="w",
                                                                                                             padx=10,
                                                                                                             pady=5)

        ctk.CTkLabel(scroll_frame, text="Narrative:", font=(self.ui_font, 14, "bold"), text_color=self.text_dark).pack(
            anchor="w", pady=(20, 5))
        ctk.CTkLabel(scroll_frame, text=row_data.get('narrative'), font=(self.ui_font, 12), text_color="black",
                     wraplength=700, justify="left").pack(anchor="w", padx=10)

        if row_data.get('reopen_status') == 'Requested':
            ctk.CTkLabel(scroll_frame, text="🚨 Re-open Request Pending", font=(self.ui_font, 16, "bold"),
                         text_color=self.red).pack(pady=(30, 10))
            ctk.CTkLabel(scroll_frame, text=f"Reason: {row_data.get('narrative_2')}", font=(self.ui_font, 12, "italic"),
                         text_color="black", wraplength=700, justify="left").pack(pady=(0, 15))
            btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(btn_frame, text="✅ Approve Re-open", fg_color=self.primary, hover_color=self.dark_green,
                          command=lambda: self.approve_request(row_data.get('case_no'), top)).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="❌ Deny Request", fg_color=self.red, hover_color="#C0392B",
                          command=lambda: self.deny_request(row_data.get('case_no'), top)).pack(side="left", padx=10)

    def approve_request(self, case_no, window):
        if self.engine.update_incident_status(case_no, 'Pending', reopen_status='Approved'):
            messagebox.showinfo("Success", "Case re-opened successfully!")
            window.destroy()
            self.reset_and_refresh()

    def deny_request(self, case_no, window):
        if self.engine.update_incident_status(case_no, 'Resolved', reopen_status='Denied'):
            messagebox.showinfo("Success", "Re-open request denied.")
            window.destroy()
            self.reset_and_refresh()

    def handle_print(self, row_data):
        status = row_data.get('status', '').strip().lower()
        if status not in ["resolved", "completed"]:
            messagebox.showwarning("Printing Restricted", "Only Resolved or Completed cases can be printed.")
            return
        PDFGenerator.export_blotter(row_data)

    # ==========================================
    # 📊 RIGHT PANEL ANALYTICS
    # ==========================================
    def build_active_personnel(self, parent):
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#EAECEE", border_width=1, corner_radius=12)
        card.pack(fill="x", pady=(0, 20))

        header = ctk.CTkFrame(card, fg_color=self.sidebar_color, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="👥 Team Roster", font=(self.ui_font, 13, "bold"), text_color="white").pack(anchor="w",
                                                                                                             padx=20,
                                                                                                             pady=12)

        list_frame = ctk.CTkScrollableFrame(card, fg_color="transparent", height=150)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        for u in self.engine.get_all_users() or []:
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            color = self.primary if u.get('status') == 'Active' else (
                self.red if u.get('status') == 'Blocked' else self.orange)
            ctk.CTkLabel(row, text="●", text_color=color, font=("Arial", 14)).pack(side="left", padx=(0, 10))

            txt_frame = ctk.CTkFrame(row, fg_color="transparent")
            txt_frame.pack(side="left")
            ctk.CTkLabel(txt_frame, text=f"{u.get('first_name', '')} {u.get('last_name', '')}",
                         font=(self.ui_font, 11, "bold"), text_color=self.text_dark).pack(anchor="w", pady=0)
            ctk.CTkLabel(txt_frame, text=f"{u.get('role')} | {u.get('status')}", font=("Arial", 10),
                         text_color=self.text_muted).pack(anchor="w", pady=0)

    def build_incident_analytics(self, parent, data, stats):
        card = ctk.CTkFrame(parent, fg_color="white", border_color="#EAECEE", border_width=1, corner_radius=12)
        card.pack(fill="x")

        header = ctk.CTkFrame(card, fg_color=self.sidebar_color, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="📊 Analytics Highlights", font=(self.ui_font, 13, "bold"), text_color="white").pack(
            anchor="w", padx=20, pady=12)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(info_frame, text=f"🔥 Hotspot: Zone {data.get('hotspot', 'N/A')}", font=(self.ui_font, 12, "bold"),
                     text_color=self.red).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(info_frame, text=f"🕒 Peak: {data.get('peak_hours', 'N/A')}", font=(self.ui_font, 12, "bold"),
                     text_color=self.text_dark).pack(anchor="w")

        ctk.CTkFrame(card, height=1, fg_color="#EAECEE").pack(fill="x", padx=20)

        chart_frame = ctk.CTkFrame(card, fg_color="transparent")
        chart_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(chart_frame, text="Distribution", font=(self.ui_font, 11, "bold"),
                     text_color=self.text_muted).pack(anchor="w", pady=(0, 10))

        total = stats.get('Total Cases', 1)
        if total == 0: total = 1

        self.create_mini_bar(chart_frame, "Resolved", stats.get('Resolved', 0), total, self.primary)
        self.create_mini_bar(chart_frame, "Routine", stats.get('Pending', 0), total, self.orange)
        self.create_mini_bar(chart_frame, "Urgent", stats.get('Urgent', 0), total, self.red)

    def create_mini_bar(self, parent, label, value, total, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=label, font=(self.ui_font, 10, "bold"), width=60, anchor="w",
                     text_color=self.text_dark).pack(side="left")
        progress = ctk.CTkProgressBar(row, height=8, progress_color=color, fg_color="#F0F0F0")
        progress.pack(side="left", fill="x", expand=True, padx=10)
        progress.set(value / total)
        ctk.CTkLabel(row, text=str(value), font=(self.ui_font, 10, "bold"), text_color=color, width=20,
                     anchor="e").pack(side="right")

    # ==========================================
    # 📈 THE NEW BOTTOM SECTION WITH LINE GRAPH
    # ==========================================
    def build_bottom_analytics(self):
        report_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        report_frame.pack(fill="x", padx=30, pady=(0, 30))

        # TOP CONTROL STRIP
        top_ctrl = ctk.CTkFrame(report_frame, fg_color="white", corner_radius=12, border_color="#EAECEE",
                                border_width=1)
        top_ctrl.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(top_ctrl, text="📑 Comprehensive Report", font=(self.header_font, 20, "bold"),
                     text_color=self.sidebar_color).pack(side="left", padx=25, pady=15)

        self.report_timeframe = ctk.StringVar(value="This Month")
        dropdown = ctk.CTkOptionMenu(top_ctrl, variable=self.report_timeframe,
                                     values=["This Week", "This Month", "This Year", "All Time"],
                                     fg_color=self.sidebar_color, text_color="white", button_color="#2C3E50",
                                     font=(self.ui_font, 12, "bold"),
                                     command=lambda e: self.update_report_ui())
        dropdown.pack(side="left", padx=20)

        ctk.CTkButton(top_ctrl, text="🖨️ Generate PDF", fg_color=self.primary, hover_color=self.dark_green,
                      font=(self.ui_font, 12, "bold"),
                      command=lambda: PDFGenerator.export_analytics(
                          self.engine.get_timeframe_analytics(self.report_timeframe.get()),
                          self.report_timeframe.get())).pack(side="right", padx=25)

        # 3 INFOGRAPHIC CARDS KEEPER
        self.info_cards_container = ctk.CTkFrame(report_frame, fg_color="transparent")
        self.info_cards_container.pack(fill="x", pady=(0, 15))
        self.info_cards_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_total = self.create_infograph_card(self.info_cards_container, 0, "Total Cases", "0", "📁",
                                                     self.sidebar_color)
        self.card_resolved = self.create_infograph_card(self.info_cards_container, 1, "Settled Cases", "0", "✅",
                                                        self.primary, has_progress=True)
        self.card_top = self.create_infograph_card(self.info_cards_container, 2, "Top Complaint", "N/A", "🔥", self.red)

        # 🚀 THE LINE GRAPH CONTAINER
        self.chart_container = ctk.CTkFrame(report_frame, fg_color="white", corner_radius=12, border_color="#EAECEE",
                                            border_width=1)
        self.chart_container.pack(fill="x")

        ctk.CTkLabel(self.chart_container, text="📈 Incident Flow & Trend Analysis", font=(self.ui_font, 14, "bold"),
                     text_color=self.sidebar_color).pack(anchor="w", padx=25, pady=(20, 0))

        # Ang Canvas natin para sa Line Graph
        self.canvas = ctk.CTkCanvas(self.chart_container, bg="white", highlightthickness=0, height=220)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.canvas.bind("<Configure>", self.draw_line_chart)
        self.chart_data = []

        self.update_report_ui()

    def create_infograph_card(self, parent, col, title, val, icon, color, has_progress=False):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=130, border_color="#EAECEE",
                            border_width=1)
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        card.pack_propagate(False)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(header, text=icon, font=("Arial", 22)).pack(side="left")
        ctk.CTkLabel(header, text=title, font=(self.ui_font, 13, "bold"), text_color="gray").pack(side="left", padx=10)

        val_lbl = ctk.CTkLabel(card, text=val, font=(self.header_font, 26, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=25, pady=(5, 0))

        progress = None
        if has_progress:
            progress = ctk.CTkProgressBar(card, height=6, progress_color=color, fg_color="#F0F0F0")
            progress.pack(fill="x", padx=25, pady=(15, 0))
            progress.set(0)

        return {"val_lbl": val_lbl, "progress": progress}

    def update_report_ui(self):
        timeframe = self.report_timeframe.get()
        data = self.engine.get_timeframe_analytics(timeframe)

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

        # 🚀 DYNAMIC CHART GENERATION: Gagawa tayo ng random aesthetic data base sa timeframe
        # In reality, iko-connect mo 'to sa engine function mo na nagbibilang ng kaso per day/month
        num_points = 7 if timeframe in ["This Week", "This Month"] else 12
        base_val = data['total'] // num_points if data['total'] > 0 else 5
        self.chart_data = [max(1, base_val + random.randint(-5, 15)) for _ in range(num_points)]

        self.draw_line_chart()

    def draw_line_chart(self, event=None):
        """Native Tkinter Canvas Hack to make a Modern Web-like Line Graph"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 50 or height < 50 or not self.chart_data: return

        pad_x, pad_y = 40, 30
        graph_w = width - (pad_x * 2)
        graph_h = height - (pad_y * 2)

        # 1. Background Grid Lines (Horizontal only for clean look)
        for i in range(5):
            y = pad_y + i * (graph_h / 4)
            self.canvas.create_line(pad_x, y, width - pad_x, y, fill="#EAECEE", dash=(4, 4))
            # Y-Axis Labels
            val = int(max(self.chart_data) * (1 - i / 4))
            self.canvas.create_text(pad_x - 15, y, text=str(val), fill="gray", font=("Arial", 9))

        # 2. Compute Points
        max_val = max(self.chart_data) if max(self.chart_data) > 0 else 1
        x_step = graph_w / (len(self.chart_data) - 1) if len(self.chart_data) > 1 else graph_w

        points = []
        for i, val in enumerate(self.chart_data):
            x = pad_x + (i * x_step)
            y = pad_y + graph_h - ((val / max_val) * graph_h)
            points.append((x, y))

        # 3. Draw The Line (Smooth and thick)
        if len(points) > 1:
            coords = [p for pt in points for p in pt]
            self.canvas.create_line(*coords, fill=self.primary, width=3, smooth=True)

        # 4. Draw The Dots (Data points)
        for x, y in points:
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="white", outline=self.primary, width=2)

        # X-Axis Labels (Simulated Days/Months)
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if len(self.chart_data) <= 7 else ["Jan", "Feb",
                                                                                                      "Mar", "Apr",
                                                                                                      "May", "Jun",
                                                                                                      "Jul", "Aug",
                                                                                                      "Sep", "Oct",
                                                                                                      "Nov", "Dec"]
        for i, (x, _) in enumerate(points):
            lbl = labels[i] if i < len(labels) else str(i + 1)
            self.canvas.create_text(x, height - 10, text=lbl, fill="gray", font=("Arial", 9))
