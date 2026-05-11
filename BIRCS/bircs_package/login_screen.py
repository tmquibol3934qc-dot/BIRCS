import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os


class LoginWindow:
    def __init__(self, root, auth_engine):
        self.root = root
        self.engine = auth_engine
        self.root.overrideredirect(True)
        ctk.set_appearance_mode("light")

        # 🚀 POGI UPDATE: Web-Accurate Palette based on your Image!
        self.color_accent = "#E05D3A"  # The specific reddish-orange in the image
        self.color_card_bg = "#FDFCF6"  # Cream / Off-white background
        self.color_border = "#4A90E2"  # Thin blue border of the card

        self.text_dark = "#2B2B2B"
        self.header_font = "Young Serif"  # Gagamitin natin sa LOG IN at Button
        self.ui_font = "Poppins"

        self.root.title("BICRS Login")

        w, h = 1000, 650

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.load_images()

        # Full screen background
        self.bg_label = ctk.CTkLabel(self.root, text="", image=self.bg_image)
        self.bg_label.pack(fill="both", expand=True)

        self.create_login_card()

    def load_images(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        try:
            bg_path = os.path.join(current_path, "background.jpg")
            raw_img = Image.open(bg_path).convert("RGBA")
            raw_img = raw_img.resize((1000, 650))
            overlay = Image.new("RGBA", raw_img.size,
                                (255, 255, 255, 120))  # Less white overlay para mas kita background
            final_bg = Image.alpha_composite(raw_img, overlay)
            self.bg_image = ctk.CTkImage(light_image=final_bg, size=(1000, 650))
        except Exception:
            self.bg_image = None

        try:
            logo_path = os.path.join(current_path, "logo.jpg")
            pil_logo = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_logo, size=(100, 100))  # Pinalaki ng konti
        except Exception:
            self.logo_image = None

    def create_login_card(self):
        # 🚀 POGI UPDATE: The Web Card Clone
        # Cream background, sharp radius, blue border outline
        card = ctk.CTkFrame(self.bg_label, fg_color=self.color_card_bg, width=450, height=520,
                            corner_radius=8, border_width=1, border_color=self.color_border)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Invisible or minimal back button (pang close kung walang X window)
        back_btn = ctk.CTkButton(card, text="✕", width=30, fg_color="transparent",
                                 text_color="gray", font=("Arial", 16, "bold"),
                                 hover_color="#E0E0E0", command=self.confirm_exit)
        back_btn.place(x=10, y=10)

        # 1. LOGO
        if self.logo_image:
            logo_label = ctk.CTkLabel(card, text="", image=self.logo_image)
            logo_label.pack(pady=(40, 5))
        else:
            ctk.CTkLabel(card, text="LOGO", width=90, height=90, fg_color="#EEE", corner_radius=45).pack(pady=(40, 5))

        # 2. LOG IN HEADER
        ctk.CTkLabel(card, text="LOG IN", font=(self.header_font, 28, "bold"),
                     text_color=self.color_accent).pack(pady=(15, 25))

        # 3. INPUT FIELDS
        self.user_entry = self.create_input_field(card, "Enter your Employee ID", icon="👤")
        self.user_entry.bind('<Return>', lambda event: self.handle_login())

        self.pass_entry, self.eye_btn = self.create_password_field(card, "Enter your password")
        self.pass_entry.bind('<Return>', lambda event: self.handle_login())

        # 4. FORGOT PASSWORD (Right Aligned)
        opts_frame = ctk.CTkFrame(card, fg_color="transparent")
        opts_frame.pack(fill="x", padx=60, pady=(0, 25))

        forgot = ctk.CTkLabel(opts_frame, text="Forgot Password?",
                              font=(self.ui_font, 11), text_color=self.color_accent, cursor="hand2")
        forgot.pack(side="right")
        forgot.bind("<Button-1>", lambda e: self.open_forgot_popup())

        # 5. SOLID LOGIN BUTTON
        login_btn = ctk.CTkButton(card, text="LOGIN", command=self.handle_login,
                                  width=160, height=45, corner_radius=8,
                                  fg_color=self.color_accent, hover_color="#C0392B",
                                  font=(self.header_font, 16, "bold"), text_color="white")
        login_btn.pack(pady=(5, 20))

        self.user_entry.focus_set()

    def create_input_field(self, parent, placeholder, icon):
        # 🚀 POGI UPDATE: Pure white field inside the cream card with grey border
        container = ctk.CTkFrame(parent, height=45, fg_color="#FFFFFF", border_width=1, border_color="#C0C0C0",
                                 corner_radius=8)
        container.pack(pady=(0, 15), padx=60, fill="x")  # padx=60 makes it narrower than the card

        # Icon Label
        ctk.CTkLabel(container, text=icon, font=("Arial", 16), text_color="black", fg_color="transparent",
                     width=35).pack(side="left", padx=(10, 0))

        # Entry Field
        entry = ctk.CTkEntry(container, height=35, border_width=0, fg_color="#FFFFFF", text_color="black",
                             placeholder_text_color="#9E9E9E", placeholder_text=placeholder, font=(self.ui_font, 12))
        entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=4)
        return entry

    def create_password_field(self, parent, placeholder):
        container = ctk.CTkFrame(parent, height=45, fg_color="#FFFFFF", border_width=1, border_color="#C0C0C0",
                                 corner_radius=8)
        container.pack(pady=(0, 5), padx=60, fill="x")

        # Icon Label
        ctk.CTkLabel(container, text="🔒", font=("Arial", 16), text_color="black", fg_color="transparent",
                     width=35).pack(side="left", padx=(10, 0))

        # Entry Field
        entry = ctk.CTkEntry(container, height=35, border_width=0, fg_color="#FFFFFF", text_color="black",
                             placeholder_text_color="#9E9E9E", placeholder_text=placeholder, font=(self.ui_font, 12),
                             show="*")
        entry.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=4)

        # Eye Button
        eye_btn = ctk.CTkButton(container, text="👁", width=30, fg_color="transparent", text_color="black",
                                hover_color="#EAEAEA", font=("Arial", 14),
                                command=lambda: self.toggle_password(entry, eye_btn))
        eye_btn.pack(side="right", padx=(0, 10), pady=4)
        return entry, eye_btn

    def toggle_password(self, entry, btn):
        if entry.cget('show') == '*':
            entry.configure(show='')
            btn.configure(text="🚫")
        else:
            entry.configure(show='*')
            btn.configure(text="👁")

    def handle_login(self):
        # [Unchanged backend logic]
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()

        if not u:
            messagebox.showwarning("Input Error", "Please enter your Username, ID, or tap RFID.")
            return

        auth_result = self.engine.authenticate_user(u, p)

        if auth_result.get("success"):
            user_data = auth_result.get("user_data")
            role = user_data.get('role', 'Staff')
            fname = user_data.get('first_name', '')
            lname = user_data.get('last_name', '')

            messagebox.showinfo("Login Success", f"Welcome back, {role.title()} {fname} {lname}!")
            self.root.withdraw()

            try:
                if role.lower() == "kapitan" or role.lower() == "admin":
                    try:
                        from bircs_package.admin_dashboard import AdminDashboardWindow
                    except ImportError:
                        from admin_dashboard import AdminDashboardWindow

                    self.admin_window = AdminDashboardWindow(self.engine, user_data, parent_dashboard=self)
                else:
                    try:
                        from bircs_package.dashboard_screen import DashboardWindow
                    except ImportError:
                        from dashboard_screen import DashboardWindow

                    self.dashboard = DashboardWindow(self.engine, user_data, on_logout=self.logout_user)

            except Exception as e:
                print(f"Dashboard Error: {e}")
                messagebox.showerror("Dashboard Error", f"Failed to load the dashboard: {e}")
                self.root.deiconify()

        else:
            error_message = auth_result.get("message", "Invalid Credentials or Unregistered RFID.")
            messagebox.showerror("Login Failed", error_message)
            self.pass_entry.delete(0, 'end')
            self.user_entry.focus_set()

    def logout_user(self):
        self.root.deiconify()
        self.user_entry.delete(0, 'end')
        self.pass_entry.delete(0, 'end')
        self.user_entry.focus_set()

    # 🚀 ETO YUNG NAWALA KANINA! I-paste mo 'to boss:
    def restore_dashboard(self):
        self.logout_user()

    def open_forgot_popup(self):
        try:
            try:
                from bircs_package.ForgotPasswordDialog import ForgotPasswordDialog
            except ImportError:
                from ForgotPasswordDialog import ForgotPasswordDialog
            ForgotPasswordDialog(self.root, self.engine)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load screen: {e}")

    def confirm_exit(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to close the BICRS system?")
        if response:
            self.root.destroy()
