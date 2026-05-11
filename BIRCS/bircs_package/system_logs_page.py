import customtkinter as ctk
import datetime
from tkinter import messagebox


class SystemLogsPage:
    def __init__(self, parent_frame, engine):
        self.engine = engine

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"  # Web Canvas Gray
        self.color_card = "#FFFFFF"  # Crisp White
        self.color_border = "#EAECEE"  # Subtle borders
        self.primary = "#27AE60"  # Emerald Green
        self.blue = "#3498DB"  # Action Blue
        self.orange = "#E05D3A"  # Alert Orange
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # 📌 HEADER SECTION
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(30, 15))

        ctk.CTkLabel(header_frame, text="🕒 System Audit Logs", font=(self.ui_font, 26, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        # 📌 THE TIME-SCOPE FILTER PANEL (Web-App Card Style)
        filter_frame = ctk.CTkFrame(self.container, fg_color=self.color_card, corner_radius=10, border_width=1,
                                    border_color=self.color_border)
        filter_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(filter_frame, text="Archive Date:", font=(self.ui_font, 13, "bold"),
                     text_color=self.color_sidebar).pack(side="left", padx=(25, 10), pady=20)

        # Date Entry with modern border
        self.date_var = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(filter_frame, textvariable=self.date_var, placeholder_text="YYYY-MM-DD",
                                       placeholder_text_color="#A6ACAF", width=160, height=38, font=(self.ui_font, 12),
                                       fg_color="#F8F9FA", border_color=self.color_border, text_color="black")
        self.date_entry.pack(side="left", padx=5)

        # Clean Calendar Button
        self.cal_btn = ctk.CTkButton(filter_frame, text="📅", width=40, height=38, fg_color="#F8F9FA", border_width=1,
                                     border_color=self.color_border,
                                     text_color="black", hover_color="#EAECEE", font=("Arial", 16),
                                     command=self.open_calendar_popup)
        self.cal_btn.pack(side="left", padx=(0, 15))

        # Modern Action Buttons
        ctk.CTkButton(filter_frame, text="🔍 Search", fg_color=self.blue, hover_color="#2980B9", height=38,
                      corner_radius=8, font=(self.ui_font, 12, "bold"), width=110, command=self.search_archive).pack(
            side="left", padx=5)

        ctk.CTkButton(filter_frame, text="🔄 Show Latest", fg_color=self.primary, hover_color="#1E8449", height=38,
                      corner_radius=8, font=(self.ui_font, 12, "bold"), width=120, command=self.load_default_logs).pack(
            side="left", padx=5)

        self.status_label = ctk.CTkLabel(filter_frame, text="Viewing: Latest 50 Logs (Fast Mode)",
                                         font=(self.ui_font, 12, "italic"), text_color=self.text_muted)
        self.status_label.pack(side="right", padx=25)

        # 📌 TABLE HEADER (High Contrast Navy - Senior Friendly)
        table_container = ctk.CTkFrame(self.container, fg_color=self.color_card, corner_radius=10, border_width=1,
                                       border_color=self.color_border)
        table_container.pack(fill="both", expand=True, padx=30, pady=(15, 30))

        title_row = ctk.CTkFrame(table_container, fg_color=self.color_sidebar, corner_radius=0, height=45)
        title_row.pack(fill="x", padx=2, pady=(2, 0))
        title_row.pack_propagate(False)

        ctk.CTkLabel(title_row, text="User Info", font=(self.ui_font, 12, "bold"), text_color="white", width=250,
                     anchor="w").pack(side="left", padx=(55, 10))
        ctk.CTkLabel(title_row, text="Login Time", font=(self.ui_font, 12, "bold"), text_color="white", width=200,
                     anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(title_row, text="Logout Time / Status", font=(self.ui_font, 12, "bold"), text_color="white",
                     width=200, anchor="w").pack(side="left", padx=10)

        # 📌 LOGS CONTAINER
        self.logs_scroll = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.logs_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_default_logs()

    def open_calendar_popup(self):
        try:
            from tkcalendar import Calendar
        except ImportError:
            messagebox.showerror("Error", "Missing tkcalendar library. Please run: pip install tkcalendar",
                                 parent=self.container.winfo_toplevel())
            return

        cal_window = ctk.CTkToplevel(self.container)
        cal_window.title("Select Date")
        cal_window.geometry("320x380")
        cal_window.transient(self.container.winfo_toplevel())
        cal_window.grab_set()
        cal_window.configure(fg_color=self.color_card)

        cal_window.update_idletasks()
        x = int((cal_window.winfo_screenwidth() / 2) - (320 / 2))
        y = int((cal_window.winfo_screenheight() / 2) - (380 / 2))
        cal_window.geometry(f"+{x}+{y}")

        today = datetime.date.today()

        cal = Calendar(cal_window, selectmode='day', year=today.year, month=today.month, day=today.day,
                       date_pattern='y-mm-dd', background=self.color_sidebar, foreground='white',
                       bordercolor=self.color_border, headersbackground=self.color_sidebar,
                       headersforeground='white', selectbackground=self.primary)
        cal.pack(pady=20, fill="both", expand=True, padx=20)

        def confirm_date():
            selected_date = cal.get_date()
            self.date_var.set(selected_date)
            cal_window.destroy()

        ctk.CTkButton(cal_window, text="✓ Confirm Date", fg_color=self.primary, hover_color="#1E8449",
                      font=(self.ui_font, 13, "bold"), height=40, corner_radius=8, command=confirm_date).pack(
            pady=(0, 20), padx=20, fill="x")

    def load_default_logs(self):
        self.date_var.set("")
        self.status_label.configure(text="Viewing: Latest 50 Logs (Fast Mode)", text_color=self.primary)
        logs = self.engine.get_optimized_logs(limit=50)
        self.render_logs(logs)

    def search_archive(self):
        target_date = self.date_var.get().strip()
        if not target_date:
            messagebox.showwarning("Missing Date", "Please enter a date in YYYY-MM-DD format.",
                                   parent=self.container.winfo_toplevel())
            return

        try:
            datetime.datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Format", "Wrong date format! Please use YYYY-MM-DD.\nExample: 2026-04-20",
                                 parent=self.container.winfo_toplevel())
            return

        self.status_label.configure(text=f"Viewing Archive: {target_date}", text_color=self.color_sidebar)
        logs = self.engine.get_optimized_logs(filter_date=target_date)

        if not logs:
            messagebox.showinfo("No Logs", f"No activity recorded on {target_date}.",
                                parent=self.container.winfo_toplevel())

        self.render_logs(logs)

    def render_logs(self, logs_data):
        for widget in self.logs_scroll.winfo_children():
            widget.destroy()

        if not logs_data:
            ctk.CTkLabel(self.logs_scroll, text="📭 No logs to display.", font=(self.ui_font, 14, "italic"),
                         text_color=self.text_muted).pack(pady=60)
            return

        def to_ampm(date_val):
            if not date_val or str(date_val).strip().lower() in ["", "none", "n/a"]:
                return None
            try:
                if isinstance(date_val, datetime.datetime):
                    return date_val.strftime("%Y-%m-%d %I:%M %p")
                time_str = str(date_val).split(".")[0]
                dt_obj = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                return dt_obj.strftime("%Y-%m-%d %I:%M %p")
            except Exception:
                return str(date_val)

        for idx, log in enumerate(logs_data):
            user_name = log.get('employee_name', 'Unknown User')
            role = log.get('role', 'Staff')

            raw_in = log.get('login_time')
            formatted_in = to_ampm(raw_in)
            time_in = formatted_in if formatted_in else "N/A"

            raw_out = log.get('logout_time')
            formatted_out = to_ampm(raw_out)
            time_out = formatted_out if formatted_out else "Active Session"

            row_bg = "#FFFFFF" if idx % 2 == 0 else "#FDFCF6"

            row = ctk.CTkFrame(self.logs_scroll, fg_color=row_bg, corner_radius=6, border_width=1,
                               border_color=self.color_border, height=55)
            row.pack(fill="x", pady=2, padx=5)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text="👤", font=("Arial", 20), text_color=self.color_sidebar).pack(side="left",
                                                                                                padx=(20, 15))

            user_frame = ctk.CTkFrame(row, fg_color="transparent", width=250)
            user_frame.pack(side="left", fill="y", pady=8)
            user_frame.pack_propagate(False)
            ctk.CTkLabel(user_frame, text=user_name, font=(self.ui_font, 12, "bold"), text_color=self.text_dark).pack(
                anchor="w")
            ctk.CTkLabel(user_frame, text=role, font=(self.ui_font, 10), text_color=self.text_muted).pack(anchor="w")

            time_in_frame = ctk.CTkFrame(row, fg_color="transparent", width=200)
            time_in_frame.pack(side="left", fill="y", pady=8)
            time_in_frame.pack_propagate(False)
            ctk.CTkLabel(time_in_frame, text=time_in, font=(self.ui_font, 12), text_color=self.text_dark).pack(
                anchor="w", pady=6)

            time_out_frame = ctk.CTkFrame(row, fg_color="transparent")
            time_out_frame.pack(side="left", fill="both", expand=True, pady=8)

            if time_out == "Active Session":
                badge = ctk.CTkFrame(time_out_frame, fg_color=self.primary, corner_radius=12, width=110, height=26)
                badge.pack(anchor="w", pady=4)
                badge.pack_propagate(False)
                ctk.CTkLabel(badge, text="ACTIVE NOW", font=(self.ui_font, 10, "bold"), text_color="white").place(
                    relx=0.5, rely=0.5, anchor="center")
            else:
                ctk.CTkLabel(time_out_frame, text=time_out, font=(self.ui_font, 12), text_color=self.text_dark).pack(
                    anchor="w", pady=6)
