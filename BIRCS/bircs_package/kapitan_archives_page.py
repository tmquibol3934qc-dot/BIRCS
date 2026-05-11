import customtkinter as ctk
import math
from tkinter import messagebox
from .modals import IncidentDetailsModal


class KapitanArchivesPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        # 🎨 THE PREMIUM WEB PALETTE & TYPOGRAPHY
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"       # Web Canvas Gray
        self.color_card = "#FFFFFF"     # Crisp White
        self.color_border = "#EAECEE"   # Subtle borders
        self.primary = "#27AE60"        # Emerald Green
        self.orange = "#E05D3A"         # Alert Orange
        self.red = "#E74C3C"            # Danger Red
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD (Goodbye Young Serif!)
        self.ui_font = "Poppins"

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Default view mode
        self.view_mode = "Archives"

        self.build_ui()

    def build_ui(self):
        # 📌 HEADER SECTION
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="🗄️ Case Archives & Appeals", font=(self.ui_font, 26, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        # 🚀 WEB-STYLE SEGMENTED TABS (Toggle Buttons)
        toggle_frame = ctk.CTkFrame(header_frame, fg_color="#F8F9FA", border_width=1, border_color=self.color_border,
                                    corner_radius=8)
        toggle_frame.pack(side="right", ipady=2, ipadx=2)

        self.btn_archives = ctk.CTkButton(toggle_frame, text="📁 View All Archives", width=150, height=35,
                                          font=(self.ui_font, 12, "bold"), corner_radius=6,
                                          command=lambda: self.switch_mode("Archives"))
        self.btn_archives.pack(side="left", padx=2)

        self.btn_appeals = ctk.CTkButton(toggle_frame, text="⚖️ Pending Appeals", width=150, height=35,
                                         font=(self.ui_font, 12, "bold"), corner_radius=6,
                                         command=lambda: self.switch_mode("Appeals"))
        self.btn_appeals.pack(side="left", padx=2)

        # 📌 MAIN CARD CONTAINER (White Floating Card)
        table_container = ctk.CTkFrame(self.container, fg_color=self.color_card, corner_radius=12, border_width=1,
                                       border_color=self.color_border)
        table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.current_page, self.items_per_page = 1, 15

        # 📌 CONTROLS SECTION (Search & Filter)
        self.top_ctrls = ctk.CTkFrame(table_container, fg_color="transparent")
        self.top_ctrls.pack(fill="x", padx=25, pady=20)

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        self.cat_dropdown = ctk.CTkOptionMenu(self.top_ctrls, variable=self.filter_category_var, values=cat_list,
                                              fg_color="#F8F9FA", text_color=self.text_dark,
                                              button_color=self.color_border,
                                              button_hover_color="#D5D8DC", font=(self.ui_font, 12), width=180,
                                              height=38,
                                              command=lambda e: self.trigger_live_filter(reset_page=True))
        self.cat_dropdown.pack(side="left")

        self.search_entry = ctk.CTkEntry(self.top_ctrls, placeholder_text="Search Case ID or Name...", width=300,
                                         height=38, fg_color="#F8F9FA", border_color=self.color_border,
                                         text_color=self.text_dark, font=(self.ui_font, 12))
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self.delayed_search)

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

        self.action_header = ctk.CTkLabel(title_row, text="Status", font=(self.ui_font, 12, "bold"), text_color="white",
                                          width=140, anchor="e")
        self.action_header.pack(side="right", padx=30)

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

        self.switch_mode("Archives")  # Initialize colors

    def switch_mode(self, mode):
        self.view_mode = mode
        if mode == "Archives":
            self.btn_archives.configure(fg_color=self.primary, text_color="white")
            self.btn_appeals.configure(fg_color="transparent", text_color=self.text_muted)
            self.action_header.configure(text="Status")
            self.top_ctrls.pack(fill="x", padx=25, pady=20)
        else:
            self.btn_archives.configure(fg_color="transparent", text_color=self.text_muted)
            self.btn_appeals.configure(fg_color=self.orange, text_color="white")
            self.action_header.configure(text="Kapitan Action")
            self.top_ctrls.pack_forget()

        self.trigger_live_filter(reset_page=True)

    def delayed_search(self, event):
        if hasattr(self, 'search_timer') and self.search_timer: self.container.after_cancel(self.search_timer)
        self.search_timer = self.container.after(500, lambda: self.trigger_live_filter(reset_page=True))

    def trigger_live_filter(self, reset_page=True):
        if reset_page: self.current_page = 1

        if self.view_mode == "Appeals":
            all_data = self.engine.get_reopen_requests()
        else:
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
            empty_msg = "📭 No pending appeals to review." if self.view_mode == "Appeals" else "📭 No records found in archives."
            return ctk.CTkLabel(self.table_rows_frame, text=empty_msg, text_color=self.text_muted,
                                font=(self.ui_font, 14, "italic")).pack(pady=60)

        for case in data_to_draw:
            # 🚀 ROW CONTAINER: Hover-friendly web row design
            row = ctk.CTkFrame(self.table_rows_frame, fg_color="#FDFDFD", border_width=1,
                               border_color=self.color_border,
                               height=55, corner_radius=6, cursor="hand2")
            row.pack(fill="x", pady=4, padx=5)
            row.pack_propagate(False)

            # Define Row Highlight Color based on Status
            status = case.get('status')
            reopen_stat = case.get('reopen_status')

            if self.view_mode == "Appeals" or reopen_stat == 'Requested':
                row_color = self.orange
            elif status == 'Resolved':
                row_color = self.primary
            elif status == 'Urgent':
                row_color = self.red
            else:
                row_color = "#3498DB"  # Nice blue for standard pending

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

            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.pack(side="right", padx=15)

            if self.view_mode == "Archives":
                # PILL BADGE FOR STATUS
                if status == "Pending":
                    display_status = "Normal"
                elif status == "Urgent":
                    display_status = "High Priority"
                else:
                    display_status = status

                status_badge = ctk.CTkFrame(action_frame, fg_color=row_color, corner_radius=12, width=120, height=28)
                status_badge.pack()
                status_badge.pack_propagate(False)
                ctk.CTkLabel(status_badge, text=display_status.upper(), text_color="white",
                             font=(self.ui_font, 10, "bold")).place(
                    relx=0.5, rely=0.5, anchor="center")

            else:  # APPEALS MODE
                # 🚀 CHUNKY ACTION BUTTONS (Senior Friendly!)
                btn_approve = ctk.CTkButton(action_frame, text="✓ Approve", fg_color=self.primary,
                                            hover_color="#1E8449",
                                            width=90, height=32, corner_radius=6, font=(self.ui_font, 12, "bold"),
                                            command=lambda c=case: self.handle_appeal(c, 'Approve'))
                btn_approve.pack(side="left", padx=5)

                btn_deny = ctk.CTkButton(action_frame, text="✗ Deny", fg_color="transparent", border_width=1,
                                         border_color=self.red,
                                         text_color=self.red, hover_color="#FDEDEC",  # Soft red hover
                                         width=90, height=32, corner_radius=6, font=(self.ui_font, 12, "bold"),
                                         command=lambda c=case: self.handle_appeal(c, 'Deny'))
                btn_deny.pack(side="left")

            # BIND CLICK EVENT TO ROW (But exclude the action frame so buttons still work)
            click_command = lambda e, c=case: IncidentDetailsModal(self.container.winfo_toplevel(), c, self.engine,
                                                                   self.user, self.trigger_live_filter)

            row.bind("<Button-1>", click_command)
            for child in row.winfo_children():
                if child != action_frame:
                    child.bind("<Button-1>", click_command)

    def handle_appeal(self, case, action):
        case_no = case.get('case_no')
        if messagebox.askyesno(f"{action} Appeal",
                               f"Are you sure you want to {action.upper()} the reopen request for Case {case_no}?",
                               parent=self.container.winfo_toplevel()):
            success = self.engine.handle_reopen_request(case_no, action)
            if success:
                messagebox.showinfo("Success", f"Appeal {action}d successfully!",
                                    parent=self.container.winfo_toplevel())
                self.trigger_live_filter(reset_page=False)
            else:
                messagebox.showerror("Error", "Failed to process appeal.", parent=self.container.winfo_toplevel())
