import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = 'tasks.json'

class Task:
    def __init__(self, id, title, description, due_date, priority, category):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date  # YYYY-MM-DD string
        self.priority = priority  # int
        self.category = category

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'priority': self.priority,
            'category': self.category
        }

    @staticmethod
    def from_dict(d):
        return Task(
            d['id'], d['title'], d['description'],
            d['due_date'], d['priority'], d['category']
        )

class TaskManager:
    def __init__(self, username):
        self.username = username
        self.data = self._load_data()
        # ensure user key exists
        if 'users' not in self.data:
            self.data['users'] = {}
        if username not in self.data['users']:
            self.data['users'][username] = []
        self._save()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_tasks(self):
        return [Task.from_dict(d) for d in self.data['users'][self.username]]

    def add_task(self, task):
        self.data['users'][self.username].append(task.to_dict())
        self._save()

    def update_task(self, task):
        tasks = self.data['users'][self.username]
        for i, d in enumerate(tasks):
            if d['id'] == task.id:
                tasks[i] = task.to_dict()
                break
        self._save()

    def delete_task(self, task_id):
        tasks = self.data['users'][self.username]
        self.data['users'][self.username] = [d for d in tasks if d['id'] != task_id]
        self._save()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.geometry("800x600")
        self.task_manager = None
        self._login_screen()

    def _login_screen(self):
        frame = ttk.Frame(self)
        frame.pack(pady=200)
        ttk.Label(frame, text="Enter Username:").grid(row=0, column=0, padx=5)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Login", command=lambda: self._on_login(frame)).grid(row=1, columnspan=2, pady=10)

    def _on_login(self, frame):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return
        self.task_manager = TaskManager(username)
        frame.destroy()
        self._main_screen()

    def _main_screen(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text="Add Task", command=self._add_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit Task", command=self._edit_task).pack(side='left')
        ttk.Button(toolbar, text="Delete Task", command=self._delete_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Report", command=self._show_report).pack(side='right', padx=5)
        
        # Filter by category
        ttk.Label(toolbar, text="Filter:").pack(side='left', padx=(20,5))
        self.filter_var = tk.StringVar(value="All")
        choices = ["All"] + sorted({t.category for t in self.task_manager.get_tasks()})
        self.filter_menu = ttk.OptionMenu(toolbar, self.filter_var, *choices, command=lambda _: self._load_tasks())
        self.filter_menu.pack(side='left')

        # Treeview
        cols = ('Title','Due Date','Priority','Category')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self._sort_by(_c))
            self.tree.column(c, width=150)
        self.tree.pack(fill='both', expand=True, pady=10)
        self._load_tasks()

    def _load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        tasks = self.task_manager.get_tasks()
        f = self.filter_var.get()
        for t in tasks:
            if f != "All" and t.category != f:
                continue
            self.tree.insert('', 'end', iid=t.id, values=(t.title, t.due_date, t.priority, t.category))

    def _get_selected_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "No task selected.")
            return None
        task_id = sel[0]
        for t in self.task_manager.get_tasks():
            if t.id == task_id:
                return t
        return None

    def _add_task(self):
        TaskDialog(self, "Add Task", self.task_manager)

    def _edit_task(self):
        t = self._get_selected_task()
        if t:
            TaskDialog(self, "Edit Task", self.task_manager, task=t)

    def _delete_task(self):
        t = self._get_selected_task()
        if t and messagebox.askyesno("Confirm", "Delete this task?"):
            self.task_manager.delete_task(t.id)
            self._load_tasks()

    def _sort_by(self, col):
        tasks = self.task_manager.get_tasks()
        keymap = {'Title': lambda t: t.title,
                  'Due Date': lambda t: datetime.fromisoformat(t.due_date),
                  'Priority': lambda t: t.priority,
                  'Category': lambda t: t.category}
        tasks.sort(key=keymap[col])
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in tasks:
            f = self.filter_var.get()
            if f != "All" and t.category != f:
                continue
            self.tree.insert('', 'end', iid=t.id, values=(t.title, t.due_date, t.priority, t.category))

    def _show_report(self):
        data = self.task_manager.get_tasks()
        counts = {}
        for t in data:
            counts[t.category] = counts.get(t.category, 0) + 1
        # Pie chart
        fig = Figure(figsize=(4,4))
        ax = fig.add_subplot(111)
        ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%')
        report_win = tk.Toplevel(self)
        report_win.title("Task Categories Report")
        canvas = FigureCanvasTkAgg(fig, master=report_win)
        canvas.draw()
        canvas.get_tk_widget().pack()

class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title, manager, task=None):
        super().__init__(parent)
        self.manager = manager
        self.task = task
        self.title(title)
        self.resizable(False, False)
        # form fields
        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky='e')
        self.title_var = tk.StringVar(value=task.title if task else "")
        ttk.Entry(self, textvariable=self.title_var).grid(row=0, column=1)
        ttk.Label(self, text="Description:").grid(row=1, column=0, sticky='e')
        self.desc_var = tk.StringVar(value=task.description if task else "")
        ttk.Entry(self, textvariable=self.desc_var).grid(row=1, column=1)
        ttk.Label(self, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, sticky='e')
        self.due_var = tk.StringVar(value=task.due_date if task else datetime.now().date().isoformat())
        ttk.Entry(self, textvariable=self.due_var).grid(row=2, column=1)
        ttk.Label(self, text="Priority (1-5):").grid(row=3, column=0, sticky='e')
        self.prio_var = tk.IntVar(value=task.priority if task else 3)
        ttk.Spinbox(self, from_=1, to=5, textvariable=self.prio_var).grid(row=3, column=1)
        ttk.Label(self, text="Category:").grid(row=4, column=0, sticky='e')
        self.cat_var = tk.StringVar(value=task.category if task else "General")
        ttk.Entry(self, textvariable=self.cat_var).grid(row=4, column=1)
        ttk.Button(self, text="Save", command=self._on_save).grid(row=5, columnspan=2, pady=10)

    def _on_save(self):
        # validate
        try:
            datetime.fromisoformat(self.due_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return
        t = self.task or Task(str(uuid.uuid4()), '', '', '', 1, '')
        t.title = self.title_var.get().strip()
        t.description = self.desc_var.get().strip()
        t.due_date = self.due_var.get()
        t.priority = self.prio_var.get()
        t.category = self.cat_var.get().strip() or 'General'
        if self.task:
            self.manager.update_task(t)
        else:
            self.manager.add_task(t)
        self.master._load_tasks()
        self.destroy()

if __name__ == '__main__':
    App().mainloop()