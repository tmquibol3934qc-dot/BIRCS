import customtkinter as ctk
from tkinter import messagebox


class SecurityAlertsPage:
    def __init__(self, parent_frame, engine):
        self.engine = engine
        self.primary = "#27AE60"
        self.red = "#E74C3C"
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"
        self.bg_color = "#F4F7F6"

        self.page_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="🚨 Security & Authorization Alerts", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, fg_color="#E0E0E0", text_color=self.text_dark,
                      hover_color="#D0D0D0", command=self.refresh_logs).pack(side="right")

        # Container para sa mga logs
        self.logs_container = ctk.CTkScrollableFrame(self.page_frame, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_logs()

    def refresh_logs(self):
        # Linisin muna ang container
        for widget in self.logs_container.winfo_children():
            widget.destroy()

        # NOTE: Kailangan nating gawin yung get_security_logs sa engine.py mamaya
        try:
            logs = self.engine.get_security_logs()
        except AttributeError:
            ctk.CTkLabel(self.logs_container, text="Pending Backend Setup: Please add get_security_logs to engine.py",
                         text_color=self.red).pack(pady=20)
            return

        if not logs:
            ctk.CTkLabel(self.logs_container, text="No security alerts at this time. Everything is safe.",
                         text_color="gray",
                         font=("Arial", 14, "italic")).pack(pady=50)
            return

        for log in logs:
            self.build_alert_card(log)

    def build_alert_card(self, log):
        is_read = log.get('is_read', 0)
        border_col = "#E0E0E0" if is_read else self.red
        bg_col = "#F9F9F9" if is_read else "white"

        card = ctk.CTkFrame(self.logs_container, fg_color=bg_col, border_color=border_col, border_width=2,
                            corner_radius=8)
        card.pack(fill="x", pady=5, padx=10)

        left_info = ctk.CTkFrame(card, fg_color="transparent")
        left_info.pack(side="left", padx=15, pady=15)

        action = log.get('action_type', 'System Alert')
        details = log.get('details', 'No details provided.')
        time_str = log.get('created_at', '')

        # Title
        ctk.CTkLabel(left_info, text=action, font=("Arial", 14, "bold"),
                     text_color=self.red if not is_read else self.text_muted).pack(anchor="w")
        # Details
        ctk.CTkLabel(left_info, text=details, font=("Arial", 12),
                     text_color=self.text_dark if not is_read else "gray").pack(anchor="w", pady=(2, 0))
        # Time
        ctk.CTkLabel(left_info, text=str(time_str), font=("Arial", 10, "italic"), text_color="gray").pack(anchor="w",
                                                                                                          pady=(5, 0))

        # Button (Kung hindi pa nababasa)
        if not is_read:
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=15)

            ctk.CTkButton(btn_frame, text="Mark as Reviewed", width=120, fg_color=self.primary, hover_color="#1E8449",
                          command=lambda l_id=log.get('log_id'): self.mark_as_reviewed(l_id)).pack()

    def mark_as_reviewed(self, log_id):
        # NOTE: Kailangan din natin i-add 'to sa engine.py mamaya
        try:
            self.engine.mark_security_log_read(log_id)
            self.refresh_logs()  # I-reload yung UI para maging gray na yung binasa
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update log: {e}")
