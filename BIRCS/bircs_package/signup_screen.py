import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import os
import re
import shutil


class SignupWindow:
    def __init__(self, parent_root, engine, is_admin_mode=False, on_refresh=None):
        self.parent_root = parent_root
        self.engine = engine
        self.is_admin_mode = is_admin_mode
        self.on_refresh = on_refresh

        # --- WINDOW SETUP ---
        self.window = ctk.CTkToplevel()
        self.window.overrideredirect(True)
        self.window.title("BICRS - Create Account")

        w, h = 950, 680
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        if self.is_admin_mode:
            self.window.transient(self.parent_root)
            self.window.grab_set()

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_card_bg = "#FDFCF6"  # Cream Background
        self.color_border = "#4A90E2"  # Thin blue outline
        self.color_accent = "#E05D3A"  # Orange Action Color
        self.color_dark_blue = "#1D2153"  # Navy Headers
        self.color_success = "#27AE60"
        self.color_inactive = "#D5D8DC"
        self.text_dark = "#2C3E50"

        self.ui_font = "Poppins"
        self.header_font = "Young Serif"

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_images()

        # --- FULL SCREEN BACKGROUND ---
        self.bg_label = ctk.CTkLabel(self.window, text="", image=self.bg_image)
        self.bg_label.pack(fill="both", expand=True)

        # --- MAIN FLOATING CARD ---
        self.main_card = ctk.CTkFrame(self.bg_label, width=600, height=620, fg_color=self.color_card_bg,
                                      corner_radius=12, border_width=1, border_color=self.color_border)
        self.main_card.place(relx=0.5, rely=0.5, anchor="center")
        self.main_card.pack_propagate(False)

        # CLOSE BUTTON
        self.back_btn = ctk.CTkButton(self.main_card, text="✕", width=30, fg_color="transparent",
                                      text_color="gray", font=("Arial", 16, "bold"),
                                      hover_color="#EAECEE", command=self.handle_back)
        self.back_btn.place(x=555, y=10)

        # --- FIXED STICKY HEADER (Hindi sumasama sa scroll) ---
        self.header_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(25, 5))

        self.title_lbl = ctk.CTkLabel(self.header_frame, text="Create an Account", font=(self.header_font, 26, "bold"),
                                      text_color=self.color_dark_blue)
        self.title_lbl.pack()
        self.subtitle_lbl = ctk.CTkLabel(self.header_frame, text="Step 1: Personal Details", font=(self.ui_font, 12),
                                         text_color="gray")
        self.subtitle_lbl.pack()

        # STEPPER DOTS
        self.stepper_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stepper_frame.pack(pady=(10, 5))
        self.dot1 = ctk.CTkFrame(self.stepper_frame, width=12, height=12, corner_radius=6, fg_color=self.color_accent)
        self.dot1.pack(side="left", padx=4)
        self.line1 = ctk.CTkFrame(self.stepper_frame, width=40, height=2, fg_color=self.color_inactive)
        self.line1.pack(side="left", padx=2)
        self.dot2 = ctk.CTkFrame(self.stepper_frame, width=12, height=12, corner_radius=6, fg_color=self.color_inactive)
        self.dot2.pack(side="left", padx=4)

        # --- SCROLLABLE CONTENT AREA ---
        self.scroll_container = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.step1_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.step2_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")

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
            overlay = Image.new("RGBA", raw_img.size, (255, 255, 255, 140))  # Pinakinang ng konti
            final_bg = Image.alpha_composite(raw_img, overlay)
            self.bg_image = ctk.CTkImage(light_image=final_bg, size=(1000, 700))
        except Exception:
            self.bg_image = None

    def limit_input(self, entry, limit, num_only, no_num):
        val = entry.get()
        new_val = val
        if num_only:
            new_val = "".join([c for c in val if c.isdigit()])
        elif no_num:
            new_val = "".join([c for c in val if not c.isdigit()])
        if len(new_val) > limit: new_val = new_val[:limit]
        if val != new_val:
            entry.delete(0, "end")
            entry.insert(0, new_val)

    def update_stepper(self, step):
        if step == 1:
            self.dot1.configure(fg_color=self.color_accent)
            self.line1.configure(fg_color=self.color_inactive)
            self.dot2.configure(fg_color=self.color_inactive)
            self.subtitle_lbl.configure(text="Step 1: Personal Details")
        elif step == 2:
            self.dot1.configure(fg_color=self.color_success)
            self.line1.configure(fg_color=self.color_success)
            self.dot2.configure(fg_color=self.color_accent)
            self.subtitle_lbl.configure(text="Step 2: Security & Verification")

    # =========================================================================
    # STEP 1: PERSONAL INFORMATION
    # =========================================================================
    def build_step_1(self):
        # 🚀 GRID LAYOUT PARA SA MGA PANGALAN
        grid_frame = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        grid_frame.pack(padx=20, fill="x", pady=(10, 0))
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        self.fname_entry = self.create_grid_box(grid_frame, "First Name", 0, 0, limit=50, no_num=True)
        self.mname_entry = self.create_grid_box(grid_frame, "Middle Name", 0, 1, limit=50, no_num=True)
        self.lname_entry = self.create_grid_box(grid_frame, "Last Name", 1, 0, limit=50, no_num=True)
        self.contact_entry = self.create_grid_box(grid_frame, "Contact No. (11 digits)", 1, 1, limit=11, num_only=True)
        self.pos_entry = self.create_grid_box(grid_frame, "Position", 2, 0, limit=50)
        self.emp_id_entry = self.create_grid_box(grid_frame, "Employee ID (Nums Only)", 2, 1, limit=20, num_only=True)

        # FULL WIDTH LAYOUTS
        self.addr_entry = self.create_full_width_box(self.step1_frame, "Address (Unit No. /Subdivision/Purok)",
                                                     limit=100)

        ctk.CTkLabel(self.step1_frame, text="Tap RFID Card Here (Optional):", font=(self.ui_font, 11, "bold"),
                     text_color=self.color_dark_blue).pack(pady=(10, 2), anchor="w", padx=30)
        self.rfid_entry = self.create_full_width_box(self.step1_frame, "Click box & Tap Card (Leave blank if none)...",
                                                     limit=30)

        ctk.CTkLabel(self.step1_frame, text="Account Security:", font=(self.ui_font, 11, "bold"),
                     text_color=self.color_dark_blue).pack(pady=(15, 2), anchor="w", padx=30)
        self.pass_entry = self.create_full_width_box(self.step1_frame, "Create Password", is_pass=True, limit=50)

        # Password Criteria (Clean Row)
        self.criteria_frame = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        self.criteria_frame.pack(pady=(0, 10), padx=30, fill="x")
        self.lbl_len = self.create_criteria_label(self.criteria_frame, "• 8+ Chars", 0, 0)
        self.lbl_upper = self.create_criteria_label(self.criteria_frame, "• Uppercase", 0, 1)
        self.lbl_lower = self.create_criteria_label(self.criteria_frame, "• Lowercase", 0, 2)
        self.lbl_num = self.create_criteria_label(self.criteria_frame, "• Number", 1, 0)
        self.lbl_spec = self.create_criteria_label(self.criteria_frame, "• Special Char", 1, 1)
        self.pass_entry.bind("<KeyRelease>", self.check_password_strength)

        self.c_pass_entry = self.create_full_width_box(self.step1_frame, "Confirm Password", is_pass=True, limit=50)

        self.create_upload_box(self.step1_frame)

        next_btn = ctk.CTkButton(self.step1_frame, text="Proceed to Security ➡", width=250, height=45, corner_radius=8,
                                 fg_color=self.color_accent, hover_color="#C0392B",
                                 font=(self.header_font, 14, "bold"), command=self.go_to_step_2)
        next_btn.pack(pady=(25, 30))

    def create_grid_box(self, parent, placeholder, r, c, limit=50, num_only=False, no_num=False):
        container = ctk.CTkFrame(parent, height=42, fg_color="#FFFFFF", border_width=1, border_color="#EAECEE",
                                 corner_radius=6)
        container.grid(row=r, column=c, padx=5, pady=8, sticky="nsew")
        container.grid_propagate(False)

        entry = ctk.CTkEntry(container, border_width=0, fg_color="transparent", text_color="black",
                             placeholder_text=placeholder, placeholder_text_color="#A6ACAF", font=(self.ui_font, 12))
        entry.pack(fill="both", expand=True, padx=10, pady=5)
        entry.bind("<KeyRelease>", lambda e: self.limit_input(entry, limit, num_only, no_num))
        return entry

    def create_full_width_box(self, parent, placeholder, is_pass=False, limit=50):
        container = ctk.CTkFrame(parent, height=42, fg_color="#FFFFFF", border_width=1, border_color="#EAECEE",
                                 corner_radius=6)
        container.pack(pady=5, fill="x", padx=30)
        container.pack_propagate(False)

        entry = ctk.CTkEntry(container, border_width=0, fg_color="transparent", text_color="black",
                             placeholder_text=placeholder, placeholder_text_color="#A6ACAF", font=(self.ui_font, 12))
        if is_pass: entry.configure(show="*")
        entry.pack(fill="both", expand=True, padx=10, pady=5)
        entry.bind("<KeyRelease>", lambda e: self.limit_input(entry, limit, False, False))
        return entry

    def create_upload_box(self, parent):
        self.upload_btn = ctk.CTkButton(parent, text="📸 Upload Profile Picture (Optional)",
                                        height=45, fg_color="transparent", corner_radius=8,
                                        border_width=1, border_color="#BDC3C7", text_color="#7F8C8D",
                                        font=(self.ui_font, 12, "bold"), hover_color="#F8F9FA",
                                        command=self.select_file)
        self.upload_btn.pack(fill="x", padx=30, pady=(15, 5))
        self.selected_file_path = None

    def create_criteria_label(self, parent, text, r, c):
        lbl = ctk.CTkLabel(parent, text=text, font=(self.ui_font, 11), text_color="#E74C3C")
        lbl.grid(row=r, column=c, padx=10, pady=2, sticky="w")
        return lbl

    # =========================================================================
    # STEP 2: SECURITY QUESTIONS (Vertical Flow)
    # =========================================================================
    def build_step_2(self):
        self.q_list = ["What is your mother's maiden name?", "What was the name of your first pet?",
                       "What city were you born in?", "What is your favorite food?",
                       "What is the name of your elementary school?"]

        # 🚀 FLATTENED CAROUSEL: Naka-stack na siya pataas para mukhang modern Web Form
        q_container = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        q_container.pack(fill="both", expand=True, padx=30, pady=(10, 0))

        self.q1_var, self.q1_menu, self.ans1_entry = self.create_security_card(q_container, "Security Question 1",
                                                                               self.q_list[0])
        self.q2_var, self.q2_menu, self.ans2_entry = self.create_security_card(q_container, "Security Question 2",
                                                                               self.q_list[1])
        self.q3_var, self.q3_menu, self.ans3_entry = self.create_security_card(q_container, "Security Question 3",
                                                                               self.q_list[2])

        self.update_security_dropdowns()

        self.terms_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        self.terms_frame.pack(fill="x", pady=(20, 10))

        self.terms_var = ctk.BooleanVar(value=False)
        self.terms_chk = ctk.CTkCheckBox(self.terms_frame, text="I accept the Terms of Agreement",
                                         variable=self.terms_var, text_color=self.text_dark,
                                         font=(self.ui_font, 12, "bold", "underline"),
                                         fg_color=self.color_success, hover_color="#1E8449",
                                         command=self.click_terms_checkbox)
        self.terms_chk.pack(pady=(10, 20))

        btn_group = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        btn_group.pack(pady=(0, 30))

        ctk.CTkButton(btn_group, text="◀ Back", width=120, height=45, corner_radius=8,
                      fg_color="#BDC3C7", hover_color="#A6ACAF", text_color="black",
                      font=(self.header_font, 14, "bold"), command=self.go_to_step_1).pack(side="left", padx=10)

        ctk.CTkButton(btn_group, text="REGISTER NOW", width=180, height=45, corner_radius=8,
                      fg_color=self.color_success, hover_color="#1E8449",
                      font=(self.header_font, 14, "bold"), command=self.handle_register).pack(side="left", padx=10)

    def create_security_card(self, parent, label_text, default_val):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#EAECEE", corner_radius=8)
        card.pack(fill="x", pady=8)

        ctk.CTkLabel(card, text=label_text, font=(self.ui_font, 12, "bold"), text_color=self.color_accent).pack(
            anchor="w", padx=15, pady=(10, 0))

        var = ctk.StringVar(value=default_val)
        menu = ctk.CTkOptionMenu(card, variable=var, values=self.q_list, fg_color="#FDFCF6", text_color="black",
                                 button_color="#EAECEE", button_hover_color="#D5D8DC", font=(self.ui_font, 12),
                                 corner_radius=6, height=35, command=self.update_security_dropdowns)
        menu.pack(fill="x", padx=15, pady=(5, 5))

        # Underlined text entry
        ans_entry = ctk.CTkEntry(card, height=30, border_width=0, fg_color="transparent", text_color="black",
                                 font=(self.ui_font, 12), placeholder_text="Enter your answer...")
        ans_entry.pack(fill="x", padx=15, pady=(0, 5))
        ctk.CTkFrame(card, height=1, fg_color="#E0E0E0").pack(fill="x", padx=15, pady=(0, 10))

        ans_entry.bind("<KeyRelease>", lambda e: self.limit_input(ans_entry, 100, False, False))

        return var, menu, ans_entry

    def update_security_dropdowns(self, *args):
        s1, s2, s3 = self.q1_var.get(), self.q2_var.get(), self.q3_var.get()
        l1 = [q for q in self.q_list if q == s1 or (q != s2 and q != s3)]
        l2 = [q for q in self.q_list if q == s2 or (q != s1 and q != s3)]
        l3 = [q for q in self.q_list if q == s3 or (q != s1 and q != s2)]
        self.q1_menu.configure(values=l1)
        self.q2_menu.configure(values=l2)
        self.q3_menu.configure(values=l3)

    # =========================================================================
    # OTHER LOGICS
    # =========================================================================
    def check_password_strength(self, event):
        pwd = self.pass_entry.get()
        self.lbl_len.configure(text_color=self.color_success if len(pwd) >= 8 else "#E74C3C")
        self.lbl_upper.configure(text_color=self.color_success if re.search(r"[A-Z]", pwd) else "#E74C3C")
        self.lbl_lower.configure(text_color=self.color_success if re.search(r"[a-z]", pwd) else "#E74C3C")
        self.lbl_num.configure(text_color=self.color_success if re.search(r"\d", pwd) else "#E74C3C")
        self.lbl_spec.configure(
            text_color=self.color_success if re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd) else "#E74C3C")

    def is_password_valid(self):
        pwd = self.pass_entry.get()
        return (len(pwd) >= 8 and re.search(r"[A-Z]", pwd) and re.search(r"[a-z]", pwd) and
                re.search(r"\d", pwd) and re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd))

    def select_file(self):
        filename = filedialog.askopenfilename(title="Select 1x1 Profile Picture",
                                              filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if filename:
            self.selected_file_path = filename
            short_name = os.path.basename(filename)
            self.upload_btn.configure(text=f"✅ Image Selected: {short_name[:15]}...", text_color=self.color_success,
                                      border_color=self.color_success)

    def process_and_save_image(self):
        if not self.selected_file_path: return None
        try:
            profile_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "profiles")
            if not os.path.exists(profile_dir): os.makedirs(profile_dir)
            new_filename = f"emp_{self.emp_id_entry.get()}{os.path.splitext(self.selected_file_path)[1]}"
            new_filepath = os.path.join(profile_dir, new_filename)
            shutil.copy2(self.selected_file_path, new_filepath)
            return new_filepath.replace("\\", "/")
        except Exception as e:
            print(f"Failed to process image: {e}")
            return None

    def handle_back(self):
        if self.current_step == 2:
            self.go_to_step_1()
        else:
            self.on_close()

    def go_to_step_2(self):
        if not self.fname_entry.get() or not self.lname_entry.get() or not self.pass_entry.get():
            messagebox.showerror("Missing Info", "Please fill in all required fields.", parent=self.window)
            return
        if len(self.contact_entry.get()) != 11:
            messagebox.showerror("Invalid Contact", "Contact number must be EXACTLY 11 digits.", parent=self.window)
            return
        if not self.emp_id_entry.get().isdigit():
            messagebox.showerror("Invalid ID", "Employee ID must contain numbers only.", parent=self.window)
            return
        if not self.is_password_valid():
            messagebox.showerror("Weak Password", "Password does not meet the requirements.", parent=self.window)
            return
        if self.pass_entry.get() != self.c_pass_entry.get():
            messagebox.showerror("Password Error", "Passwords do not match.", parent=self.window)
            return

        # Smooth Web Transition
        self.step1_frame.pack_forget()
        self.update_stepper(2)
        self.step2_frame.pack(fill="both", expand=True)
        self.current_step = 2
        self.scroll_container._parent_canvas.yview_moveto(0)

    def go_to_step_1(self):
        self.step2_frame.pack_forget()
        self.update_stepper(1)
        self.step1_frame.pack(fill="both", expand=True)
        self.current_step = 1
        self.scroll_container._parent_canvas.yview_moveto(0)

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
        t_window.configure(fg_color=self.color_card_bg)  # Iwas transparency crash!

        x = int((t_window.winfo_screenwidth() / 2) - (600 / 2))
        y = int((t_window.winfo_screenheight() / 2) - (600 / 2))
        t_window.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkFrame(t_window, fg_color=self.color_card_bg, border_width=2, border_color=self.color_border)
        main_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="TERMS & CONDITIONS", font=(self.header_font, 22, "bold"),
                     text_color=self.color_dark_blue).pack(pady=(20, 10))

        scroll_txt = ctk.CTkScrollableFrame(main_frame, width=520, height=400, fg_color="#FFFFFF", border_width=1,
                                            border_color="#EAECEE")
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

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)
        ctk.CTkButton(btn_frame, text="Close", fg_color="#BDC3C7", text_color="black", hover_color="#A6ACAF",
                      font=(self.ui_font, 12, "bold"), command=t_window.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="I Accept These Terms", fg_color=self.color_success,
                      font=(self.ui_font, 12, "bold"), hover_color="#1E8449",
                      command=lambda: self.accept_terms(t_window)).pack(side="left", padx=10)

    def add_term_section(self, parent, title, text):
        ctk.CTkLabel(parent, text=title, font=(self.ui_font, 14, "bold"), text_color=self.color_accent,
                     anchor="w").pack(fill="x", pady=(10, 2), padx=10)
        if text: ctk.CTkLabel(parent, text=text, font=(self.ui_font, 12), text_color="#555", justify="left",
                              wraplength=480, anchor="w").pack(fill="x", padx=10)

    def add_term_sub(self, parent, title, text):
        ctk.CTkLabel(parent, text=title, font=(self.ui_font, 12, "bold"), text_color=self.text_dark, anchor="w").pack(
            fill="x", pady=(10, 0), padx=(25, 0))
        ctk.CTkLabel(parent, text=text, font=(self.ui_font, 12), text_color="#555", justify="left", wraplength=460,
                     anchor="w").pack(fill="x", padx=(25, 0))

    def accept_terms(self, modal):
        self.terms_var.set(True)
        modal.destroy()

    def handle_register(self):
        if not self.ans1_entry.get().strip() or not self.ans2_entry.get().strip() or not self.ans3_entry.get().strip():
            messagebox.showerror("Error", "Please answer all three security questions.", parent=self.window)
            return
        if not self.terms_var.get():
            messagebox.showerror("Error", "You must accept the Terms & Conditions.", parent=self.window)
            return

        saved_image_path = self.process_and_save_image()
        rfid_input = self.rfid_entry.get().strip()
        rfid_val = rfid_input if rfid_input != "" else None

        try:
            result = self.engine.register_user(
                self.emp_id_entry.get().strip(), rfid_val, self.fname_entry.get().strip(),
                self.lname_entry.get().strip(), self.contact_entry.get().strip(),
                self.pass_entry.get().strip(), self.q1_var.get(), self.ans1_entry.get().strip(),
                self.q2_var.get(), self.ans2_entry.get().strip(), self.q3_var.get(),
                self.ans3_entry.get().strip(), self.pos_entry.get().strip(), saved_image_path
            )

            if isinstance(result, tuple):
                success, message = result
            else:
                success = result
                message = "Account successfully registered!" if success else "Failed to register account."

            if success:
                messagebox.showinfo("Success", message, parent=self.window)
                self.window.destroy()
                if self.is_admin_mode and self.on_refresh:
                    self.on_refresh()
                elif not self.is_admin_mode:
                    self.parent_root.deiconify()
            else:
                messagebox.showerror("Error", message, parent=self.window)

        except Exception as e:
            messagebox.showerror("System Error", f"Registration crashed!\nReason: {str(e)}", parent=self.window)

    def on_close(self):
        self.window.destroy()
        if not self.is_admin_mode:
            self.parent_root.deiconify()
