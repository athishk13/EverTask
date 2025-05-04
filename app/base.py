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
    def __init__(self, id, title, description, due_date, due_time='00:00', priority=1, category='General', completed=False):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date  # YYYY-MM-DD
        self.due_time = due_time  # HH:MM  
        self.priority = priority
        self.category = category
        self.completed = completed 

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'due_time': self.due_time, 
            'priority': self.priority,
            'category': self.category,
            'completed': self.completed  
        }

    @staticmethod
    def from_dict(d):
        return Task(
            d['id'],
            d['title'],
            d['description'],
            d['due_date'],
            d.get('due_time', '00:00'), 
            d.get('priority', 1),
            d.get('category', 'General'),
            d.get('completed', False)  
        )

class TaskManager:
    def __init__(self, username):
        self.username = username
        self.data = self._load_data()
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

        # Treeview with new columns
        cols = ('Title', 'Due Date', 'Due Time', 'Priority', 'Category', 'Completed')  
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self._sort_by(_c))
            self.tree.column(c, width=100)
        self.tree.pack(fill='both', expand=True, pady=10)
        # Bind click to toggle completion
        self.tree.bind('<Button-1>', self._on_tree_click)  

        self._load_tasks()

    def _load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        tasks = self.task_manager.get_tasks()
        f = self.filter_var.get()
        for t in tasks:
            if f != "All" and t.category != f:
                continue
            status = '☑' if t.completed else '☐'  
            self.tree.insert('', 'end', iid=t.id, values=(t.title, t.due_date, t.due_time, t.priority, t.category, status))

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
        keymap = {
            'Title': lambda t: t.title,
            'Due Date': lambda t: datetime.fromisoformat(t.due_date),
            'Due Time': lambda t: t.due_time, 
            'Priority': lambda t: t.priority,
            'Category': lambda t: t.category,
            'Completed': lambda t: t.completed 
        }
        tasks.sort(key=keymap[col])
        for row in self.tree.get_children():
            self.tree.delete(row)
        f = self.filter_var.get()
        for t in tasks:
            if f != "All" and t.category != f:
                continue
            status = '☑' if t.completed else '☐'
            self.tree.insert('', 'end', iid=t.id, values=(t.title, t.due_date, t.due_time, t.priority, t.category, status))

    def _on_tree_click(self, event):
        """Toggle completion status when clicking the checkbox column."""
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        col = self.tree.identify_column(event.x)
        # Completed is the last column
        if col == f"#{len(self.tree['columns'])}":
            row_id = self.tree.identify_row(event.y)
            if row_id:
                t = next((task for task in self.task_manager.get_tasks() if task.id == row_id), None)
                if t:
                    t.completed = not t.completed  
                    self.task_manager.update_task(t)
                    self._load_tasks()

    def _show_report(self):
        data = self.task_manager.get_tasks()
        counts = {}
        for t in data:
            counts[t.category] = counts.get(t.category, 0) + 1
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

        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky='e')
        self.title_var = tk.StringVar(value=task.title if task else "")
        ttk.Entry(self, textvariable=self.title_var).grid(row=0, column=1)

        ttk.Label(self, text="Description:").grid(row=1, column=0, sticky='e')
        self.desc_var = tk.StringVar(value=task.description if task else "")
        ttk.Entry(self, textvariable=self.desc_var).grid(row=1, column=1)

        ttk.Label(self, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, sticky='e')
        self.due_var = tk.StringVar(value=task.due_date if task else datetime.now().date().isoformat())
        ttk.Entry(self, textvariable=self.due_var).grid(row=2, column=1)

        if task:
            h24, m = map(int, task.due_time.split(':'))
            if h24 == 0:
                hour12, ampm = 12, 'AM'
            elif h24 < 12:
                hour12, ampm = h24, 'AM'
            elif h24 == 12:
                hour12, ampm = 12, 'PM'
            else:
                hour12, ampm = h24 - 12, 'PM'
        else:
            hour12, m, ampm = 12, 0, 'AM'
        self.hour_var = tk.IntVar(value=hour12)  
        self.min_var = tk.IntVar(value=m)
        self.ampm_var = tk.StringVar(value=ampm)  
        time_frame = ttk.Frame(self)
        time_frame.grid(row=3, column=1)
        ttk.Spinbox(time_frame, from_=1, to=12, textvariable=self.hour_var, width=2).pack(side='left')  
        ttk.Label(time_frame, text=":").pack(side='left')
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.min_var, width=2).pack(side='left')
        ttk.OptionMenu(time_frame, self.ampm_var, self.ampm_var.get(), 'AM', 'PM').pack(side='left', padx=5)  

        ttk.Label(self, text="Priority (1-5):").grid(row=4, column=0, sticky='e')
        self.prio_var = tk.IntVar(value=task.priority if task else 3)
        ttk.Spinbox(self, from_=1, to=5, textvariable=self.prio_var).grid(row=4, column=1)

        ttk.Label(self, text="Category:").grid(row=5, column=0, sticky='e')
        self.cat_var = tk.StringVar(value=task.category if task else "General")
        ttk.Entry(self, textvariable=self.cat_var).grid(row=5, column=1)

        ttk.Button(self, text="Save", command=self._on_save).grid(row=6, columnspan=2, pady=10)

    def _on_save(self):
        try:
            datetime.fromisoformat(self.due_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return
        # compute 24h hour from 12h+AM/PM
        h12 = self.hour_var.get() % 12
        if self.ampm_var.get() == 'PM':
            h24 = h12 + 12
        else:
            h24 = h12
        due_time = f"{h24:02d}:{self.min_var.get():02d}"  
        t = self.task or Task(str(uuid.uuid4()), '', '', '', '00:00', 1, '')
        t.title = self.title_var.get().strip()
        t.description = self.desc_var.get().strip()
        t.due_date = self.due_var.get()
        t.due_time = due_time
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
