import customtkinter as ctk
from datetime import datetime


class SystemLogsPage:
    def __init__(self, parent_frame, engine):
        self.parent = parent_frame
        self.engine = engine

        # Colors
        self.text_dark = "#2B2B2B"
        self.text_muted = "#7A7A7A"
        self.blue = "#3F51B5"
        self.green = "#27AE60"

        self.setup_ui()

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="System Access Logs", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, fg_color="#E0E0E0", text_color=self.text_dark,
                      hover_color="#D0D0D0", command=self.load_logs).pack(side="right")

        headers = ctk.CTkFrame(self.parent, fg_color="transparent")
        headers.pack(fill="x", padx=40, pady=(10, 5))

        ctk.CTkLabel(headers, text="Employee", font=("Arial", 12, "bold"), text_color=self.text_muted, width=200,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Role", font=("Arial", 12, "bold"), text_color=self.text_muted, width=100,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Time In", font=("Arial", 12, "bold"), text_color=self.text_muted, width=180,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Time Out", font=("Arial", 12, "bold"), text_color=self.text_muted, width=180,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(headers, text="Session Time", font=("Arial", 12, "bold"), text_color=self.text_muted, width=100,
                     anchor="e").pack(side="right", padx=10)

        ctk.CTkFrame(self.parent, height=2, fg_color="#E0E0E0").pack(fill="x", padx=30)

        self.logs_container = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_logs()

    def load_logs(self):
        for widget in self.logs_container.winfo_children():
            widget.destroy()

        logs = self.engine.get_login_logs()

        if not logs:
            ctk.CTkLabel(self.logs_container, text="No system logs found in the database.", text_color="gray",
                         font=("Arial", 14, "italic")).pack(pady=50)
            return

        for log in logs:
            self.build_log_row(self.logs_container, log)

    def build_log_row(self, parent, log):
        row = ctk.CTkFrame(parent, fg_color="white", corner_radius=5, height=45)
        row.pack(fill="x", pady=2, padx=10)
        row.pack_propagate(False)

        name = log.get('employee_name', 'Unknown')
        role = log.get('role', 'N/A')
        login_time = log.get('login_time')
        logout_time = log.get('logout_time')

        try:
            if isinstance(login_time, str): login_time = datetime.strptime(login_time, '%Y-%m-%d %H:%M:%S')
            login_str = login_time.strftime("%b %d, %Y - %I:%M %p")

            if logout_time:
                if isinstance(logout_time, str): logout_time = datetime.strptime(logout_time, '%Y-%m-%d %H:%M:%S')
                logout_str = logout_time.strftime("%b %d, %Y - %I:%M %p")

                duration = logout_time - login_time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)

                if hours > 0:
                    duration_str = f"{int(hours)}h {int(minutes)}m"
                else:
                    duration_str = f"{int(minutes)} mins"
                    if int(minutes) == 0: duration_str = "< 1 min"
            else:
                duration_str = "Active Now"
                logout_str = "---"
        except Exception:
            login_str, logout_str, duration_str = str(login_time), str(logout_time), "Error"

        ctk.CTkLabel(row, text=name, font=("Arial", 12, "bold"), text_color=self.text_dark, width=200, anchor="w").pack(
            side="left", padx=(10, 0))
        ctk.CTkLabel(row, text=role.upper(), font=("Arial", 10, "bold"), text_color=self.blue, width=100,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=login_str, font=("Arial", 11), text_color=self.text_muted, width=180, anchor="w").pack(
            side="left")
        ctk.CTkLabel(row, text=logout_str, font=("Arial", 11), text_color=self.text_muted, width=180, anchor="w").pack(
            side="left")

        dur_color = self.green if duration_str == "Active Now" else self.text_muted
        ctk.CTkLabel(row, text=duration_str, font=("Arial", 11, "bold"), text_color=dur_color, width=100,
                     anchor="e").pack(side="right", padx=10)
