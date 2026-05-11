import customtkinter as ctk
from tkinter import messagebox
from .pdf_generator import PDFGenerator


class IncidentDetailsModal:
    def __init__(self, parent_window, row_data, engine, user_data, refresh_callback=None):
        self.engine = engine
        self.user = user_data
        self.refresh_callback = refresh_callback

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#FDFCF6"  # Premium Cream for Modals
        self.color_card = "#FFFFFF"  # Crisp White
        self.color_border = "#EAECEE"  # Subtle borders
        self.primary = "#27AE60"  # Emerald Green
        self.blue = "#3498DB"  # Clean Blue
        self.orange = "#E05D3A"  # Alert Orange
        self.red = "#E74C3C"  # Danger Red
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        self.ui_font = "Poppins"
        self.header_font = "Poppins"

        self.popup = ctk.CTkToplevel(parent_window)
        self.popup.title(f"Case Report - #{row_data.get('case_no')}")

        # 🚀 PERFECT CENTERING
        window_width = 750
        window_height = 800

        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))

        self.popup.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        self.popup.transient(parent_window)
        self.popup.grab_set()
        self.popup.configure(fg_color=self.color_bg)

        self.build_ui(row_data)

    def build_ui(self, row_data):
        # 📌 1. DEEP NAVY REPORT HEADER
        header_bg = ctk.CTkFrame(self.popup, fg_color=self.color_sidebar, corner_radius=0, height=80)
        header_bg.pack(fill="x")
        header_bg.pack_propagate(False)

        ctk.CTkLabel(header_bg, text=f"📋 Official Case Report: #{row_data.get('case_no')}",
                     font=(self.header_font, 22, "bold"), text_color="white").pack(pady=(25, 0))

        # SCROLLABLE BODY
        scroll_area = ctk.CTkScrollableFrame(self.popup, fg_color="transparent")
        scroll_area.pack(fill="both", expand=True, padx=15, pady=10)

        # 📌 2. GENERAL INFO CARD
        info_frame = ctk.CTkFrame(scroll_area, fg_color=self.color_card, border_color=self.color_border, border_width=1,
                                  corner_radius=10)
        info_frame.pack(fill="x", padx=15, pady=(10, 15))

        # Category
        ctk.CTkLabel(info_frame, text="Category:", font=(self.ui_font, 12, "bold"), text_color=self.text_muted).grid(
            row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(info_frame, text=row_data.get('category', 'Uncategorized'), text_color=self.color_sidebar,
                     font=(self.ui_font, 13, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(15, 5))

        # Status Logic & Badge
        status = row_data.get('status') or 'N/A'
        if status == "Pending":
            display_status = "Normal"
        elif status == "Urgent":
            display_status = "High Priority"
        else:
            display_status = status

        status_color = self.red if status == 'Urgent' else (self.primary if status == 'Resolved' else self.orange)

        ctk.CTkLabel(info_frame, text="Current Status:", font=(self.ui_font, 12, "bold"),
                     text_color=self.text_muted).grid(row=0, column=2, sticky="w", padx=(30, 10), pady=(15, 5))

        badge = ctk.CTkFrame(info_frame, fg_color=status_color, corner_radius=12, width=120, height=28)
        badge.grid(row=0, column=3, sticky="w", padx=10, pady=(15, 5))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=display_status.upper(), text_color="white", font=(self.ui_font, 10, "bold")).place(
            relx=0.5, rely=0.5, anchor="center")

        # 📌 3. PARTIES INVOLVED CARD
        parties_frame = ctk.CTkFrame(scroll_area, fg_color="#F8F9FA", border_color=self.color_border, border_width=1,
                                     corner_radius=10)
        parties_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(parties_frame, text="Nagsusumbong (Plaintiff):", font=(self.ui_font, 12, "bold"),
                     text_color=self.blue).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(parties_frame,
                     text=f"{row_data.get('complainant_name')}  •  📞 {row_data.get('complainant_contact') or 'N/A'}",
                     font=(self.ui_font, 12), text_color=self.text_dark).grid(row=0, column=1, sticky="w", padx=10,
                                                                              pady=(15, 5))

        ctk.CTkLabel(parties_frame, text="Inirereklamo (Opposing):", font=(self.ui_font, 12, "bold"),
                     text_color=self.red).grid(row=1, column=0, sticky="w", padx=20, pady=(5, 15))
        ctk.CTkLabel(parties_frame,
                     text=f"{row_data.get('respondent_name')}  •  📞 {row_data.get('respondent_contact') or 'N/A'}",
                     font=(self.ui_font, 12), text_color=self.text_dark).grid(row=1, column=1, sticky="w", padx=10,
                                                                              pady=(5, 15))

        # 📌 4. NARRATIVES & SETTLEMENTS (PHASE 1)
        ctk.CTkLabel(scroll_area, text="📝 Phase 1: Original Report", font=(self.ui_font, 14, "bold"),
                     text_color=self.color_sidebar).pack(anchor="w", padx=20, pady=(10, 5))

        n1_box = ctk.CTkTextbox(scroll_area, height=100, fg_color=self.color_card, text_color=self.text_dark,
                                border_width=1, border_color=self.color_border, font=(self.ui_font, 12))
        n1_box.pack(fill="x", padx=20, pady=5)
        n1_box.insert("1.0", f"NARRATIVE:\n\n{row_data.get('narrative') or 'N/A'}")
        n1_box.configure(state="disabled")

        r1_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F2FAF5", text_color=self.text_dark, border_width=1,
                                border_color="#A9DFBF", font=(self.ui_font, 12))  # Soft Green
        r1_box.pack(fill="x", padx=20, pady=(5, 15))
        r1_box.insert("1.0", f"SETTLEMENT DECISION:\n\n{row_data.get('settlement_details') or 'Case still pending.'}")
        r1_box.configure(state="disabled")

        # 📌 5. RE-OPEN STATUS (PHASE 2)
        reopen_stat = row_data.get('reopen_status')
        if row_data.get('narrative_2'):
            p2_title, title_col = "🔄 Phase 2: Case Re-opened", self.primary
            if reopen_stat == 'Requested':
                p2_title, title_col = "⏳ Phase 2: Re-open Request (Pending)", self.orange
            elif reopen_stat == 'Denied':
                p2_title, title_col = "❌ Phase 2: Request Denied", self.red

            ctk.CTkFrame(scroll_area, height=1, fg_color=self.color_border).pack(fill="x", padx=30, pady=10)
            ctk.CTkLabel(scroll_area, text=p2_title, font=(self.ui_font, 14, "bold"), text_color=title_col).pack(
                anchor="w", padx=20, pady=(10, 5))

            n2_box = ctk.CTkTextbox(scroll_area, height=100, fg_color=self.color_card, text_color=self.text_dark,
                                    border_width=1, border_color=self.color_border, font=(self.ui_font, 12))
            n2_box.pack(fill="x", padx=20, pady=5)
            n2_box.insert("1.0", f"STAFF REASON:\n\n{row_data.get('narrative_2')}")
            n2_box.configure(state="disabled")

            if row_data.get('settlement_details_2'):
                r2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F2FAF5", text_color=self.text_dark,
                                        border_width=1, border_color="#A9DFBF", font=(self.ui_font, 12))
                r2_box.pack(fill="x", padx=20, pady=(5, 15))
                r2_box.insert("1.0", f"NEW SETTLEMENT DECISION:\n\n{row_data.get('settlement_details_2')}")
                r2_box.configure(state="disabled")

        # 📌 6. ACTION BUTTONS (BOTTOM)
        btn_frame = ctk.CTkFrame(scroll_area, fg_color="transparent")
        btn_frame.pack(pady=(15, 30))

        if status in ['Resolved', 'Completed']:
            current_user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
            case_processor = row_data.get('processed_by', '')
            user_role = self.user.get('role', 'Staff').lower()
            can_reopen = (current_user_name == case_processor) or (user_role in ['admin', 'kapitan'])

            if reopen_stat == 'Requested':
                ctk.CTkLabel(btn_frame, text="⏳ Pending Kapitan's Approval", text_color=self.orange,
                             font=(self.ui_font, 12, "bold")).pack(side="left", padx=15)
            elif reopen_stat == 'Approved':
                ctk.CTkLabel(btn_frame, text="✅ Case Re-opened", text_color=self.primary,
                             font=(self.ui_font, 12, "bold")).pack(side="left", padx=15)
            elif reopen_stat == 'Denied':
                ctk.CTkLabel(btn_frame, text="❌ Request Denied", text_color=self.red,
                             font=(self.ui_font, 12, "bold")).pack(side="left", padx=15)
                if can_reopen:
                    ctk.CTkButton(btn_frame, text="Submit New Request", fg_color="transparent", border_width=1,
                                  border_color=self.orange, text_color=self.orange, hover_color="#FFF3E0",
                                  font=(self.ui_font, 12, "bold"), height=38, corner_radius=8,
                                  command=lambda: self.prompt_reopen_request(row_data.get('case_no'))).pack(side="left",
                                                                                                            padx=10)
                else:
                    ctk.CTkLabel(btn_frame, text="(Assigned Officer Only)", font=(self.ui_font, 11, "italic"),
                                 text_color=self.text_muted).pack(side="left", padx=10)
            else:
                if can_reopen:
                    ctk.CTkButton(btn_frame, text="Request Re-open", fg_color="transparent", border_width=1,
                                  border_color=self.orange, text_color=self.orange, hover_color="#FFF3E0",
                                  font=(self.ui_font, 12, "bold"), height=38, corner_radius=8,
                                  command=lambda: self.prompt_reopen_request(row_data.get('case_no'))).pack(side="left",
                                                                                                            padx=10)
                else:
                    ctk.CTkLabel(btn_frame, text="(Assigned Officer Only)", font=(self.ui_font, 11, "italic"),
                                 text_color=self.text_muted).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="🖨️ Print Blotter", fg_color=self.blue, hover_color="#2980B9", text_color="white",
                      font=(self.ui_font, 12, "bold"), height=38, corner_radius=8,
                      command=lambda: self.handle_print(row_data)).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Close Report", fg_color="#EAECEE", hover_color="#D5D8DC",
                      text_color=self.text_dark, font=(self.ui_font, 12, "bold"), height=38, corner_radius=8,
                      command=self.popup.destroy).pack(side="left", padx=10)

    # ==================================================
    # LOGIC: REOPEN MODAL
    # ==================================================
    def prompt_reopen_request(self, case_no):
        req_window = ctk.CTkToplevel(self.popup)
        req_window.title(f"Request Re-open: {case_no}")
        req_window.geometry("500x380")

        # Centering
        req_window.update_idletasks()
        x = int((req_window.winfo_screenwidth() / 2) - (500 / 2))
        y = int((req_window.winfo_screenheight() / 2) - (380 / 2))
        req_window.geometry(f"+{x}+{y}")

        req_window.transient(self.popup)
        req_window.grab_set()
        req_window.configure(fg_color=self.color_bg)

        # Header banner
        header = ctk.CTkFrame(req_window, fg_color=self.color_sidebar, corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="⚠️ Request to Re-open Case", font=(self.header_font, 16, "bold"),
                     text_color="white").pack(pady=12)

        ctk.CTkLabel(req_window, text="Please state the official reason for re-opening:",
                     font=(self.ui_font, 12, "bold"), text_color=self.text_dark).pack(anchor="w", padx=25, pady=(20, 5))

        reason_box = ctk.CTkTextbox(req_window, height=130, fg_color="#FFFFFF", text_color="black", border_width=1,
                                    border_color=self.color_border, font=(self.ui_font, 12))
        reason_box.pack(fill="x", padx=25, pady=(0, 20))

        def submit_request():
            reason = reason_box.get("1.0", "end-1c").strip()
            if not reason:
                return messagebox.showwarning("Missing Info", "Please enter a valid reason.", parent=req_window)

            if self.engine.request_case_reopen(case_no, reason):
                messagebox.showinfo("Success", "Request officially sent to Kapitan for approval!", parent=self.popup)
                req_window.destroy()
                self.popup.destroy()
                if self.refresh_callback: self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to send request. Check your connection.", parent=req_window)

        ctk.CTkButton(req_window, text="📤 Submit Request to Admin", fg_color=self.orange, hover_color="#C64D2B",
                      font=(self.ui_font, 13, "bold"), height=42, corner_radius=8, command=submit_request).pack(pady=5,
                                                                                                                padx=25,
                                                                                                                fill="x")

    def handle_print(self, row_data):
        status = row_data.get('status', '').strip()

        if status.lower() not in ["resolved", "completed"]:
            messagebox.showwarning(
                "Printing Restricted",
                f"Case cannot be printed. Status is currently: {status.upper()}.\n\nMake sure the case is officially 'Resolved' before generating the PDF report.",
                parent=self.popup
            )
            return

        PDFGenerator.export_blotter(row_data)
