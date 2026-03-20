import customtkinter as ctk
from tkinter import messagebox
import random


class IncidentBlotterPage:
    def __init__(self, parent_frame, engine, user_data):
        self.engine = engine
        self.user = user_data

        # Colors (Matched to Dashboard)
        self.primary = "#E79124"
        self.orange = "#F2994A"
        self.green = "#27AE60"
        self.red = "#EB5757"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"

        self.page_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # --- 1. HEADER ---
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="New Incident Blotter", font=("Arial", 22, "bold"),
                     text_color=self.primary).pack(side="left")
        ctk.CTkLabel(header_frame, text="Case ID: (Auto-Generated)", font=("Arial", 14, "bold"),
                     text_color=self.red).pack(side="right")

        # --- 2. TOP SECTION ---
        top_card = ctk.CTkFrame(self.page_frame, fg_color="white", corner_radius=10)
        top_card.pack(fill="x", padx=30, pady=(0, 15))

        r1_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r1_frame.pack(fill="x", padx=20, pady=(20, 10))
        self.comp_name = self.create_input_group(r1_frame, "Complainant Name", side="left")
        self.resp_name = self.create_input_group(r1_frame, "Respondent Name", side="right")

        r2_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        r2_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.comp_contact = self.create_input_group(r2_frame, "Contact No.", side="left")
        self.resp_address = self.create_input_group(r2_frame, "Last Known Address", side="right")

        # --- 3. MIDDLE SECTION ---
        mid_card = ctk.CTkFrame(self.page_frame, fg_color="white", corner_radius=10)
        mid_card.pack(fill="x", padx=30, pady=(0, 15))

        mid_inner = ctk.CTkFrame(mid_card, fg_color="transparent")
        mid_inner.pack(fill="x", padx=20, pady=20)

        date_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        date_group.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(date_group, text="Date of Incident", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        self.date_entry = ctk.CTkEntry(date_group, height=35, border_color="#E0E0E0", fg_color="#F9F9F9",
                                       text_color="black")
        self.date_entry.pack(fill="x", pady=(5, 0))

        zone_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        zone_group.pack(side="left", fill="x", expand=True, padx=(10, 10))
        ctk.CTkLabel(zone_group, text="Zone", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(anchor="w")
        self.zone_entry = ctk.CTkEntry(zone_group, height=35, border_color="#E0E0E0", fg_color="#F9F9F9",
                                       text_color="black")
        self.zone_entry.pack(fill="x", pady=(5, 0))

        # --- NEW PRIORITY STATUS DROPDOWN ---
        status_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        status_group.pack(side="left", fill="x", expand=True, padx=(10, 10))
        ctk.CTkLabel(status_group, text="Priority", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")
        self.status_var = ctk.StringVar(value="Pending")
        ctk.CTkOptionMenu(status_group, variable=self.status_var, values=["Pending", "Urgent"],
                          height=35, fg_color=self.primary, button_color=self.primary, text_color="white").pack(
            fill="x", pady=(5, 0))

        time_group = ctk.CTkFrame(mid_inner, fg_color="transparent")
        time_group.pack(side="right", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(time_group, text="Exact Time", font=("Arial", 12, "bold"), text_color=self.text_muted).pack(
            anchor="w")

        time_controls = ctk.CTkFrame(time_group, fg_color="transparent")
        time_controls.pack(fill="x", pady=(5, 0))

        hours = [f"{i:02d}" for i in range(1, 13)]
        mins = [f"{i:02d}" for i in range(0, 60, 5)]

        self.hr_var = ctk.StringVar(value="01")
        self.min_var = ctk.StringVar(value="00")
        self.ampm_var = ctk.StringVar(value="AM")

        ctk.CTkOptionMenu(time_controls, variable=self.hr_var, values=hours, width=65, height=35, fg_color=self.primary,
                          button_color=self.primary).pack(side="left", padx=(0, 5))
        ctk.CTkOptionMenu(time_controls, variable=self.min_var, values=mins, width=65, height=35, fg_color=self.primary,
                          button_color=self.primary).pack(side="left", padx=(0, 5))
        ctk.CTkOptionMenu(time_controls, variable=self.ampm_var, values=["AM", "PM"], width=65, height=35,
                          fg_color=self.primary, button_color=self.primary).pack(side="left")

        # --- 4. BOTTOM SECTION ---
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
                      font=("Arial", 14, "bold"), height=45, width=150,
                      command=self.save_blotter_record).pack(side="right")

    def create_input_group(self, parent, label_text, side):
        group = ctk.CTkFrame(parent, fg_color="transparent")
        group.pack(side=side, fill="x", expand=True, padx=10)

        ctk.CTkLabel(group, text=label_text, font=("Arial", 12, "bold"), text_color=self.text_muted).pack(anchor="w")
        entry = ctk.CTkEntry(group, height=35, border_color="#E0E0E0", fg_color="#F9F9F9", text_color="black")
        entry.pack(fill="x", pady=(5, 0))
        return entry

    def save_blotter_record(self):
        # 1. Gather all data from the UI
        comp = self.comp_name.get()
        resp = self.resp_name.get()
        contact = self.comp_contact.get()
        address = self.resp_address.get()
        date = self.date_entry.get()
        zone = self.zone_entry.get()
        status = self.status_var.get()  # <--- PULLS THE PRIORITY STATUS

        time_str = f"{self.hr_var.get()}:{self.min_var.get()} {self.ampm_var.get()}"
        narrative = self.narrative_box.get('1.0', 'end-1c')

        officer = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}"
        case_no = f"2026-{random.randint(100, 999)}"

        # 2. Validation
        if not comp or not resp or not narrative.strip():
            messagebox.showwarning("Missing Info", "Please fill in Complainant, Respondent, and Narrative.")
            return

        # 3. Send to Database Engine (Passing status at the end)
        success, msg = self.engine.save_incident(
            case_no, comp, resp, contact, address, date, time_str, zone, narrative, officer, status
        )

        # 4. Result and Clear
        if success:
            messagebox.showinfo("Success", msg)
            self.comp_name.delete(0, 'end')
            self.resp_name.delete(0, 'end')
            self.comp_contact.delete(0, 'end')
            self.resp_address.delete(0, 'end')
            self.date_entry.delete(0, 'end')
            self.zone_entry.delete(0, 'end')
            self.narrative_box.delete('1.0', 'end')
            self.status_var.set("Pending")  # Resets dropdown
        else:
            messagebox.showerror("Error", msg)
