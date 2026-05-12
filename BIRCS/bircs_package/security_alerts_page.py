import customtkinter as ctk
from tkinter import messagebox
import re


class SecurityAlertsPage:
    def __init__(self, parent_frame, engine):
        self.engine = engine

        # 🎨 THE PREMIUM WEB PALETTE
        self.color_sidebar = "#1D2153"  # Deep Navy
        self.color_bg = "#F4F6F7"  # Web Canvas Gray
        self.color_card = "#FFFFFF"  # Crisp White
        self.color_border = "#EAECEE"  # Subtle borders
        self.primary = "#27AE60"  # Emerald Green
        self.red = "#E74C3C"  # Danger Red
        self.orange = "#E05D3A"  # Warning Orange
        self.text_dark = "#2C3E50"
        self.text_muted = "#7F8C8D"

        # 🚀 SINGLE SOSYALIN FONT STANDARD
        self.ui_font = "Poppins"

        self.page_frame = ctk.CTkFrame(parent_frame, fg_color=self.color_bg)
        self.page_frame.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        # 📌 HEADER SECTION
        header_frame = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(25, 10))

        ctk.CTkLabel(header_frame, text="🚨 Security Alerts", font=(self.ui_font, 24, "bold"),
                     text_color=self.color_sidebar).pack(side="left")

        ctk.CTkButton(header_frame, text="🔄 Refresh", width=100, height=32, corner_radius=6,
                      fg_color="#FFFFFF", border_width=1, border_color=self.color_border, text_color=self.text_dark,
                      hover_color="#F8F9FA", font=(self.ui_font, 11, "bold"), command=self.refresh_logs).pack(
            side="right")

        # 📌 SCROLLABLE ALERTS CONTAINER
        self.logs_container = ctk.CTkScrollableFrame(self.page_frame, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True, padx=25, pady=5)

        self.refresh_logs()

    def refresh_logs(self):
        for widget in self.logs_container.winfo_children():
            widget.destroy()

        try:
            logs = self.engine.get_security_logs()
        except AttributeError:
            ctk.CTkLabel(self.logs_container, text="Backend Error: get_security_logs missing",
                         text_color=self.red, font=(self.ui_font, 13, "bold")).pack(pady=20)
            return

        if not logs:
            empty_frame = ctk.CTkFrame(self.logs_container, fg_color="transparent")
            empty_frame.pack(pady=60)
            ctk.CTkLabel(empty_frame, text="🛡️", font=(self.ui_font, 36)).pack()
            ctk.CTkLabel(empty_frame, text="No security alerts detected.",
                         text_color=self.text_muted, font=(self.ui_font, 14, "italic")).pack(pady=5)
            return

        for log in logs:
            self.build_alert_card(log)

    def build_alert_card(self, log):
        is_read = log.get('is_read', 0)

        strip_col = "#BDC3C7" if is_read else self.red
        bg_col = "#FDFCF6" if is_read else "#FFFFFF"
        title_col = self.text_muted if is_read else self.red
        desc_col = "#95A5A6" if is_read else self.text_dark

        # 🚀 THE POGI FIX: Kinulong natin siya sa HEIGHT=85 at naka-propagate(False) para hindi lumobo!
        card = ctk.CTkFrame(self.logs_container, fg_color=bg_col, border_color=self.color_border,
                            border_width=1, corner_radius=8, cursor="hand2", height=85)
        card.pack(fill="x", pady=4, padx=10)
        card.pack_propagate(False)  # Hinding hindi na 'to tataba boss!

        # Subtle Color Strip
        ctk.CTkFrame(card, width=4, fg_color=strip_col, corner_radius=0).pack(side="left", fill="y")

        action = log.get('action', log.get('action_type', 'System Alert'))
        raw_details = log.get('details', 'No details.')
        time_str = log.get('timestamp', log.get('created_at', ''))
        display_details = re.sub(r'\[REQ_PWD:.*?\]', '', raw_details).strip()

        # Right-aligned Time (Umakyat ng konti para pantay sa title)
        time_frame = ctk.CTkFrame(card, fg_color="transparent")
        time_frame.pack(side="right", padx=15, pady=(15, 0), anchor="ne")

        ctk.CTkLabel(time_frame, text=f"🕒 {time_str}", font=(self.ui_font, 12, "italic"),
                     text_color=self.text_muted).pack()

        # Content Frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
        content_frame.pack(fill="both", side="left", expand=True, padx=15, pady=10)

        # 🚀 JUMBO FONT UPDATE: Size 16 para sa Title, Size 14 para sa Description!
        lbl_title = ctk.CTkLabel(content_frame, text=action, font=(self.ui_font, 16, "bold"), text_color=title_col)
        lbl_title.pack(anchor="w", pady=(0, 2))

        lbl_details = ctk.CTkLabel(content_frame, text=display_details, font=(self.ui_font, 14),
                                   text_color=desc_col, wraplength=700, justify="left")
        lbl_details.pack(anchor="w")

        # Click Bindings
        click_cmd = lambda e=None, l=log, r=raw_details: self.show_alert_details(l, r)
        card.bind("<Button-1>", click_cmd)
        content_frame.bind("<Button-1>", click_cmd)
        time_frame.bind("<Button-1>", click_cmd)

        for child in content_frame.winfo_children():
            child.bind("<Button-1>", click_cmd)
            child.configure(cursor="hand2")
        for child in time_frame.winfo_children():
            child.bind("<Button-1>", click_cmd)
            child.configure(cursor="hand2")

    # =========================================================================
    # THE ALERT DETAILS MODAL (HINDI GINALAW TULAD NG SABI MO)
    # =========================================================================
    def show_alert_details(self, log, raw_details):
        root_window = self.page_frame.winfo_toplevel()
        popup = ctk.CTkToplevel(root_window)
        popup.title("Security Report")

        window_width = 580
        window_height = 500

        # Perfect Centering
        popup.update_idletasks()
        x = int((popup.winfo_screenwidth() / 2) - (window_width / 2))
        y = int((popup.winfo_screenheight() / 2) - (window_height / 2))
        popup.geometry(f"{window_width}x{window_height}+{x}+{y}")

        popup.transient(root_window)
        popup.grab_set()
        popup.configure(fg_color="#FDFCF6")

        # Header
        header_bg = ctk.CTkFrame(popup, fg_color=self.color_sidebar, corner_radius=0, height=70)
        header_bg.pack(fill="x")
        header_bg.pack_propagate(False)
        ctk.CTkLabel(header_bg, text="🚨 Security Incident Details", font=(self.ui_font, 20, "bold"),
                     text_color="white").pack(pady=20)

        # Info Grid
        info_frame = ctk.CTkFrame(popup, fg_color="#FFFFFF", border_color=self.color_border, border_width=1,
                                  corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=20, pady=15)

        def create_grid_row(parent, row_idx, label, value, val_color=self.text_dark):
            ctk.CTkLabel(parent, text=label, font=(self.ui_font, 13, "bold"), text_color=self.text_muted).grid(
                row=row_idx, column=0, sticky="w", padx=15, pady=8)
            ctk.CTkLabel(parent, text=value, font=(self.ui_font, 13, "bold"), text_color=val_color).grid(
                row=row_idx, column=1, sticky="w", padx=10, pady=8)

        create_grid_row(info_frame, 0, "Log Reference:", f"#{log.get('log_id', 'N/A')}")
        create_grid_row(info_frame, 1, "Occurrence:", f"{log.get('timestamp', log.get('created_at', 'N/A'))}")

        # Employee Logic
        emp_name = log.get('employee_name', '').strip()
        user_id = log.get('user_id', 'N/A')
        if not emp_name or emp_name == "System / Not Found":
            name_match = re.search(r'password for (.*?)\(', raw_details)
            emp_name = name_match.group(1).strip() if name_match else "Unknown User"

        create_grid_row(info_frame, 2, "Account Name:", f"{emp_name} (ID: {user_id})")

        action = log.get('action', log.get('action_type', 'N/A'))
        create_grid_row(info_frame, 3, "Activity Type:", action, val_color=self.orange)

        # Narrative Box
        ctk.CTkLabel(info_frame, text="Full Narrative:", font=(self.ui_font, 13, "bold"),
                     text_color=self.text_muted).grid(row=4, column=0, sticky="nw", padx=15, pady=8)

        display_details = re.sub(r'\[REQ_PWD:.*?\]', '', raw_details).strip()

        narrative_box = ctk.CTkTextbox(info_frame, height=90, fg_color="#F8F9FA", border_width=1,
                                       border_color=self.color_border, text_color="black", font=(self.ui_font, 13))
        narrative_box.grid(row=4, column=1, sticky="nsew", padx=10, pady=10)
        narrative_box.insert("1.0", display_details)
        narrative_box.configure(state="disabled")

        info_frame.grid_columnconfigure(1, weight=1)

        # Actions
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))

        if action == "PASSWORD RESET REQUEST" and log.get('is_read') == 0:
            ctk.CTkButton(btn_frame, text="✅ Approve", fg_color=self.primary, hover_color="#1E8449",
                          font=(self.ui_font, 13, "bold"), width=130, height=40, corner_radius=8,
                          command=lambda: self.approve_password(log, raw_details, popup)).pack(side="left", padx=8)

            ctk.CTkButton(btn_frame, text="❌ Deny", fg_color="transparent", border_width=1, border_color=self.red,
                          text_color=self.red, hover_color="#FDEDEC", font=(self.ui_font, 13, "bold"), width=100,
                          height=40, corner_radius=8,
                          command=lambda: self.deny_password(log, popup)).pack(side="left", padx=8)
        else:
            ctk.CTkButton(btn_frame, text="Close Report", fg_color=self.color_sidebar, hover_color="#2A2F6C",
                          font=(self.ui_font, 13, "bold"), width=180, height=40, corner_radius=8,
                          command=popup.destroy).pack()

            if log.get('is_read') == 0:
                try:
                    self.engine.mark_alert_as_read(log.get('log_id'))
                    self.refresh_logs()
                except Exception:
                    pass

    def approve_password(self, log, raw_details, window):
        user_id = log.get('user_id')
        if not user_id: return messagebox.showerror("Error", "User ID missing.", parent=window)

        if self.engine.approve_pending_password(user_id):
            self.engine.log_security_event(user_id, "PASSWORD RESET APPROVED", "Kapitan approved the reset.")
            self.engine.mark_alert_as_read(log.get('log_id'))
            messagebox.showinfo("Success", "Account successfully reset!", parent=window)
            window.destroy()
            self.refresh_logs()
        else:
            messagebox.showerror("Error", "Request failed or expired.", parent=window)

    def deny_password(self, log, window):
        user_id = log.get('user_id')
        self.engine.clear_pending_reset(user_id)
        self.engine.log_security_event(user_id, "PASSWORD RESET DENIED", "Kapitan denied the request.")
        self.engine.mark_alert_as_read(log.get('log_id'))
        messagebox.showinfo("Denied", "Request has been denied.", parent=window)
        window.destroy()
        self.refresh_logs()
