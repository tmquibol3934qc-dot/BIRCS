import customtkinter as ctk
from tkinter import messagebox


class AdminDashboardWindow:
    def __init__(self, engine, user_data, parent_dashboard=None):
        self.engine = engine
        self.user = user_data
        self.parent_dashboard = parent_dashboard

        self.window = ctk.CTkToplevel()
        self.window.title("BICRS - Kapitan Control Center")
        self.window.state('zoomed')
        self.window.configure(fg_color="#F4F7F6")

        # --- THEME COLORS ---
        self.primary = "#27AE60"
        self.dark_green = "#1E8449"
        self.bg_color = "#F4F7F6"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"
        self.red = "#E74C3C"
        self.orange = "#E79124"
        self.blue = "#3F51B5"

        self.setup_layout()
        self.show_master_dashboard()

    def setup_layout(self):
        # --- SIDEBAR ---
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

        # Nav Buttons
        self.btn_master = ctk.CTkButton(self.sidebar, text="📁 Master Dashboard", font=("Arial", 14, "bold"),
                                        fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                        anchor="w", command=self.show_master_dashboard)
        self.btn_master.pack(fill="x", padx=15, pady=5)

        self.btn_team = ctk.CTkButton(self.sidebar, text="👥 Team Management", font=("Arial", 14, "bold"),
                                      fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                      anchor="w", command=self.show_user_management)
        self.btn_team.pack(fill="x", padx=15, pady=5)

        self.btn_analytics = ctk.CTkButton(self.sidebar, text="📊 Deep Analytics", font=("Arial", 14, "bold"),
                                           fg_color="transparent", text_color="white", hover_color=self.dark_green,
                                           anchor="w")
        self.btn_analytics.pack(fill="x", padx=15, pady=5)

        # Logout
        ctk.CTkButton(self.sidebar, text="Lock & Exit Admin", font=("Arial", 12, "bold"), fg_color="transparent",
                      text_color=self.red, hover_color="#34495E", anchor="w", command=self.lock_and_exit).pack(
            side="bottom", fill="x", padx=15, pady=30)

        # --- MAIN FRAME ---
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def set_active_tab(self, tab_name):
        self.btn_master.configure(fg_color=self.primary if tab_name == "master" else "transparent")
        self.btn_team.configure(fg_color=self.primary if tab_name == "users" else "transparent")
        self.btn_analytics.configure(fg_color=self.primary if tab_name == "analytics" else "transparent")

    # ==========================================
    # 1. MASTER DASHBOARD
    # ==========================================
    def show_master_dashboard(self):
        self.clear_main_frame()
        self.set_active_tab("master")

        ctk.CTkLabel(self.main_frame, text="Master Database (All Cases)", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=30, pady=(30, 15))

        list_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=20, pady=10)

        cases = self.engine.get_all_incidents()

        if not cases:
            ctk.CTkLabel(list_container, text="No cases found in the database.", text_color="gray").pack(pady=50)
            return

        for case in cases:
            self.build_master_case_card(list_container, case)

    def build_master_case_card(self, parent, case):
        case_no = case.get('case_no')
        status = case.get('status')
        comp = case.get('complainant_name', 'Not Recorded')
        resp = case.get('respondent_name', 'Not Recorded')
        officer = case.get('processed_by', 'Unknown')

        border_col = self.red if status == 'Urgent' else (self.primary if status == 'Resolved' else self.orange)

        card = ctk.CTkFrame(parent, fg_color="white", border_color=border_col, border_width=2, corner_radius=8)
        card.pack(fill="x", pady=5, padx=10)

        left_info = ctk.CTkFrame(card, fg_color="transparent")
        left_info.pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(left_info, text=f"Case #{case_no}", font=("Arial", 14, "bold"), text_color=self.text_dark).pack(
            anchor="w")
        ctk.CTkLabel(left_info, text=f"{comp} vs {resp}", font=("Arial", 12), text_color="gray").pack(anchor="w")

        right_info = ctk.CTkFrame(card, fg_color="transparent")
        right_info.pack(side="right", padx=15, pady=10)
        ctk.CTkLabel(right_info, text=status, font=("Arial", 12, "bold"), text_color=border_col).pack(anchor="e")
        ctk.CTkLabel(right_info, text=f"Officer: {officer}", font=("Arial", 11, "italic"), text_color="gray").pack(
            anchor="e")

        ctk.CTkButton(card, text="View Details", width=100, fg_color="#F0F0F0", text_color=self.text_dark,
                      hover_color="#E0E0E0", command=lambda c=case: self.show_incident_details(c)).pack(side="right",
                                                                                                        padx=20)

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
        ctk.CTkLabel(scroll_area, text="📋 General Information", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)
        info_frame = ctk.CTkFrame(scroll_area, fg_color="#FFFFFF", corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(info_frame, text="Zone Level:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w",
                                                                                      padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=row_data.get('zone', 'N/A')).grid(row=0, column=1, sticky="w", padx=(0, 40))

        exact_date = row_data.get('date_of_incident') or 'N/A'
        exact_time = row_data.get('exact_time') or ''
        ctk.CTkLabel(info_frame, text="Logged Date/Time:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w",
                                                                                            padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=f"{exact_date} {exact_time}").grid(row=1, column=1, sticky="w", padx=(0, 40))

        processed_by = row_data.get('processed_by') or 'Not Recorded'
        ctk.CTkLabel(info_frame, text="Handling Officer:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w",
                                                                                            pady=5)
        ctk.CTkLabel(info_frame, text=processed_by, text_color=self.primary, font=("Arial", 12, "bold")).grid(row=0,
                                                                                                              column=3,
                                                                                                              sticky="w",
                                                                                                              padx=10)

        status = row_data.get('status') or 'N/A'
        ctk.CTkLabel(info_frame, text="Current Status:", font=("Arial", 12, "bold")).grid(row=1, column=2, sticky="w",
                                                                                          pady=5)
        status_color = self.red if status == 'Urgent' else (self.primary if status == 'Resolved' else self.orange)
        ctk.CTkLabel(info_frame, text=status, text_color=status_color, font=("Arial", 12, "bold")).grid(row=1, column=3,
                                                                                                        sticky="w",
                                                                                                        padx=10)

        # --- SECTION 2: PARTIES ---
        ctk.CTkLabel(scroll_area, text="👥 Involved Parties", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)
        parties_frame = ctk.CTkFrame(scroll_area, fg_color="#F8F9FA", corner_radius=8)
        parties_frame.pack(fill="x", padx=20, pady=(5, 15))

        complainant = row_data.get('complainant_name') or "Not Recorded"
        defendant = row_data.get('respondent_name') or "Not Recorded"

        ctk.CTkLabel(parties_frame, text="Complainant:", font=("Arial", 12, "bold"), text_color=self.primary).grid(
            row=0, column=0, sticky="w", padx=15, pady=8)
        ctk.CTkLabel(parties_frame, text=complainant, font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(parties_frame, text="Defendant/Respondent:", font=("Arial", 12, "bold"), text_color=self.red).grid(
            row=1, column=0, sticky="w", padx=15, pady=(0, 8))
        ctk.CTkLabel(parties_frame, text=defendant, font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=10)

        # --- SECTION 3: NARRATIVE & AUDIT ---
        ctk.CTkLabel(scroll_area, text="📝 Officer's Narrative", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)
        nar_box = ctk.CTkTextbox(scroll_area, height=130, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                 border_color="#E0E0E0")
        nar_box.pack(fill="x", padx=20, pady=(5, 2))

        narrative = row_data.get('narrative') or "No narrative provided for this case."
        nar_box.insert("1.0", narrative)
        nar_box.configure(state="disabled")

        log_stamp = f"Initial report filed by: {processed_by} | {exact_date} {exact_time}".strip()
        ctk.CTkLabel(scroll_area, text=log_stamp, font=("Arial", 11, "italic"), text_color=self.text_muted).pack(
            anchor="e", padx=25, pady=(0, 15))

        # --- SECTION 4: RESOLUTION & AUDIT ---
        ctk.CTkLabel(scroll_area, text="⚖️ Settlement & Resolution Terms", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)

        stage = row_data.get('hearing_stage') or 'N/A'
        deadline = row_data.get('compliance_deadline') or 'N/A'
        if stage != 'N/A' or deadline != 'N/A':
            ctk.CTkLabel(scroll_area, text=f"Stage: {stage}   |   Deadline: {deadline}", font=("Arial", 11, "italic"),
                         text_color=self.text_muted).pack(anchor="w", padx=20, pady=(0, 5))

        res_box = ctk.CTkTextbox(scroll_area, height=130, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                 border_color="#E0E0E0")
        res_box.pack(fill="x", padx=20, pady=(0, 2))

        res_text = row_data.get(
            'settlement_details') or "Case is still pending. No settlement agreement has been recorded yet."
        res_box.insert("1.0", res_text)
        res_box.configure(state="disabled")

        if status == 'Resolved':
            ctk.CTkLabel(scroll_area, text=f"Resolution finalized & authorized by: {processed_by}",
                         font=("Arial", 11, "italic"), text_color=self.text_muted).pack(anchor="e", padx=25,
                                                                                        pady=(0, 10))

        ctk.CTkButton(scroll_area, text="Close Report", command=popup.destroy, fg_color="#E0E0E0",
                      text_color=self.text_dark, hover_color="#CCCCCC").pack(pady=(10, 20))

    # ==========================================
    # 2. TEAM MANAGEMENT & ACCOUNT CREATION
    # ==========================================
    def show_user_management(self):
        self.clear_main_frame()
        self.set_active_tab("users")

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="Team Management", font=("Arial", 24, "bold"), text_color=self.text_dark).pack(
            side="left")

        # THE ADD ACCOUNT BUTTON
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

        # Blue Performance Header
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

        # THE FIX: Changed 'Username' to 'Employee ID'
        emp_entry = create_field("Employee ID", user.get('employee_id'))

        # THE FIX: Added the new RFID text box right below it!
        rfid_entry = create_field("RFID Code", user.get('rfid_code'))

        pwd_entry = create_field("Password", user.get('password'))

        ctk.CTkLabel(scroll_frame, text="System Role", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 2))
        role_var = ctk.StringVar(value=user.get('role', 'Staff'))
        ctk.CTkOptionMenu(scroll_frame, variable=role_var, values=["Staff", "Admin", "Kapitan"], fg_color="white",
                          text_color="black").pack(fill="x")

        # Suspension Logic
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

            success = self.engine.update_user_account(
                user['id'], fname, lname, emp_id, pwd, role_val, stat_val, new_rfid, s_val, s_type
            )

            if success:
                messagebox.showinfo("Success", "User account successfully updated!")
                popup.destroy()
                self.show_user_management()
            else:
                messagebox.showerror("Error", "Failed to update user. Check database connection.")

        ctk.CTkButton(scroll_frame, text="Save Changes", fg_color=self.primary, hover_color=self.dark_green,
                      font=("Arial", 14, "bold"), height=45, command=save_changes).pack(pady=30)

    # ==========================================
    # EXIT ROUTINE
    # ==========================================
    def lock_and_exit(self):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to lock the Admin Dashboard and log out?"):
            self.window.destroy()
            if self.parent_dashboard:
                self.parent_dashboard.restore_dashboard()
