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
        # Header Section
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="🚨 Security & Authorization Alerts", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")

        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, fg_color="#E0E0E0", text_color=self.text_dark,
                      hover_color="#D0D0D0", command=self.refresh_logs).pack(side="right")

        # Scrollable Container para sa mga logs
        self.logs_container = ctk.CTkScrollableFrame(self.page_frame, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_logs()

    def refresh_logs(self):
        # Linisin ang listahan bago mag-reload
        for widget in self.logs_container.winfo_children():
            widget.destroy()

        try:
            logs = self.engine.get_security_logs()
        except AttributeError:
            ctk.CTkLabel(self.logs_container, text="Pending Backend Setup: Please add get_security_logs to engine.py",
                         text_color=self.red).pack(pady=20)
            return

        if not logs:
            ctk.CTkLabel(self.logs_container, text="No security alerts at this time. Everything is safe.",
                         text_color="gray", font=("Arial", 14, "italic")).pack(pady=50)
            return

        for log in logs:
            self.build_alert_card(log)

    def build_alert_card(self, log):
        # 1. STATUS & STYLING
        is_read = log.get('is_read', 0)
        border_col = "#E0E0E0" if is_read else self.red
        bg_col = "#F8F9FA" if is_read else "white"
        title_col = self.text_muted if is_read else self.red
        desc_col = "gray" if is_read else self.text_dark
        font_weight = "normal" if is_read else "bold"

        # 2. MAIN CARD FRAME
        # Gagamit tayo ng 'cursor="hand2"' sa card mismo
        card = ctk.CTkFrame(self.logs_container, fg_color=bg_col, border_color=border_col,
                            border_width=2, corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=8, padx=10)

        # 3. CONTENT AREA (Ito yung dapat lumitaw!)
        content_frame = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
        content_frame.pack(fill="x", padx=20, pady=15)

        action = log.get('action', log.get('action_type', 'System Alert'))
        details = log.get('details', 'No details provided.')
        time_str = log.get('timestamp', log.get('created_at', ''))

        lbl_title = ctk.CTkLabel(content_frame, text=action, font=("Arial", 15, "bold"), text_color=title_col)
        lbl_title.pack(anchor="w")

        lbl_details = ctk.CTkLabel(content_frame, text=details, font=("Arial", 12),
                                   text_color=desc_col, wraplength=800, justify="left")
        lbl_details.pack(anchor="w", pady=(5, 0))

        lbl_time = ctk.CTkLabel(content_frame, text=f"📅 {time_str}", font=("Arial", 10, "italic"), text_color="gray")
        lbl_time.pack(anchor="w", pady=(8, 0))

        # ============================================================
        # 4. THE IMMORTAL CLICK BINDING (No More Invisible Buttons!)
        # ============================================================
        click_cmd = lambda e=None, l=log: self.show_alert_details(l)

        # I-bind ang click sa main frame
        card.bind("<Button-1>", click_cmd)
        content_frame.bind("<Button-1>", click_cmd)

        # I-bind ang click sa LAHAT ng labels sa loob para hindi sila maging 'dead spot'
        for child in content_frame.winfo_children():
            child.bind("<Button-1>", click_cmd)
            child.configure(cursor="hand2")

    def show_alert_details(self, log):
        root_window = self.page_frame.winfo_toplevel()

        popup = ctk.CTkToplevel(root_window)
        popup.title("Security Alert Details")
        popup.geometry("550x450")
        popup.transient(root_window)
        popup.grab_set()
        popup.configure(fg_color="#F8F9FA")

        # HEADER
        ctk.CTkLabel(popup, text="🚨 Complete Alert Report", font=("Arial", 20, "bold"), text_color=self.red).pack(
            pady=(20, 10))

        # INFO BOX
        info_frame = ctk.CTkFrame(popup, fg_color="white", border_color="#E0E0E0", border_width=1, corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(info_frame, text=f"Log ID:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=15,
                                                                                   pady=(15, 5))
        ctk.CTkLabel(info_frame, text=f"#{log.get('log_id', 'N/A')}", font=("Arial", 12)).grid(row=0, column=1,
                                                                                               sticky="w", padx=10,
                                                                                               pady=(15, 5))

        ctk.CTkLabel(info_frame, text=f"Timestamp:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w",
                                                                                      padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=f"{log.get('timestamp', log.get('created_at', 'N/A'))}", font=("Arial", 12)).grid(
            row=1, column=1, sticky="w", padx=10, pady=5)

        # ============================================================
        # DITO NA PUMASOK YUNG NAME FIX NATIN SA ROW=2!
        # ============================================================
        emp_name = log.get('employee_name', 'System / Not Found')
        user_id = log.get('user_id', 'N/A')
        display_user = f"{emp_name} (ID: {user_id})"

        ctk.CTkLabel(info_frame, text="Employee:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w",
                                                                                    padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=display_user, font=("Arial", 12, "bold"),
                     text_color=self.text_dark).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        # ============================================================

        ctk.CTkLabel(info_frame, text=f"Action Type:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w",
                                                                                        padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=f"{log.get('action', log.get('action_type', 'N/A'))}", font=("Arial", 12, "bold"),
                     text_color="#E79124").grid(row=3, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(info_frame, text="Full Narrative:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="nw",
                                                                                          padx=15, pady=(15, 5))

        narrative_box = ctk.CTkTextbox(info_frame, height=100, fg_color="#F4F7F6", text_color="black")
        narrative_box.grid(row=4, column=1, sticky="nsew", padx=10, pady=(15, 10))
        narrative_box.insert("1.0", log.get('details', 'No additional details provided.'))
        narrative_box.configure(state="disabled")

        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(popup, text="Acknowledge & Close", fg_color=self.primary, hover_color="#1E8449",
                      command=popup.destroy).pack(pady=(10, 20))

        # Auto-mark as read logic
        if log.get('is_read') == 0:
            try:
                # Dito tinatawag yung function sa engine.py
                self.engine.mark_alert_as_read(log.get('log_id'))
                self.refresh_logs()
            except Exception:
                pass
