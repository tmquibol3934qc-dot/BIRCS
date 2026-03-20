import customtkinter as ctk


class ForgotPasswordDialog:
    def __init__(self, parent_window):
        # Create a Floating Window (Toplevel)
        self.window = ctk.CTkToplevel(parent_window)

        # --- MAKE WINDOW FRAMELESS ---
        self.window.overrideredirect(True)

        self.window.title("Recovery")
        self.window.geometry("400x380")
        # self.window.resizable(False, False) # Not needed

        # Make it float on top and look like a modal
        self.window.transient(parent_window)  # Float over parent
        self.window.grab_set()  # Prevent clicking the background window

        # Center the popup relative to the screen
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = int((sw / 2) - (400 / 2))
        y = int((sh / 2) - (380 / 2))
        self.window.geometry(f"+{x}+{y}")

        self.window.configure(fg_color="white")

        self.create_ui()

    def create_ui(self):
        # Add a border frame for visual definition
        main_frame = ctk.CTkFrame(self.window, fg_color="white", border_width=2, border_color="#E79124")
        main_frame.pack(fill="both", expand=True)

        # 1. Title
        ctk.CTkLabel(main_frame, text="Enter Your Employee ID",
                     font=("Poppins", 16, "bold"), text_color="#333").pack(pady=(30, 20))

        # 2. Input Box
        self.id_entry = ctk.CTkEntry(main_frame, width=300, height=45,
                                     placeholder_text="Employee ID",
                                     border_color="#E0E0E0", border_width=2,
                                     fg_color="#F9F9F9", text_color="black",
                                     font=("Poppins", 12))
        self.id_entry.pack(pady=(0, 20))

        # 3. Submit Button (Solid Orange)
        self.submit_btn = ctk.CTkButton(main_frame, text="Submit", width=300, height=40,
                                        fg_color="#E79124", hover_color="#C67B1D",
                                        font=("Poppins", 13, "bold"),
                                        command=self.window.destroy)  # Just closes for now
        self.submit_btn.pack(pady=(0, 10))

        # 4. Cancel Button (White with Orange Border)
        self.cancel_btn = ctk.CTkButton(main_frame, text="Cancel", width=300, height=40,
                                        fg_color="white", hover_color="#F0F0F0",
                                        border_color="#E79124", border_width=2,
                                        text_color="#E79124", font=("Poppins", 13, "bold"),
                                        command=self.window.destroy)
        self.cancel_btn.pack(pady=(0, 20))

        # 5. Extra Links (Recovery Key / Email OTP)
        link_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        link_frame.pack(pady=0)

        l1 = ctk.CTkLabel(link_frame, text="Use Recovery Key Instead",
                          font=("Poppins", 11), text_color="#6A5ACD", cursor="hand2")
        l1.pack()

        l2 = ctk.CTkLabel(link_frame, text="Reset via Email OTP",
                          font=("Poppins", 11), text_color="#6A5ACD", cursor="hand2")
        l2.pack()