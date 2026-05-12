import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


class IncidentBlotterPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"  # Web Canvas Gray
        self.color_card = "#FFFFFF"  # Crisp White
        self.color_border = "#EAECEE"  # Subtle borders
        self.primary = "#27AE60"  # Emerald Green (For Save/Active)
        self.blue = "#3498DB"  # Clean Blue
        self.orange = "#E05D3A"  # Alert Orange
        self.red = "#E74C3C"  # Danger Red
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        # 🚀 THE FIX: Ginawa nating ScrollableFrame para hindi lumubog ang button!
        self.page_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True)

        self.build_ui()

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

    def build_ui(self):
        # 📌 1. HEADER SECTION
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="📝 New Incident Blotter", font=(self.ui_font, 26, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        # Auto-Generated Badge
        badge_frame = ctk.CTkFrame(header_frame, fg_color="#FDFCF6", border_width=1, border_color="#F5B7B1",
                                   corner_radius=8)
        badge_frame.pack(side="right")
        ctk.CTkLabel(badge_frame, text="Case ID: Auto-Generated", font=(self.ui_font, 12, "bold"),
                     text_color=self.red).pack(padx=15, pady=6)

        # 📌 2. TOP CARD: PARTIES INVOLVED
        ctk.CTkLabel(self.page_frame, text="Parties Involved", font=(self.ui_font, 13, "bold"),
                     text_color=self.text_muted).pack(anchor="w", padx=40, pady=(10, 5))

        top_card = ctk.CTkFrame(self.page_frame, fg_color=self.color_card, corner_radius=12, border_width=1,
                                border_color=self.color_border)
        top_card.pack(fill="x", padx=35, pady=(0, 15))

        r1_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r1_frame.pack(fill="x", padx=20, pady=(20, 5))
        self.comp_name = self.create_input_group(r1_frame, "Plaintiff Name", side="left", limit=50, no_num=True)
        self.resp_name = self.create_input_group(r1_frame, "Opposing Party Name", side="right", limit=50, no_num=True)

        r2_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r2_frame.pack(fill="x", padx=20, pady=5)
        self.comp_contact = self.create_input_group(r2_frame, "Plaintiff Contact No.", side="left", limit=11,
                                                    num_only=True)
        self.resp_contact = self.create_input_group(r2_frame, "Opposing Party Contact No.", side="right", limit=11,
                                                    num_only=True)

        r3_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r3_frame.pack(fill="x", padx=20, pady=5)
        self.comp_address = self.create_input_group(r3_frame, "Plaintiff Address", side="left", limit=100)
        self.resp_address = self.create_input_group(r3_frame, "Opposing Party Address", side="right", limit=100)

        # Checkbox Row
        r4_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r4_frame.pack(fill="x", padx=30, pady=(10, 20))

        self.unknown_resp_var = ctk.BooleanVar(value=False)
        self.chk_unknown = ctk.CTkCheckBox(r4_frame, text="Opposing Party's Contact & Address is Unknown",
                                           variable=self.unknown_resp_var, command=self.toggle_resp_info,
                                           fg_color=self.primary, hover_color="#1E8449", border_color=self.color_border,
                                           font=(self.ui_font, 12, "bold"), text_color=self.text_dark)
        self.chk_unknown.pack(side="right")

        # 📌 3. MIDDLE CARD: INCIDENT DETAILS
        ctk.CTkLabel(self.page_frame, text="Incident Details", font=(self.ui_font, 13, "bold"),
                     text_color=self.text_muted).pack(anchor="w", padx=40, pady=(10, 5))

        mid_card = ctk.CTkFrame(self.page_frame, fg_color=self.color_card, corner_radius=12, border_width=1,
                                border_color=self.color_border)
        mid_card.pack(fill="x", padx=35, pady=(0, 15))

        mid_inner = ctk.CTkFrame(mid_card, fg_color="transparent")
        mid_inner.pack(fill="x", padx=20, pady=20)

        now = datetime.now()

        # Date Input
        date_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        date_group.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(date_group, text="Date of Incident", font=(self.ui_font, 11, "bold"),
                     text_color=self.text_muted).pack(anchor="w")

        date_input_frame = ctk.CTkFrame(date_group, fg_color="transparent")
        date_input_frame.pack(fill="x", pady=(5, 0))
        self.date_entry = ctk.CTkEntry(date_input_frame, height=38, border_width=1, border_color=self.color_border,
                                       fg_color="#F8F9FA", text_color=self.text_dark, font=(self.ui_font, 12))
        self.date_entry.pack(side="left", fill="x", expand=True)
        self.date_entry.insert(0, now.strftime("%m/%d/%Y"))

        ctk.CTkButton(date_input_frame, text="📅", width=38, height=38, fg_color="#F8F9FA", hover_color="#EAECEE",
                      border_width=1, border_color=self.color_border, text_color="black", font=(self.ui_font, 14),
                      command=self.open_calendar_popup).pack(side="left", padx=(5, 0))

        # 🚀 THE MAGIC COMBOBOX: Dynamic Auto-Filter Category!
        cat_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        cat_group.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(cat_group, text="Category", font=(self.ui_font, 11, "bold"), text_color=self.text_muted).pack(
            anchor="w")

        self.default_categories = ["Theft", "Physical Assault", "Noise Complaint", "Property Damage", "Trespassing"]
        db_categories = self.engine.get_incident_categories()

        # Save the master list of categories
        self.combined_cats = list(dict.fromkeys(self.default_categories + db_categories))

        self.category_var = ctk.StringVar(value=self.combined_cats[0] if self.combined_cats else "")
        self.cat_combo = ctk.CTkComboBox(cat_group, variable=self.category_var, values=self.combined_cats, height=38,
                                         fg_color="#F8F9FA", border_color=self.color_border, text_color=self.text_dark,
                                         button_color=self.color_border, dropdown_hover_color="#D5D8DC",
                                         font=(self.ui_font, 12))
        self.cat_combo.pack(fill="x", pady=(5, 0))

        # 🚀 REAL-TIME TYPING LISTENER
        self.category_var.trace_add("write", self.filter_category_list)

        # Zone (Deep Navy Styling)
        zone_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        zone_group.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(zone_group, text="Zone", font=(self.ui_font, 11, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        self.zone_var = ctk.StringVar(value="Phase 3")
        self.zone_combo = ctk.CTkComboBox(zone_group, variable=self.zone_var, values=["Phase 3", "Phase 5"], height=38,
                                          fg_color=self.color_sidebar, border_color=self.color_sidebar,
                                          text_color="white",
                                          button_color="#2C3E50", dropdown_hover_color="#34495E",
                                          font=(self.ui_font, 12, "bold"))
        self.zone_combo.pack(fill="x", pady=(5, 0))

        # Priority Status
        status_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        status_group.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(status_group, text="Priority", font=(self.ui_font, 11, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        self.status_var = ctk.StringVar(value="Normal") # Default natin sa Normal
        ctk.CTkOptionMenu(status_group, variable=self.status_var, values=["Normal", "High Priority"], height=38,
                          fg_color=self.orange, button_color=self.orange, button_hover_color="#C64D2B",
                          text_color="white", font=(self.ui_font, 12, "bold")).pack(fill="x", pady=(5, 0))

        # 📌 4. BOTTOM SECTION: NARRATIVE
        bot_card = ctk.CTkFrame(self.page_frame, fg_color=self.color_card, corner_radius=12, border_width=1,
                                border_color=self.color_border)
        # 🚀 THE FIX: Tinanggal ang expand=True dito para di siya umagaw ng space!
        bot_card.pack(fill="x", padx=35, pady=(0, 20))

        ctk.CTkLabel(bot_card, text="Sworn Statement (Narrative)", font=(self.ui_font, 13, "bold"),
                     text_color=self.color_sidebar).pack(anchor="w", padx=25, pady=(20, 5))

        # 🚀 THE FIX: Binigyan ng fixed height na 150 at tinanggal ang expand=True!
        self.narrative_box = ctk.CTkTextbox(bot_card, height=150, fg_color="#F8F9FA", border_color=self.color_border,
                                            border_width=1, text_color=self.text_dark, font=(self.ui_font, 12))
        self.narrative_box.pack(fill="x", padx=25, pady=(0, 25))

        # 📌 5. SAVE BUTTON
        btn_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        # 🚀 Padding sa baba para hindi dumikit pag ini-scroll!
        btn_frame.pack(fill="x", padx=35, pady=(0, 40))

        ctk.CTkButton(btn_frame, text="💾 Save Official Record", fg_color=self.primary, hover_color="#1E8449",
                      corner_radius=8,
                      font=(self.ui_font, 14, "bold"), height=45, width=200, command=self.save_blotter_record).pack(
            side="right")

    # ==================================================
    # HELPER FUNCTIONS & LOGIC
    # ==================================================

    def filter_category_list(self, *args):
        typed_text = self.category_var.get().strip()
        if not typed_text:
            self.cat_combo.configure(values=self.combined_cats)
            return

        filtered_list = [c for c in self.combined_cats if typed_text.lower() in c.lower()]
        if filtered_list:
            self.cat_combo.configure(values=filtered_list)
        else:
            self.cat_combo.configure(values=self.combined_cats)

    def toggle_resp_info(self):
        if self.unknown_resp_var.get():
            self.resp_contact.delete(0, 'end')
            self.resp_contact.configure(state="disabled", fg_color="#EAECEE")
            self.resp_address.delete(0, 'end')
            self.resp_address.configure(state="disabled", fg_color="#EAECEE")
        else:
            self.resp_contact.configure(state="normal", fg_color="#F8F9FA")
            self.resp_address.configure(state="normal", fg_color="#F8F9FA")

    def create_input_group(self, parent, label_text, side, limit=50, num_only=False, no_num=False):
        group = ctk.CTkFrame(parent, fg_color="transparent")
        group.pack(side=side, fill="x", expand=True, padx=10)
        ctk.CTkLabel(group, text=label_text, font=(self.ui_font, 11, "bold"), text_color=self.text_muted).pack(
            anchor="w")

        entry = ctk.CTkEntry(group, height=38, border_width=1, border_color=self.color_border, fg_color="#F8F9FA",
                             text_color=self.text_dark, font=(self.ui_font, 12))
        entry.pack(fill="x", pady=(5, 0))

        entry.bind("<KeyRelease>", lambda e: self.limit_input(entry, limit, num_only, no_num))
        return entry

    def open_calendar_popup(self):
        try:
            from tkcalendar import Calendar
        except ImportError:
            messagebox.showerror("Missing Library", "Please open terminal and run:\npip install tkcalendar",
                                 parent=self.page_frame.winfo_toplevel())
            return

        top = ctk.CTkToplevel(self.page_frame.winfo_toplevel())
        top.title("Select Date")
        top.geometry("320x350")
        top.transient(self.page_frame.winfo_toplevel())
        top.grab_set()
        top.configure(fg_color=self.color_card)

        top.update_idletasks()
        x = int((top.winfo_screenwidth() / 2) - (320 / 2))
        y = int((top.winfo_screenheight() / 2) - (350 / 2))
        top.geometry(f"+{x}+{y}")

        cal = Calendar(top, selectmode='day', date_pattern='mm/dd/yyyy', showweeknumbers=False,
                       background=self.color_sidebar, foreground='white', bordercolor=self.color_border,
                       headersbackground=self.color_sidebar, headersforeground='white', selectbackground=self.primary)
        cal.pack(pady=20, padx=20, fill="both", expand=True)

        def set_date():
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, cal.get_date())
            top.destroy()

        ctk.CTkButton(top, text="✓ Confirm Date", command=set_date, height=38, corner_radius=8,
                      font=(self.ui_font, 12, "bold"),
                      fg_color=self.primary, hover_color="#1E8449").pack(pady=(0, 20), padx=20, fill="x")

    def save_blotter_record(self):
        top_level = self.page_frame.winfo_toplevel()

        comp = self.comp_name.get().strip()
        comp_cont = self.comp_contact.get().strip()
        comp_addr = self.comp_address.get().strip()

        resp = self.resp_name.get().strip()

        if self.unknown_resp_var.get():
            resp_cont = None
            resp_addr = None
        else:
            resp_cont = self.resp_contact.get().strip()
            resp_addr = self.resp_address.get().strip()

        date = self.date_entry.get().strip()
        zone = self.zone_var.get().strip()
        ui_status = self.status_var.get()
        category = self.category_var.get().strip()

        time_str = datetime.now().strftime("%I:%M %p")
        narrative = self.narrative_box.get('1.0', 'end-1c').strip()
        officer = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()

        if not comp or not resp or not narrative or not category:
            messagebox.showwarning("Missing Info", "Please fill in Plaintiff, Opposing Party, Category, and Narrative.",
                                   parent=top_level)
            return

        if comp_cont and len(comp_cont) != 11:
            messagebox.showwarning("Invalid Contact", "Plaintiff contact number must be exactly 11 digits.",
                                   parent=top_level)
            return

        if not self.unknown_resp_var.get() and resp_cont and len(resp_cont) != 11:
            messagebox.showwarning("Invalid Contact", "Opposing Party contact number must be exactly 11 digits.",
                                   parent=top_level)
            return

        db_status = "Pending" if ui_status == "Normal" else "Urgent"

        success, case_id_or_msg = self.engine.save_incident(
            comp, comp_cont, comp_addr,
            resp, resp_cont, resp_addr,
            date, time_str, zone, category, narrative, officer, db_status
        )

        if success:
            messagebox.showinfo("Success", f"Incident successfully filed!\n\nOfficial Case ID: {case_id_or_msg}",
                                parent=top_level)

            self.comp_name.delete(0, 'end')
            self.comp_contact.delete(0, 'end')
            self.comp_address.delete(0, 'end')

            self.resp_contact.configure(state="normal", fg_color="#F8F9FA")
            self.resp_address.configure(state="normal", fg_color="#F8F9FA")
            self.resp_name.delete(0, 'end')
            self.resp_contact.delete(0, 'end')
            self.resp_address.delete(0, 'end')
            self.unknown_resp_var.set(False)

            self.narrative_box.delete('1.0', 'end')

            self.zone_var.set("Phase 3")
            self.status_var.set("Normal")

            now = datetime.now()
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, now.strftime("%m/%d/%Y"))

            db_cats = self.engine.get_incident_categories()
            self.combined_cats = list(dict.fromkeys(self.default_categories + db_cats))
            self.cat_combo.configure(values=self.combined_cats)
        else:
            messagebox.showerror("Error", case_id_or_msg, parent=top_level)
