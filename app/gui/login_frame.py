import tkinter as tk
from app.utils.auth import authenticate

# Login Frame class, inherits from tk.Frame
class LoginFrame(tk.Frame):
    def __init__(self, master):
        # Links to the master tkinter window
        super().__init__(master)

        # Username entry field
        tk.Label(self, text="Username").pack()
        self.username = tk.Entry(self)
        self.username.pack()

        # Password entry field, hidden text *
        tk.Label(self, text="Password").pack()
        self.password = tk.Entry(self, show="*")
        self.password.pack()

        # Login button calls login()
        tk.Button(self, text="Login", command=self.login).pack()
        # Register button calls switch_to_register()
        tk.Button(self, text="Register", command=master.switch_to_register).pack()

    # Login function, authenticates user and password before switching to tasks frame
    def login(self):
        # Call authenticate helper function in utils
        user = authenticate(self.master.db, self.username.get(), self.password.get())
        # IF valid login, switch to tasks frame
        if user:
            self.master.user = user
            self.master.switch_to_tasks()
        # ELSE display failed login text
        else:
            tk.Label(self, text="Login failed!", fg="red").pack()
