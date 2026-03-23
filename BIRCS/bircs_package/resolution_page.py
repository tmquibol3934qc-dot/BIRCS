import customtkinter as ctk
from tkinter import messagebox


class ResolutionPage:
    def __init__(self, parent_frame, engine, user_data):
        self.parent = parent_frame
        self.engine = engine
        self.user = user_data
        self.selected_case = None

        self.primary = "#27AE60"
        self.orange = "#E79124"
        self.red = "#E74C3C"
        self.text_dark = "#2B2B2B"

        self.setup_ui()
        self.load_pending_cases()

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- LEFT PANEL ---
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="white", width=300, corner_radius=10)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        self.left_panel.pack_propagate(False)

        ctk.CTkLabel(self.left_panel, text="My Pending Cases", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(pady=(15, 10))
        self.case_list_frame = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.case_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- RIGHT PANEL ---
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.form_header = ctk.CTkLabel(self.right_panel, text="Select a case from the left to resolve",
                                        font=("Arial", 18, "bold"), text_color="gray")
        self.form_header.pack(pady=30)

        self.details_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def load_pending_cases(self):
        for widget in self.case_list_frame.winfo_children():
            widget.destroy()

        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        role = self.user.get('role', 'Staff')

        my_incidents = self.engine.get_my_pending_cases(officer_name, role)
        self.pending_incidents = [inc for inc in my_incidents if inc.get('status') in ['Pending', 'Urgent']]

        self.pending_incidents.sort(key=lambda x: (
            0 if x.get('status') == 'Urgent' else 1,
            x.get('date_of_incident', ''),
            x.get('exact_time', '')
        ))

        if not self.pending_incidents:
            ctk.CTkLabel(self.case_list_frame, text="No pending cases\nassigned to you.", font=("Arial", 12, "italic"),
                         text_color="gray").pack(pady=40)
            return

        for case in self.pending_incidents:
            self.draw_case_card(case)

    def draw_case_card(self, case):
        case_no = case.get('case_no')
        status = case.get('status')
        comp = case.get('complainant_name', 'Unknown')

        border_col = self.red if status == 'Urgent' else self.primary

        card = ctk.CTkFrame(self.case_list_frame, fg_color="#F8F9FA", border_color=border_col, border_width=2,
                            corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=5)
        card.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5, 0))

        lbl_id = ctk.CTkLabel(header_frame, text=f"Case #{case_no}", font=("Arial", 12, "bold"),
                              text_color=self.text_dark)
        lbl_id.pack(side="left")
        lbl_id.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))

        lbl_stat = ctk.CTkLabel(header_frame, text=status, font=("Arial", 10, "bold"), text_color=border_col)
        lbl_stat.pack(side="right")
        lbl_stat.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))

        lbl_comp = ctk.CTkLabel(card, text=f"Comp: {comp}", font=("Arial", 11), text_color="gray")
        lbl_comp.pack(anchor="w", padx=10, pady=(0, 5))
        lbl_comp.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))

    def show_case_details(self, case):
        self.selected_case = case
        self.form_header.configure(text=f"Resolving Case #{case.get('case_no')}", text_color=self.primary)

        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # --- INCIDENT DETAILS (Restored to the neat, original grid!) ---
        info_frame = ctk.CTkFrame(self.details_frame, fg_color="#F8F9FA", corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(info_frame, text="Complainant:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w",
                                                                                       padx=10, pady=(10, 2))
        ctk.CTkLabel(info_frame, text=case.get('complainant_name', 'N/A'), font=("Arial", 11)).grid(row=0, column=1,
                                                                                                    sticky="w", padx=10,
                                                                                                    pady=(10, 2))

        ctk.CTkLabel(info_frame, text="Respondent:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w",
                                                                                      padx=10, pady=2)
        ctk.CTkLabel(info_frame, text=case.get('respondent_name', 'N/A'), font=("Arial", 11)).grid(row=1, column=1,
                                                                                                   sticky="w", padx=10,
                                                                                                   pady=2)

        ctk.CTkLabel(info_frame, text="Narrative:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="nw",
                                                                                     padx=10, pady=(5, 10))
        ctk.CTkLabel(info_frame, text=case.get('narrative', 'N/A'), font=("Arial", 11), wraplength=400,
                     justify="left").grid(row=2, column=1, sticky="w", padx=10, pady=(5, 10))

        # --- RESOLUTION FORM ---
        ctk.CTkLabel(self.details_frame, text="Resolution & Settlement Terms", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", pady=(10, 5))

        controls_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(controls_frame, text="Hearing Stage:", font=("Arial", 12)).pack(side="left")
        self.stage_var = ctk.StringVar(value="Barangay Conciliation")
        ctk.CTkOptionMenu(controls_frame, variable=self.stage_var,
                          values=["Barangay Conciliation", "Mediation", "Arbitration"], fg_color="white",
                          text_color="black").pack(side="left", padx=10)

        ctk.CTkLabel(controls_frame, text="Deadline (Days):", font=("Arial", 12)).pack(side="left", padx=(20, 0))
        self.deadline_input = ctk.CTkEntry(controls_frame, width=80)
        self.deadline_input.pack(side="left", padx=10)

        self.resolution_input = ctk.CTkTextbox(self.details_frame, height=120, fg_color="#FFFFFF", text_color="black",
                                               border_width=1, border_color="gray")
        self.resolution_input.pack(fill="x", pady=10)

        # --- AI SMART SUGGESTIONS AREA ---
        ctk.CTkLabel(self.details_frame, text="✨ AI Smart Suggestions (Click a card to apply)",
                     font=("Arial", 12, "bold"), text_color=self.primary).pack(anchor="w", pady=(15, 5))
        self.suggestion_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.suggestion_frame.pack(fill="x")

        # Silently fetches the category and passes it to the AI filter!
        category_name = case.get('category') or ""
        self.display_smart_suggestions(case.get('narrative', ''), case.get('zone', ''), category_name)

        submit_btn = ctk.CTkButton(self.details_frame, text="Mark Case as Resolved", font=("Arial", 14, "bold"),
                                   fg_color=self.primary, hover_color="#1E8449", height=45,
                                   command=self.submit_resolution)
        submit_btn.pack(pady=30)

    def display_smart_suggestions(self, narrative, zone, category):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()

        suggestions = self.engine.get_resolution_suggestion(narrative, zone, category)

        if not suggestions:
            # The fallback message when the AI finds nothing
            fallback_msg = f"There are no viable settlements recorded for this type of incident.\nPlease draft a custom settlement manually."
            ctk.CTkLabel(self.suggestion_frame, text=fallback_msg, font=("Arial", 12, "italic"),
                         text_color="gray").pack(pady=10)
            return

        for item in suggestions:
            # The whole card acts like a button now!
            card = ctk.CTkFrame(self.suggestion_frame, fg_color="#F0F8FF", border_color="#27AE60", border_width=1,
                                corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=5)

            header = ctk.CTkLabel(card, text=f"⚡ {item['match']}% Match", font=("Arial", 12, "bold"),
                                  text_color="#27AE60", cursor="hand2")
            header.pack(anchor="w", padx=10, pady=(5, 0))

            text_lbl = ctk.CTkLabel(card, text=item['text'], font=("Arial", 11), text_color="#2B2B2B", wraplength=450,
                                    justify="left", cursor="hand2")
            text_lbl.pack(anchor="w", padx=10, pady=(2, 10))

            # Bind the click to the card and its text
            def on_click(event, t=item['text']):
                self.insert_ai_suggestion(t)

            card.bind("<Button-1>", on_click)
            header.bind("<Button-1>", on_click)
            text_lbl.bind("<Button-1>", on_click)

    def insert_ai_suggestion(self, suggestion_text):
        """Clears the text box and pastes the AI suggestion"""
        self.resolution_input.delete("1.0", "end")
        self.resolution_input.insert("1.0", suggestion_text)

    def submit_resolution(self):
        if not self.selected_case:
            return

        settlement_text = self.resolution_input.get("1.0", "end-1c").strip()
        if not settlement_text:
            messagebox.showwarning("Missing Information", "Please enter the final settlement details.")
            return

        stage = self.stage_var.get()
        deadline = self.deadline_input.get().strip()
        case_id = self.selected_case.get('case_no')

        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        if not officer_name:
            officer_name = "Admin/Kapitan"

        try:
            success = self.engine.update_incident_resolution(case_id, settlement_text, stage, deadline, officer_name)

            if success:
                messagebox.showinfo("Success", f"Case #{case_id} has been officially resolved by {officer_name}!")
                self.selected_case = None
                for widget in self.details_frame.winfo_children():
                    widget.destroy()
                self.form_header.configure(text="Select a case from the left to resolve", text_color="gray")
                self.load_pending_cases()
            else:
                messagebox.showerror("Database Error", "Failed to update case. Check database connection.")
        except Exception as e:
            print(f"Save Error: {e}")
            messagebox.showwarning("Error", "Could not save resolution to database. Check terminal.")
