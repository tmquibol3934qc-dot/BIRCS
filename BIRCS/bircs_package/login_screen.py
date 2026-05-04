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

        # Colors
        self.color_orange = "#E79124"
        self.text_dark = "#2C3E50"
        self.header_font = "Young Serif"
        self.ui_font = "Poppins"

        self.root.title("BICRS Login")

        w, h = 1000, 650

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.load_images()

        # 🚀 POGI UPDATE: Full screen background, no more blocking top bar!
        self.bg_label = ctk.CTkLabel(self.root, text="", image=self.bg_image)
        self.bg_label.pack(fill="both", expand=True)

        self.create_login_card()

    def load_images(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        try:
            bg_path = os.path.join(current_path, "background.jpg")
            raw_img = Image.open(bg_path).convert("RGBA")
            raw_img = raw_img.resize((1000, 650))
            overlay = Image.new("RGBA", raw_img.size, (255, 255, 255, 180))  # Slightly clearer background
            final_bg = Image.alpha_composite(raw_img, overlay)
            self.bg_image = ctk.CTkImage(light_image=final_bg, size=(1000, 650))
        except Exception:
            self.bg_image = None
        try:
            logo_path = os.path.join(current_path, "logo.jpg")
            pil_logo = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_logo, size=(90, 90))  # Saktong size lang
        except Exception:
            self.logo_image = None

    def create_login_card(self):
        # 🚀 POGI UPDATE: Modern White Card with smooth corners
        card = ctk.CTkFrame(self.bg_label, fg_color="white", width=420, height=520, corner_radius=15)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        back_btn = ctk.CTkButton(card, text="✕", width=30, fg_color="transparent",
                                 text_color="gray", font=("Arial", 18, "bold"),
                                 hover_color="#F0F0F0", command=self.confirm_exit)
        back_btn.place(x=15, y=15)

        if self.logo_image:
            logo_label = ctk.CTkLabel(card, text="", image=self.logo_image)
            logo_label.pack(pady=(35, 5))
        else:
            ctk.CTkLabel(card, text="LOGO", width=80, height=80, fg_color="#EEE", corner_radius=40).pack(pady=(35, 5))

        # 🚀 POGI UPDATE: Better Greeting Typography
        ctk.CTkLabel(card, text="Welcome Back!", font=(self.header_font, 24, "bold"), text_color=self.text_dark).pack(
            pady=(5, 0))
        ctk.CTkLabel(card, text="Please sign in to continue", font=(self.ui_font, 12), text_color="gray").pack(
            pady=(0, 25))

        # Modern Inputs
        self.user_entry = self.create_input_field(card, "Employee ID or tap RFID", icon="👤")
        self.user_entry.bind('<Return>', lambda event: self.handle_login())

        self.pass_entry, self.eye_btn = self.create_password_field(card, "Enter your password")
        self.pass_entry.bind('<Return>', lambda event: self.handle_login())

        # Forgot Password Section
        opts_frame = ctk.CTkFrame(card, fg_color="transparent")
        opts_frame.pack(fill="x", padx=40, pady=(5, 25))

        forgot = ctk.CTkLabel(opts_frame, text="Forgot Password?",
                              font=(self.ui_font, 11, "bold"), text_color=self.color_orange, cursor="hand2")
        forgot.pack(side="right")
        forgot.bind("<Button-1>", lambda e: self.open_forgot_popup())

        # Primary Login Button
        login_btn = ctk.CTkButton(card, text="LOG IN", command=self.handle_login,
                                  width=200, height=45, corner_radius=8,
                                  fg_color=self.color_orange, hover_color="#C67B1D",
                                  font=(self.ui_font, 14, "bold"))
        login_btn.pack(pady=5)

        self.user_entry.focus_set()

    def create_input_field(self, parent, placeholder, icon):
        # 🚀 POGI UPDATE: Soft backgrounds and smooth borders! Bye bye rigid black borders!
        container = ctk.CTkFrame(parent, height=45, fg_color="#F8F9FA", border_width=1, border_color="#E0E0E0",
                                 corner_radius=8)
        container.pack(pady=(0, 15), padx=40, fill="x")

        ctk.CTkLabel(container, text=icon, font=("Arial", 16), text_color="gray", fg_color="transparent",
                     width=40).pack(side="left", padx=(10, 5))

        entry = ctk.CTkEntry(container, height=35, border_width=0, fg_color="#F8F9FA", text_color="black",
                             placeholder_text=placeholder, font=(self.ui_font, 12))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)
        return entry

    def create_password_field(self, parent, placeholder):
        container = ctk.CTkFrame(parent, height=45, fg_color="#F8F9FA", border_width=1, border_color="#E0E0E0",
                                 corner_radius=8)
        container.pack(pady=(0, 15), padx=40, fill="x")

        ctk.CTkLabel(container, text="🔒", font=("Arial", 16), text_color="gray", fg_color="transparent", width=40).pack(
            side="left", padx=(10, 5))

        entry = ctk.CTkEntry(container, height=35, border_width=0, fg_color="#F8F9FA", text_color="black",
                             placeholder_text=placeholder, font=(self.ui_font, 12), show="*")
        entry.pack(side="left", fill="x", expand=True, pady=5)

        eye_btn = ctk.CTkButton(container, text="👁", width=40, fg_color="transparent", text_color="gray",
                                hover_color="#EAEAEA",
                                font=("Arial", 14), command=lambda: self.toggle_password(entry, eye_btn))
        eye_btn.pack(side="right", padx=(5, 10), pady=5)
        return entry, eye_btn

    def toggle_password(self, entry, btn):
        if entry.cget('show') == '*':
            entry.configure(show='')
            btn.configure(text="🚫")
        else:
            entry.configure(show='*')
            btn.configure(text="👁")

    def handle_login(self):
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

    def restore_dashboard(self):
        self.logout_user()

    def close_app(self):
        self.root.destroy()

    def open_forgot_popup(self):
        try:
            try:
                from bircs_package.ForgotPasswordDialog import ForgotPasswordDialog
            except ImportError:
                from ForgotPasswordDialog import ForgotPasswordDialog

            ForgotPasswordDialog(self.root, self.engine)

        except TypeError as e:
            print(f"Ghost File Error: {e}")
            messagebox.showerror("Ghost File Detected",
                                 "Python is reading an old version of forgot_password.py!\n\nPlease check your folders and delete any extra copies.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load screen: {e}")

    def confirm_exit(self):
        response = messagebox.askyesno(
            "Exit Application",
            "Are you sure you want to close the BICRS system?"
        )

        if response:
            print("System shutting down gracefully...")
            self.root.destroy()
