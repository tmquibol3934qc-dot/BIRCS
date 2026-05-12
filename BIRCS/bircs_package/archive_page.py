import customtkinter as ctk
import math
from .modals import IncidentDetailsModal


class ArchivesPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        # 🎨 THE PREMIUM WEB PALETTE & TYPOGRAPHY
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"  # Web Canvas Gray
        self.color_card = "#FFFFFF"  # Crisp White
        self.color_border = "#EAECEE"  # Subtle borders
        self.primary = "#27AE60"  # Emerald Green (Resolved)
        self.blue = "#3498DB"  # Clean Blue
        self.orange = "#E05D3A"  # Alert Orange (Normal/Pending)
        self.red = "#E74C3C"  # Danger Red (Urgent)
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # 🚀 THE MAGIC TRIGGER: Bago i-load ang table, pilitin mag-walis ang system!
        self.engine.auto_manage_reopen_cases()

        self.build_ui()

    def build_ui(self):
        # 📌 HEADER SECTION
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="🗄️ Case Archives", font=(self.ui_font, 26, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        # 📌 MAIN CARD CONTAINER (White Floating Card)
        table_container = ctk.CTkFrame(self.container, fg_color=self.color_card, corner_radius=12, border_width=1,
                                       border_color=self.color_border)
        table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.current_page, self.items_per_page = 1, 15

        # 📌 CONTROLS (Search & Filter)
        top_ctrls = ctk.CTkFrame(table_container, fg_color="transparent")
        top_ctrls.pack(fill="x", padx=25, pady=20)

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")

        # 🚀 Save dropdown reference para ma-update natin mamaya!
        self.cat_dropdown = ctk.CTkOptionMenu(top_ctrls, variable=self.filter_category_var, values=cat_list,
                                              fg_color="#F8F9FA", text_color=self.text_dark,
                                              button_color=self.color_border,
                                              button_hover_color="#D5D8DC", width=180, height=38,
                                              font=(self.ui_font, 12),
                                              command=lambda e: self.trigger_live_filter(reset_page=True))
        self.cat_dropdown.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(top_ctrls, placeholder_text="Search Case ID or Name...", width=300, height=38,
                                         fg_color="#F8F9FA", border_width=1, border_color=self.color_border,
                                         text_color=self.text_dark, font=(self.ui_font, 12))
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.delayed_search)

        # 🚀 THE NEW REFRESH BUTTON (Web Style)
        self.btn_refresh = ctk.CTkButton(top_ctrls, text="🔄 Refresh", width=110, height=38, fg_color="#FFFFFF",
                                         border_width=1, border_color=self.color_border, text_color=self.text_dark,
                                         hover_color="#F8F9FA", font=(self.ui_font, 12, "bold"),
                                         command=self.refresh_data)
        self.btn_refresh.pack(side="right")

        # 📌 TABLE HEADER (High Contrast Navy)
        title_row = ctk.CTkFrame(table_container, fg_color=self.color_sidebar, corner_radius=0, height=45)
        title_row.pack(fill="x", padx=2)
        title_row.pack_propagate(False)

        ctk.CTkLabel(title_row, text="Case #", font=(self.ui_font, 12, "bold"), text_color="white", width=90,
                     anchor="w").pack(side="left", padx=(30, 0))
        ctk.CTkLabel(title_row, text="Category & Zone", font=(self.ui_font, 12, "bold"), text_color="white", width=220,
                     anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_row, text="Processed By", font=(self.ui_font, 12, "bold"), text_color="white", width=150,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(title_row, text="Status", font=(self.ui_font, 12, "bold"), text_color="white", width=140,
                     anchor="e").pack(side="right", padx=30)

        # 📌 TABLE ROWS CONTAINER
        self.table_rows_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        self.table_rows_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 📌 PAGINATION (Clean Footer)
        self.pagination_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=25, pady=(15, 20))

        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="◀ Previous", width=110, height=35,
                                      fg_color="#F8F9FA",
                                      border_width=1, border_color=self.color_border, text_color=self.text_dark,
                                      hover_color=self.color_border,
                                      font=(self.ui_font, 12, "bold"), command=lambda: self.change_page(-1))
        self.btn_prev.pack(side="left")

        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=(self.ui_font, 12, "bold"),
                                     text_color=self.text_muted)
        self.lbl_page.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next ▶", width=110, height=35, fg_color="#F8F9FA",
                                      border_width=1, border_color=self.color_border, text_color=self.text_dark,
                                      hover_color=self.color_border,
                                      font=(self.ui_font, 12, "bold"), command=lambda: self.change_page(1))
        self.btn_next.pack(side="right")

        self.trigger_live_filter(reset_page=True)

    # ==================================================
    # REFRESH LOGIC (THE POGI FIX)
    # ==================================================
    def refresh_data(self):
        # 1. Force a DB check if any cases need to be managed
        self.engine.auto_manage_reopen_cases()

        # 2. Silently update the Category Dropdown with fresh DB values!
        new_cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.cat_dropdown.configure(values=new_cat_list)

        # 3. Pull fresh data for the table
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
            self.btn_prev.configure(state="disabled")
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
            return ctk.CTkLabel(self.table_rows_frame, text="📭 No records found in archives.",
                                text_color=self.text_muted,
                                font=(self.ui_font, 14, "italic")).pack(pady=60)

        for case in data_to_draw:
            # 🚀 ROW CONTAINER: Hover-friendly web row design
            row = ctk.CTkFrame(self.table_rows_frame, fg_color="#FDFDFD", border_width=1,
                               border_color=self.color_border,
                               height=55, corner_radius=6, cursor="hand2")
            row.pack(fill="x", pady=4, padx=5)
            row.pack_propagate(False)

            status = case.get('status')
            row_color = self.primary if status == 'Resolved' else (self.red if status == 'Urgent' else self.orange)

            # 🚀 THE COLOR STRIP INDICATOR
            ctk.CTkFrame(row, width=4, fg_color=row_color, corner_radius=0).pack(side="left", fill="y")

            # ROW CONTENT
            ctk.CTkLabel(row, text=case.get('case_no'), font=(self.ui_font, 13, "bold"), text_color=self.color_sidebar,
                         width=80,
                         anchor="w").pack(side="left", padx=(20, 0))
            ctk.CTkLabel(row, text=f"{case.get('category', 'Uncategorized')} (Zone {case.get('zone', 'N/A')})",
                         font=(self.ui_font, 12), text_color=self.text_dark, width=220, anchor="w").pack(side="left",
                                                                                                         padx=(0, 10))
            ctk.CTkLabel(row, text=case.get('processed_by'), font=(self.ui_font, 12), text_color=self.text_muted,
                         width=150,
                         anchor="w").pack(side="left")

            if status == "Pending":
                display_status = "Normal"
            elif status == "Urgent":
                display_status = "High Priority"
            else:
                display_status = status

            # PILL BADGE FOR STATUS
            status_frame = ctk.CTkFrame(row, fg_color=row_color, corner_radius=12, width=120, height=28)
            status_frame.pack(side="right", padx=15)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=display_status.upper(), text_color="white",
                         font=(self.ui_font, 10, "bold")).place(
                relx=0.5, rely=0.5, anchor="center")

            # BIND CLICK EVENT
            click_command = lambda e, c=case: IncidentDetailsModal(self.container.winfo_toplevel(), c, self.engine,
                                                                   self.user, self.trigger_live_filter)
            row.bind("<Button-1>", click_command)
            for child in row.winfo_children(): child.bind("<Button-1>", click_command)
            for child in status_frame.winfo_children(): child.bind("<Button-1>", click_command)
