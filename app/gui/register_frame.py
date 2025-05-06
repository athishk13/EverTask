import tkinter as tk
from app.utils.auth import create_user

class RegisterFrame(tk.Frame):
    """Register Frame class. Inherits from tk.Frame"""
    def __init__(self, master):
        """Init for Register Frame class. Input: Main App window."""
        # Links to the master tkinter window
        super().__init__(master)

        # Username entry field
        tk.Label(self, text="New Username").pack()
        self.username = tk.Entry(self)
        self.username.pack()

        # Password entry field, hidden text *
        tk.Label(self, text="New Password").pack()
        self.password = tk.Entry(self, show="*")
        self.password.pack()

        # Register button calls register()
        tk.Button(self, text="Register", command=self.register).pack()
        # Back button calls switch_to_login()
        tk.Button(self, text="Back", command=master.switch_to_login).pack()

    def register(self):
        """Register function, creates a new user before returning to login screen"""
        # Call create_user helper function in utils
        # IF user does not already exist, switch to login screen
        if create_user(self.master.db, self.username.get(), self.password.get()):
            self.master.switch_to_login()
        # ELSE display an error message
        else:
            tk.Label(self, text="Error! User already exists.", fg="red").pack()


