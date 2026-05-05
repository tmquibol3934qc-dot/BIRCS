import customtkinter as ctk
import math
from tkinter import messagebox
from .modals import IncidentDetailsModal


class KapitanArchivesPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        self.sidebar_color, self.text_dark, self.text_muted = "#1D2153", "#2B2B2B", "#7A7A7A"
        self.primary, self.orange, self.red, self.green = "#2980B9", "#F39C12", "#E74C3C", "#27AE60"

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Default view mode
        self.view_mode = "Archives"

        self.build_ui()

    def build_ui(self):
        # HEADER
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="🗄️ Kapitan Archives & Appeals", font=("Arial", 28, "bold"),
                     text_color=self.sidebar_color).pack(side="left")

        # 🚀 THE KAPITAN TOGGLE BUTTONS
        toggle_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        toggle_frame.pack(side="right")

        self.btn_archives = ctk.CTkButton(toggle_frame, text="📁 View All Archives", fg_color=self.primary,
                                          font=("Arial", 12, "bold"), command=lambda: self.switch_mode("Archives"))
        self.btn_archives.pack(side="left", padx=5)

        self.btn_appeals = ctk.CTkButton(toggle_frame, text="⚖️ Pending Appeals", fg_color="#34495E",
                                         hover_color=self.orange, font=("Arial", 12, "bold"),
                                         command=lambda: self.switch_mode("Appeals"))
        self.btn_appeals.pack(side="left", padx=5)

        # MAIN CARD
        table_container = ctk.CTkFrame(self.container, fg_color="white", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        self.current_page, self.items_per_page = 1, 15

        # CONTROLS
        self.top_ctrls = ctk.CTkFrame(table_container, fg_color="transparent")
        self.top_ctrls.pack(fill="x", padx=20, pady=15)

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        self.cat_dropdown = ctk.CTkOptionMenu(self.top_ctrls, variable=self.filter_category_var, values=cat_list,
                                              fg_color="#F8F9FA",
                                              text_color=self.text_dark, button_color="#E0E0E0", width=160, height=35,
                                              command=lambda e: self.trigger_live_filter(reset_page=True))
        self.cat_dropdown.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(self.top_ctrls, placeholder_text="Search Case ID or Name...", width=280,
                                         height=35, fg_color="#F8F9FA", text_color=self.text_dark)
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

        self.action_header = ctk.CTkLabel(title_row, text="Status", font=("Arial", 12, "bold"), text_color="white",
                                          width=120, anchor="e")
        self.action_header.pack(side="right", padx=20)

        self.table_rows_frame = ctk.CTkFrame(table_container, fg_color="white")
        self.table_rows_frame.pack(fill="both", expand=True)

        # PAGINATION
        self.pagination_frame = ctk.CTkFrame(table_container, fg_color="white")
        self.pagination_frame.pack(fill="x", padx=20, pady=(10, 15))
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="◀ Previous", width=100, fg_color="#F0F0F0",
                                      text_color=self.text_dark, command=lambda: self.change_page(-1))
        self.btn_prev.pack(side="left", padx=10)
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Arial", 12, "bold"),
                                     text_color=self.text_dark)
        self.lbl_page.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next ▶", width=100, fg_color="#F0F0F0",
                                      text_color=self.text_dark, command=lambda: self.change_page(1))
        self.btn_next.pack(side="right", padx=10)

        self.trigger_live_filter(reset_page=True)

    def switch_mode(self, mode):
        self.view_mode = mode
        if mode == "Archives":
            self.btn_archives.configure(fg_color=self.primary)
            self.btn_appeals.configure(fg_color="#34495E")
            self.action_header.configure(text="Status")
            self.top_ctrls.pack(fill="x", padx=20, pady=15)
        else:
            self.btn_archives.configure(fg_color="#34495E")
            self.btn_appeals.configure(fg_color=self.orange)
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
            empty_msg = "No pending appeals." if self.view_mode == "Appeals" else "No records found in archives."
            return ctk.CTkLabel(self.table_rows_frame, text=empty_msg, text_color=self.text_muted,
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

            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.pack(side="right", padx=20)

            if self.view_mode == "Archives":
                # 🚀 POGI UPDATE: High Priority at Normal Statuses!
                status = case.get('status')
                color = self.green if status == 'Resolved' else (self.red if status == 'Urgent' else self.orange)

                if status == "Pending":
                    display_status = "Normal"
                elif status == "Urgent":
                    display_status = "High Priority"
                else:
                    display_status = status

                status_badge = ctk.CTkFrame(action_frame, fg_color=color, corner_radius=15, width=110, height=25)
                status_badge.pack()
                status_badge.pack_propagate(False)
                ctk.CTkLabel(status_badge, text=display_status, text_color="white", font=("Arial", 10, "bold")).place(
                    relx=0.5, rely=0.5, anchor="center")

            else:  # APPEALS MODE
                btn_approve = ctk.CTkButton(action_frame, text="✓ Approve", fg_color=self.green, hover_color="#1E8449",
                                            width=80, height=25, font=("Arial", 11, "bold"),
                                            command=lambda c=case: self.handle_appeal(c, 'Approve'))
                btn_approve.pack(side="left", padx=5)

                btn_deny = ctk.CTkButton(action_frame, text="✗ Deny", fg_color=self.red, hover_color="#C0392B",
                                         width=80, height=25, font=("Arial", 11, "bold"),
                                         command=lambda c=case: self.handle_appeal(c, 'Deny'))
                btn_deny.pack(side="left")

            click_command = lambda e, c=case: IncidentDetailsModal(self.container.winfo_toplevel(), c, self.engine,
                                                                   self.user, self.trigger_live_filter)
            row.bind("<Button-1>", click_command)
            for child in row.winfo_children():
                if child != action_frame: child.bind("<Button-1>", click_command)

            ctk.CTkFrame(self.table_rows_frame, height=1, fg_color="#F0F0F0").pack(fill="x")

    def handle_appeal(self, case, action):
        case_no = case.get('case_no')
        if messagebox.askyesno(f"{action} Appeal",
                               f"Are you sure you want to {action.upper()} the reopen request for Case {case_no}?"):
            success = self.engine.handle_reopen_request(case_no, action)
            if success:
                messagebox.showinfo("Success", f"Appeal {action}d successfully!")
                self.trigger_live_filter(reset_page=False)
            else:
                messagebox.showerror("Error", "Failed to process appeal.")
