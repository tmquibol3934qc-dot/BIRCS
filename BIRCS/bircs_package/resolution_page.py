import customtkinter as ctk
from tkinter import messagebox


class ResolutionPage:
    def __init__(self, parent_frame, engine, user_data):
        self.parent = parent_frame
        self.engine = engine
        self.user = user_data
        self.selected_case = None

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"  # Canvas Gray
        self.color_card = "#FFFFFF"  # Crisp White
        self.color_border = "#EAECEE"  # Subtle borders
        self.soft_blue = "#F0F4F8"  # Light modern blue
        self.primary = "#27AE60"  # Emerald Green
        self.orange = "#E05D3A"  # Alert Orange
        self.red = "#E74C3C"  # Danger Red
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        self.setup_ui()
        self.load_pending_cases()

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 📌 LEFT PANEL (Pending Cases List)
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color=self.color_card, width=340, corner_radius=12,
                                       border_width=1, border_color=self.color_border)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        self.left_panel.pack_propagate(False)

        header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 10), padx=20)

        ctk.CTkLabel(header_frame, text="My Pending Cases", font=(self.ui_font, 18, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        ctk.CTkButton(header_frame, text="🔄", width=35, height=35, fg_color="#F8F9FA", border_width=1,
                      border_color=self.color_border,
                      text_color="black", hover_color="#EAECEE", font=(self.ui_font, 14),
                      command=self.load_pending_cases).pack(side="right")

        self.case_list_frame = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.case_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 📌 RIGHT PANEL (Case Resolution Area)
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color=self.color_card, corner_radius=12, border_width=1,
                                        border_color=self.color_border)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.form_header = ctk.CTkLabel(self.right_panel, text="Select a case from the left to resolve",
                                        font=(self.ui_font, 20, "bold"), text_color=self.text_muted)
        self.form_header.pack(pady=40)

        self.details_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def load_pending_cases(self):
        for widget in self.case_list_frame.winfo_children(): widget.destroy()
        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
        role = self.user.get('role', 'Staff')

        my_incidents = self.engine.get_my_pending_cases(officer_name, role)
        self.pending_incidents = [inc for inc in my_incidents if inc.get('status') in ['Pending', 'Urgent']]

        if not self.pending_incidents:
            ctk.CTkLabel(self.case_list_frame, text="📭 No pending cases\nassigned to you.",
                         font=(self.ui_font, 14, "italic"),
                         text_color=self.text_muted).pack(pady=60)
            return

        for case in self.pending_incidents:
            # Subtle web card style
            card = ctk.CTkFrame(self.case_list_frame, fg_color="#FDFCF6", border_color=self.color_border,
                                border_width=1,
                                corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=6, padx=5)

            # Color Strip
            strip_color = self.red if case.get('status') == 'Urgent' else self.primary
            ctk.CTkFrame(card, width=4, fg_color=strip_color, corner_radius=0).pack(side="left", fill="y")

            # Content
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15, pady=10)

            ctk.CTkLabel(content, text=f"Case #{case.get('case_no')}", font=(self.ui_font, 14, "bold"),
                         text_color=self.color_sidebar).pack(anchor="w")
            ctk.CTkLabel(content, text=case.get('complainant_name'), font=(self.ui_font, 12),
                         text_color=self.text_dark).pack(anchor="w")

            # Bindings
            click_cmd = lambda e, c=case: self.show_case_details(c)
            card.bind("<Button-1>", click_cmd)
            content.bind("<Button-1>", click_cmd)
            for child in content.winfo_children():
                child.bind("<Button-1>", click_cmd)

    def show_case_details(self, case):
        self.selected_case = case
        self.form_header.configure(text=f"📋 Resolving Case #{case.get('case_no')}", text_color=self.color_sidebar)
        for widget in self.details_frame.winfo_children(): widget.destroy()

        # 🚀 THE CATEGORY BADGE (Para makita agad ni User!)
        cat_frame = ctk.CTkFrame(self.details_frame, fg_color="#FDEDEC", corner_radius=8, border_color="#F5B7B1",
                                 border_width=1)
        cat_frame.pack(anchor="w", pady=(0, 15))
        ctk.CTkLabel(cat_frame, text=f"Category: {case.get('category', 'Uncategorized').upper()}",
                     font=(self.ui_font, 11, "bold"),
                     text_color=self.orange).pack(padx=15, pady=6)

        # INFO BOX
        info_frame = ctk.CTkFrame(self.details_frame, fg_color=self.soft_blue, corner_radius=10,
                                  border_color=self.color_border, border_width=1)
        info_frame.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(info_frame, text=f"Plaintiff: {case.get('complainant_name')}", font=(self.ui_font, 14, "bold"),
                     text_color=self.color_sidebar).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(info_frame, text=f"Opposing Party: {case.get('respondent_name')}", font=(self.ui_font, 14, "bold"),
                     text_color=self.color_sidebar).grid(row=1, column=0, sticky="w", padx=20, pady=5)

        ctk.CTkLabel(info_frame, text=f"Sworn Statement:\n{case.get('narrative')}", font=(self.ui_font, 13),
                     wraplength=700,
                     justify="left", text_color=self.text_dark).grid(row=2, column=0, sticky="w", padx=20,
                                                                     pady=(10, 20))

        # REOPEN LOGIC
        if case.get('reopen_status') == 'Approved':
            hist_frame = ctk.CTkFrame(self.details_frame, fg_color="#F2FAF5", border_color="#A9DFBF", border_width=1,
                                      corner_radius=10)
            hist_frame.pack(fill="x", pady=(0, 20))

            ctk.CTkLabel(hist_frame, text="🔒 Phase 1: Initial Resolution", font=(self.ui_font, 13, "bold"),
                         text_color=self.primary).pack(anchor="w", padx=20, pady=(15, 0))
            ctk.CTkLabel(hist_frame, text=case.get('settlement_details', ''), font=(self.ui_font, 12), wraplength=700,
                         justify="left", text_color=self.text_dark).pack(anchor="w", padx=20, pady=(5, 10))

            ctk.CTkLabel(hist_frame, text="💬 Reason for Re-opening", font=(self.ui_font, 13, "bold"),
                         text_color=self.orange).pack(anchor="w", padx=20, pady=(10, 0))
            ctk.CTkLabel(hist_frame, text=case.get('narrative_2', ''), font=(self.ui_font, 12), wraplength=700,
                         justify="left", text_color=self.text_dark).pack(anchor="w", padx=20, pady=(5, 15))

            ctk.CTkLabel(self.details_frame, text="📝 Phase 2: New Resolution Terms", font=(self.ui_font, 14, "bold"),
                         text_color=self.orange).pack(anchor="w", pady=(10, 5))
        else:
            ctk.CTkLabel(self.details_frame, text="Resolution Agreement Terms", font=(self.ui_font, 15, "bold"),
                         text_color=self.color_sidebar).pack(anchor="w", pady=(10, 5))

        # RESOLUTION INPUT
        self.resolution_input = ctk.CTkTextbox(self.details_frame, height=140, fg_color="#F8F9FA",
                                               text_color=self.text_dark,
                                               border_width=1, border_color=self.color_border, font=(self.ui_font, 13))
        self.resolution_input.pack(fill="x", pady=5)

        # AI SUGGESTIONS HEADER
        ctk.CTkLabel(self.details_frame, text="✨ AI Smart Suggestions (Historical Match)",
                     font=(self.ui_font, 13, "bold"),
                     text_color=self.primary).pack(anchor="w", pady=(25, 5))

        self.suggestion_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.suggestion_frame.pack(fill="x")
        self.display_smart_suggestions(case.get('narrative', ''), case.get('zone', ''), case.get('category') or "")

        # SUBMIT BUTTON
        ctk.CTkButton(self.details_frame, text="💾 Mark Case as Resolved", font=(self.ui_font, 15, "bold"),
                      fg_color=self.primary, hover_color="#1E8449", height=50, corner_radius=8,
                      command=self.submit_resolution).pack(pady=40)

    def display_smart_suggestions(self, narrative, zone, category):
        for widget in self.suggestion_frame.winfo_children(): widget.destroy()

        suggestions = self.engine.get_resolution_suggestion(narrative, zone, category)

        if not suggestions:
            ctk.CTkLabel(self.suggestion_frame, text="No strong historical matches found for this case.",
                         font=(self.ui_font, 12, "italic"), text_color=self.text_muted).pack(anchor="w", pady=10)
            return

        for item in suggestions:
            raw_score = item.get('score', item.get('match_score', 50))
            match_percentage = int(raw_score * 100) if isinstance(raw_score, float) and raw_score <= 1.0 else int(
                raw_score)

            if match_percentage >= 80:
                badge_color = self.primary
            elif match_percentage >= 50:
                badge_color = self.orange
            else:
                badge_color = self.red

            card = ctk.CTkFrame(self.suggestion_frame, fg_color="#FFFFFF", border_color=self.color_border,
                                border_width=1,
                                corner_radius=8, cursor="hand2")
            card.pack(fill="x", pady=6)

            click_cmd = lambda e, t=item['text']: self.insert_ai_suggestion(t)
            card.bind("<Button-1>", click_cmd)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(12, 0))
            top_row.bind("<Button-1>", click_cmd)

            ctk.CTkLabel(top_row, text="💡 AI Suggestion", font=(self.ui_font, 12, "bold"),
                         text_color=self.color_sidebar,
                         cursor="hand2").pack(side="left")

            badge = ctk.CTkLabel(top_row, text=f"{match_percentage}% Match", font=(self.ui_font, 11, "bold"),
                                 fg_color=badge_color, text_color="white", width=80, height=26, corner_radius=13,
                                 cursor="hand2")
            badge.pack(side="right")
            badge.bind("<Button-1>", click_cmd)

            text_lbl = ctk.CTkLabel(card, text=item['text'], font=(self.ui_font, 13), wraplength=700, justify="left",
                                    text_color=self.text_dark, cursor="hand2")
            text_lbl.pack(anchor="w", padx=15, pady=(8, 15))
            text_lbl.bind("<Button-1>", click_cmd)

    def insert_ai_suggestion(self, txt):
        self.resolution_input.delete("1.0", "end")
        self.resolution_input.insert("1.0", txt)

    def submit_resolution(self):
        settlement_text = self.resolution_input.get("1.0", "end-1c").strip()
        officer_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()

        if not settlement_text:
            return messagebox.showerror("Missing Information", "Please add some information before proceeding.",
                                        parent=self.parent.winfo_toplevel())

        if len(settlement_text) < 15:
            return messagebox.showwarning("Warning",
                                          "Input is too short. Please ensure the Resolution Agreement contains sufficient details.",
                                          parent=self.parent.winfo_toplevel())

        confirm = messagebox.askyesno("Confirm Resolution",
                                      "Please review and confirm the Resolution Agreement for this case. This action cannot be undone.",
                                      parent=self.parent.winfo_toplevel())
        if not confirm: return

        if self.engine.update_incident_resolution(self.selected_case.get('case_no'), settlement_text, "Stage", "0",
                                                  officer_name):
            messagebox.showinfo("Success", "Case has been successfully resolved and locked!",
                                parent=self.parent.winfo_toplevel())
            self.form_header.configure(text="Select a case from the left to resolve", text_color=self.text_muted)
            for widget in self.details_frame.winfo_children(): widget.destroy()
            self.load_pending_cases()
        else:
            messagebox.showerror("Database Error", "Failed to save resolution.", parent=self.parent.winfo_toplevel())
