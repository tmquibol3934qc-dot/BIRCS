import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os


class TeamManagementPage:
    def __init__(self, parent_frame, engine, root_window):
        self.parent = parent_frame
        self.engine = engine
        self.root = root_window

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"       # Web Canvas Gray
        self.color_card = "#FFFFFF"     # Crisp White
        self.color_border = "#EAECEE"   # Subtle borders
        self.primary = "#27AE60"        # Emerald Green (Active)
        self.dark_green = "#1E8449"     # Hover Green
        self.orange = "#E05D3A"         # Alert Orange (Suspended)
        self.red = "#E74C3C"            # Danger Red (Blocked)
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        self.setup_ui()

    def setup_ui(self):
        # 📌 HEADER SECTION
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="👥 Team Management", font=(self.ui_font, 26, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        # 🚀 CHUNKY ADD BUTTON
        add_btn = ctk.CTkButton(header_frame, text="+ Add New Account", fg_color=self.primary,
                                hover_color=self.dark_green,
                                font=(self.ui_font, 13, "bold"), height=40, corner_radius=8,
                                command=self.launch_add_account)
        add_btn.pack(side="right")

        # 📌 SCROLLABLE LIST CONTAINER
        self.user_list_container = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.user_list_container.pack(fill="both", expand=True, padx=25, pady=10)

        self.load_users()

    def load_users(self):
        for widget in self.user_list_container.winfo_children():
            widget.destroy()

        users = self.engine.get_all_users()

        if not users:
            ctk.CTkLabel(self.user_list_container, text="📭 No user accounts found.", text_color=self.text_muted,
                         font=(self.ui_font, 14, "italic")).pack(pady=50)
            return

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
        # 🚀 WEB-STYLE CARD
        card = ctk.CTkFrame(parent, fg_color=self.color_card, border_width=1, border_color=self.color_border,
                            corner_radius=8, height=70)
        card.pack(fill="x", pady=6, padx=10)
        card.pack_propagate(False)

        fname = user.get('first_name', '')
        lname = user.get('last_name', '')
        role = user.get('role', 'Staff')
        status = user.get('status', 'Active')

        # Identify Status Color
        if status == "Active":
            stat_color = self.primary
        elif status == "Blocked":
            stat_color = self.red
        else:
            stat_color = self.orange

        # 🚀 THE COLOR STRIP INDICATOR
        ctk.CTkFrame(card, width=5, fg_color=stat_color, corner_radius=0).pack(side="left", fill="y")

        # 📌 AVATAR SECTION
        pic_path = user.get('profile_pic')
        avatar_img = None

        if pic_path and os.path.exists(pic_path):
            try:
                img = Image.open(pic_path)
                avatar_img = ctk.CTkImage(light_image=img, size=(46, 46))
            except Exception:
                pass

        if avatar_img:
            avatar = ctk.CTkLabel(card, text="", image=avatar_img)
            avatar.pack(side="left", padx=(15, 10))
        else:
            avatar = ctk.CTkLabel(card, text=fname[0].upper() if fname else "?", font=(self.ui_font, 18, "bold"),
                                  width=46, height=46, fg_color="#EBF5FB", text_color=self.color_sidebar,
                                  corner_radius=23)
            avatar.pack(side="left", padx=(15, 10))

        # 📌 INFO SECTION
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=5, pady=12)

        ctk.CTkLabel(info_frame, text=f"{fname} {lname}", font=(self.ui_font, 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", pady=0)

        role_stat_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        role_stat_frame.pack(anchor="w", pady=0)
        ctk.CTkLabel(role_stat_frame, text=f"{role}  |  ", font=(self.ui_font, 11), text_color=self.text_muted).pack(
            side="left")
        ctk.CTkLabel(role_stat_frame, text=status, font=(self.ui_font, 11, "bold"), text_color=stat_color).pack(
            side="left")

        # 📌 ACTION BUTTON
        ctk.CTkButton(card, text="✏️ Manage", width=100, height=32, fg_color="transparent", border_width=1,
                      border_color=self.color_border, text_color=self.color_sidebar, hover_color="#F8F9FA",
                      font=(self.ui_font, 12, "bold"),
                      command=lambda u=user: self.show_manage_user_popup(u)).pack(side="right", padx=20)

    # =========================================================================
    # THE MANAGE USER MODAL
    # =========================================================================
    def show_manage_user_popup(self, user):
        popup = ctk.CTkToplevel(self.root)
        popup.title(f"Manage User - {user.get('first_name', '')}")

        window_width = 460
        window_height = 760
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        popup.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        popup.transient(self.root)
        popup.grab_set()
        popup.configure(fg_color="#FDFCF6")

        # 🚀 1. DEEP NAVY PROFILE HEADER
        perf_frame = ctk.CTkFrame(popup, fg_color=self.color_sidebar, corner_radius=0)
        perf_frame.pack(fill="x")

        self.temp_pic_path = user.get('profile_pic')

        def change_photo():
            file_path = filedialog.askopenfilename(
                title="Select Profile Picture",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
            )
            if file_path:
                self.temp_pic_path = file_path
                try:
                    new_img = Image.open(file_path)
                    updated_popup_img = ctk.CTkImage(light_image=new_img, size=(86, 86))
                    pic_preview_label.configure(image=updated_popup_img, text="")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not preview image: {e}", parent=popup)

        # Avatar Display
        pic_btn_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        pic_btn_frame.pack(pady=(25, 10))

        try:
            current_img = Image.open(self.temp_pic_path) if self.temp_pic_path and os.path.exists(
                self.temp_pic_path) else None
            display_img = ctk.CTkImage(light_image=current_img, size=(86, 86)) if current_img else None
        except:
            display_img = None

        if not display_img:
            pic_preview_label = ctk.CTkLabel(pic_btn_frame, text=user.get('first_name', '?')[0].upper(),
                                             font=(self.ui_font, 36, "bold"), width=86, height=86,
                                             fg_color="#EBF5FB", text_color=self.color_sidebar, corner_radius=43)
        else:
            pic_preview_label = ctk.CTkLabel(pic_btn_frame, text="", image=display_img, width=86, height=86,
                                             corner_radius=43)

        pic_preview_label.pack()

        ctk.CTkButton(perf_frame, text="📸 Change Photo", font=(self.ui_font, 11, "bold"), corner_radius=12,
                      fg_color="white", text_color=self.color_sidebar, hover_color="#F0F0F0", height=28,
                      command=change_photo).pack(pady=(5, 15))

        # User Stats
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
        stats = self.engine.get_user_performance_stats(full_name)
        handled = stats.get('handled', 0)
        resolved = stats.get('resolved', 0)

        ctk.CTkLabel(perf_frame, text=full_name, font=(self.ui_font, 20, "bold"), text_color="white").pack(
            pady=(0, 2))

        stat_lbl_frame = ctk.CTkFrame(perf_frame, fg_color="#2A2F6C", corner_radius=10)
        stat_lbl_frame.pack(pady=(5, 25), ipadx=10, ipady=2)
        ctk.CTkLabel(stat_lbl_frame, text=f"Cases Handled: {handled}   |   Resolved: {resolved}",
                     font=(self.ui_font, 11, "bold"), text_color="#A9CCE3").pack()

        # 🚀 2. CRISP WEB FORM AREA
        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def create_clean_field(label_text, default_val, is_disabled=False):
            ctk.CTkLabel(scroll_frame, text=label_text, font=(self.ui_font, 12, "bold"),
                         text_color=self.text_dark).pack(anchor="w", pady=(15, 5), padx=5)

            bg_col = "#F0F0F0" if is_disabled else "#FFFFFF"
            entry = ctk.CTkEntry(scroll_frame, height=40, font=(self.ui_font, 13), fg_color=bg_col, border_width=1,
                                 border_color=self.color_border, corner_radius=6, text_color="black")
            entry.pack(fill="x", padx=5)
            if default_val is not None:
                entry.insert(0, str(default_val))
            if is_disabled:
                entry.configure(state="disabled", text_color="gray")
            return entry

        fname_entry = create_clean_field("First Name", user.get('first_name'))
        lname_entry = create_clean_field("Last Name", user.get('last_name'))
        emp_entry = create_clean_field("Employee ID", user.get('employee_id'))
        rfid_entry = create_clean_field("RFID Code (Optional)", user.get('rfid_code'))
        pwd_entry = create_clean_field("Password", user.get('password'))

        original_password = user.get('password')

        # 📌 DROPDOWNS
        ctk.CTkLabel(scroll_frame, text="System Role", font=(self.ui_font, 12, "bold"), text_color=self.text_dark).pack(
            anchor="w", pady=(15, 5), padx=5)
        current_role = user.get('role', 'Staff')
        role_var = ctk.StringVar(value=current_role)

        if current_role == "Kapitan":
            role_menu = ctk.CTkOptionMenu(scroll_frame, variable=role_var, values=["Kapitan"], state="disabled",
                                          fg_color="#F0F0F0", text_color="gray", button_color="#E0E0E0")
        else:
            role_menu = ctk.CTkOptionMenu(scroll_frame, variable=role_var, values=["Staff", "Admin"],
                                          fg_color="#FFFFFF",
                                          text_color="black", button_color="#EAECEE", button_hover_color="#D5D8DC",
                                          font=(self.ui_font, 13), height=40, corner_radius=6)
        role_menu.pack(fill="x", padx=5)

        ctk.CTkLabel(scroll_frame, text="Account Status", font=(self.ui_font, 12, "bold"),
                     text_color=self.text_dark).pack(anchor="w", pady=(15, 5), padx=5)
        stat_var = ctk.StringVar(value=user.get('status', 'Active'))

        stat_menu = ctk.CTkOptionMenu(scroll_frame, variable=stat_var, values=["Active", "Suspended", "Blocked"],
                                      fg_color="#FFFFFF",
                                      text_color="black", button_color="#EAECEE", button_hover_color="#D5D8DC",
                                      font=(self.ui_font, 13), height=40, corner_radius=6)
        stat_menu.pack(fill="x", padx=5)

        # 📌 SUSPENSION CONTROLS
        susp_frame = ctk.CTkFrame(scroll_frame, fg_color="#FDEDEC", border_width=1, border_color="#F5B7B1",
                                  corner_radius=8)

        ctk.CTkLabel(susp_frame, text="Suspend For:", font=(self.ui_font, 12, "bold"), text_color="#C0392B").pack(
            side="left", padx=15, pady=15)
        susp_val_entry = ctk.CTkEntry(susp_frame, width=60, height=35, fg_color="#FFFFFF", border_width=1,
                                      border_color="#F5B7B1", text_color="black")
        susp_val_entry.pack(side="left", padx=5)
        susp_val_entry.insert(0, "24")

        susp_type_var = ctk.StringVar(value="Hours")
        ctk.CTkOptionMenu(susp_frame, variable=susp_type_var, values=["Hours", "Days"], width=90, height=35,
                          fg_color="#FFFFFF",
                          text_color="black", button_color="#F5B7B1", button_hover_color="#E6B0AA", font=(self.ui_font, 12)).pack(side="left",
                                                                                                         padx=5)

        def toggle_suspension(*args):
            if stat_var.get() == "Suspended":
                susp_frame.pack(fill="x", padx=5, pady=15)
            else:
                susp_frame.pack_forget()

        stat_var.trace_add("write", toggle_suspension)
        toggle_suspension()

        # 📌 SAVE BUTTON
        def save_changes():
            fname = fname_entry.get().strip()
            lname = lname_entry.get().strip()
            emp_id = emp_entry.get().strip()
            new_pwd = pwd_entry.get().strip()
            role_val = role_var.get()
            stat_val = stat_var.get()
            new_pic = self.temp_pic_path

            rfid_input = rfid_entry.get().strip()
            new_rfid = rfid_input if rfid_input != "" else None
            s_val = susp_val_entry.get() if stat_val == "Suspended" else 0
            s_type = susp_type_var.get()

            try:
                success = self.engine.update_user_account(
                    user['id'], fname, lname, emp_id, new_pwd, role_val, stat_val,
                    new_rfid, s_val, s_type, profile_pic=new_pic
                )

                if success:
                    if new_pwd != original_password:
                        self.engine.log_security_event(user_id=emp_id, action="FORCED PASSWORD RESET",
                                                       details=f"VIA ADMIN: Password changed for {fname} {lname}.")
                    messagebox.showinfo("Success", "User account successfully updated!", parent=popup)
                    popup.destroy()
                    self.load_users()
                else:
                    messagebox.showerror("Error", "Failed to update user.", parent=popup)
            except Exception as e:
                messagebox.showerror("Error", f"Something went wrong: {e}", parent=popup)

        ctk.CTkButton(scroll_frame, text="💾 Save Changes", fg_color=self.primary, hover_color=self.dark_green,
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=8, command=save_changes).pack(
            pady=(30, 20), padx=5, fill="x")
