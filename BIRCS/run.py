import customtkinter as ctk
from bircs_package.login_screen import LoginWindow
from bircs_package.engine import DatabaseEngine  # <--- Make sure this matches!

ctk.set_window_scaling(1.0)
ctk.set_widget_scaling(1.0)

if __name__ == "__main__":
    root = ctk.CTk()

    # Initialize the ONE engine
    system_engine = DatabaseEngine()

    # Pass it to the login window
    app = LoginWindow(root, system_engine)

    root.mainloop()
