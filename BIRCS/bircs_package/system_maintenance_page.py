import customtkinter as ctk
from tkinter import messagebox
import os
import glob
import time
import sys         # <--- DAGDAG MO 'TO
import subprocess  # <--- DAGDAG MO 'TO


class SystemMaintenancePage:
    def __init__(self, parent_frame, engine, admin_window):
        self.engine = engine
        self.parent_window = admin_window

        self.text_dark = "#2B2B2B"
        self.primary = "#27AE60"
        self.blue = "#2980B9"
        self.red = "#E74C3C"
        self.orange = "#E79124"

        # 1. I-setup ang totoong Backup Folder
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.backup_dir = os.path.join(current_dir, "backups", "sql_versions")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        self.container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.build_ui()

    def build_ui(self):
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="⚙️ Database & System Maintenance", font=("Arial", 24, "bold"),
                     text_color=self.text_dark).pack(side="left")

        controls_frame = ctk.CTkFrame(self.container, fg_color="white", corner_radius=10, border_width=1,
                                      border_color="#E0E0E0")
        controls_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(controls_frame, text="Quick Controls (RFID Required)", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20, pady=(15, 10))

        btn_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(btn_row, text="💾 Manual Backup", height=40, font=("Arial", 12, "bold"), fg_color=self.blue,
                      hover_color="#1F618D", command=self.manual_backup).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="⏱️ Auto-Backup Schedule", height=40, font=("Arial", 12, "bold"),
                      fg_color=self.orange, hover_color="#C67B1D", text_color="white", command=self.set_schedule).pack(
            side="left", padx=10)
        ctk.CTkButton(btn_row, text="🧹 Optimise (Delete Oldest)", height=40, font=("Arial", 12, "bold"),
                      fg_color=self.red, hover_color="#B03A2E", command=self.optimise_backups).pack(side="right")

        list_frame = ctk.CTkFrame(self.container, fg_color="white", corner_radius=10, border_width=1,
                                  border_color="#E0E0E0")
        list_frame.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        ctk.CTkLabel(list_frame, text="Local Backup Repository", font=("Arial", 16, "bold"),
                     text_color=self.text_dark).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(list_frame, text="Select a backup version below to force a system rollback.",
                     font=("Arial", 12, "italic"), text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

        self.backup_list_area = ctk.CTkScrollableFrame(list_frame, fg_color="#F8F9F5")
        self.backup_list_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_backup_list()

    # ==========================================
    # 🔒 UNIVERSAL KAPITAN AUTHENTICATOR
    # ==========================================
    def prompt_rfid(self, action_name):
        """Reusable function para humingi ng RFID sa bawat action"""
        scan = ctk.CTkInputDialog(text=f"Action: {action_name}\nPlease scan Kapitan RFID to authorize:",
                                  title="Security Check").get_input()
        if not scan:
            return False

        success, _ = self.engine.verify_kapitan_access(scan)
        if not success:
            messagebox.showerror("Access Denied", "Invalid RFID. Unauthorized action stopped.")
            return False
        return True

    # ==========================================
    # ACTION LOGIC
    # ==========================================
    def manual_backup(self):
        if not self.prompt_rfid("Manual Database Backup"): return

        timestamp = time.strftime("%Y-%m-%d_%I%M%p")
        zip_file_path = os.path.join(self.backup_dir, f"BICRS_Backup_{timestamp}.zip")

        # 🚀 TATAWAGIN NA NATIN YUNG ENGINE!
        success, message = self.engine.create_database_backup(zip_file_path)

        if success:
            messagebox.showinfo("Backup Successful", message)
            self.refresh_backup_list()
        else:
            messagebox.showerror("Backup Failed", message)

    def trigger_rollback(self, filename):
        if not self.prompt_rfid(f"System Rollback ({filename})"): return

        if messagebox.askyesno("CRITICAL WARNING",
                               f"You are about to overwrite the current database with:\n{filename}\n\nDon't worry, a safety backup of your CURRENT data will be created first.\n\nDo you want to proceed?"):

            # 🛡️ YUNG PATH NG TARGET ROLLBACK
            target_zip = os.path.join(self.backup_dir, filename)

            # 🛡️ YUNG PATH NG SAFETY NET BACKUP NATIN
            timestamp = time.strftime("%Y-%m-%d_%I%M%p")
            emergency_zip = os.path.join(self.backup_dir, f"SAFETY_NET_BeforeRollback_{timestamp}.zip")

            messagebox.showwarning("Rollback Initiated",
                                   "System is now executing Disaster Recovery Protocol. Please wait, do not turn off the system...")

            # 🚀 TATAWAGIN NA NATIN YUNG TIME MACHINE ENGINE!
            success, message = self.engine.execute_rollback(target_zip, emergency_zip)

            if success:
                messagebox.showinfo("Rollback Complete", f"{message}\n\nThe system will now restart to apply changes.")

                # 🚀 THE SILENT NINJA RESTART
                # (WALA NANG IMPORTS DITO, DAHIL NASA TAAS NA SILA LAHAT)

                script_path = os.path.abspath(sys.argv[0])
                python_exe = sys.executable

                # 0x08000000 ay ang code ni Windows para sa "CREATE_NO_WINDOW"
                CREATE_NO_WINDOW = 0x08000000

                subprocess.Popen([python_exe, script_path], creationflags=CREATE_NO_WINDOW)

                # Patayin ang lumang app
                self.parent_window.destroy()
                sys.exit()
            else:
                messagebox.showerror("Rollback Failed", message)

    def set_schedule(self):
        if not self.prompt_rfid("Modify Backup Schedule"): return

        sched_win = ctk.CTkToplevel(self.parent_window)
        sched_win.title("Auto-Backup Timer")
        sched_win.geometry("300x200")
        sched_win.transient(self.parent_window)
        sched_win.grab_set()

        ctk.CTkLabel(sched_win, text="Backup Interval:", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        var = ctk.StringVar(value="Every 12 Hours")
        ctk.CTkOptionMenu(sched_win, variable=var, values=["Every 6 Hours", "Every 12 Hours", "Daily (Midnight)"],
                          fg_color=self.orange).pack(pady=10)

        ctk.CTkButton(sched_win, text="Save Settings", fg_color=self.primary,
                      command=lambda: [messagebox.showinfo("Saved", f"Schedule set to: {var.get()}"),
                                       sched_win.destroy()]).pack(pady=20)

    def optimise_backups(self):
        if not self.prompt_rfid("Optimise (Delete Oldest Backup)"): return

        # Basahin lahat ng ZIP files at tanggalin ang pinakaluma
        files = glob.glob(os.path.join(self.backup_dir, "*.zip"))
        if not files:
            messagebox.showinfo("Optimise", "Storage is empty. No backups to delete.")
            return

        if messagebox.askyesno("Confirm Delete",
                               "Are you sure you want to permanently delete the OLDEST backup version?"):
            files.sort(key=os.path.getmtime)  # I-sort mula pinakaluma hanggang pinakabago
            oldest_file = files[0]  # Kunin yung nasa top ng list (oldest)

            try:
                os.remove(oldest_file)  # Burahin sa computer!
                messagebox.showinfo("Optimised", "Oldest backup successfully removed to free up space.")
                self.refresh_backup_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")


    # ==========================================
    # DYNAMIC LIST RENDERER
    # ==========================================
    def refresh_backup_list(self):
        for widget in self.backup_list_area.winfo_children(): widget.destroy()

        # Basahin ang TOTOONG files sa folder
        search_pattern = os.path.join(self.backup_dir, "*.zip")
        files = glob.glob(search_pattern)

        # I-sort mula pinakabago hanggang pinakaluma para laging nasa taas ang latest
        files.sort(key=os.path.getmtime, reverse=True)

        if not files:
            ctk.CTkLabel(self.backup_list_area, text="No backup files found in the repository.",
                         font=("Arial", 12, "italic"), text_color="gray").pack(pady=40)
            return

        for file_path in files:
            filename = os.path.basename(file_path)
            size_bytes = os.path.getsize(file_path)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            if size_mb == 0.0: size_mb = 0.01  # Fallback lang para hindi 0.0 MB ang makita

            # Kunin ang date created
            mtime = os.path.getmtime(file_path)
            date_str = time.strftime('%b %d, %Y - %I:%M %p', time.localtime(mtime))

            row = ctk.CTkFrame(self.backup_list_area, fg_color="white", corner_radius=5, border_width=1,
                               border_color="#E0E0E0")
            row.pack(fill="x", pady=5)

            ctk.CTkLabel(row, text="🗄️", font=("Arial", 20)).pack(side="left", padx=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(info, text=filename, font=("Arial", 12, "bold"), text_color=self.text_dark).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Size: {size_mb} MB | Saved: {date_str}", font=("Arial", 10),
                         text_color="gray").pack(anchor="w")

            ctk.CTkButton(row, text="🔄 Rollback", width=100, fg_color="#F0F0F0", text_color=self.red,
                          hover_color="#FADBD8", font=("Arial", 11, "bold"),
                          command=lambda f=filename: self.trigger_rollback(f)).pack(side="right", padx=15)
