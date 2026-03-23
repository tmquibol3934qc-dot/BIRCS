import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import re


class SignupWindow:
    def __init__(self, parent_root, engine, is_admin_mode=False, on_refresh=None):
        self.parent_root = parent_root
        self.engine = engine
        self.is_admin_mode = is_admin_mode  # Tells the window WHO opened it
        self.on_refresh = on_refresh  # Tells the window how to refresh the Admin list

        # --- WINDOW SETUP ---
        self.window = ctk.CTkToplevel()
        self.window.overrideredirect(True)  # Frameless
        self.window.title("BIRCS - Create Account")

        w, h = 1000, 700
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        # If admin mode, make sure it stays on top of the dashboard!
        if self.is_admin_mode:
            self.window.transient(self.parent_root)
            self.window.grab_set()

        # Design Settings
        self.color_orange = "#E79124"
        self.color_gray_btn = "#666666"
        self.color_red = "#FF5555"
        self.color_green = "#6A9C4E"

        self.ui_font = "Poppins"
        self.header_font = "Young Serif"

        # Handle Closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load Images
        self.load_images()

        # --- MAIN LAYOUT ---
        self.create_top_bar()
        self.bg_label = ctk.CTkLabel(self.window, text="", image=self.bg_image)
        self.bg_label.pack(fill="both", expand=True)

        self.card = ctk.CTkScrollableFrame(self.bg_label, width=500, height=550,
                                           fg_color="white", corner_radius=10)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # --- INITIALIZE STEPS ---
        self.step1_frame = ctk.CTkFrame(self.card, fg_color="white")
        self.step2_frame = ctk.CTkFrame(self.card, fg_color="white")

        self.build_step_1()
        self.build_step_2()

        self.step1_frame.pack(fill="both", expand=True)
        self.current_step = 1

    def load_images(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        try:
            bg_path = os.path.join(current_path, "background.jpg")
            raw_img = Image.open(bg_path).convert("RGBA")
            raw_img = raw_img.resize((1000, 700))
            overlay = Image.new("RGBA", raw_img.size, (255, 255, 255, 200))
            final_bg = Image.alpha_composite(raw_img, overlay)
            self.bg_image = ctk.CTkImage(light_image=final_bg, size=(1000, 700))
        except Exception:
            self.bg_image = None

    def create_top_bar(self):
        top_bar = ctk.CTkFrame(self.window, height=60, fg_color=self.color_orange, corner_radius=0)
        top_bar.pack(side="top", fill="x")
        self.top_back_btn = ctk.CTkButton(top_bar, text="←", width=40, fg_color="transparent",
                                          font=("Arial", 20, "bold"), hover_color="#C67B1D",
                                          command=self.handle_back)
        self.top_back_btn.pack(side="left", padx=10)
        ctk.CTkLabel(top_bar, text="🏛 BIRCS", font=("Arial", 20, "bold"), text_color="white").pack(side="left", padx=10)

    # =========================================================================
    # STEP 1: PERSONAL INFORMATION & RFID
    # =========================================================================
    def build_step_1(self):
        title_frame = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 10))
        ctk.CTkLabel(title_frame, text="CREATE ACCOUNT", font=(self.header_font, 24, "bold"),
                     text_color=self.color_orange).pack()
        ctk.CTkLabel(title_frame, text="Step 1 of 2: Personal Details", font=(self.ui_font, 12),
                     text_color="gray").pack()

        grid_frame = ctk.CTkFrame(self.step1_frame, fg_color="white")
        grid_frame.pack(padx=20, fill="x")

        self.fname_entry = self.create_box(grid_frame, "First Name", 0, 0)
        self.mname_entry = self.create_box(grid_frame, "Middle Name", 0, 1)
        self.lname_entry = self.create_box(grid_frame, "Last Name", 1, 0)
        self.contact_entry = self.create_box(grid_frame, "Contact No. (11 digits)", 1, 1)
        self.pos_entry = self.create_box(grid_frame, "Position", 2, 0)
        self.emp_id_entry = self.create_box(grid_frame, "Employee ID (Nums Only)", 2, 1)

        self.addr_entry = self.create_full_width_box(self.step1_frame, "Address (Unit No. /Subdivision/Village/Purok)")

        # --- NEW: RFID FIELD ---
        ctk.CTkLabel(self.step1_frame, text="Tap RFID Card Here:", font=(self.ui_font, 12, "bold"),
                     text_color="gray").pack(pady=(10, 0))
        self.rfid_entry = self.create_full_width_box(self.step1_frame, "Click box & Tap Card...")

        # --- PASSWORD SECTION ---
        self.pass_entry = self.create_full_width_box(self.step1_frame, "Create Password", is_pass=True)
        self.criteria_frame = ctk.CTkFrame(self.step1_frame, fg_color="white")
        self.criteria_frame.pack(pady=(0, 10))
        self.lbl_upper = self.create_criteria_label(self.criteria_frame, "• Uppercase", 0, 0)
        self.lbl_lower = self.create_criteria_label(self.criteria_frame, "• Lowercase", 0, 1)
        self.lbl_num = self.create_criteria_label(self.criteria_frame, "• Number", 1, 0)
        self.lbl_spec = self.create_criteria_label(self.criteria_frame, "• Special Char", 1, 1)
        self.pass_entry.bind("<KeyRelease>", self.check_password_strength)

        self.c_pass_entry = self.create_full_width_box(self.step1_frame, "Confirm Password", is_pass=True)

        self.create_upload_box(self.step1_frame)

        next_btn = ctk.CTkButton(self.step1_frame, text="NEXT STEP ➡", width=200, height=45,
                                 fg_color=self.color_orange, hover_color="#C67B1D",
                                 font=(self.ui_font, 14, "bold"), command=self.go_to_step_2)
        next_btn.pack(pady=(20, 40))

    def create_criteria_label(self, parent, text, r, c):
        lbl = ctk.CTkLabel(parent, text=text, font=(self.ui_font, 10), text_color=self.color_red)
        lbl.grid(row=r, column=c, padx=10, sticky="w")
        return lbl

    def check_password_strength(self, event):
        pwd = self.pass_entry.get()
        if re.search(r"[A-Z]", pwd):
            self.lbl_upper.configure(text_color=self.color_green)
        else:
            self.lbl_upper.configure(text_color=self.color_red)
        if re.search(r"[a-z]", pwd):
            self.lbl_lower.configure(text_color=self.color_green)
        else:
            self.lbl_lower.configure(text_color=self.color_red)
        if re.search(r"\d", pwd):
            self.lbl_num.configure(text_color=self.color_green)
        else:
            self.lbl_num.configure(text_color=self.color_red)
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
            self.lbl_spec.configure(text_color=self.color_green)
        else:
            self.lbl_spec.configure(text_color=self.color_red)

    def is_password_valid(self):
        pwd = self.pass_entry.get()
        return (len(pwd) >= 8 and re.search(r"[A-Z]", pwd) and re.search(r"[a-z]", pwd) and
                re.search(r"\d", pwd) and re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd))

    # =========================================================================
    # STEP 2: SECURITY QUESTIONS & TERMS
    # =========================================================================
    def build_step_2(self):
        title_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 10))
        ctk.CTkLabel(title_frame, text="SECURITY & TERMS", font=(self.header_font, 24, "bold"),
                     text_color=self.color_orange).pack()
        ctk.CTkLabel(title_frame, text="Step 2 of 2: Finalize Account", font=(self.ui_font, 12),
                     text_color="gray").pack()

        content_frame = ctk.CTkFrame(self.step2_frame, fg_color="white")
        content_frame.pack(padx=30, fill="x", pady=10)

        q_list = ["What is your mother's maiden name?", "What was the name of your first pet?",
                  "What city were you born in?", "What is your favorite food?",
                  "What is the name of your elementary school?"]
        self.q1_var, self.ans1_entry = self.create_security_group(content_frame, "Question 1", q_list)
        self.q2_var, self.ans2_entry = self.create_security_group(content_frame, "Question 2", q_list)
        self.q3_var, self.ans3_entry = self.create_security_group(content_frame, "Question 3", q_list)

        self.terms_var = ctk.BooleanVar(value=False)
        self.terms_chk = ctk.CTkCheckBox(self.step2_frame, text="I accept the Terms of Agreement",
                                         variable=self.terms_var, text_color=self.color_orange,
                                         font=(self.ui_font, 12, "bold", "underline"),
                                         fg_color=self.color_orange, hover_color="#C67B1D",
                                         command=self.click_terms_checkbox)
        self.terms_chk.pack(pady=20, anchor="w", padx=40)

        reg_btn = ctk.CTkButton(self.step2_frame, text="REGISTER", width=200, height=45,
                                fg_color=self.color_orange, hover_color="#C67B1D",
                                font=(self.ui_font, 14, "bold"), command=self.handle_register)
        reg_btn.pack(pady=(0, 40))

    # --- HELPERS ---
    def create_box(self, parent, placeholder, r, c):
        entry = ctk.CTkEntry(parent, width=210, height=40, border_width=2, border_color="black",
                             fg_color="white", text_color="black", placeholder_text=placeholder,
                             font=(self.ui_font, 12), corner_radius=0)
        entry.grid(row=r, column=c, padx=5, pady=10)
        return entry

    def create_full_width_box(self, parent, placeholder, is_pass=False):
        entry = ctk.CTkEntry(parent, width=440, height=40, border_width=2, border_color="black",
                             fg_color="white", text_color="black", placeholder_text=placeholder,
                             font=(self.ui_font, 12), corner_radius=0)
        if is_pass: entry.configure(show="*")
        entry.pack(pady=10)
        return entry

    def create_upload_box(self, parent):
        self.upload_btn = ctk.CTkButton(parent, text="☁\nUpload your Barangay ID (PDF, JPG, jpg)",
                                        width=440, height=80, fg_color="transparent",
                                        border_width=2, border_color="black", text_color="gray",
                                        font=(self.ui_font, 12), hover_color="#F9F9F9",
                                        command=self.select_file)
        self.upload_btn.pack(pady=10)
        self.selected_file_path = None

    def create_security_group(self, parent, label_text, options):
        ctk.CTkLabel(parent, text=label_text, font=(self.ui_font, 12, "bold"), text_color="black").pack(anchor="w",
                                                                                                        pady=(10, 2))
        var = ctk.StringVar(value=options[0])
        wrapper = ctk.CTkFrame(parent, fg_color="white", border_width=2, border_color="black")
        wrapper.pack(fill="x", pady=(0, 5))
        menu = ctk.CTkOptionMenu(wrapper, variable=var, values=options, fg_color="white", text_color="black",
                                 button_color="white", button_hover_color="#EEE", dropdown_fg_color="white",
                                 dropdown_text_color="black",
                                 font=(self.ui_font, 12), corner_radius=0)
        menu.pack(fill="x", padx=2, pady=2)
        ctk.CTkLabel(parent, text="Answer", font=(self.ui_font, 11), text_color="gray").pack(anchor="w")
        ans_entry = ctk.CTkEntry(parent, height=35, border_width=1, border_color="gray",
                                 fg_color="#F9F9F9", text_color="black", font=(self.ui_font, 12))
        ans_entry.pack(fill="x", pady=(0, 10))
        return var, ans_entry

    def select_file(self):
        filename = filedialog.askopenfilename(title="Select ID",
                                              filetypes=[("Image Files", "*.jpg;*.jpg"), ("PDF", "*.pdf")])
        if filename:
            self.selected_file_path = filename
            short_name = os.path.basename(filename)
            self.upload_btn.configure(text=f"✅ Selected:\n{short_name}", text_color="green")

    # --- NAVIGATION & TERMS ---
    def handle_back(self):
        if self.current_step == 2:
            self.go_to_step_1()
        else:
            self.on_close()

    def go_to_step_2(self):
        if not self.fname_entry.get() or not self.lname_entry.get() or not self.pass_entry.get():
            messagebox.showerror("Missing Info", "Please fill in all required fields.")
            return
        contact = self.contact_entry.get()
        if not contact.isdigit() or len(contact) != 11:
            messagebox.showerror("Invalid Contact", "Contact number must be exactly 11 digits.")
            return
        emp_id = self.emp_id_entry.get()
        if not emp_id.isdigit():
            messagebox.showerror("Invalid ID", "Employee ID must contain numbers only.")
            return
        if any(char.isdigit() for char in self.fname_entry.get()) or any(
                char.isdigit() for char in self.lname_entry.get()):
            messagebox.showerror("Invalid Name", "Names cannot contain numbers.")
            return
        if not self.is_password_valid():
            messagebox.showerror("Weak Password", "Password does not meet the requirements.")
            return
        if self.pass_entry.get() != self.c_pass_entry.get():
            messagebox.showerror("Password Error", "Passwords do not match.")
            return
        self.step1_frame.pack_forget()
        self.step2_frame.pack(fill="both", expand=True)
        self.current_step = 2
        self.card._parent_canvas.yview_moveto(0)

    def go_to_step_1(self):
        self.step2_frame.pack_forget()
        self.step1_frame.pack(fill="both", expand=True)
        self.current_step = 1
        self.card._parent_canvas.yview_moveto(0)

    def click_terms_checkbox(self):
        if self.terms_var.get():
            self.terms_var.set(False)
            self.show_terms_modal()

    def show_terms_modal(self):
        t_window = ctk.CTkToplevel(self.window)
        t_window.overrideredirect(True)
        t_window.geometry("600x600")
        t_window.transient(self.window)
        t_window.grab_set()
        sw = t_window.winfo_screenwidth()
        sh = t_window.winfo_screenheight()
        x = int((sw / 2) - (600 / 2))
        y = int((sh / 2) - (600 / 2))
        t_window.geometry(f"+{x}+{y}")
        t_window.configure(fg_color="white")

        main_frame = ctk.CTkFrame(t_window, fg_color="white", border_width=2, border_color=self.color_orange)
        main_frame.pack(fill="both", expand=True)
        top_frame = ctk.CTkFrame(main_frame, fg_color="white")
        top_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(top_frame, text="TERMS & CONDITIONS", font=(self.header_font, 22, "bold"),
                     text_color=self.color_orange).pack(pady=10)
        scroll_txt = ctk.CTkScrollableFrame(main_frame, width=520, height=400, fg_color="white")
        scroll_txt.pack(pady=10)

        self.add_term_section(scroll_txt, "1. ACCEPTANCE OF TERMS",
                              "By accessing and using the Barangay Incident and Complaint System (BIRCS), authorized barangay personnel agree to comply with these Terms and Conditions governing the proper use and management of the system.")
        self.add_term_section(scroll_txt, "2. AUTHORIZED ACCESS", "")
        self.add_term_sub(scroll_txt, "2.1 System Access",
                          "Only authorized barangay officials and designated personnel are allowed to access and operate the BIRCS.")
        self.add_term_sub(scroll_txt, "2.2 Account Responsibility",
                          "Users are responsible for maintaining the confidentiality of their login credentials. Sharing of accounts is strictly prohibited.")
        self.add_term_sub(scroll_txt, "2.3 Unauthorized Use",
                          "Unauthorized access, misuse, or attempted manipulation of system data is strictly prohibited and subject to disciplinary action.")
        self.add_term_section(scroll_txt, "3. DATA ENTRY AND MANAGEMENT", "")
        self.add_term_sub(scroll_txt, "3.1 Accurate Data Recording",
                          "Personnel must ensure that all incident and complaint records entered into the system are accurate, complete, and truthful.")
        self.add_term_section(scroll_txt, "7. INCIDENT AND COMPLAINT HANDLING RESPONSIBILITY",
                              "By accessing and using the Barangay Incident and Complaint System (BIRCS), authorized barangay personnel agree to comply with these Terms and Conditions governing the proper use and management of the system.")
        self.add_term_section(scroll_txt, "8. SYSTEM MAINTENANCE AND UPDATES",
                              "The barangay administration reserves the right to update, maintain, or temporarily restrict system access for maintenance purposes.")
        self.add_term_section(scroll_txt, "9. VIOLATIONS AND SANCTIONS",
                              "Improper use of the system, data tampering, or breach of confidentiality may result in disciplinary action in accordance with barangay policies.")
        self.add_term_section(scroll_txt, "10. AMENDMENTS",
                              "These terms may be revised as necessary, and authorized users will be informed of updates.")

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)
        ctk.CTkButton(btn_frame, text="Close", fg_color=self.color_gray_btn, command=t_window.destroy).pack(side="left",
                                                                                                            padx=10)
        ctk.CTkButton(btn_frame, text="I Accept These Terms", fg_color=self.color_orange,
                      command=lambda: self.accept_terms(t_window)).pack(side="left", padx=10)

    def add_term_section(self, parent, title, text):
        ctk.CTkLabel(parent, text=title, font=(self.header_font, 14, "bold"), text_color=self.color_orange,
                     anchor="w").pack(fill="x", pady=(10, 2))
        if text: ctk.CTkLabel(parent, text=text, font=(self.ui_font, 12), text_color="#555", justify="left",
                              wraplength=480, anchor="w").pack(fill="x")

    def add_term_sub(self, parent, title, text):
        ctk.CTkLabel(parent, text=title, font=(self.header_font, 12, "bold"), text_color=self.color_orange,
                     anchor="w").pack(fill="x", pady=(5, 0), padx=(20, 0))
        ctk.CTkLabel(parent, text=text, font=(self.ui_font, 12), text_color="#555", justify="left", wraplength=460,
                     anchor="w").pack(fill="x", padx=(20, 0))

    def accept_terms(self, modal):
        self.terms_var.set(True)
        modal.destroy()

    def handle_register(self):
        if not self.ans1_entry.get() or not self.ans2_entry.get() or not self.ans3_entry.get():
            messagebox.showerror("Error", "Please answer all 3 security questions.")
            return
        if not self.terms_var.get():
            messagebox.showerror("Error", "You must accept the Terms & Conditions.")
            return

        data = {
            "name": f"{self.fname_entry.get()} {self.lname_entry.get()}",
            "emp_id": self.emp_id_entry.get(),
            "rfid": self.rfid_entry.get(),
            "position": self.pos_entry.get(),
            "pass": self.pass_entry.get(),
            "q1": self.q1_var.get(), "a1": self.ans1_entry.get(),
            "q2": self.q2_var.get(), "a2": self.ans2_entry.get(),
            "q3": self.q3_var.get(), "a3": self.ans3_entry.get()
        }

        success, message = self.engine.register_user(data)
        if success:
            messagebox.showinfo("Success", message)
            self.window.destroy()

            # THE FIX: If Admin opened it, refresh the list. If Login opened it, un-hide Login!
            if self.is_admin_mode and self.on_refresh:
                self.on_refresh()
            elif not self.is_admin_mode:
                self.parent_root.deiconify()
        else:
            messagebox.showerror("Error", message)

    def on_close(self):
        self.window.destroy()
        # THE FIX: Only un-hide the login screen if we ARE NOT in Admin Mode
        if not self.is_admin_mode:
            self.parent_root.deiconify()

    def on_close(self):
        self.window.destroy()
        self.login_root.deiconify()
