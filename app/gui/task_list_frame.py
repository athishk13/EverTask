import tkinter as tk
from models.task import Task

class TaskListFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {master.user.username}").pack()
        self.refresh_tasks()

        self.new_task = tk.Entry(self)
        self.new_task.pack()
        tk.Button(self, text="Add Task", command=self.add_task).pack()
        tk.Button(self, text="Logout", command=master.switch_to_login).pack()

    def refresh_tasks(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text").startswith("Task:"):
                widget.destroy()

        tasks = self.master.db.query(Task).filter_by(user_id=self.master.user.user_id).all()
        for task in tasks:
            tk.Label(self, text=f"Task: {task.title}").pack()

    def add_task(self):
        task = Task(title=self.new_task.get(), user_id=self.master.user.user_id)
        self.master.db.add(task)
        self.master.db.commit()
        self.new_task.delete(0, tk.END)
        self.refresh_tasks()
