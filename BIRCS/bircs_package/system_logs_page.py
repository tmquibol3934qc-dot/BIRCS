import customtkinter as ctk
from tkinter import messagebox
import datetime


class SystemLogsPage:
    def __init__(self, parent_frame, engine):
        self.engine = engine

        self.text_dark = "#2B2B2B"
        self.primary = "#27AE60"
        self.blue = "#2980B9"

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="🕒 System Audit Logs", font=("Arial", 24, "bold"), text_color=self.text_dark).pack(side="left")

        # --- THE TIME-SCOPE FILTER PANEL ---
        filter_frame = ctk.CTkFrame(self.container, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        filter_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(filter_frame, text="Archive Date:", font=("Arial", 12, "bold"), text_color="gray").pack(side="left", padx=(15, 10), pady=15)

        # 1. ANG DATE ENTRY NATIN
        self.date_var = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(filter_frame, textvariable=self.date_var, placeholder_text="YYYY-MM-DD", width=150)
        self.date_entry.pack(side="left", padx=5)

        # 2. ANG CALENDAR BUTTON NA PINAKAHIINTAY MO!
        # Pag kinlik 'to, tatawagin niya yung popup function natin sa baba
        self.cal_btn = ctk.CTkButton(filter_frame, text="📅", width=40, fg_color="#F39C12", hover_color="#D68910", command=self.open_calendar_popup)
        self.cal_btn.pack(side="left", padx=(0, 10))

        # 3. Search at Reset Buttons
        ctk.CTkButton(filter_frame, text="🔍 Search", fg_color=self.blue, width=100, command=self.search_archive).pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="🔄 Show Latest 50", fg_color="#27AE60", width=120, command=self.load_default_logs).pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(filter_frame, text="Viewing: Latest 50 Logs (Fast Mode)", font=("Arial", 12, "italic"), text_color=self.primary)
        self.status_label.pack(side="right", padx=20)

        # --- LOGS CONTAINER ---
        self.logs_scroll = ctk.CTkScrollableFrame(self.container, fg_color="#F8F9F5")
        self.logs_scroll.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        self.load_default_logs()

    def open_calendar_popup(self):
        """Ito yung magpapalabas nung Calendar Widget (tkcalendar)"""
        from tkinter import messagebox
        try:
            from tkcalendar import Calendar
        except ImportError:
            messagebox.showerror("Error", "Missing tkcalendar library. Please run: pip install tkcalendar")
            return

        import datetime

        # Gawa tayo ng maliit na popup window
        cal_window = ctk.CTkToplevel(self.container)
        cal_window.title("Select Date")
        cal_window.geometry("300x350")
        cal_window.transient(self.container.winfo_toplevel())  # Para laging nasa ibabaw
        cal_window.grab_set()  # Para bawal i-click yung background habang naka-open 'to

        today = datetime.date.today()

        # Ang mismong tkcalendar widget
        cal = Calendar(cal_window, selectmode='day', year=today.year, month=today.month, day=today.day,
                       date_pattern='y-mm-dd')
        cal.pack(pady=20, fill="both", expand=True, padx=20)

        # Ang logic pag pinindot yung confirm
        def confirm_date():
            # Kunin yung pinili sa kalendaryo tapos ipasa sa Textbox!
            selected_date = cal.get_date()
            self.date_var.set(selected_date)
            cal_window.destroy()

        # 🚀 DITO YUNG NAWAWALANG CONFIRM BUTTON MO NA HINDI NA MAG-E-ERROR!
        ctk.CTkButton(cal_window, text="Confirm Date", fg_color="#27AE60", hover_color="#1E8449",
                      command=confirm_date).pack(pady=(0, 20))

    # ==========================================
    # LOGIC: LAZY LOADING & SEARCH
    # ==========================================
    def load_default_logs(self):
        """Kukunin lang ang top 50. Super bilis nito!"""
        self.date_var.set("")  # I-clear ang search box
        self.status_label.configure(text="Viewing: Latest 50 Logs (Fast Mode)", text_color=self.primary)

        # Tawagin yung engine natin
        logs = self.engine.get_optimized_logs(limit=50)
        self.render_logs(logs)

    def search_archive(self):
        """Papasok sa archive kapag may nilagay na date."""
        target_date = self.date_var.get().strip()

        # Simple Validation para di mag-crash kung mali ang type
        if not target_date:
            messagebox.showwarning("Missing Date", "Please enter a date in YYYY-MM-DD format.")
            return

        try:
            # Check kung valid 'yung format nung tinype nila
            datetime.datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Format", "Wrong date format! Please use YYYY-MM-DD.\nExample: 2026-04-20")
            return

        self.status_label.configure(text=f"Viewing Archive: {target_date}", text_color=self.text_dark)

        # Tawagin ang engine na may target date
        logs = self.engine.get_optimized_logs(filter_date=target_date)

        if not logs:
            messagebox.showinfo("No Logs", f"No activity recorded on {target_date}.")

        self.render_logs(logs)

    # ==========================================
    # UI RENDERER
    # ==========================================
    def render_logs(self, logs_data):
        # 1. Burahin muna ang kasalukuyang nakikita sa screen
        for widget in self.logs_scroll.winfo_children():
            widget.destroy()

        if not logs_data:
            ctk.CTkLabel(self.logs_scroll, text="No logs to display.", font=("Arial", 14, "italic"),
                         text_color="gray").pack(pady=50)
            return

        # 2. I-drawing ang mga bagong logs
            # 2. I-drawing ang mga bagong logs
        for log in logs_data:
            # ⚠️ TINUGMA NA NATIN SA SCREENSHOT MO YUNG MGA PANGALAN NG COLUMN!
            user_name = log.get('employee_name', 'Unknown User')
            role = log.get('role', 'Staff')
            time_in = log.get('login_time', 'N/A')
            time_out = log.get('logout_time', 'Active Session')

            card = ctk.CTkFrame(self.logs_scroll, fg_color="white", corner_radius=5, border_width=1,
                                border_color="#E0E0E0")
            card.pack(fill="x", pady=3, padx=5)

            ctk.CTkLabel(card, text="👤", font=("Arial", 18)).pack(side="left", padx=(15, 10))

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=5)

            ctk.CTkLabel(info_frame, text=f"{user_name} ({role})", font=("Arial", 12, "bold"),
                         text_color=self.text_dark).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Login: {time_in}  |  Logout: {time_out}", font=("Arial", 11),
                         text_color="gray").pack(anchor="w")
