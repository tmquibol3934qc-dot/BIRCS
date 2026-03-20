import customtkinter as ctk
from tkinter import messagebox


class ResolutionPage:
    def __init__(self, parent_frame, engine, user_data):
        self.parent = parent_frame
        self.engine = engine
        self.user = user_data

        self.primary = "#E79124"
        self.green = "#27AE60"
        self.red = "#EB5757"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"

        self.main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=20)

        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.list_panel = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=10)
        self.list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.form_panel = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=10)
        self.form_panel.grid(row=0, column=1, sticky="nsew")

        self.selected_case = None

        self.setup_list_panel()
        self.setup_form_panel()
        self.load_pending_cases()

    def setup_list_panel(self):
        header_frame = ctk.CTkFrame(self.list_panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header_frame, text="Active Cases", font=("Arial", 18, "bold"), text_color=self.text_dark).pack(
            side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_cases)
        search_entry = ctk.CTkEntry(header_frame, textvariable=self.search_var, placeholder_text="Search ID or Zone...",
                                    width=140, height=30)
        search_entry.pack(side="right")

        self.cases_container = ctk.CTkScrollableFrame(self.list_panel, fg_color="transparent")
        self.cases_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def load_pending_cases(self):
        all_incidents = self.engine.get_all_incidents()
        self.pending_incidents = [inc for inc in all_incidents if inc.get('status') in ['Pending', 'Urgent']]

        # Sorting: Urgent (0) at the top, Pending (1) below
        self.pending_incidents.sort(key=lambda x: (
            0 if x.get('status') == 'Urgent' else 1,
            x.get('exact_date', ''),
            x.get('exact_time', '')
        ))

        self.draw_case_list(self.pending_incidents)

    def filter_cases(self, *args):
        query = self.search_var.get().lower()
        if not query:
            self.draw_case_list(self.pending_incidents)
            return

        filtered = []
        for case in self.pending_incidents:
            search_str = f"{case.get('case_no', '')} {case.get('zone', '')} {case.get('processed_by', '')}".lower()
            if query in search_str:
                filtered.append(case)

        self.draw_case_list(filtered)

    def draw_case_list(self, cases_to_draw):
        for widget in self.cases_container.winfo_children():
            widget.destroy()

        if not cases_to_draw:
            ctk.CTkLabel(self.cases_container, text="No cases found.", text_color=self.text_muted).pack(pady=20)
            return

        for case in cases_to_draw:
            color = self.red if case.get('status') == 'Urgent' else self.primary

            card = ctk.CTkFrame(self.cases_container, fg_color="#F8F9FA", corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=5, padx=5)

            def on_enter(e, c=card):
                c.configure(fg_color="#E8F5E9")

            def on_leave(e, c=card):
                c.configure(fg_color="#F8F9FA")

            click_cmd = lambda e, c=case: self.select_case(c)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            card.bind("<Button-1>", click_cmd)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 0))
            ctk.CTkLabel(top_row, text=f"Case #{case.get('case_no')}", font=("Arial", 14, "bold"),
                         text_color=self.text_dark).pack(side="left")
            ctk.CTkLabel(top_row, text=case.get('status'), font=("Arial", 11, "bold"), text_color=color).pack(
                side="right")

            ctk.CTkLabel(card, text=f"Zone: {case.get('zone')}", font=("Arial", 12), text_color=self.text_muted).pack(
                anchor="w", padx=10, pady=(0, 10))

            for w in card.winfo_children():
                w.bind("<Button-1>", click_cmd)
                for child in w.winfo_children():
                    child.bind("<Button-1>", click_cmd)

    def setup_form_panel(self):
        self.form_header = ctk.CTkLabel(self.form_panel, text="Select a case from the left to resolve",
                                        font=("Arial", 18, "bold"), text_color=self.text_dark)
        self.form_header.pack(pady=20, padx=20, anchor="w")

        self.details_frame = ctk.CTkFrame(self.form_panel, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=20)

    def select_case(self, case_data):
        self.selected_case = case_data

        # Clear previous form details
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        self.form_header.configure(text=f"Resolving Case #{case_data.get('case_no')} - Zone: {case_data.get('zone')}")

        # 1. Display The Narrative
        ctk.CTkLabel(self.details_frame, text="Incident Narrative:", font=("Arial", 13, "bold")).pack(anchor="w",
                                                                                                      pady=(10, 5))
        nar_box = ctk.CTkTextbox(self.details_frame, height=90, fg_color="#F0F0F0", text_color=self.text_dark)
        nar_box.pack(fill="x")
        nar_box.insert("1.0", case_data.get('narrative', 'No narrative provided.'))
        nar_box.configure(state="disabled")

        # 2. Display the AI NLP Smart Suggestion
        ctk.CTkLabel(self.details_frame, text="🤖 AI Smart Suggestion (TF-IDF Match):", font=("Arial", 13, "bold"),
                     text_color=self.green).pack(anchor="w", pady=(15, 5))

        try:
            suggestion = self.engine.get_resolution_suggestion(case_data.get('narrative', ''),
                                                               case_data.get('zone', ''))
        except Exception as e:
            print(f"AI Error: {e}")
            suggestion = "Error loading AI Suggestion. Check PyCharm terminal for details."

        sugg_box = ctk.CTkTextbox(self.details_frame, height=80, fg_color="#E8F5E9", text_color="#1E392A",
                                  border_width=1, border_color=self.green)
        sugg_box.pack(fill="x")
        sugg_box.insert("1.0", str(suggestion))
        sugg_box.configure(state="disabled")

        # --- THE CLICKABLE SUGGESTION BUTTON ---
        def apply_ai_suggestion():
            self.resolution_input.delete("1.0", "end")  # Clear anything currently in the box

            # Grab the text, but strip out the "Match Confidence" header so it's clean!
            raw_text = sugg_box.get("1.0", "end-1c")
            if "Suggested Approach:\n" in raw_text:
                clean_text = raw_text.split("Suggested Approach:\n")[1]
            else:
                clean_text = raw_text

            self.resolution_input.insert("1.0", clean_text.strip())  # Paste it in!

        # Put the button right under the AI box, aligned to the right side
        ctk.CTkButton(self.details_frame, text="⬇️ Use This Suggestion", fg_color=self.green, hover_color="#1E8449",
                      height=28, command=apply_ai_suggestion).pack(anchor="e", pady=(5, 0))

        # 3. Input for the actual human resolution
        ctk.CTkLabel(self.details_frame, text="Final Settlement Details:", font=("Arial", 13, "bold")).pack(anchor="w",
                                                                                                            pady=(15,
                                                                                                                  5))
        self.resolution_input = ctk.CTkTextbox(self.details_frame, height=130)
        self.resolution_input.pack(fill="x")

        # 4. Hearing Stage & Deadline Controls
        row_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=15)

        ctk.CTkLabel(row_frame, text="Hearing Stage:").pack(side="left")
        self.stage_var = ctk.StringVar(value="Barangay Conciliation")
        ctk.CTkOptionMenu(row_frame, variable=self.stage_var,
                          values=["Barangay Conciliation", "Mediation", "Arbitration"]).pack(side="left", padx=10)

        ctk.CTkLabel(row_frame, text="Compliance Deadline:").pack(side="left", padx=(20, 0))
        self.deadline_input = ctk.CTkEntry(row_frame, placeholder_text="e.g. 7 days, None")
        self.deadline_input.pack(side="left", padx=10)

        # 5. The Big Resolve Button
        btn_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="Mark as Resolved", fg_color=self.green, hover_color="#1E8449",
                      font=("Arial", 14, "bold"), height=40, command=self.submit_resolution).pack(side="right")

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

        # --- THE FIX: We grab the officer's name from the logged-in user data ---
        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        if not officer_name:
            officer_name = "Admin/Kapitan"  # Failsafe backup

        try:
            # --- THE FIX: We pass all 5 pieces of info to the Engine ---
            success = self.engine.update_incident_resolution(case_id, settlement_text, stage, deadline, officer_name)

            if success:
                messagebox.showinfo("Success", f"Case #{case_id} has been officially resolved by {officer_name}!")
                self.selected_case = None
                for widget in self.details_frame.winfo_children():
                    widget.destroy()
                self.form_header.configure(text="Select a case from the left to resolve")
                self.load_pending_cases()
            else:
                messagebox.showerror("Database Error", "Failed to update case. Check database connection.")
        except Exception as e:
            print(f"Save Error: {e}")
            messagebox.showwarning("Error", "Could not save resolution to database. Check terminal.")