import tkinter as tk
from utils.auth import create_user

class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="New Username").pack()
        self.username = tk.Entry(self)
        self.username.pack()

        tk.Label(self, text="New Password").pack()
        self.password = tk.Entry(self, show="*")
        self.password.pack()

        tk.Button(self, text="Register", command=self.register).pack()
        tk.Button(self, text="Back", command=master.switch_to_login).pack()

    def register(self):
        create_user(self.master.db, self.username.get(), self.password.get())
        self.master.switch_to_login()
