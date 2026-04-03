import customtkinter as ctk
from tkinter import messagebox


class TeamManagementPage:
    def __init__(self, parent_frame, engine, root_window):
        self.parent = parent_frame
        self.engine = engine
        self.root = root_window  # Kailangan natin 'to para sa Popups

        # Colors
        self.primary = "#27AE60"
        self.dark_green = "#1E8449"
        self.blue = "#3F51B5"
        self.red = "#E74C3C"
        self.text_dark = "#2B2B2B"

        self.setup_ui()

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="Team Management", font=("Arial", 24, "bold"), text_color=self.text_dark).pack(
            side="left")

        add_btn = ctk.CTkButton(header_frame, text="+ Add Account", fg_color=self.primary, hover_color=self.dark_green,
                                font=("Arial", 12, "bold"), height=35, command=self.launch_add_account)
        add_btn.pack(side="right")

        self.user_list_container = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.user_list_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_users()

    def load_users(self):
        for widget in self.user_list_container.winfo_children():
            widget.destroy()

        users = self.engine.get_all_users()
        for u in users:
            self.build_user_card(self.user_list_container, u)

    def launch_add_account(self):
        try:
            try:
                from bircs_package.signup_screen import SignupWindow
            except ImportError:
                from signup_screen import SignupWindow

            SignupWindow(self.root, self.engine, is_admin_mode=True, on_refresh=self.load_users)
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

    def show_manage_user_popup(self, user):
        popup = ctk.CTkToplevel(self.root)
        popup.title(f"Manage User - {user.get('first_name', '')}")
        popup.geometry("450x700")
        popup.transient(self.root)
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

        current_role = user.get('role', 'Staff')
        role_var = ctk.StringVar(value=current_role)

        if current_role == "Kapitan":
            role_menu = ctk.CTkOptionMenu(scroll_frame, variable=role_var, values=["Kapitan"], state="disabled",
                                          fg_color="#E0E0E0", text_color="gray")
        else:
            role_menu = ctk.CTkOptionMenu(scroll_frame, variable=role_var, values=["Staff", "Admin"], fg_color="white",
                                          text_color="black")

        role_menu.pack(fill="x")

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
                self.load_users()
            else:
                messagebox.showerror("Error", "Failed to update user. Check database connection.")

        ctk.CTkButton(scroll_frame, text="Save Changes", fg_color=self.primary, hover_color=self.dark_green,
                      font=("Arial", 14, "bold"), height=45, command=save_changes).pack(pady=30)
