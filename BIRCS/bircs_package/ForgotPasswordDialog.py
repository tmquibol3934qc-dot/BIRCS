import customtkinter as ctk
from tkinter import messagebox
import re

class ForgotPasswordDialog:
    def __init__(self, root, engine):
        self.parent = root
        self.engine = engine

        self.window = ctk.CTkToplevel(root)
        self.window.title("BIRCS - Account Recovery")
        self.window.geometry("450x550")
        self.window.transient(root)
        self.window.grab_set()
        self.window.configure(fg_color="white")

        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = int((sw / 2) - (450 / 2))
        y = int((sh / 2) - (550 / 2))
        self.window.geometry(f"+{x}+{y}")

        self.color_orange = "#E79124"
        self.ui_font = "Poppins"

        ctk.CTkLabel(self.window, text="Account Recovery", font=("Young Serif", 22, "bold"),
                     text_color=self.color_orange).pack(pady=(30, 5))
        self.sub_header = ctk.CTkLabel(self.window, text="Step 1: Identify your account", font=(self.ui_font, 12),
                                       text_color="gray")
        self.sub_header.pack(pady=(0, 20))

        # --- STEP 1 ---
        self.step1_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.step1_frame.pack(fill="both", expand=True, padx=40)

        ctk.CTkLabel(self.step1_frame, text="Enter your Employee ID:", font=(self.ui_font, 12, "bold"),
                     text_color="black").pack(anchor="w", pady=(10, 5))
        self.emp_id_entry = ctk.CTkEntry(self.step1_frame, height=40, font=(self.ui_font, 14), border_color="black",
                                         border_width=1, corner_radius=0)
        self.emp_id_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(self.step1_frame, text="Find Account", fg_color=self.color_orange, hover_color="#C67B1D",
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=0, command=self.find_account).pack(fill="x")

        # --- STEP 2 ---
        self.step2_frame = ctk.CTkFrame(self.window, fg_color="transparent")

        self.q1_lbl = ctk.CTkLabel(self.step2_frame, text="Q1:", font=(self.ui_font, 11, "bold"), text_color="black", wraplength=350, justify="left")
        self.q1_lbl.pack(anchor="w", pady=(5, 0))
        self.a1_entry = ctk.CTkEntry(self.step2_frame, height=35, font=(self.ui_font, 12), border_color="gray", corner_radius=0)
        self.a1_entry.pack(fill="x", pady=(0, 10))

        self.q2_lbl = ctk.CTkLabel(self.step2_frame, text="Q2:", font=(self.ui_font, 11, "bold"), text_color="black", wraplength=350, justify="left")
        self.q2_lbl.pack(anchor="w", pady=(5, 0))
        self.a2_entry = ctk.CTkEntry(self.step2_frame, height=35, font=(self.ui_font, 12), border_color="gray", corner_radius=0)
        self.a2_entry.pack(fill="x", pady=(0, 10))

        self.q3_lbl = ctk.CTkLabel(self.step2_frame, text="Q3:", font=(self.ui_font, 11, "bold"), text_color="black", wraplength=350, justify="left")
        self.q3_lbl.pack(anchor="w", pady=(5, 0))
        self.a3_entry = ctk.CTkEntry(self.step2_frame, height=35, font=(self.ui_font, 12), border_color="gray", corner_radius=0)
        self.a3_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(self.step2_frame, text="Verify Answers", fg_color=self.color_orange, hover_color="#C67B1D",
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=0, command=self.verify_answers).pack(fill="x")

        # --- STEP 3 ---
        self.step3_frame = ctk.CTkFrame(self.window, fg_color="transparent")

        ctk.CTkLabel(self.step3_frame, text="Enter New Password:", font=(self.ui_font, 12, "bold"), text_color="black").pack(anchor="w", pady=(10, 5))
        self.new_pass_entry = ctk.CTkEntry(self.step3_frame, height=40, font=(self.ui_font, 14), show="*", border_color="black", border_width=1, corner_radius=0)
        self.new_pass_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.step3_frame, text="Confirm New Password:", font=(self.ui_font, 12, "bold"), text_color="black").pack(anchor="w", pady=(10, 5))
        self.conf_pass_entry = ctk.CTkEntry(self.step3_frame, height=40, font=(self.ui_font, 14), show="*", border_color="black", border_width=1, corner_radius=0)
        self.conf_pass_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(self.step3_frame, text="Submit Request", fg_color="#27AE60", hover_color="#1E8449",
                      font=(self.ui_font, 14, "bold"), height=45, corner_radius=0, command=self.save_new_password).pack(fill="x")

        ctk.CTkButton(self.window, text="Cancel", fg_color="transparent", text_color="gray", hover_color="#EEEEEE",
                      command=self.window.destroy).pack(side="bottom", pady=20)

    def find_account(self):
        self.target_id = self.emp_id_entry.get().strip()
        if not self.target_id:
            messagebox.showwarning("Error", "Please enter an Employee ID or Username.")
            return

        questions = self.engine.get_user_security_questions(self.target_id)

        if questions and questions.get('q1'):
            self.q1_lbl.configure(text=f"1. {questions['q1']}")
            self.q2_lbl.configure(text=f"2. {questions['q2']}")
            self.q3_lbl.configure(text=f"3. {questions['q3']}")

            self.step1_frame.pack_forget()
            self.sub_header.configure(text="Step 2: Answer your security questions")
            self.step2_frame.pack(fill="both", expand=True, padx=40)
        else:
            messagebox.showerror("Not Found", "We could not find an account with that ID, or security questions were never set up.")

    def verify_answers(self):
        a1 = self.a1_entry.get().strip()
        a2 = self.a2_entry.get().strip()
        a3 = self.a3_entry.get().strip()

        if not a1 or not a2 or not a3:
            messagebox.showwarning("Error", "Please answer all three questions.")
            return

        if self.engine.verify_security_answers(self.target_id, a1, a2, a3):
            self.step2_frame.pack_forget()
            self.sub_header.configure(text="Step 3: Create a new password")
            self.step3_frame.pack(fill="both", expand=True, padx=40)
        else:
            messagebox.showerror("Access Denied", "One or more answers are incorrect.")

    def save_new_password(self):
        pwd1 = self.new_pass_entry.get()
        pwd2 = self.conf_pass_entry.get()

        if len(pwd1) < 8:
            messagebox.showwarning("Weak Password", "Password must be at least 8 characters long.")
            return
        if not re.search(r"[A-Z]", pwd1):
            messagebox.showwarning("Weak Password", "Password must contain at least one uppercase letter.")
            return
        if not re.search(r"[0-9]", pwd1):
            messagebox.showwarning("Weak Password", "Password must contain at least one number.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd1):
            messagebox.showwarning("Weak Password", "Password must contain at least one special character.")
            return

        if pwd1 != pwd2:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        # 🚀 THE POGI UPDATE: Ginawa na nating Approval Request! Hindi muna nag-change.
        try:
            self.engine.log_security_event(
                user_id=self.target_id,
                action="PASSWORD RESET REQUEST",
                # Itatago natin yung password sa dulo gamit ang Ninja Tag [REQ_PWD:...]
                details=f"User with ID '{self.target_id}' is requesting to reset their password.\n\n[REQ_PWD:{pwd1}]"
            )
            messagebox.showinfo("Request Sent", "Your password reset request has been sent to Kapitan for approval!\n\nYou can continue logging in using your OLD password until it gets approved.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Logging Error", f"Failed to alert Kapitan:\n{e}")
