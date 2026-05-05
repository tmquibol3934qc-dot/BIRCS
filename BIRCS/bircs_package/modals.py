import customtkinter as ctk
from tkinter import messagebox
from .pdf_generator import PDFGenerator


class IncidentDetailsModal:
    def __init__(self, parent_window, row_data, engine, user_data, refresh_callback=None):
        self.engine = engine
        self.user = user_data
        self.refresh_callback = refresh_callback

        self.primary, self.orange, self.red, self.green = "#2980B9", "#F39C12", "#E74C3C", "#27AE60"
        self.text_dark = "#2B2B2B"

        self.popup = ctk.CTkToplevel(parent_window)
        self.popup.title(f"Incident Details - Case #{row_data.get('case_no')}")
        self.popup.geometry("700x750")
        self.popup.transient(parent_window)
        self.popup.grab_set()

        self.build_ui(row_data)

    def build_ui(self, row_data):
        scroll_area = ctk.CTkScrollableFrame(self.popup, fg_color="transparent")
        scroll_area.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_area, text=f"Case #{row_data.get('case_no')} Comprehensive Report",
                     font=("Arial", 22, "bold"), text_color="#1D2153").pack(pady=(10, 15))

        info_frame = ctk.CTkFrame(scroll_area, fg_color="#FFFFFF", border_color="#E0E0E0", border_width=1,
                                  corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(info_frame, text="Category:", font=("Arial", 12, "bold"), text_color=self.text_dark).grid(row=0,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               padx=15,
                                                                                                               pady=(10,
                                                                                                                     5))
        ctk.CTkLabel(info_frame, text=row_data.get('category', 'Uncategorized'), text_color=self.primary,
                     font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 5))

        # 🚀 POGI UPDATE: High Priority at Normal Statuses!
        status = row_data.get('status') or 'N/A'
        if status == "Pending":
            display_status = "Normal"
        elif status == "Urgent":
            display_status = "High Priority"
        else:
            display_status = status

        status_color = self.red if status == 'Urgent' else (self.green if status == 'Resolved' else self.orange)

        ctk.CTkLabel(info_frame, text="Status:", font=("Arial", 12, "bold"), text_color=self.text_dark).grid(row=0,
                                                                                                             column=2,
                                                                                                             sticky="w",
                                                                                                             padx=15,
                                                                                                             pady=(10,
                                                                                                                   5))
        ctk.CTkLabel(info_frame, text=display_status, text_color=status_color, font=("Arial", 12, "bold")).grid(row=0,
                                                                                                                column=3,
                                                                                                                sticky="w",
                                                                                                                padx=10,
                                                                                                                pady=(
                                                                                                                    10,
                                                                                                                    5))

        parties_frame = ctk.CTkFrame(scroll_area, fg_color="#F8F9FA", corner_radius=8)
        parties_frame.pack(fill="x", padx=20, pady=(5, 15))

        # 🚀 POGI UPDATE: Nagsusumbong at Inirereklamo!
        ctk.CTkLabel(parties_frame, text="Nagsusumbong:", font=("Arial", 12, "bold"), text_color=self.primary).grid(
            row=0, column=0, sticky="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(parties_frame,
                     text=f"{row_data.get('complainant_name')} (Contact: {row_data.get('complainant_contact') or 'N/A'})",
                     font=("Arial", 12)).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))

        ctk.CTkLabel(parties_frame, text="Inirereklamo:", font=("Arial", 12, "bold"), text_color=self.red).grid(row=1,
                                                                                                                column=0,
                                                                                                                sticky="w",
                                                                                                                padx=15,
                                                                                                                pady=(2,
                                                                                                                      10))
        ctk.CTkLabel(parties_frame,
                     text=f"{row_data.get('respondent_name')} (Contact: {row_data.get('respondent_contact') or 'N/A'})",
                     font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=10, pady=(2, 10))

        ctk.CTkLabel(scroll_area, text="📝 Phase 1: Original Report & Settlement", font=("Arial", 14, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20)

        n1_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                border_color="#E0E0E0")
        n1_box.pack(fill="x", padx=20, pady=5)
        n1_box.insert("1.0", f"NARRATIVE:\n{row_data.get('narrative') or 'N/A'}")
        n1_box.configure(state="disabled")

        r1_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F0FFF0", text_color="#2B2B2B", border_width=1,
                                border_color="#E0E0E0")
        r1_box.pack(fill="x", padx=20, pady=5)
        r1_box.insert("1.0", f"SETTLEMENT:\n{row_data.get('settlement_details') or 'Case still pending.'}")
        r1_box.configure(state="disabled")

        reopen_stat = row_data.get('reopen_status')
        if row_data.get('narrative_2'):
            p2_title, title_col = "🔄 Phase 2: Case Re-opened", self.green
            if reopen_stat == 'Requested':
                p2_title, title_col = "⏳ Phase 2: Re-open Request (Pending)", self.orange
            elif reopen_stat == 'Denied':
                p2_title, title_col = "❌ Phase 2: Request Denied", self.red

            ctk.CTkLabel(scroll_area, text=p2_title, font=("Arial", 14, "bold"), text_color=title_col).pack(anchor="w",
                                                                                                            padx=20,
                                                                                                            pady=(15,
                                                                                                                  5))

            n2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#FFFFFF", text_color="#2B2B2B", border_width=1,
                                    border_color="#E0E0E0")
            n2_box.pack(fill="x", padx=20, pady=5)
            n2_box.insert("1.0", f"STAFF REASON:\n{row_data.get('narrative_2')}")
            n2_box.configure(state="disabled")

            if row_data.get('settlement_details_2'):
                r2_box = ctk.CTkTextbox(scroll_area, height=80, fg_color="#F0FFF0", text_color="#2B2B2B",
                                        border_width=1, border_color="#E0E0E0")
                r2_box.pack(fill="x", padx=20, pady=5)
                r2_box.insert("1.0", f"NEW SETTLEMENT:\n{row_data.get('settlement_details_2')}")
                r2_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(scroll_area, fg_color="transparent")
        btn_frame.pack(pady=(20, 20))

        if status == 'Resolved':
            current_user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip()
            case_processor = row_data.get('processed_by', '')
            user_role = self.user.get('role', 'Staff').lower()
            can_reopen = (current_user_name == case_processor) or (user_role in ['admin', 'kapitan'])

            if reopen_stat == 'Requested':
                ctk.CTkLabel(btn_frame, text="⏳ Pending Kapitan's Approval", text_color=self.orange,
                             font=("Arial", 12, "bold")).pack(side="left", padx=10)
            elif reopen_stat == 'Approved':
                ctk.CTkLabel(btn_frame, text="✅ Case Re-opened", text_color=self.green,
                             font=("Arial", 12, "bold")).pack(side="left", padx=10)
            elif reopen_stat == 'Denied':
                ctk.CTkLabel(btn_frame, text="❌ Request Denied", text_color=self.red, font=("Arial", 12, "bold")).pack(
                    side="left", padx=10)
                if can_reopen:
                    ctk.CTkButton(btn_frame, text="Submit New Request", fg_color="white", border_width=1,
                                  border_color=self.orange, text_color=self.orange, hover_color="#FFF3E0",
                                  font=("Arial", 12, "bold"),
                                  command=lambda: self.prompt_reopen_request(row_data.get('case_no'))).pack(side="left",
                                                                                                            padx=10)
                else:
                    ctk.CTkLabel(btn_frame, text="(Assigned Officer Only)", font=("Arial", 10, "italic"),
                                 text_color="gray").pack(side="left", padx=10)
            else:
                if can_reopen:
                    ctk.CTkButton(btn_frame, text="Request Re-open", fg_color="white", border_width=1,
                                  border_color=self.orange, text_color=self.orange, hover_color="#FFF3E0",
                                  font=("Arial", 12, "bold"),
                                  command=lambda: self.prompt_reopen_request(row_data.get('case_no'))).pack(side="left",
                                                                                                            padx=10)
                else:
                    ctk.CTkLabel(btn_frame, text="(Assigned Officer Only)", font=("Arial", 10, "italic"),
                                 text_color="gray").pack(side="left", padx=10)

        # ---------------------------------------------------------
        # 🚀 PRINT BUTTON NA MAY BOUNCER
        # ---------------------------------------------------------
        ctk.CTkButton(btn_frame, text="🖨️ Print Blotter", fg_color=self.primary, hover_color="#1E8449",
                      text_color="white", font=("Arial", 12, "bold"), command=lambda: self.handle_print(row_data)).pack(
            side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Close Report", command=self.popup.destroy, fg_color="#E0E0E0",
                      text_color=self.text_dark, hover_color="#CCCCCC", font=("Arial", 12, "bold")).pack(side="left",
                                                                                                         padx=10)

    def prompt_reopen_request(self, case_no):
        req_window = ctk.CTkToplevel(self.popup)
        req_window.title(f"Request Re-open: {case_no}")
        req_window.geometry("500x350")
        req_window.transient(self.popup)
        req_window.grab_set()

        ctk.CTkLabel(req_window, text="Reason for Re-opening", font=("Arial", 14, "bold"),
                     text_color=self.primary).pack(pady=(20, 10))
        reason_box = ctk.CTkTextbox(req_window, height=150, fg_color="#FFFFFF", text_color="black", border_width=1,
                                    border_color="#E0E0E0")
        reason_box.pack(fill="x", padx=20, pady=(0, 20))

        def submit_request():
            reason = reason_box.get("1.0", "end-1c").strip()
            if not reason: return messagebox.showwarning("Missing Info", "Please enter a reason.")
            if self.engine.request_case_reopen(case_no, reason):
                messagebox.showinfo("Success", "Request sent to Kapitan!")
                req_window.destroy()
                self.popup.destroy()
                if self.refresh_callback: self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to send request.")

        ctk.CTkButton(req_window, text="Send Request", fg_color=self.primary, font=("Arial", 12, "bold"),
                      command=submit_request).pack(pady=10)

    def handle_print(self, row_data):
        status = row_data.get('status', '').strip()

        if status.lower() not in ["resolved", "completed"]:
            messagebox.showwarning(
                "Printing Restricted",
                f"Bawal i-print ang kasong ito dahil {status.upper()} pa.\n\n"
                "Siguraduhing 'Resolved' o 'Completed' na ang status bago humingi ng Certificate/Report."
            )
            return

        PDFGenerator.export_blotter(row_data)
