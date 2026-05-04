import customtkinter as ctk
from tkinter import messagebox
import re


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
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="🚨 Security & Authorization Alerts", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")

        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, fg_color="#E0E0E0", text_color=self.text_dark,
                      hover_color="#D0D0D0", command=self.refresh_logs).pack(side="right")

        self.logs_container = ctk.CTkScrollableFrame(self.page_frame, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_logs()

    def refresh_logs(self):
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
        is_read = log.get('is_read', 0)
        border_col = "#E0E0E0" if is_read else self.red
        bg_col = "#F8F9FA" if is_read else "white"
        title_col = self.text_muted if is_read else self.red
        desc_col = "gray" if is_read else self.text_dark

        card = ctk.CTkFrame(self.logs_container, fg_color=bg_col, border_color=border_col,
                            border_width=2, corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=8, padx=10)

        content_frame = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
        content_frame.pack(fill="x", padx=20, pady=15)

        action = log.get('action', log.get('action_type', 'System Alert'))
        raw_details = log.get('details', 'No details provided.')
        time_str = log.get('timestamp', log.get('created_at', ''))

        display_details = re.sub(r'\[REQ_PWD:.*?\]', '', raw_details).strip()

        lbl_title = ctk.CTkLabel(content_frame, text=action, font=("Arial", 15, "bold"), text_color=title_col)
        lbl_title.pack(anchor="w")

        lbl_details = ctk.CTkLabel(content_frame, text=display_details, font=("Arial", 12),
                                   text_color=desc_col, wraplength=800, justify="left")
        lbl_details.pack(anchor="w", pady=(5, 0))

        lbl_time = ctk.CTkLabel(content_frame, text=f"📅 {time_str}", font=("Arial", 10, "italic"), text_color="gray")
        lbl_time.pack(anchor="w", pady=(8, 0))

        click_cmd = lambda e=None, l=log, r=raw_details: self.show_alert_details(l, r)

        card.bind("<Button-1>", click_cmd)
        content_frame.bind("<Button-1>", click_cmd)

        for child in content_frame.winfo_children():
            child.bind("<Button-1>", click_cmd)
            child.configure(cursor="hand2")

    def show_alert_details(self, log, raw_details):
        root_window = self.page_frame.winfo_toplevel()

        popup = ctk.CTkToplevel(root_window)
        popup.title("Security Alert Details")

        # 🚀 POGI UPDATE: THE CENTERING MATH!
        window_width = 550
        window_height = 450

        # Kunin ang screen size
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        # Compute ang X at Y coordinates para pumagitna
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))

        popup.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        popup.transient(root_window)
        popup.grab_set()
        popup.configure(fg_color="#F8F9FA")

        ctk.CTkLabel(popup, text="🚨 Complete Alert Report", font=("Arial", 20, "bold"), text_color=self.red).pack(
            pady=(20, 10))

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

        # 🚀 POGI UPDATE: Mas Matibay na Employee Name Logic
        # Susubukan nating hanapin ang pangalan sa raw_details kung nagfa-fail 'yung dictionary fetch!
        emp_name = log.get('employee_name', '').strip()
        user_id = log.get('user_id', 'N/A')

        # Fallback Name Search sa Narrative (e.g. "password for Kristan Ariate (Staff)")
        if not emp_name or emp_name == "System / Not Found":
            name_match = re.search(r'password for (.*?)\(', raw_details)
            if name_match:
                emp_name = name_match.group(1).strip()
            else:
                emp_name = "Target User"

        display_user = f"{emp_name} (ID: {user_id})"

        ctk.CTkLabel(info_frame, text="Employee:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w",
                                                                                    padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=display_user, font=("Arial", 12, "bold"), text_color=self.text_dark).grid(row=2,
                                                                                                                column=1,
                                                                                                                sticky="w",
                                                                                                                padx=10,
                                                                                                                pady=5)

        action = log.get('action', log.get('action_type', 'N/A'))

        ctk.CTkLabel(info_frame, text=f"Action Type:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w",
                                                                                        padx=15, pady=5)
        ctk.CTkLabel(info_frame, text=action, font=("Arial", 12, "bold"), text_color="#E79124").grid(row=3, column=1,
                                                                                                     sticky="w",
                                                                                                     padx=10, pady=5)

        ctk.CTkLabel(info_frame, text="Full Narrative:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="nw",
                                                                                          padx=15, pady=(15, 5))

        display_details = re.sub(r'\[REQ_PWD:.*?\]', '', raw_details).strip()

        narrative_box = ctk.CTkTextbox(info_frame, height=100, fg_color="#F4F7F6", text_color="black")
        narrative_box.grid(row=4, column=1, sticky="nsew", padx=10, pady=(15, 10))
        narrative_box.insert("1.0", display_details)
        narrative_box.configure(state="disabled")

        info_frame.grid_columnconfigure(1, weight=1)

        if action == "PASSWORD RESET REQUEST" and log.get('is_read') == 0:
            btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
            btn_frame.pack(pady=(10, 20))

            ctk.CTkButton(btn_frame, text="✅ Approve Reset", fg_color=self.primary, hover_color="#1E8449",
                          command=lambda: self.approve_password(log, raw_details, popup)).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="❌ Deny", fg_color=self.red, hover_color="#C0392B",
                          command=lambda: self.deny_password(log, popup)).pack(side="left", padx=10)
        else:
            ctk.CTkButton(popup, text="Acknowledge & Close", fg_color=self.primary, hover_color="#1E8449",
                          command=popup.destroy).pack(pady=(10, 20))

            if log.get('is_read') == 0:
                try:
                    self.engine.mark_alert_as_read(log.get('log_id'))
                    self.refresh_logs()
                except Exception:
                    pass

    def approve_password(self, log, raw_details, window):
        user_id = log.get('user_id')
        log_id = log.get('log_id')

        match = re.search(r'\[REQ_PWD:(.*?)\]', raw_details)
        if match and user_id:
            new_pwd = match.group(1)

            if self.engine.reset_user_password(user_id, new_pwd):
                self.engine.log_security_event(user_id, "PASSWORD RESET APPROVED",
                                               f"Kapitan has successfully approved and applied the password change for ID: {user_id}.")
                self.engine.mark_alert_as_read(log_id)

                messagebox.showinfo("Approved", "Password change successfully approved and applied!")
                window.destroy()
                self.refresh_logs()
            else:
                messagebox.showerror("Error", "Failed to update password in database.")
        else:
            messagebox.showerror("Error", "Could not extract the new password. The request might be corrupted.")

    def deny_password(self, log, window):
        log_id = log.get('log_id')
        user_id = log.get('user_id')

        self.engine.log_security_event(user_id, "PASSWORD RESET DENIED",
                                       f"Kapitan has denied the password change request for ID: {user_id}.")
        self.engine.mark_alert_as_read(log_id)

        messagebox.showinfo("Denied", "The password reset request has been denied.")
        window.destroy()
        self.refresh_logs()
