import tkinter as tk
from utils.auth import authenticate

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Username").pack()
        self.username = tk.Entry(self)
        self.username.pack()

        tk.Label(self, text="Password").pack()
        self.password = tk.Entry(self, show="*")
        self.password.pack()

        tk.Button(self, text="Login", command=self.login).pack()
        tk.Button(self, text="Register", command=master.switch_to_register).pack()

    def login(self):
        user = authenticate(self.master.db, self.username.get(), self.password.get())
        if user:
            self.master.user = user
            self.master.switch_to_tasks()
        else:
            tk.Label(self, text="Login failed!", fg="red").pack()
