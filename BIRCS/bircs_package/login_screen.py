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
        self.color_orange = "#E79124"
        self.header_font = "Young Serif"
        self.ui_font = "Poppins"
        self.root.title("BIRCS Login")

        w, h = 1000, 650

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.load_images()
        self.create_top_bar()
        self.bg_label = ctk.CTkLabel(self.root, text="", image=self.bg_image)
        self.bg_label.pack(fill="both", expand=True)
        self.create_login_card()


    def load_images(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        try:
            bg_path = os.path.join(current_path, "background.jpg")
            raw_img = Image.open(bg_path).convert("RGBA")
            raw_img = raw_img.resize((1000, 650))
            overlay = Image.new("RGBA", raw_img.size, (255, 255, 255, 200))
            final_bg = Image.alpha_composite(raw_img, overlay)
            self.bg_image = ctk.CTkImage(light_image=final_bg, size=(1000, 650))
        except Exception:
            self.bg_image = None
        try:
            logo_path = os.path.join(current_path, "logo.jpg")
            pil_logo = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_logo, size=(100, 100))
        except Exception:
            self.logo_image = None

    def create_top_bar(self):
        top_bar = ctk.CTkFrame(self.root, height=60, fg_color=self.color_orange, corner_radius=0)
        top_bar.pack(side="top", fill="x")
        logo_text = ctk.CTkLabel(top_bar, text="🏛 BIRCS", font=("Arial", 20, "bold"), text_color="white")
        logo_text.pack(side="left", padx=20, pady=10)

    def create_login_card(self):
        # Slightly shorter card since we removed the Sign Up button
        card = ctk.CTkFrame(self.bg_label, fg_color="white", width=450, height=500, corner_radius=10)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        back_btn = ctk.CTkButton(card, text="✕", width=30, fg_color="transparent",
                                 text_color=self.color_orange, font=("Arial", 20, "bold"),
                                 hover_color="#EEE", command=self.confirm_exit)
        back_btn.place(x=10, y=10)

        if self.logo_image:
            logo_label = ctk.CTkLabel(card, text="", image=self.logo_image)
            logo_label.pack(pady=(30, 10))
        else:
            ctk.CTkLabel(card, text="LOGO", width=80, height=80, fg_color="#EEE").pack(pady=(40, 10))

        ctk.CTkLabel(card, text="LOG IN", font=(self.header_font, 26, "bold"), text_color=self.color_orange).pack(
            pady=(0, 20))

        self.user_entry = self.create_input_field(card, "Enter ID or tap RFID", icon="👤")
        self.user_entry.bind('<Return>', lambda event: self.handle_login())

        self.pass_entry, self.eye_btn = self.create_password_field(card, "Enter your password")

        opts_frame = ctk.CTkFrame(card, fg_color="white")
        opts_frame.pack(pady=(5, 20), padx=40, fill="x")

        self.rem_var = ctk.BooleanVar()
        chk = ctk.CTkCheckBox(opts_frame, text="Remember Me", variable=self.rem_var,
                              font=(self.ui_font, 11), text_color="gray",
                              fg_color=self.color_orange, hover_color="#C67B1D",
                              border_color="gray", border_width=1, corner_radius=3)
        chk.pack(side="left")

        forgot = ctk.CTkLabel(opts_frame, text="Forgot Password?",
                              font=(self.ui_font, 11, "bold"), text_color=self.color_orange, cursor="hand2")
        forgot.pack(side="right")
        forgot.bind("<Button-1>", lambda e: self.open_forgot_popup())

        login_btn = ctk.CTkButton(card, text="LOGIN", command=self.handle_login,
                                  width=200, height=45, corner_radius=0,
                                  fg_color=self.color_orange, hover_color="#C67B1D",
                                  font=(self.ui_font, 14, "bold"))
        login_btn.pack(pady=10)

        self.user_entry.focus_set()

    def create_input_field(self, parent, placeholder, icon):
        container = ctk.CTkFrame(parent, height=50, fg_color="white", border_width=2, border_color="black",
                                 corner_radius=0)
        container.pack(pady=(0, 15), padx=40, fill="x")
        ctk.CTkLabel(container, text=icon, font=("Arial", 20), text_color="black", fg_color="white", width=40).pack(
            side="left", padx=(10, 5))
        entry = ctk.CTkEntry(container, height=30, border_width=0, fg_color="white", text_color="black",
                             placeholder_text=placeholder, font=(self.ui_font, 12))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)
        return entry

    def create_password_field(self, parent, placeholder):
        container = ctk.CTkFrame(parent, height=50, fg_color="white", border_width=2, border_color="black",
                                 corner_radius=0)
        container.pack(pady=(0, 15), padx=40, fill="x")
        ctk.CTkLabel(container, text="🔒", font=("Arial", 18), text_color="black", fg_color="white", width=40).pack(
            side="left", padx=(10, 5))
        entry = ctk.CTkEntry(container, height=30, border_width=0, fg_color="white", text_color="black",
                             placeholder_text=placeholder, font=(self.ui_font, 12), show="*")
        entry.pack(side="left", fill="x", expand=True, pady=5)
        eye_btn = ctk.CTkButton(container, text="👁", width=40, fg_color="white", text_color="black", hover_color="#EEE",
                                font=("Arial", 16), command=lambda: self.toggle_password(entry, eye_btn))
        eye_btn.pack(side="right", padx=(5, 10), pady=5)
        return entry, eye_btn

    def toggle_password(self, entry, btn):
        if entry.cget('show') == '*':
            entry.configure(show='')
            btn.configure(text="🚫")
        else:
            entry.configure(show='*')
            btn.configure(text="👁")

    # --- UPGRADED LOGIN LOGIC ---
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

            # --- THE BULLETPROOF IMPORTS FIX ---
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

    # ==========================================
    # CONFIRM EXIT SA LOGIN SCREEN
    # ==========================================
    def confirm_exit(self):
        # Maglalabas 'to ng popup na may Yes or No
        response = messagebox.askyesno(
            "Exit Application",
            "Are you sure you want to close the BICRS system?"
        )

        # Kung nag-Yes siya, patayin ang window. Kung No, walang mangyayari.
        if response:
            print("System shutting down gracefully...")
            self.root.destroy()
