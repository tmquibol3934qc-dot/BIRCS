import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


class AdminDashboardWindow:
    def __init__(self, engine, user_data, parent_dashboard=None):
        self.engine = engine
        self.user = user_data
        self.parent_dashboard = parent_dashboard

        self.window = ctk.CTkToplevel()
        self.window.title("BICRS - Kapitan Control Center")
        self.window.attributes('-fullscreen', True)
        self.window.bind("<Key>", self.handle_shortcuts)
        self.window.configure(fg_color="#F4F7F6")

        self.primary = "#27AE60"
        self.dark_green = "#1E8449"
        self.green = "#27AE60"
        self.bg_color = "#F4F7F6"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"
        self.red = "#E74C3C"
        self.orange = "#E79124"
        self.blue = "#3F51B5"

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        user_role = self.user.get('role', 'Kapitan')  # Siguraduhing Kapitan ang lalabas sa role

        # Save agad sa database pag-open!
        self.audit_id = self.engine.log_user_login(user_name, user_role)

        # Saluhin din natin yung "X" button or Alt+F4 ni Kapitan
        self.window.protocol("WM_DELETE_WINDOW", self.force_logout_on_close)

        self.setup_layout()
        self.show_master_dashboard()

    def setup_layout(self):
        self.sidebar = ctk.CTkFrame(self.window, width=250, corner_radius=0, fg_color="#2C3E50")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="BICRS ADMIN", font=("Arial", 22, "bold"), text_color="white").pack(
            pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="Kapitan Override Active", font=("Arial", 11, "italic"),
                     text_color=self.primary).pack(pady=(0, 30))

        user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        ctk.CTkLabel(self.sidebar, text=f"Welcome, {user_name}", font=("Arial", 14, "bold"), text_color="white").pack(
            pady=(10, 2))
        ctk.CTkLabel(self.sidebar, text="KAPITAN", font=("Arial", 10, "bold"), text_color=self.primary).pack(
            pady=(0, 30))

        self.btn_master = ctk.CTkButton(self.sidebar, text="📁 Master Dashboard", font=("Arial", 14, "bold"),
                                        fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                        anchor="w", command=self.show_master_dashboard)
        self.btn_master.pack(fill="x", padx=15, pady=5)

        self.btn_team = ctk.CTkButton(self.sidebar, text="👥 Team Management", font=("Arial", 14, "bold"),
                                      fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                      anchor="w", command=self.show_user_management)
        self.btn_team.pack(fill="x", padx=15, pady=5)

        self.btn_logs = ctk.CTkButton(self.sidebar, text="🕒 System Logs", font=("Arial", 14, "bold"),
                                      fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                      anchor="w", command=self.show_login_logs)
        self.btn_logs.pack(fill="x", padx=15, pady=5)

        self.btn_analytics = ctk.CTkButton(self.sidebar, text="📊 Deep Analytics", font=("Arial", 14, "bold"),
                                           fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                           anchor="w")
        self.btn_analytics.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(self.sidebar, text="Lock & Exit Admin", font=("Arial", 12, "bold"), fg_color="transparent",
                      text_color=self.red, hover_color="#34495E", anchor="w", command=self.lock_and_exit).pack(
            side="bottom", fill="x", padx=15, pady=30)

        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def set_active_tab(self, tab_name):
        self.btn_master.configure(fg_color=self.primary if tab_name == "master" else "transparent")
        self.btn_team.configure(fg_color=self.primary if tab_name == "users" else "transparent")
        self.btn_logs.configure(fg_color=self.primary if tab_name == "logs" else "transparent")
        self.btn_analytics.configure(fg_color=self.primary if tab_name == "analytics" else "transparent")

    # ==========================================
    # 1. MASTER DASHBOARD (WITH LIVE SEARCH)
    # ==========================================
    def show_master_dashboard(self):
        self.clear_main_frame()
        self.set_active_tab("master")

        ctk.CTkLabel(self.main_frame, text="Master Database (All Cases)", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=30, pady=(30, 0))

        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(15, 10))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var,
                                         placeholder_text="e.g., Search by Case ID, Complainant, or Respondent name...",
                                         width=350, height=40, font=("Arial", 12))
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_case_list())

        cat_list = ["All Categories"] + self.engine.get_incident_categories()
        self.filter_category_var = ctk.StringVar(value="All Categories")
        self.category_dropdown = ctk.CTkOptionMenu(filter_frame, variable=self.filter_category_var, values=cat_list,
                                                   width=200, height=40, fg_color=self.primary,
                                                   button_color=self.primary,
                                                   command=lambda e: self.refresh_case_list())
        self.category_dropdown.pack(side="left")

        self.list_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_case_list()

    def refresh_case_list(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        keyword = self.search_var.get()
        category = self.filter_category_var.get()

        filtered_cases = self.engine.advanced_search_incidents(keyword, category)

        if not filtered_cases:
            ctk.CTkLabel(self.list_container, text="No cases match your search criteria.", text_color="gray",
                         font=("Arial", 14, "italic")).pack(pady=50)
            return

        for case in filtered_cases:
            self.build_master_case_card(self.list_container, case)

    def build_master_case_card(self, parent, case):
        case_no = case.get('case_no')
        status = case.get('status')
        reopen_stat = case.get('reopen_status')
        comp = case.get('complainant_name', 'Not Recorded')
        resp = case.get('respondent_name', 'Not Recorded')
        officer = case.get('processed_by', 'Unknown')
        category = case.get('category', 'Uncategorized')

        if reopen_stat == 'Requested':
            display_status = "Re-open Requested"
            border_col = self.orange
        elif status == 'Urgent':
            display_status = "Urgent"
            border_col = self.red
        elif status == 'Resolved':
            display_status = "Resolved"
            border_col = self.primary
        else:
            display_status = "Pending"
            border_col = self.orange

        card = ctk.CTkFrame(parent, fg_color="white", border_color=border_col, border_width=2, corner_radius=8,
                            cursor="hand2")
        card.pack(fill="x", pady=5, padx=10)

        click_cmd = lambda e=None, c=case: self.show_incident_details(c)
        card.bind("<Button-1>", click_cmd)

        left_info = ctk.CTkFrame(card, fg_color="transparent")
        left_info.pack(side="left", padx=15, pady=10)

        lbl_id = ctk.CTkLabel(left_info, text=f"Case #{case_no}", font=("Arial", 14, "bold"), text_color=self.text_dark,
                              cursor="hand2")
        lbl_id.pack(anchor="w")
        lbl_id.bind("<Button-1>", click_cmd)

        lbl_names = ctk.CTkLabel(left_info, text=f"{comp} vs {resp}", font=("Arial", 12), text_color="gray",
                                 cursor="hand2")
        lbl_names.pack(anchor="w")
        lbl_names.bind("<Button-1>", click_cmd)

        lbl_cat = ctk.CTkLabel(left_info, text=f"Category: {category}", font=("Arial", 11, "italic"),
                               text_color=self.primary, cursor="hand2")
        lbl_cat.pack(anchor="w")
        lbl_cat.bind("<Button-1>", click_cmd)

        right_info = ctk.CTkFrame(card, fg_color="transparent")
        right_info.pack(side="right", padx=15, pady=10)

        lbl_stat = ctk.CTkLabel(right_info, text=display_status, font=("Arial", 12, "bold"), text_color=border_col,
                                cursor="hand2")
        lbl_stat.pack(anchor="e")
        lbl_stat.bind("<Button-1>", click_cmd)

        lbl_off = ctk.CTkLabel(right_info, text=f"Officer: {officer}", font=("Arial", 11, "italic"), text_color="gray",
                               cursor="hand2")
        lbl_off.pack(anchor="e")
        lbl_off.bind("<Button-1>", click_cmd)

        ctk.CTkButton(card, text="View Details", width=100, fg_color="#F0F0F0", text_color=self.text_dark,
                      hover_color="#E0E0E0", command=click_cmd).pack(side="right", padx=20)

    # ==========================================
    # POPUP: INCIDENT DETAILS & APPROVAL
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
        status_color = self.red if status == 'Urgent' else (self.green if status == 'Resolved' else self.orange)
        ctk.CTkLabel(info_frame, text="Status:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w", padx=15,
                                                                                  pady=(10, 5))
        ctk.CTkLabel(info_frame, text=status, text_color=status_color, font=("Arial", 12, "bold")).grid(row=0, column=3,
                                                                                                        sticky="w",
                                                                                                        padx=10,
                                                                                                        pady=(10, 5))

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

        if row_data.get('narrative_2'):
            ctk.CTkLabel(scroll_area, text="🔄 Phase 2: Re-open Details", font=("Arial", 14, "bold"),
                         text_color=self.orange).pack(anchor="w", padx=20, pady=(15, 5))

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

        btn_frame = ctk.CTkFrame(scroll_area, fg_color="transparent")
        btn_frame.pack(pady=(20, 20))

        if row_data.get('reopen_status') == 'Requested':
            ctk.CTkButton(btn_frame, text="Approve Re-open", fg_color=self.primary, hover_color=self.dark_green,
                          font=("Arial", 12, "bold"),
                          command=lambda: self.process_appeal(row_data['case_no'], 'Approve', popup)).pack(side="left",
                                                                                                           padx=10)
            ctk.CTkButton(btn_frame, text="Deny Request", fg_color=self.red, font=("Arial", 12, "bold"),
                          command=lambda: self.process_appeal(row_data['case_no'], 'Deny', popup)).pack(side="left",
                                                                                                        padx=10)

        ctk.CTkButton(btn_frame, text="Close Report", command=popup.destroy, fg_color="#E0E0E0",
                      text_color=self.text_dark, hover_color="#CCCCCC", font=("Arial", 12, "bold")).pack(side="left",
                                                                                                         padx=10)

    def process_appeal(self, case_no, action, popup):
        if self.engine.handle_reopen_request(case_no, action):
            messagebox.showinfo("Success", f"Re-open request {action}d successfully.")
            popup.destroy()
            self.refresh_case_list()
        else:
            messagebox.showerror("Error", "Failed to process the request.")

    # ==========================================
    # 2. TEAM MANAGEMENT
    # ==========================================
    def show_user_management(self):
        self.clear_main_frame()
        self.set_active_tab("users")

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="Team Management", font=("Arial", 24, "bold"), text_color=self.text_dark).pack(
            side="left")

        add_btn = ctk.CTkButton(header_frame, text="+ Add Account", fg_color=self.primary, hover_color=self.dark_green,
                                font=("Arial", 12, "bold"), height=35, command=self.launch_add_account)
        add_btn.pack(side="right")

        self.user_list_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.user_list_container.pack(fill="both", expand=True, padx=20, pady=10)

        users = self.engine.get_all_users()
        for u in users:
            self.build_user_card(self.user_list_container, u)

    def launch_add_account(self):
        try:
            try:
                from bircs_package.signup_screen import SignupWindow
            except ImportError:
                from signup_screen import SignupWindow

            SignupWindow(self.window, self.engine, is_admin_mode=True, on_refresh=self.show_user_management)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch Account Creator: {e}")

    def build_user_card(self, parent, user):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8)
        card.pack(fill="x", pady=5, padx=10)

        fname = user.get('first_name', '')
        lname = user.get('last_name', '')
        role = user.get('role', 'Staff')
        status = user.get('status', 'Active')

        avatar = ctk.CTkLabel(card, text=fname[0] if fname else "?", font=("Arial", 16, "bold"), width=40, height=40,
                              fg_color="#E8EAF6", text_color=self.blue, corner_radius=20)
        avatar.pack(side="left", padx=15, pady=10)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=5)

        ctk.CTkLabel(info_frame, text=f"{fname} {lname}", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w")

        stat_color = self.primary if status == "Active" else self.red
        ctk.CTkLabel(info_frame, text=f"• {role} ({status})", font=("Arial", 11), text_color=stat_color).pack(
            anchor="w")

        ctk.CTkButton(card, text="View Details", width=100, fg_color="transparent", border_width=1,
                      border_color="#D0D0D0", text_color=self.blue,
                      command=lambda u=user: self.show_manage_user_popup(u)).pack(side="right", padx=20)

    # ==========================================
    # 3. MANAGE USER POPUP
    # ==========================================
    def show_manage_user_popup(self, user):
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Manage User - {user.get('first_name', '')}")
        popup.geometry("450x700")
        popup.transient(self.window)
        popup.grab_set()

        perf_frame = ctk.CTkFrame(popup, fg_color=self.blue, corner_radius=0)
        perf_frame.pack(fill="x")

        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
        stats = self.engine.get_user_performance_stats(full_name)
        handled = stats.get('handled', 0)
        resolved = stats.get('resolved', 0)

        ctk.CTkLabel(perf_frame, text=f"Performance: {full_name}", font=("Arial", 16, "bold"), text_color="white").pack(
            pady=(20, 5))
        ctk.CTkLabel(perf_frame, text=f"Total Cases Handled: {handled}  |  Successfully Resolved: {resolved}",
                     font=("Arial", 11), text_color="white").pack(pady=(0, 20))

        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def create_field(label_text, default_val, is_disabled=False):
            ctk.CTkLabel(scroll_frame, text=label_text, font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 2))
            entry = ctk.CTkEntry(scroll_frame, height=35, font=("Arial", 12))
            entry.pack(fill="x")
            if default_val: entry.insert(0, default_val)
            if is_disabled: entry.configure(state="disabled", fg_color="#F0F0F0")
            return entry

        fname_entry = create_field("First Name", user.get('first_name'))
        lname_entry = create_field("Last Name", user.get('last_name'))
        emp_entry = create_field("Employee ID", user.get('employee_id'))
        rfid_entry = create_field("RFID Code", user.get('rfid_code'))
        pwd_entry = create_field("Password", user.get('password'))

        ctk.CTkLabel(scroll_frame, text="System Role", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 2))
        role_var = ctk.StringVar(value=user.get('role', 'Staff'))
        ctk.CTkOptionMenu(scroll_frame, variable=role_var, values=["Staff", "Admin", "Kapitan"], fg_color="white",
                          text_color="black").pack(fill="x")

        ctk.CTkLabel(scroll_frame, text="Account Status", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 2))
        stat_var = ctk.StringVar(value=user.get('status', 'Active'))
        stat_menu = ctk.CTkOptionMenu(scroll_frame, variable=stat_var, values=["Active", "Suspended", "Blocked"])
        stat_menu.pack(fill="x")

        susp_frame = ctk.CTkFrame(scroll_frame, fg_color="#FFF3CD", corner_radius=8)
        ctk.CTkLabel(susp_frame, text="Suspend For:", font=("Arial", 11, "bold"), text_color="#856404").pack(
            side="left", padx=10, pady=10)
        susp_val_entry = ctk.CTkEntry(susp_frame, width=60, height=30)
        susp_val_entry.pack(side="left", padx=5)
        susp_val_entry.insert(0, "24")

        susp_type_var = ctk.StringVar(value="Hours")
        ctk.CTkOptionMenu(susp_frame, variable=susp_type_var, values=["Hours", "Days"], width=80, height=30).pack(
            side="left", padx=5)

        def toggle_suspension(*args):
            if stat_var.get() == "Suspended":
                susp_frame.pack(fill="x", pady=10)
            else:
                susp_frame.pack_forget()

        stat_var.trace_add("write", toggle_suspension)
        toggle_suspension()

        def save_changes():
            fname = fname_entry.get().strip()
            lname = lname_entry.get().strip()
            emp_id = emp_entry.get().strip()
            pwd = pwd_entry.get().strip()
            role_val = role_var.get()
            stat_val = stat_var.get()
            new_rfid = rfid_entry.get().strip()
            s_val = susp_val_entry.get() if stat_val == "Suspended" else 0
            s_type = susp_type_var.get()

            success = self.engine.update_user_account(user['id'], fname, lname, emp_id, pwd, role_val, stat_val,
                                                      new_rfid, s_val, s_type)
            if success:
                messagebox.showinfo("Success", "User account successfully updated!")
                popup.destroy()
                self.show_user_management()
            else:
                messagebox.showerror("Error", "Failed to update user. Check database connection.")

        ctk.CTkButton(scroll_frame, text="Save Changes", fg_color=self.primary, hover_color=self.dark_green,
                      font=("Arial", 14, "bold"), height=45, command=save_changes).pack(pady=30)

    # ==========================================
    # 4. SYSTEM LOGS (AUDIT TRAIL)
    # ==========================================
    def show_login_logs(self):
        self.clear_main_frame()
        self.set_active_tab("logs")

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="System Access Logs", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, fg_color="#E0E0E0", text_color=self.text_dark,
                      hover_color="#D0D0D0", command=self.show_login_logs).pack(side="right")

        headers = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        headers.pack(fill="x", padx=40, pady=(10, 5))

        ctk.CTkLabel(headers, text="Employee", font=("Arial", 12, "bold"), text_color=self.text_muted, width=200,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Role", font=("Arial", 12, "bold"), text_color=self.text_muted, width=100,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Time In", font=("Arial", 12, "bold"), text_color=self.text_muted, width=180,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Time Out", font=("Arial", 12, "bold"), text_color=self.text_muted, width=180,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Session Time", font=("Arial", 12, "bold"), text_color=self.text_muted, width=100,
                     anchor="e").pack(side="right", padx=10)

        ctk.CTkFrame(self.main_frame, height=2, fg_color="#E0E0E0").pack(fill="x", padx=30)

        self.logs_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True, padx=20, pady=10)

        logs = self.engine.get_login_logs()

        if not logs:
            ctk.CTkLabel(self.logs_container, text="No system logs found in the database.", text_color="gray",
                         font=("Arial", 14, "italic")).pack(pady=50)
            return

        for log in logs:
            self.build_log_row(self.logs_container, log)

    def build_log_row(self, parent, log):
        row = ctk.CTkFrame(parent, fg_color="white", corner_radius=5, height=45)
        row.pack(fill="x", pady=2, padx=10)
        row.pack_propagate(False)

        name = log.get('employee_name', 'Unknown')
        role = log.get('role', 'N/A')
        login_time = log.get('login_time')
        logout_time = log.get('logout_time')

        try:
            if isinstance(login_time, str):
                login_time = datetime.strptime(login_time, '%Y-%m-%d %H:%M:%S')

            login_str = login_time.strftime("%b %d, %Y - %I:%M %p")

            if logout_time:
                if isinstance(logout_time, str):
                    logout_time = datetime.strptime(logout_time, '%Y-%m-%d %H:%M:%S')

                logout_str = logout_time.strftime("%b %d, %Y - %I:%M %p")

                duration = logout_time - login_time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)

                if hours > 0:
                    duration_str = f"{int(hours)}h {int(minutes)}m"
                else:
                    duration_str = f"{int(minutes)} mins"
                    if int(minutes) == 0: duration_str = "< 1 min"

            else:
                duration_str = "Active Now"
                logout_str = "---"
        except Exception as e:
            login_str = str(login_time)
            logout_str = str(logout_time)
            duration_str = "Error"

        ctk.CTkLabel(row, text=name, font=("Arial", 12, "bold"), text_color=self.text_dark, width=200, anchor="w").pack(
            side="left", padx=(10, 0))
        ctk.CTkLabel(row, text=role.upper(), font=("Arial", 10, "bold"), text_color=self.blue, width=100,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=login_str, font=("Arial", 11), text_color=self.text_muted, width=180, anchor="w").pack(
            side="left")
        ctk.CTkLabel(row, text=logout_str, font=("Arial", 11), text_color=self.text_muted, width=180, anchor="w").pack(
            side="left")

        dur_color = self.green if duration_str == "Active Now" else self.text_muted
        ctk.CTkLabel(row, text=duration_str, font=("Arial", 11, "bold"), text_color=dur_color, width=100,
                     anchor="e").pack(side="right", padx=10)

    def lock_and_exit(self):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to lock the Admin Dashboard and log out?"):

            # --- I-SAVE ANG EXACT LOGOUT TIME NI KAPITAN ---
            if hasattr(self, 'audit_id'):
                self.engine.log_user_logout(self.audit_id)
            # -----------------------------------------------

            self.window.destroy()

            # Ibalik sa Staff Dashboard (kung may naiwan) o sa Login
            if self.parent_dashboard:
                self.parent_dashboard.restore_dashboard()

    def force_logout_on_close(self):
        # I-save muna sa database bago mamatay ang admin panel!
        if hasattr(self, 'audit_id'):
            print("Admin Dashboard closed via X or Alt+F4. Saving exact logout time...")
            self.engine.log_user_logout(self.audit_id)

        self.window.destroy()

        if self.parent_dashboard:
            self.parent_dashboard.restore_dashboard()

    # ==========================================
    # SMART KEYBOARD SHORTCUTS (KAPITAN)
    # ==========================================
    def handle_shortcuts(self, event):
        # 1. THE SAFETY LOCK
        focused_widget = self.window.focus_get()
        if focused_widget:
            widget_type = type(focused_widget).__name__
            if widget_type in ['CTkEntry', 'CTkTextbox', 'Entry', 'Text']:
                return

        # 2. THE HOTKEYS
        key = event.char.lower()

        if key == '1':
            print("Shortcut: 1 pressed -> Master Dashboard")
            self.show_master_dashboard()
        elif key == '2':
            print("Shortcut: 2 pressed -> Team Management")
            self.show_user_management()
        elif key == '3':
            print("Shortcut: 3 pressed -> System Logs")
            self.show_login_logs()
        elif key == 'l':
            print("Shortcut: L pressed -> Lock and Exit")
            self.lock_and_exit()
