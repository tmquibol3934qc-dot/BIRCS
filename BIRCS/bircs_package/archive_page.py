import customtkinter as ctk
import math
from .modals import IncidentDetailsModal


class ArchivesPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        self.sidebar_color, self.text_dark, self.text_muted = "#1D2153", "#2B2B2B", "#7A7A7A"
        self.primary, self.orange, self.red, self.green = "#2980B9", "#F39C12", "#E74C3C", "#27AE60"

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # HEADER
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="🗄️ Case Archives", font=("Arial", 28, "bold"),
                     text_color=self.sidebar_color).pack(side="left")

        # MAIN CARD
        table_container = ctk.CTkFrame(self.container, fg_color="white", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        self.current_page, self.items_per_page = 1, 15

        # CONTROLS (Search & Filter)
        top_ctrls = ctk.CTkFrame(table_container, fg_color="transparent")
        top_ctrls.pack(fill="x", padx=20, pady=15)

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        ctk.CTkOptionMenu(top_ctrls, variable=self.filter_category_var, values=cat_list, fg_color="#F8F9FA",
                          text_color=self.text_dark, button_color="#E0E0E0", button_hover_color="#D0D0D0", width=160,
                          height=35, command=lambda e: self.trigger_live_filter(reset_page=True)).pack(side="left",
                                                                                                       padx=(0, 10))

        self.search_entry = ctk.CTkEntry(top_ctrls, placeholder_text="Search Case ID or Name...", width=280, height=35,
                                         fg_color="#F8F9FA", border_color="#E0E0E0", text_color=self.text_dark)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.delayed_search)

        # TABLE HEADER
        title_row = ctk.CTkFrame(table_container, fg_color=self.sidebar_color, corner_radius=0, height=40)
        title_row.pack(fill="x")
        title_row.pack_propagate(False)
        ctk.CTkLabel(title_row, text="Case #", font=("Arial", 12, "bold"), text_color="white", width=80,
                     anchor="w").pack(side="left", padx=(20, 0))
        ctk.CTkLabel(title_row, text="Category & Zone", font=("Arial", 12, "bold"), text_color="white", width=200,
                     anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_row, text="Processed By", font=("Arial", 12, "bold"), text_color="white", width=150,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(title_row, text="Status", font=("Arial", 12, "bold"), text_color="white", width=120,
                     anchor="e").pack(side="right", padx=20)

        self.table_rows_frame = ctk.CTkFrame(table_container, fg_color="white")
        self.table_rows_frame.pack(fill="both", expand=True)

        # PAGINATION
        self.pagination_frame = ctk.CTkFrame(table_container, fg_color="white")
        self.pagination_frame.pack(fill="x", padx=20, pady=(10, 15))
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="◀ Previous", width=100, fg_color="#F0F0F0",
                                      text_color=self.text_dark, hover_color="#E0E0E0",
                                      command=lambda: self.change_page(-1))
        self.btn_prev.pack(side="left", padx=10)
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 12, "bold"),
                                     text_color=self.text_dark)
        self.lbl_page.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next ▶", width=100, fg_color="#F0F0F0",
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
            return ctk.CTkLabel(self.table_rows_frame, text="No records found in archives.", text_color=self.text_muted,
                                font=("Arial", 14, "italic")).pack(pady=50)

        for case in data_to_draw:
            row = ctk.CTkFrame(self.table_rows_frame, fg_color="transparent", height=45, cursor="hand2")
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=case.get('case_no'), font=("Arial", 12, "bold"), text_color=self.text_dark, width=80,
                         anchor="w").pack(side="left", padx=(20, 0))
            ctk.CTkLabel(row, text=f"{case.get('category', 'Uncategorized')} (Zone {case.get('zone', 'N/A')})",
                         font=("Arial", 12), text_color=self.text_dark, width=200, anchor="w").pack(side="left",
                                                                                                    padx=(0, 10))
            ctk.CTkLabel(row, text=case.get('processed_by'), font=("Arial", 12), text_color=self.text_muted, width=150,
                         anchor="w").pack(side="left")

            # 🚀 POGI UPDATE: Nandito na yung "Normal" at "High Priority" logic!
            status = case.get('status')
            color = self.green if status == 'Resolved' else (self.red if status == 'Urgent' else self.orange)

            if status == "Pending":
                display_status = "Normal"
            elif status == "Urgent":
                display_status = "High Priority"
            else:
                display_status = status

            status_frame = ctk.CTkFrame(row, fg_color=color, corner_radius=15, width=110, height=25)
            status_frame.pack(side="right", padx=20)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=display_status, text_color="white", font=("Arial", 10, "bold")).place(
                relx=0.5, rely=0.5, anchor="center")

            click_command = lambda e, c=case: IncidentDetailsModal(self.container.winfo_toplevel(), c, self.engine,
                                                                   self.user, self.trigger_live_filter)
            row.bind("<Button-1>", click_command)
            for child in row.winfo_children(): child.bind("<Button-1>", click_command)
            for child in status_frame.winfo_children(): child.bind("<Button-1>", click_command)

            ctk.CTkFrame(self.table_rows_frame, height=1, fg_color="#F0F0F0").pack(fill="x")
