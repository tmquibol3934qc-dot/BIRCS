import customtkinter as ctk
from tkinter import messagebox
import re
import random
import string


class ForgotPasswordDialog:
    def __init__(self, root, engine):
        self.parent = root
        self.engine = engine

        self.window = ctk.CTkToplevel(root)
        self.window.title("BICRS - Account Recovery")
        self.window.geometry("450x620")  # Tinaasan ng konti para sa Stepper at Question Frames
        self.window.transient(root)
        self.window.grab_set()
        self.window.configure(fg_color="white")  # Binalik sa white na paborito mo

        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = int((sw / 2) - (450 / 2))
        y = int((sh / 2) - (620 / 2))
        self.window.geometry(f"+{x}+{y}")

        self.color_orange = "#E79124"
        self.color_dark_blue = "#1D2153"
        self.color_gray = "#E0E0E0"  # Para sa pending dots
        self.ui_font = "Poppins"

        ctk.CTkLabel(self.window, text="Account Recovery", font=("Young Serif", 22, "bold"),
                     text_color=self.color_orange).pack(pady=(30, 5))

        self.sub_header = ctk.CTkLabel(self.window, text="Step 1: Identify your account", font=(self.ui_font, 12),
                                       text_color="gray")
        self.sub_header.pack(pady=(0, 15))

        # 🚀 THE STEPPER (Progress Indicator)
        self.stepper_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.stepper_frame.pack(pady=(0, 20))

        # Step 1 Dot (Active initially)
        self.dot1 = ctk.CTkFrame(self.stepper_frame, width=12, height=12, corner_radius=6,
                                 fg_color=self.color_dark_blue)
        self.dot1.pack(side="left", padx=5)
        self.line1 = ctk.CTkFrame(self.stepper_frame, width=40, height=2, fg_color=self.color_gray)
        self.line1.pack(side="left")

        # Step 2 Dot
        self.dot2 = ctk.CTkFrame(self.stepper_frame, width=12, height=12, corner_radius=6, fg_color=self.color_gray)
        self.dot2.pack(side="left", padx=5)
        self.line2 = ctk.CTkFrame(self.stepper_frame, width=40, height=2, fg_color=self.color_gray)
        self.line2.pack(side="left")

        # Step 3 Dot
        self.dot3 = ctk.CTkFrame(self.stepper_frame, width=12, height=12, corner_radius=6, fg_color=self.color_gray)
        self.dot3.pack(side="left", padx=5)

        # MAIN CONTAINER PARA SA MGA STEPS
        self.container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40)

        # Build all steps beforehand
        self.build_step1()
        self.build_step2()
        self.build_step3()

        # Display Step 1 automatically
        self.step1_frame.pack(fill="both", expand=True)

    def update_stepper(self, step):
        """Transitions the dots seamlessly based on current step"""
        if step == 2:
            self.dot1.configure(fg_color=self.color_orange)  # Done
            self.line1.configure(fg_color=self.color_orange)  # Connected
            self.dot2.configure(fg_color=self.color_dark_blue)  # Active
            self.sub_header.configure(text="Step 2: Answer your security questions")
        elif step == 3:
            self.dot2.configure(fg_color=self.color_orange)  # Done
            self.line2.configure(fg_color=self.color_orange)  # Connected
            self.dot3.configure(fg_color=self.color_dark_blue)  # Active
            self.sub_header.configure(text="Step 3: Create a new password")

    # --- UI BUILDERS ---

    def build_step1(self):
        self.step1_frame = ctk.CTkFrame(self.container, fg_color="transparent")

        ctk.CTkLabel(self.step1_frame, text="Enter your Employee ID:", font=(self.ui_font, 12, "bold"),
                     text_color="black").pack(anchor="w", pady=(10, 5))
        self.emp_id_entry = ctk.CTkEntry(self.step1_frame, height=40, font=(self.ui_font, 14), border_color="black",
                                         border_width=1, corner_radius=0)
        self.emp_id_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(self.step1_frame, text="Find Account", fg_color=self.color_dark_blue, hover_color="#111438",
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=0, command=self.find_account).pack(
            fill="x")

    def build_step2(self):
        self.step2_frame = ctk.CTkFrame(self.container, fg_color="transparent")

        # 🚀 POGI UPDATE: Clean Individual Question Cards!
        def create_q_card(parent):
            card = ctk.CTkFrame(parent, fg_color="#F9F9F9", border_width=1, border_color="#E0E0E0", corner_radius=0)
            card.pack(fill="x", pady=(0, 12))

            lbl = ctk.CTkLabel(card, text="Q:", font=(self.ui_font, 11, "bold"), text_color="black", wraplength=330,
                               justify="left")
            lbl.pack(anchor="w", padx=10, pady=(8, 2))

            entry = ctk.CTkEntry(card, height=28, border_width=0, fg_color="#F9F9F9", text_color="black",
                                 font=(self.ui_font, 12))
            entry.pack(fill="x", padx=10, pady=(0, 5))

            # Sub-border para sa aesthetic underline
            ctk.CTkFrame(card, height=1, fg_color="#D0D0D0").pack(fill="x", padx=10, pady=(0, 5))
            return lbl, entry

        self.q1_lbl, self.a1_entry = create_q_card(self.step2_frame)
        self.q2_lbl, self.a2_entry = create_q_card(self.step2_frame)
        self.q3_lbl, self.a3_entry = create_q_card(self.step2_frame)

        ctk.CTkButton(self.step2_frame, text="Verify Answers", fg_color=self.color_dark_blue, hover_color="#111438",
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=0, command=self.verify_answers).pack(
            fill="x", pady=(5, 0))

    def build_step3(self):
        self.step3_frame = ctk.CTkFrame(self.container, fg_color="transparent")

        ctk.CTkLabel(self.step3_frame, text="Enter New Password:", font=(self.ui_font, 12, "bold"),
                     text_color="black").pack(anchor="w", pady=(10, 5))
        self.new_pass_entry = ctk.CTkEntry(self.step3_frame, height=40, font=(self.ui_font, 14), show="*",
                                           border_color="black", border_width=1, corner_radius=0)
        self.new_pass_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.step3_frame, text="Confirm New Password:", font=(self.ui_font, 12, "bold"),
                     text_color="black").pack(anchor="w", pady=(10, 5))
        self.conf_pass_entry = ctk.CTkEntry(self.step3_frame, height=40, font=(self.ui_font, 14), show="*",
                                            border_color="black", border_width=1, corner_radius=0)
        self.conf_pass_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(self.step3_frame, text="Submit Request", fg_color="#27AE60", hover_color="#1E8449",
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=0,
                      command=self.process_reset_request).pack(fill="x")

        ctk.CTkButton(self.window, text="Cancel", fg_color="transparent", text_color="gray", hover_color="#EEEEEE",
                      command=self.window.destroy).pack(side="bottom", pady=20)

    # --- LOGIC & TRANSITIONS ---

    def find_account(self):
        self.target_id = self.emp_id_entry.get().strip()
        if not self.target_id:
            # 🚀 BUG FIX: parent=self.window
            messagebox.showwarning("Input Required", "Please enter your Employee ID or Username.", parent=self.window)
            return

        is_pending = self.engine.check_if_pending_reset(self.target_id)
        if is_pending:
            messagebox.showerror("Request Pending",
                                 "You already have an active password reset request.\n\n"
                                 "If you have lost your Temporary Password, "
                                 "please contact Admin to approve your account.", parent=self.window)
            return

        questions = self.engine.get_user_security_questions(self.target_id)

        if questions and questions.get('q1'):
            self.q1_lbl.configure(text=f"1. {questions['q1']}")
            self.q2_lbl.configure(text=f"2. {questions['q2']}")
            self.q3_lbl.configure(text=f"3. {questions['q3']}")

            # 🚀 SNAP SWAP TRANSITION
            self.step1_frame.pack_forget()
            self.update_stepper(2)
            self.step2_frame.pack(fill="both", expand=True)
        else:
            messagebox.showerror("Account Not Found",
                                 "We could not find an account associated with that ID, "
                                 "or security questions were never configured.", parent=self.window)

    def verify_answers(self):
        a1 = self.a1_entry.get().strip()
        a2 = self.a2_entry.get().strip()
        a3 = self.a3_entry.get().strip()

        if not a1 or not a2 or not a3:
            messagebox.showwarning("Error", "Please answer all three questions.", parent=self.window)
            return

        if self.engine.verify_security_answers(self.target_id, a1, a2, a3):
            # 🚀 SNAP SWAP TRANSITION
            self.step2_frame.pack_forget()
            self.update_stepper(3)
            self.step3_frame.pack(fill="both", expand=True)
        else:
            messagebox.showerror("Access Denied", "One or more answers are incorrect.", parent=self.window)

    def process_reset_request(self):
        pwd1 = self.new_pass_entry.get()
        pwd2 = self.conf_pass_entry.get()

        if len(pwd1) < 8:
            messagebox.showwarning("Weak Password", "Password must be at least 8 characters long.", parent=self.window)
            return
        if not re.search(r"[A-Z]", pwd1):
            messagebox.showwarning("Weak Password", "Password must contain at least one uppercase letter.",
                                   parent=self.window)
            return
        if not re.search(r"[0-9]", pwd1):
            messagebox.showwarning("Weak Password", "Password must contain at least one number.", parent=self.window)
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd1):
            messagebox.showwarning("Weak Password", "Password must contain at least one special character.",
                                   parent=self.window)
            return
        if pwd1 != pwd2:
            messagebox.showerror("Error", "Passwords do not match!", parent=self.window)
            return

        chars = string.ascii_uppercase + string.digits
        temp_pass = "BCRS-" + ''.join(random.choice(chars) for _ in range(6))

        try:
            # 🚀 ENGINE FIX: Pinasa natin yung pwd1 (Ang requested new password!)
            db_save_success = self.engine.create_password_reset_request(self.target_id, temp_pass, pwd1)

            if db_save_success:
                self.engine.log_security_event(
                    user_id=self.target_id,
                    action="PASSWORD RESET REQUEST",
                    details=f"User '{self.target_id}' requested a reset."
                )
                self.show_mandatory_temp_pass(temp_pass)
            else:
                messagebox.showerror("Database Error", "Hindi na-save ang Temporary Password sa database.",
                                     parent=self.window)

        except Exception as e:
            messagebox.showerror("Error", f"System Error:\n{e}", parent=self.window)

    def show_mandatory_temp_pass(self, temp_pass):
        popup = ctk.CTkToplevel(self.window)
        popup.title("EMERGENCY ACCESS CODE")
        popup.geometry("400x380")

        # Walang transparent bugs dito!
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.configure(fg_color="white")

        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        x = int((sw / 2) - (400 / 2))
        y = int((sh / 2) - (380 / 2))
        popup.geometry(f"+{x}+{y}")

        # Border Frame
        card = ctk.CTkFrame(popup, fg_color="white", corner_radius=0, border_width=2, border_color=self.color_dark_blue)
        card.pack(fill="both", expand=True)

        ctk.CTkLabel(card, text="⚠️ REQUEST SENT", font=("Poppins", 18, "bold"), text_color="#C0392B").pack(
            pady=(30, 5))

        info_text = ("Your request is pending Admin approval.\n"
                     "You CANNOT request another one.\n\n"
                     "Use this Temporary Password to log in.\n"
                     "If you lose this, ikaw na mag-explain kay Kapitan.")

        ctk.CTkLabel(card, text=info_text, font=("Poppins", 12), text_color="black", justify="center").pack(pady=10)

        pass_frame = ctk.CTkFrame(card, fg_color="#F9F9F9", border_width=2, border_color=self.color_orange,
                                  corner_radius=0)
        pass_frame.pack(pady=15, padx=30, fill="x")

        ctk.CTkLabel(pass_frame, text=temp_pass, font=("Consolas", 24, "bold"), text_color=self.color_dark_blue).pack(
            pady=15)

        def copy_and_close():
            self.window.clipboard_clear()
            self.window.clipboard_append(temp_pass)
            self.window.update()
            # 🚀 FIX: parent=popup
            messagebox.showinfo("Copied!", "Temporary Password copied to clipboard. Do not lose it!", parent=popup)
            popup.destroy()
            self.window.destroy()

        ctk.CTkButton(card, text="📋 COPY & CLOSE", fg_color=self.color_orange, hover_color="#C67B1D",
                      font=("Poppins", 14, "bold"), height=45, corner_radius=0, command=copy_and_close).pack(
            pady=(10, 20), padx=40, fill="x")
