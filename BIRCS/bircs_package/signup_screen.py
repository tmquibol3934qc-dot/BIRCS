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
        self.window.title("BIRCS - Create Account")

        w, h = 1000, 700
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        if self.is_admin_mode:
            self.window.transient(self.parent_root)
            self.window.grab_set()

        self.color_orange = "#E79124"
        self.color_gray_btn = "#666666"
        self.color_red = "#E74C3C"
        self.color_green = "#27AE60"
        self.text_dark = "#2C3E50"

        self.ui_font = "Poppins"
        self.header_font = "Young Serif"

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_images()

        # --- MAIN LAYOUT ---
        self.bg_label = ctk.CTkLabel(self.window, text="", image=self.bg_image)
        self.bg_label.pack(fill="both", expand=True)

        self.card = ctk.CTkScrollableFrame(self.bg_label, width=550, height=600,
                                           fg_color="white", corner_radius=15)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.back_btn = ctk.CTkButton(self.card, text="✕", width=30, fg_color="transparent",
                                      text_color="gray", font=("Arial", 18, "bold"),
                                      hover_color="#F0F0F0", command=self.handle_back)
        self.back_btn.pack(anchor="nw", pady=(10, 0), padx=10)

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
            overlay = Image.new("RGBA", raw_img.size, (255, 255, 255, 180))
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

        if len(new_val) > limit:
            new_val = new_val[:limit]

        if val != new_val:
            entry.delete(0, "end")
            entry.insert(0, new_val)

    # =========================================================================
    # STEP 1: PERSONAL INFORMATION
    # =========================================================================
    def build_step_1(self):
        title_frame = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="CREATE ACCOUNT", font=(self.header_font, 26, "bold"),
                     text_color=self.color_orange).pack()
        ctk.CTkLabel(title_frame, text="Step 1 of 2: Personal Details", font=(self.ui_font, 12),
                     text_color="gray").pack()

        grid_frame = ctk.CTkFrame(self.step1_frame, fg_color="white")
        grid_frame.pack(padx=20, fill="x")

        self.fname_entry = self.create_box(grid_frame, "First Name", 0, 0, limit=50, no_num=True)
        self.mname_entry = self.create_box(grid_frame, "Middle Name", 0, 1, limit=50, no_num=True)
        self.lname_entry = self.create_box(grid_frame, "Last Name", 1, 0, limit=50, no_num=True)
        self.contact_entry = self.create_box(grid_frame, "Contact No. (11 digits)", 1, 1, limit=11, num_only=True)
        self.pos_entry = self.create_box(grid_frame, "Position", 2, 0, limit=50)
        self.emp_id_entry = self.create_box(grid_frame, "Employee ID (Nums Only)", 2, 1, limit=20, num_only=True)

        self.addr_entry = self.create_full_width_box(self.step1_frame, "Address (Unit No. /Subdivision/Purok)",
                                                     limit=100)

        # 🚀 POGI UPDATE: Nilagyan natin ng "(Optional)" para malinaw sa user!
        ctk.CTkLabel(self.step1_frame, text="Tap RFID Card Here (Optional):", font=(self.ui_font, 12, "bold"),
                     text_color="gray").pack(pady=(10, 0), anchor="w", padx=40)
        self.rfid_entry = self.create_full_width_box(self.step1_frame, "Click box & Tap Card (Leave blank if none)...",
                                                     limit=30)

        self.pass_entry = self.create_full_width_box(self.step1_frame, "Create Password", is_pass=True, limit=50)

        self.criteria_frame = ctk.CTkFrame(self.step1_frame, fg_color="white")
        self.criteria_frame.pack(pady=(0, 10))
        self.lbl_len = self.create_criteria_label(self.criteria_frame, "• 8+ Chars", 0, 0)
        self.lbl_upper = self.create_criteria_label(self.criteria_frame, "• Uppercase", 0, 1)
        self.lbl_lower = self.create_criteria_label(self.criteria_frame, "• Lowercase", 0, 2)
        self.lbl_num = self.create_criteria_label(self.criteria_frame, "• Number", 1, 0)
        self.lbl_spec = self.create_criteria_label(self.criteria_frame, "• Special Char", 1, 1)
        self.pass_entry.bind("<KeyRelease>", self.check_password_strength)

        self.c_pass_entry = self.create_full_width_box(self.step1_frame, "Confirm Password", is_pass=True, limit=50)

        self.create_upload_box(self.step1_frame)

        next_btn = ctk.CTkButton(self.step1_frame, text="NEXT STEP ➡", width=250, height=45, corner_radius=8,
                                 fg_color=self.color_orange, hover_color="#C67B1D",
                                 font=(self.ui_font, 14, "bold"), command=self.go_to_step_2)
        next_btn.pack(pady=(20, 40))

    def create_box(self, parent, placeholder, r, c, limit=50, num_only=False, no_num=False):
        container = ctk.CTkFrame(parent, height=45, fg_color="#F8F9FA", border_width=1, border_color="#E0E0E0",
                                 corner_radius=8)
        container.grid(row=r, column=c, padx=5, pady=8, sticky="nsew")
        container.pack_propagate(False)

        entry = ctk.CTkEntry(container, border_width=0, fg_color="transparent", text_color="black",
                             placeholder_text=placeholder, placeholder_text_color="gray", font=(self.ui_font, 12))
        entry.pack(fill="both", expand=True, padx=10, pady=5)
        entry.bind("<KeyRelease>", lambda e: self.limit_input(entry, limit, num_only, no_num))
        return entry

    def create_full_width_box(self, parent, placeholder, is_pass=False, limit=50):
        container = ctk.CTkFrame(parent, height=45, width=440, fg_color="#F8F9FA", border_width=1,
                                 border_color="#E0E0E0", corner_radius=8)
        container.pack(pady=8, padx=40)
        container.pack_propagate(False)

        entry = ctk.CTkEntry(container, border_width=0, fg_color="transparent", text_color="black",
                             placeholder_text=placeholder, placeholder_text_color="gray", font=(self.ui_font, 12))
        if is_pass: entry.configure(show="*")
        entry.pack(fill="both", expand=True, padx=10, pady=5)
        entry.bind("<KeyRelease>", lambda e: self.limit_input(entry, limit, False, False))
        return entry

    def create_upload_box(self, parent):
        self.upload_btn = ctk.CTkButton(parent, text="📸 Upload Profile Picture (JPG/PNG)",
                                        width=440, height=50, fg_color="transparent", corner_radius=8,
                                        border_width=1, border_color="#D0D0D0", text_color="gray",
                                        font=(self.ui_font, 12), hover_color="#F0F0F0",
                                        command=self.select_file)
        self.upload_btn.pack(pady=10, padx=40)
        self.selected_file_path = None

    def create_criteria_label(self, parent, text, r, c):
        lbl = ctk.CTkLabel(parent, text=text, font=(self.ui_font, 11), text_color=self.color_red)
        lbl.grid(row=r, column=c, padx=10, sticky="w")
        return lbl

    # =========================================================================
    # STEP 2 CAROUSEL (SLIDER)
    # =========================================================================
    def build_step_2(self):
        title_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="SECURITY SETUP", font=(self.header_font, 26, "bold"),
                     text_color=self.color_orange).pack()
        ctk.CTkLabel(title_frame, text="Step 2 of 2: Security Questions", font=(self.ui_font, 12),
                     text_color="gray").pack()

        self.q_list = ["What is your mother's maiden name?", "What was the name of your first pet?",
                       "What city were you born in?", "What is your favorite food?",
                       "What is the name of your elementary school?"]

        self.carousel_container = ctk.CTkFrame(self.step2_frame, width=440, height=180, fg_color="transparent")
        self.carousel_container.pack(pady=20, padx=40)
        self.carousel_container.pack_propagate(False)

        self.q1_frame = ctk.CTkFrame(self.carousel_container, fg_color="transparent", width=440, height=180)
        self.q2_frame = ctk.CTkFrame(self.carousel_container, fg_color="transparent", width=440, height=180)
        self.q3_frame = ctk.CTkFrame(self.carousel_container, fg_color="transparent", width=440, height=180)

        self.frames = [self.q1_frame, self.q2_frame, self.q3_frame]
        self.current_q_index = 0

        self.q1_var, self.q1_menu, self.ans1_entry = self.create_security_group(self.q1_frame, "Question 1",
                                                                                self.q_list[0])
        self.q2_var, self.q2_menu, self.ans2_entry = self.create_security_group(self.q2_frame, "Question 2",
                                                                                self.q_list[1])
        self.q3_var, self.q3_menu, self.ans3_entry = self.create_security_group(self.q3_frame, "Question 3",
                                                                                self.q_list[2])

        self.q1_frame.place(x=0, y=0)
        self.update_security_dropdowns()

        self.controls_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=60, pady=10)

        self.btn_prev_q = ctk.CTkButton(self.controls_frame, text="◀ Back", width=80, fg_color="transparent",
                                        text_color=self.color_orange, font=("Arial", 14, "bold"), hover_color="#F0F0F0",
                                        command=self.slide_prev)
        self.btn_prev_q.pack(side="left")

        self.dots_label = ctk.CTkLabel(self.controls_frame, text="● ○ ○", font=("Arial", 20),
                                       text_color=self.color_orange)
        self.dots_label.pack(side="left", expand=True)

        self.btn_next_q = ctk.CTkButton(self.controls_frame, text="Next ▶", width=80, fg_color="transparent",
                                        text_color=self.color_orange, font=("Arial", 14, "bold"), hover_color="#F0F0F0",
                                        command=self.slide_next)
        self.btn_next_q.pack(side="right")

        self.terms_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")

        self.terms_var = ctk.BooleanVar(value=False)
        self.terms_chk = ctk.CTkCheckBox(self.terms_frame, text="I accept the Terms of Agreement",
                                         variable=self.terms_var, text_color=self.text_dark,
                                         font=(self.ui_font, 12, "bold", "underline"),
                                         fg_color=self.color_orange, hover_color="#C67B1D",
                                         command=self.click_terms_checkbox)
        self.terms_chk.pack(pady=(10, 20))

        self.reg_btn = ctk.CTkButton(self.terms_frame, text="REGISTER NOW", width=250, height=45, corner_radius=8,
                                     fg_color=self.color_green, hover_color="#1E8449",
                                     font=(self.ui_font, 14, "bold"), command=self.handle_register)
        self.reg_btn.pack()

        self.update_carousel_ui()

    def create_security_group(self, parent, label_text, default_val):
        parent.pack_propagate(False)
        ctk.CTkLabel(parent, text=label_text, font=(self.ui_font, 14, "bold"), text_color=self.text_dark).pack(
            anchor="center", pady=(10, 10))

        var = ctk.StringVar(value=default_val)

        menu = ctk.CTkOptionMenu(parent, variable=var, values=self.q_list, fg_color="#F8F9FA", text_color="black",
                                 button_color="#E0E0E0", button_hover_color="#D0D0D0", font=(self.ui_font, 12),
                                 corner_radius=8, height=40,
                                 command=self.update_security_dropdowns)
        menu.pack(fill="x", padx=10, pady=(0, 15))

        ans_entry = ctk.CTkEntry(parent, height=45, border_width=1, border_color="#E0E0E0", corner_radius=8,
                                 fg_color="#F8F9FA", text_color="black", font=(self.ui_font, 12),
                                 placeholder_text="Enter your answer...")
        ans_entry.pack(fill="x", padx=10)
        ans_entry.bind("<KeyRelease>", lambda e: self.limit_input(ans_entry, 100, False, False))

        return var, menu, ans_entry

    def update_security_dropdowns(self, *args):
        s1, s2, s3 = self.q1_var.get(), self.q2_var.get(), self.q3_var.get()
        l1 = [q for q in self.q_list if q == s1 or (q != s2 and q != s3)]
        l2 = [q for q in self.q_list if q == s2 or (q != s1 and q != s3)]
        l3 = [q for q in self.q_list if q == s3 or (q != s1 and q != s2)]
        self.q1_menu.configure(values=l1);
        self.q2_menu.configure(values=l2);
        self.q3_menu.configure(values=l3)

    def slide_next(self):
        if self.current_q_index < 2:
            entries = [self.ans1_entry, self.ans2_entry, self.ans3_entry]
            if not entries[self.current_q_index].get().strip():
                messagebox.showwarning("Warning", "Please answer the current question first.")
                return

            self.animate_slide(self.frames[self.current_q_index], self.frames[self.current_q_index + 1], "left")
            self.current_q_index += 1
            self.update_carousel_ui()

    def slide_prev(self):
        if self.current_q_index > 0:
            self.animate_slide(self.frames[self.current_q_index], self.frames[self.current_q_index - 1], "right")
            self.current_q_index -= 1
            self.update_carousel_ui()

    def animate_slide(self, frame_out, frame_in, direction):
        width = 440
        speed = 40
        steps = width // speed

        start_x_in = width if direction == "left" else -width
        end_x_out = -width if direction == "left" else width

        frame_in.place(x=start_x_in, y=0)
        frame_in.lift()

        def step(current_step):
            if current_step <= steps:
                progress = current_step / steps
                frame_out.place(x=int(end_x_out * progress), y=0)
                frame_in.place(x=int(start_x_in * (1 - progress)), y=0)
                self.window.after(10, step, current_step + 1)
            else:
                frame_out.place_forget()
                frame_in.place(x=0, y=0)

        step(1)

    def update_carousel_ui(self):
        dots = ["○", "○", "○"]
        dots[self.current_q_index] = "●"
        self.dots_label.configure(text=" ".join(dots))

        if self.current_q_index == 0:
            self.btn_prev_q.pack_forget()
        else:
            self.btn_prev_q.pack(side="left")

        if self.current_q_index == 2:
            self.btn_next_q.pack_forget()
            self.terms_frame.pack(fill="x", pady=20)
        else:
            self.btn_next_q.pack(side="right")
            self.terms_frame.pack_forget()

    # =========================================================================
    # OTHER LOGICS (Password, Image, Terms, Register)
    # =========================================================================
    def check_password_strength(self, event):
        pwd = self.pass_entry.get()
        self.lbl_len.configure(text_color=self.color_green if len(pwd) >= 8 else self.color_red)
        self.lbl_upper.configure(text_color=self.color_green if re.search(r"[A-Z]", pwd) else self.color_red)
        self.lbl_lower.configure(text_color=self.color_green if re.search(r"[a-z]", pwd) else self.color_red)
        self.lbl_num.configure(text_color=self.color_green if re.search(r"\d", pwd) else self.color_red)
        self.lbl_spec.configure(
            text_color=self.color_green if re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd) else self.color_red)

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
            self.upload_btn.configure(text=f"✅ Image Selected: {short_name}", text_color=self.color_green,
                                      border_color=self.color_green)

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
            messagebox.showerror("Missing Info", "Please fill in all required fields.")
            return
        if len(self.contact_entry.get()) != 11:
            messagebox.showerror("Invalid Contact", "Contact number must be EXACTLY 11 digits.")
            return
        if not self.emp_id_entry.get().isdigit():
            messagebox.showerror("Invalid ID", "Employee ID must contain numbers only.")
            return
        if not self.is_password_valid():
            messagebox.showerror("Weak Password", "Password does not meet the requirements.")
            return
        if self.pass_entry.get() != self.c_pass_entry.get():
            messagebox.showerror("Password Error", "Passwords do not match.")
            return

        if not self.selected_file_path:
            proceed = messagebox.askyesno("No Profile Picture",
                                          "You haven't uploaded a 1x1 profile picture.\nA default avatar will be used. Do you want to proceed?")
            if not proceed: return

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

        x = int((t_window.winfo_screenwidth() / 2) - (600 / 2))
        y = int((t_window.winfo_screenheight() / 2) - (600 / 2))
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
        ctk.CTkLabel(parent, text=title, font=(self.header_font, 12, "bold"), text_color=self.text_dark,
                     anchor="w").pack(fill="x", pady=(5, 0), padx=(20, 0))
        ctk.CTkLabel(parent, text=text, font=(self.ui_font, 12), text_color="#555", justify="left", wraplength=460,
                     anchor="w").pack(fill="x", padx=(20, 0))

    def accept_terms(self, modal):
        self.terms_var.set(True)
        modal.destroy()

    def handle_register(self):
        if not self.ans3_entry.get().strip():
            messagebox.showerror("Error", "Please answer the current question first.")
            return
        if not self.terms_var.get():
            messagebox.showerror("Error", "You must accept the Terms & Conditions.")
            return

        saved_image_path = self.process_and_save_image()

        rfid_input = self.rfid_entry.get().strip()
        rfid_val = rfid_input if rfid_input != "" else None

        try:
            # 🚀 POGI UPDATE: Isiningit na natin yung saved_image_path sa pinakadulo!
            result = self.engine.register_user(
                self.emp_id_entry.get().strip(),
                rfid_val,
                self.fname_entry.get().strip(),
                self.lname_entry.get().strip(),
                self.contact_entry.get().strip(),
                self.pass_entry.get().strip(),
                self.q1_var.get(),
                self.ans1_entry.get().strip(),
                self.q2_var.get(),
                self.ans2_entry.get().strip(),
                self.q3_var.get(),
                self.ans3_entry.get().strip(),
                self.pos_entry.get().strip(),
                saved_image_path  # <--- HETO YUNG NAWAWALA KANINA!
            )

            # Smart Unpacking para iwas crash
            if isinstance(result, tuple):
                success, message = result
            else:
                success = result
                message = "Account successfully registered!" if success else "Failed to register account."

            if success:
                messagebox.showinfo("Success", message)
                self.window.destroy()

                if self.is_admin_mode and self.on_refresh:
                    self.on_refresh()
                elif not self.is_admin_mode:
                    self.parent_root.deiconify()
            else:
                messagebox.showerror("Error", message)

        except TypeError as e:
            messagebox.showerror("Engine Parameter Error",
                                 f"Nakalimutan mo atang i-update ang engine.py!\n\nReason: {str(e)}\n\nSiguraduhin na may 'profile_pic' parameter sa dulo ng register_user function mo sa engine.py!")
        except Exception as e:
            messagebox.showerror("System Error", f"Registration crashed!\nReason: {str(e)}")

    def on_close(self):
        self.window.destroy()
        if not self.is_admin_mode:
            self.parent_root.deiconify()
