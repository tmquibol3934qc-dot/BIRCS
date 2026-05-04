import customtkinter as ctk
from tkinter import messagebox


class ResolutionPage:
    def __init__(self, parent_frame, engine, user_data):
        self.parent = parent_frame
        self.engine = engine
        self.user = user_data
        self.selected_case = None

        # 🚀 POGI UPDATE: Added Sidebar Blue and Soft Blue for UI depth
        self.sidebar_blue = "#1D2153"
        self.soft_blue = "#EAF2F8"
        self.primary = "#27AE60"
        self.orange = "#E79124"
        self.red = "#E74C3C"
        self.text_dark = "#2B2B2B"

        self.setup_ui()
        self.load_pending_cases()

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Nilaparan ng konti ang left panel (320) para sumakto ang malalaking font
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="white", width=320, corner_radius=10)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        self.left_panel.pack_propagate(False)

        header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(15, 10), padx=15)

        # 🚀 POGI UPDATE: Mas malaking font at kulay blue!
        ctk.CTkLabel(header_frame, text="My Pending Cases", font=("Arial", 18, "bold"),
                     text_color=self.sidebar_blue).pack(side="left")

        ctk.CTkButton(header_frame, text="🔄", width=35, height=35, fg_color="#F0F0F0",
                      text_color="black", hover_color="#E0E0E0", font=("Arial", 14),
                      command=self.load_pending_cases).pack(side="right")
        self.case_list_frame = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.case_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.form_header = ctk.CTkLabel(self.right_panel, text="Select a case from the left to resolve",
                                        font=("Arial", 22, "bold"), text_color="gray")
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
            ctk.CTkLabel(self.case_list_frame, text="No pending cases\nassigned to you.", font=("Arial", 14, "italic"),
                         text_color="gray").pack(pady=40)
            return

        for case in self.pending_incidents:
            card = ctk.CTkFrame(self.case_list_frame, fg_color="#F8F9FA", border_color=self.primary, border_width=2,
                                cursor="hand2")
            card.pack(fill="x", pady=8)  # Dinagdagan ang padding
            card.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))

            # 🚀 POGI UPDATE: Case No. is Size 14, Complainant is Size 13
            ctk.CTkLabel(card, text=f"Case #{case.get('case_no')}", font=("Arial", 14, "bold"),
                         text_color=self.sidebar_blue).pack(anchor="w", padx=15, pady=(8, 2))
            ctk.CTkLabel(card, text=case.get('complainant_name'), font=("Arial", 13),
                         text_color=self.text_dark).pack(anchor="w", padx=15, pady=(0, 8))

            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, c=case: self.show_case_details(c))

    def show_case_details(self, case):
        self.selected_case = case
        self.form_header.configure(text=f"Resolving Case #{case.get('case_no')}", text_color=self.sidebar_blue)
        for widget in self.details_frame.winfo_children(): widget.destroy()

        # 🚀 POGI UPDATE: May soft blue background na para hindi mukhang flat!
        info_frame = ctk.CTkFrame(self.details_frame, fg_color=self.soft_blue, corner_radius=10,
                                  border_color="#B9D3EE", border_width=1)
        info_frame.pack(fill="x", pady=(0, 25))

        # 🚀 POGI UPDATE: Size 15 and 14 for readability
        ctk.CTkLabel(info_frame, text=f"Plaintiff: {case.get('complainant_name')}", font=("Arial", 15, "bold"),
                     text_color=self.sidebar_blue).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(info_frame, text=f"Opposing Party: {case.get('respondent_name')}", font=("Arial", 15, "bold"),
                     text_color=self.sidebar_blue).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        ctk.CTkLabel(info_frame, text=f"Sworn Statement: {case.get('narrative')}", font=("Arial", 14), wraplength=700,
                     justify="left", text_color=self.text_dark).grid(row=2, column=0, sticky="w", padx=20, pady=(5, 15))

        if case.get('reopen_status') == 'Approved':
            hist_frame = ctk.CTkFrame(self.details_frame, fg_color="#F0FFF0", border_color=self.primary, border_width=1)
            hist_frame.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(hist_frame, text="🔒 Phase 1: Initial Resolution Agreement", font=("Arial", 14, "bold"),
                         text_color=self.primary).pack(anchor="w", padx=15, pady=(15, 0))
            ctk.CTkLabel(hist_frame, text=case.get('settlement_details', ''), font=("Arial", 13), wraplength=700,
                         justify="left").pack(anchor="w", padx=15, pady=(5, 10))

            ctk.CTkLabel(hist_frame, text="💬 Reason for Re-opening", font=("Arial", 14, "bold"),
                         text_color=self.orange).pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(hist_frame, text=case.get('narrative_2', ''), font=("Arial", 13), wraplength=700,
                         justify="left").pack(anchor="w", padx=15, pady=(5, 15))

            ctk.CTkLabel(self.details_frame, text="📝 Phase 2: New Resolution Terms", font=("Arial", 16, "bold"),
                         text_color=self.orange).pack(anchor="w", pady=(10, 5))
        else:
            ctk.CTkLabel(self.details_frame, text="Resolution Agreement Terms", font=("Arial", 16, "bold"),
                         text_color=self.sidebar_blue).pack(anchor="w", pady=(10, 5))

        # 🚀 POGI UPDATE: Nilakihan natin 'yung textbox font papuntang Size 14!
        self.resolution_input = ctk.CTkTextbox(self.details_frame, height=150, fg_color="#FFFFFF", text_color="black",
                                               border_width=1, border_color="#D0D0D0", font=("Arial", 14))
        self.resolution_input.pack(fill="x", pady=10)

        ctk.CTkLabel(self.details_frame, text="✨ AI Smart Suggestions (Historical Match)", font=("Arial", 14, "bold"),
                     text_color=self.primary).pack(anchor="w", pady=(20, 5))

        self.suggestion_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.suggestion_frame.pack(fill="x")
        self.display_smart_suggestions(case.get('narrative', ''), case.get('zone', ''), case.get('category') or "")

        ctk.CTkButton(self.details_frame, text="Mark Case as Resolved", font=("Arial", 16, "bold"),
                      fg_color=self.primary, hover_color="#1E8449", height=50,
                      command=self.submit_resolution).pack(pady=35)

    def display_smart_suggestions(self, narrative, zone, category):
        for widget in self.suggestion_frame.winfo_children(): widget.destroy()

        suggestions = self.engine.get_resolution_suggestion(narrative, zone, category)

        if not suggestions:
            ctk.CTkLabel(self.suggestion_frame, text="No strong historical matches found for this case.",
                         font=("Arial", 13, "italic"), text_color="gray").pack(anchor="w", pady=5)
            return

        for item in suggestions:
            raw_score = item.get('score', item.get('match_score', 50))

            if isinstance(raw_score, float) and raw_score <= 1.0:
                match_percentage = int(raw_score * 100)
            else:
                match_percentage = int(raw_score)

            if match_percentage >= 80:
                badge_color = self.primary
            elif match_percentage >= 50:
                badge_color = self.orange
            else:
                badge_color = self.red

            card = ctk.CTkFrame(self.suggestion_frame, fg_color="#F8F9FA", border_color="#D0D0D0", border_width=1,
                                corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=8)

            click_cmd = lambda e, t=item['text']: self.insert_ai_suggestion(t)
            card.bind("<Button-1>", click_cmd)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(12, 0))
            top_row.bind("<Button-1>", click_cmd)

            # 🚀 POGI UPDATE: Mas malaking suggestion labels
            ctk.CTkLabel(top_row, text="💡 AI Suggestion", font=("Arial", 13, "bold"), text_color=self.sidebar_blue,
                         cursor="hand2").pack(side="left")

            badge = ctk.CTkLabel(top_row, text=f"{match_percentage}% Match", font=("Arial", 11, "bold"),
                                 fg_color=badge_color, text_color="white", width=80, height=26, corner_radius=13,
                                 cursor="hand2")
            badge.pack(side="right")
            badge.bind("<Button-1>", click_cmd)

            text_lbl = ctk.CTkLabel(card, text=item['text'], font=("Arial", 14), wraplength=700, justify="left",
                                    text_color="#444444", cursor="hand2")
            text_lbl.pack(anchor="w", padx=15, pady=(8, 15))
            text_lbl.bind("<Button-1>", click_cmd)

    def insert_ai_suggestion(self, txt):
        self.resolution_input.delete("1.0", "end")
        self.resolution_input.insert("1.0", txt)

    def submit_resolution(self):
        settlement_text = self.resolution_input.get("1.0", "end-1c").strip()
        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()

        if not settlement_text:
            messagebox.showerror("Missing Information",
                                 "Please add some information before proceeding.")
            return

        if len(settlement_text) < 15:
            messagebox.showwarning("Warning",
                                   "Input is too short. Please ensure the Resolution Agreement contains sufficient details.")
            return

        confirm = messagebox.askyesno(
            "Confirm Resolution",
            "Please review and confirm the Resolution Agreement for this case. This action cannot be undone."
        )

        if not confirm:
            return

        if self.engine.update_incident_resolution(self.selected_case.get('case_no'), settlement_text, "Stage", "0",
                                                  officer_name):
            messagebox.showinfo("Success", "Case has been successfully resolved and locked!")

            self.form_header.configure(text="Select a case from the left to resolve", text_color="gray")
            for widget in self.details_frame.winfo_children():
                widget.destroy()

            self.load_pending_cases()
        else:
            messagebox.showerror("Database Error", "Failed to save resolution.")
