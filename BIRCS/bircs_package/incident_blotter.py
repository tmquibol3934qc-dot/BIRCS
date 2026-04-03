import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


class IncidentBlotterPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        # Colors
        self.primary = "#E79124"
        self.orange = "#F2994A"
        self.green = "#27AE60"
        self.red = "#EB5757"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"

        self.page_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True)

        self.build_ui()

    # =========================================================================
    # THE BOUNCER: Limit Character Input Logic
    # =========================================================================
    def limit_input(self, entry, limit, num_only, no_num):
        val = entry.get()
        new_val = val
        if num_only:
            new_val = "".join([c for c in val if c.isdigit()])
        elif no_num:
            new_val = "".join([c for c in val if not c.isdigit()])

        if len(new_val) > limit:
            new_val = new_val[:limit]

        # Kung may tinanggal ang bouncer (e.g. invalid char o sumobra sa limit)
        if val != new_val:
            entry.delete(0, "end")
            entry.insert(0, new_val)

    def build_ui(self):
        # --- 1. HEADER ---
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="New Incident Blotter", font=("Arial", 22, "bold"),
                     text_color=self.primary).pack(side="left")
        ctk.CTkLabel(header_frame, text="Case ID: (Auto-Generated on Save)", font=("Arial", 14, "bold"),
                     text_color=self.red).pack(side="right")

        # --- 2. TOP SECTION (Clean 3-Row Layout) ---
        top_card = ctk.CTkFrame(self.page_frame, fg_color="white", corner_radius=10)
        top_card.pack(fill="x", padx=30, pady=(0, 15))

        r1_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r1_frame.pack(fill="x", padx=20, pady=(20, 5))
        # THE FIX: Added constraints
        self.comp_name = self.create_input_group(r1_frame, "Complainant Name", side="left", limit=50, no_num=True)
        self.resp_name = self.create_input_group(r1_frame, "Respondent Name", side="right", limit=50, no_num=True)

        r2_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r2_frame.pack(fill="x", padx=20, pady=5)
        # THE FIX: Forced 11 numbers only
        self.comp_contact = self.create_input_group(r2_frame, "Complainant Contact No.", side="left", limit=11,
                                                    num_only=True)
        self.resp_contact = self.create_input_group(r2_frame, "Respondent Contact No.", side="right", limit=11,
                                                    num_only=True)

        r3_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r3_frame.pack(fill="x", padx=20, pady=(5, 20))
        # THE FIX: Limit to 100 characters for safety
        self.comp_address = self.create_input_group(r3_frame, "Complainant Address", side="left", limit=100)
        self.resp_address = self.create_input_group(r3_frame, "Respondent Address", side="right", limit=100)

        # --- 3. MIDDLE SECTION ---
        mid_card = ctk.CTkFrame(self.page_frame, fg_color="white", corner_radius=10)
        mid_card.pack(fill="x", padx=30, pady=(0, 15))

        mid_inner = ctk.CTkFrame(mid_card, fg_color="transparent")
        mid_inner.pack(fill="x", padx=20, pady=20)

        now = datetime.now()

        # 1. Date (Auto-filled)
        date_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        date_group.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(date_group, text="Date of Incident", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        date_input_frame = ctk.CTkFrame(date_group, fg_color="transparent")
        date_input_frame.pack(fill="x", pady=(5, 0))
        self.date_entry = ctk.CTkEntry(date_input_frame, height=35, border_color="#E0E0E0", fg_color="#F9F9F9",
                                       text_color="black")
        self.date_entry.pack(side="left", fill="x", expand=True)
        self.date_entry.insert(0, now.strftime("%m/%d/%Y"))

        ctk.CTkButton(date_input_frame, text="📅", width=35, height=35, fg_color=self.primary, hover_color="#C67B1D",
                      command=self.open_calendar_popup).pack(side="left", padx=(2, 0))

        # 2. Dynamic Category
        cat_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        cat_group.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(cat_group, text="Category", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")

        # Default list just in case DB returns empty
        self.default_categories = ["Theft", "Physical Assault", "Noise Complaint", "Property Damage", "Trespassing"]
        db_categories = self.engine.get_incident_categories()
        combined_cats = list(dict.fromkeys(self.default_categories + db_categories))  # Merge and remove duplicates!

        self.category_var = ctk.StringVar(value=combined_cats[0] if combined_cats else "")
        self.cat_combo = ctk.CTkComboBox(cat_group, variable=self.category_var, values=combined_cats, height=35,
                                         fg_color="#F9F9F9", border_color="#E0E0E0", text_color="black",
                                         button_color=self.primary, dropdown_hover_color=self.orange)
        self.cat_combo.pack(fill="x", pady=(5, 0))

        # 3. Zone
        zone_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        zone_group.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(zone_group, text="Zone", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(anchor="w")
        self.zone_entry = ctk.CTkEntry(zone_group, height=35, border_color="#E0E0E0", fg_color="#F9F9F9",
                                       text_color="black")
        self.zone_entry.pack(fill="x", pady=(5, 0))

        # 4. Priority Status
        # THE FIX: Pinalitan natin ng "Normal" ang text sa dropdown
        status_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        status_group.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(status_group, text="Priority", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        self.status_var = ctk.StringVar(value="Normal")
        ctk.CTkOptionMenu(status_group, variable=self.status_var, values=["Normal", "Urgent"], height=35,
                          fg_color=self.primary, button_color=self.primary, text_color="white").pack(fill="x",
                                                                                                     pady=(5, 0))

        # 5. Exact Time
        time_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        time_group.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(time_group, text="Exact Time", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        time_controls = ctk.CTkFrame(time_group, fg_color="transparent")
        time_controls.pack(fill="x", pady=(5, 0))

        curr_hr = now.strftime("%I")
        curr_min = f"{(now.minute // 5) * 5:02d}"
        curr_ampm = now.strftime("%p")

        self.hr_var = ctk.StringVar(value=curr_hr)
        self.min_var = ctk.StringVar(value=curr_min)
        self.ampm_var = ctk.StringVar(value=curr_ampm)

        ctk.CTkOptionMenu(time_controls, variable=self.hr_var, values=[f"{i:02d}" for i in range(1, 13)], width=55,
                          height=35, fg_color=self.primary, button_color=self.primary).pack(side="left", padx=(0, 2))
        ctk.CTkOptionMenu(time_controls, variable=self.min_var, values=[f"{i:02d}" for i in range(0, 60, 5)], width=55,
                          height=35, fg_color=self.primary, button_color=self.primary).pack(side="left", padx=(0, 2))
        ctk.CTkOptionMenu(time_controls, variable=self.ampm_var, values=["AM", "PM"], width=60, height=35,
                          fg_color=self.primary, button_color=self.primary).pack(side="left")

        # --- 4. BOTTOM SECTION (Narrative) ---
        bot_card = ctk.CTkFrame(self.page_frame, fg_color="white", corner_radius=10)
        bot_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        ctk.CTkLabel(bot_card, text="Narrative", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w", padx=20, pady=(20, 5))
        self.narrative_box = ctk.CTkTextbox(bot_card, fg_color="#F9F9F9", border_color="#E0E0E0", border_width=1,
                                            text_color="black")
        self.narrative_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # --- 5. SAVE BUTTON ---
        btn_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 30))

        ctk.CTkButton(btn_frame, text="Save Record", fg_color=self.green, hover_color="#219653",
                      font=("Arial", 14, "bold"), height=45, width=150, command=self.save_blotter_record).pack(
            side="right")

    # ==================================================
    # HELPER FUNCTIONS
    # ==================================================
    def create_input_group(self, parent, label_text, side, limit=50, num_only=False, no_num=False):
        group = ctk.CTkFrame(parent, fg_color="transparent")
        group.pack(side=side, fill="x", expand=True, padx=10)
        ctk.CTkLabel(group, text=label_text, font=("Arial", 12, "bold"), text_color=self.text_muted).pack(anchor="w")

        entry = ctk.CTkEntry(group, height=35, border_color="#E0E0E0", fg_color="#F9F9F9", text_color="black")
        entry.pack(fill="x", pady=(5, 0))

        # Ikabit natin ang bouncer tuwing may itatype!
        entry.bind("<KeyRelease>", lambda e: self.limit_input(entry, limit, num_only, no_num))

        return entry

    def open_calendar_popup(self):
        try:
            from tkcalendar import Calendar
        except ImportError:
            messagebox.showerror("Missing Library", "Please open terminal and run:\npip install tkcalendar")
            return

        top = ctk.CTkToplevel(self.page_frame)
        top.title("Select Date")
        top.geometry("300x320")
        top.transient(self.page_frame.winfo_toplevel())
        top.grab_set()

        x = self.page_frame.winfo_rootx() + (self.page_frame.winfo_width() // 2) - 150
        y = self.page_frame.winfo_rooty() + (self.page_frame.winfo_height() // 2) - 160
        top.geometry(f"+{x}+{y}")

        cal = Calendar(top, selectmode='day', date_pattern='mm/dd/yyyy', showweeknumbers=False)
        cal.pack(pady=20, padx=20, fill="both", expand=True)

        def set_date():
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, cal.get_date())
            top.destroy()

        ctk.CTkButton(top, text="Confirm Date", command=set_date, fg_color=self.green, hover_color="#219653").pack(
            pady=(0, 20))

    def save_blotter_record(self):
        comp = self.comp_name.get().strip()
        comp_cont = self.comp_contact.get().strip()
        comp_addr = self.comp_address.get().strip()

        resp = self.resp_name.get().strip()
        resp_cont = self.resp_contact.get().strip()
        resp_addr = self.resp_address.get().strip()

        date = self.date_entry.get().strip()
        zone = self.zone_entry.get().strip()
        ui_status = self.status_var.get()
        category = self.category_var.get().strip()

        time_str = f"{self.hr_var.get()}:{self.min_var.get()} {self.ampm_var.get()}"
        narrative = self.narrative_box.get('1.0', 'end-1c').strip()

        officer = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()

        # THE FIX: Validate empty fields
        if not comp or not resp or not narrative or not category:
            messagebox.showwarning("Missing Info", "Please fill in Complainant, Respondent, Category, and Narrative.")
            return

        # THE FIX: Validate EXACTLY 11 digits
        if comp_cont and len(comp_cont) != 11:
            messagebox.showwarning("Invalid Contact", "Complainant contact number must be exactly 11 digits.")
            return
        if resp_cont and len(resp_cont) != 11:
            messagebox.showwarning("Invalid Contact", "Respondent contact number must be exactly 11 digits.")
            return

        # THE FIX: UI Mapping (Save "Normal" as "Pending" in the Database)
        db_status = "Pending" if ui_status == "Normal" else ui_status

        success, case_id_or_msg = self.engine.save_incident(
            comp, comp_cont, comp_addr,
            resp, resp_cont, resp_addr,
            date, time_str, zone, category, narrative, officer, db_status
        )

        if success:
            messagebox.showinfo("Success", f"Incident successfully filed!\n\nOfficial Case ID: {case_id_or_msg}")

            self.comp_name.delete(0, 'end')
            self.comp_contact.delete(0, 'end')
            self.comp_address.delete(0, 'end')
            self.resp_name.delete(0, 'end')
            self.resp_contact.delete(0, 'end')
            self.resp_address.delete(0, 'end')
            self.narrative_box.delete('1.0', 'end')
            self.zone_entry.delete(0, 'end')
            self.status_var.set("Normal")  # Reset back to Normal

            now = datetime.now()
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, now.strftime("%m/%d/%Y"))
            self.hr_var.set(now.strftime("%I"))
            self.min_var.set(f"{(now.minute // 5) * 5:02d}")
            self.ampm_var.set(now.strftime("%p"))

            # THE FIX: Combine defaults and DB categories so it doesn't disappear
            db_cats = self.engine.get_incident_categories()
            new_list = list(dict.fromkeys(self.default_categories + db_cats))
            self.cat_combo.configure(values=new_list)
        else:
            messagebox.showerror("Error", case_id_or_msg)
