import customtkinter as ctk
from tkinter import messagebox

try:
    from .pdf_generator import PDFGenerator
except ImportError:
    pass


class MasterDashboardPage:
    def __init__(self, parent_frame, engine, root_window):
        self.parent_frame = parent_frame
        self.engine = engine
        self.root_window = root_window

        # Pagination Logic
        self.current_page = 0
        self.limit = 10  # 10 cases lang per page para swabe

        # Colors
        self.primary = "#27AE60"
        self.dark_green = "#1E8449"
        self.red = "#E74C3C"
        self.orange = "#E79124"
        self.text_dark = "#2B2B2B"

        self.container = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # --- Header ---
        ctk.CTkLabel(self.container, text="Master Database (All Cases)", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=30, pady=(30, 0))

        # --- Filter Panel ---
        filter_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(15, 10))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var,
                                         placeholder_text="Search Case ID, Complainant, or Respondent...",
                                         width=350, height=40)
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.reset_and_refresh())

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        self.category_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_category_var, values=cat_list,
                                                   width=200, height=40, fg_color=self.primary,
                                                   button_color=self.primary,
                                                   command=lambda e: self.reset_and_refresh())
        self.category_dropdown.pack(side="left")

        # --- List Area ---
        self.list_container = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Pager Navigation (The "Staff-Style" Pager) ---
        self.pager_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.pager_frame.pack(fill="x", side="bottom", pady=15)

        self.btn_prev = ctk.CTkButton(self.pager_frame, text="◀ Previous", width=100, fg_color="#BDC3C7",
                                      text_color="black", hover_color="#95A5A6", command=self.prev_page)
        self.btn_prev.pack(side="left", padx=(100, 10))

        self.page_label = ctk.CTkLabel(self.pager_frame, text="Page 1", font=("Arial", 13, "bold"))
        self.page_label.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.pager_frame, text="Next ▶", width=100, fg_color="#BDC3C7",
                                      text_color="black", hover_color="#95A5A6", command=self.next_page)
        self.btn_next.pack(side="right", padx=(10, 100))

        self.refresh_case_list()

    def reset_and_refresh(self):
        self.current_page = 0
        self.refresh_case_list()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_case_list()

    def next_page(self):
        self.current_page += 1
        self.refresh_case_list()

    def refresh_case_list(self):
        for widget in self.list_container.winfo_children(): widget.destroy()

        keyword = self.search_var.get()
        category = self.filter_category_var.get()
        offset = self.current_page * self.limit

        # ⚠️ Make sure your engine's search function supports limit and offset!
        filtered_cases = self.engine.advanced_search_incidents(keyword, category, limit=self.limit, offset=offset)

        self.page_label.configure(text=f"Page {self.current_page + 1}")

        # UI Button States
        self.btn_prev.configure(state="normal" if self.current_page > 0 else "disabled")
        self.btn_next.configure(state="normal" if len(filtered_cases) == self.limit else "disabled")

        if not filtered_cases:
            ctk.CTkLabel(self.list_container, text="No more cases to show.", text_color="gray",
                         font=("Arial", 14, "italic")).pack(pady=50)
            return

        for case in filtered_cases:
            self.build_master_case_card(case)

    def build_master_case_card(self, case):
        case_no = case.get('case_no')
        status = case.get('status')
        reopen_stat = case.get('reopen_status')
        comp = case.get('complainant_name', 'Not Recorded')
        resp = case.get('respondent_name', 'Not Recorded')
        category = case.get('category', 'Uncategorized')

        # Status Logic
        if reopen_stat == 'Requested':
            display_status, border_col = "Re-open Requested", self.orange
        elif status == 'Urgent':
            display_status, border_col = "Urgent", self.red
        elif status in ['Resolved', 'Completed']:
            display_status, border_col = status, self.primary
        else:
            display_status, border_col = "Pending", self.orange

        card = ctk.CTkFrame(self.list_container, fg_color="white", border_color=border_col, border_width=2,
                            corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=5, padx=10)

        click_cmd = lambda e=None, c=case: self.show_incident_details(c)
        card.bind("<Button-1>", click_cmd)

        left_info = ctk.CTkFrame(card, fg_color="transparent")
        left_info.pack(side="left", padx=15, pady=10)

        ctk.CTkLabel(left_info, text=f"Case #{case_no}", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w")
        ctk.CTkLabel(left_info, text=f"{comp} vs {resp}", font=("Arial", 12), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(left_info, text=f"Category: {category}", font=("Arial", 11, "italic"),
                     text_color=self.primary).pack(anchor="w")

        ctk.CTkButton(card, text="View Details", width=100, fg_color="#F0F0F0", text_color=self.text_dark,
                      hover_color="#E0E0E0", command=click_cmd).pack(side="right", padx=20)

    def show_incident_details(self, row_data):
        # (Yung mahabang details popup logic na may Handle Print at Approve/Deny buttons...)
        # I-paste mo lang dito yung show_incident_details na binigay ko sa huling turn.
        pass

    def handle_print(self, row_data):
        status = row_data.get('status', '').strip().lower()
        if status not in ["resolved", "completed"]:
            messagebox.showwarning("Printing Restricted", "Bawal i-print ang chismis na 'di pa Resolved! 😂")
            return
        PDFGenerator.export_blotter(row_data)