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

        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="white", width=300, corner_radius=10)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        self.left_panel.pack_propagate(False)

        ctk.CTkLabel(self.left_panel, text="My Pending Cases", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(pady=(15, 10))
        self.case_list_frame = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.case_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.form_header = ctk.CTkLabel(self.right_panel, text="Select a case from the left to resolve",
                                        font=("Arial", 18, "bold"), text_color="gray")
        self.form_header.pack(pady=30)

        self.details_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def load_pending_cases(self):
        for widget in self.case_list_frame.winfo_children(): widget.destroy()
        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        role = self.user.get('role', 'Staff')

        my_incidents = self.engine.get_my_pending_cases(officer_name, role)
        self.pending_incidents = [inc for inc in my_incidents if inc.get('status') in ['Pending', 'Urgent']]
        if not self.pending_incidents:
            ctk.CTkLabel(self.case_list_frame, text="No pending cases\nassigned to you.", font=("Arial", 12, "italic"),
                         text_color="gray").pack(pady=40)
            return

        for case in self.pending_incidents:
            card = ctk.CTkFrame(self.case_list_frame, fg_color="#F8F9FA", border_color=self.primary, border_width=2,
                                cursor="hand2")
            card.pack(fill="x", pady=5)
            card.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))
            ctk.CTkLabel(card, text=f"Case #{case.get('case_no')}", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                                                     padx=10,
                                                                                                     pady=(5, 0))
            ctk.CTkLabel(card, text=case.get('complainant_name'), font=("Arial", 11)).pack(anchor="w", padx=10,
                                                                                           pady=(0, 5))

    def show_case_details(self, case):
        self.selected_case = case
        self.form_header.configure(text=f"Resolving Case #{case.get('case_no')}", text_color=self.primary)
        for widget in self.details_frame.winfo_children(): widget.destroy()

        info_frame = ctk.CTkFrame(self.details_frame, fg_color="#F8F9FA", corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(info_frame, text=f"Complainant: {case.get('complainant_name')}", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text=f"Respondent: {case.get('respondent_name')}", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text=f"Narrative: {case.get('narrative')}", font=("Arial", 11), wraplength=400,
                     justify="left").grid(row=2, column=0, sticky="w", padx=10, pady=10)

        if case.get('reopen_status') == 'Approved':
            hist_frame = ctk.CTkFrame(self.details_frame, fg_color="#F0FFF0", border_color=self.primary, border_width=1)
            hist_frame.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(hist_frame, text="🔒 Phase 1: Original Resolution", font=("Arial", 12, "bold"),
                         text_color=self.primary).pack(anchor="w", padx=10, pady=(10, 0))
            ctk.CTkLabel(hist_frame, text=case.get('settlement_details', ''), font=("Arial", 11), wraplength=450,
                         justify="left").pack(anchor="w", padx=10, pady=(5, 5))

            ctk.CTkLabel(hist_frame, text="💬 Reason for Re-opening", font=("Arial", 12, "bold"),
                         text_color=self.orange).pack(anchor="w", padx=10, pady=(10, 0))
            ctk.CTkLabel(hist_frame, text=case.get('narrative_2', ''), font=("Arial", 11), wraplength=450,
                         justify="left").pack(anchor="w", padx=10, pady=(5, 10))

            ctk.CTkLabel(self.details_frame, text="📝 Phase 2: New Resolution Terms", font=("Arial", 14, "bold"),
                         text_color=self.orange).pack(anchor="w", pady=(10, 5))
        else:
            ctk.CTkLabel(self.details_frame, text="Resolution & Settlement Terms", font=("Arial", 14, "bold"),
                         text_color=self.text_dark).pack(anchor="w", pady=(10, 5))

        self.resolution_input = ctk.CTkTextbox(self.details_frame, height=120, fg_color="#FFFFFF", text_color="black",
                                               border_width=1, border_color="gray")
        self.resolution_input.pack(fill="x", pady=10)

        # Smart Suggestions Header
        ctk.CTkLabel(self.details_frame, text="✨ AI Smart Suggestions (Historical Match)", font=("Arial", 12, "bold"),
                     text_color=self.primary).pack(anchor="w", pady=(15, 5))
        self.suggestion_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.suggestion_frame.pack(fill="x")
        self.display_smart_suggestions(case.get('narrative', ''), case.get('zone', ''), case.get('category') or "")

        ctk.CTkButton(self.details_frame, text="Mark Case as Resolved", font=("Arial", 14, "bold"),
                      fg_color=self.primary, height=45, command=self.submit_resolution).pack(pady=30)

    # =========================================================
    # THE FIX: Upgraded Smart Suggestions UI
    # =========================================================
    def display_smart_suggestions(self, narrative, zone, category):
        for widget in self.suggestion_frame.winfo_children(): widget.destroy()

        suggestions = self.engine.get_resolution_suggestion(narrative, zone, category)

        if not suggestions:
            ctk.CTkLabel(self.suggestion_frame, text="No strong historical matches found for this case.",
                         font=("Arial", 11, "italic"), text_color="gray").pack(anchor="w", pady=5)
            return

        for item in suggestions:
            # Kunin ang score mula sa engine (Assume it returns 'score' or 'match_score'. Default to 50% for safety)
            raw_score = item.get('score', item.get('match_score', 50))

            # Kung ang score ay decimal (e.g., 0.85), convert to percentage integer (85)
            if isinstance(raw_score, float) and raw_score <= 1.0:
                match_percentage = int(raw_score * 100)
            else:
                match_percentage = int(raw_score)

            # Kulay ng badge depende sa score
            if match_percentage >= 80:
                badge_color = self.primary  # Green para sa sure ball
            elif match_percentage >= 50:
                badge_color = self.orange  # Orange para sa sakto lang
            else:
                badge_color = self.red  # Red para sa low match

            # The Main Card
            card = ctk.CTkFrame(self.suggestion_frame, fg_color="#F8F9FA", border_color="#D0D0D0", border_width=1,
                                corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=5)

            # Click Command
            click_cmd = lambda e, t=item['text']: self.insert_ai_suggestion(t)
            card.bind("<Button-1>", click_cmd)

            # Top Row: Title & Percentage Badge
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 0))
            top_row.bind("<Button-1>", click_cmd)

            ctk.CTkLabel(top_row, text="💡 AI Suggestion", font=("Arial", 11, "bold"), text_color=self.text_dark,
                         cursor="hand2").pack(side="left")

            badge = ctk.CTkLabel(top_row, text=f"{match_percentage}% Match", font=("Arial", 10, "bold"),
                                 fg_color=badge_color, text_color="white", width=70, height=22, corner_radius=11,
                                 cursor="hand2")
            badge.pack(side="right")
            badge.bind("<Button-1>", click_cmd)

            # Bottom Row: Suggested Text
            text_lbl = ctk.CTkLabel(card, text=item['text'], font=("Arial", 11), wraplength=430, justify="left",
                                    text_color="#444444", cursor="hand2")
            text_lbl.pack(anchor="w", padx=10, pady=(5, 10))
            text_lbl.bind("<Button-1>", click_cmd)

    def insert_ai_suggestion(self, txt):
        self.resolution_input.delete("1.0", "end")
        self.resolution_input.insert("1.0", txt)

    def submit_resolution(self):
        settlement_text = self.resolution_input.get("1.0", "end-1c").strip()
        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()

        if self.engine.update_incident_resolution(self.selected_case.get('case_no'), settlement_text, "Stage", "0",
                                                  officer_name):
            messagebox.showinfo("Success", "Resolution saved!")
            self.load_pending_cases()
