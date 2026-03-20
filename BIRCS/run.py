import customtkinter as ctk
from bircs_package.login_screen import LoginWindow
from bircs_package.engine import DatabaseEngine  # <--- Make sure this matches!

if __name__ == "__main__":
    root = ctk.CTk()

    # Initialize the ONE engine
    system_engine = DatabaseEngine()

    # Pass it to the login window
    app = LoginWindow(root, system_engine)

    root.mainloop()