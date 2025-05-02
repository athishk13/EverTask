import tkinter as tk
import uuid
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from datetime import datetime

from models.task import Task

class TaskListFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {master.user.username}").pack()

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text="Add Task", command=self.add_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit Task", command=self.add_task).pack(side='left')
        ttk.Button(toolbar, text="Delete Task", command=self.add_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Report", command=self.add_task).pack(side='right', padx=5)

        # Filter by category
        ttk.Label(toolbar, text="Filter:").pack(side='left', padx=(200, 5))
        self.filter_var = tk.StringVar(value="All")
        choices = ["All"] + sorted({task.category for task in self.master.db.query(Task).all()})
        self.filter_menu = ttk.OptionMenu(toolbar, self.filter_var, *choices, command=lambda _: self.refresh_tasks())
        self.filter_menu.pack(side='left')

        # Treeview
        cols = ('Title', 'Due Date', 'Priority', 'Category')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self.sort_by(_c))
            self.tree.column(c, width=150)
        self.tree.pack(fill='both', expand=True, pady=10)
        self.refresh_tasks()

    def refresh_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filter_category = self.filter_var.get()
        tasks_query = self.master.db.query(Task)

        # Apply category filter if it's not "All"
        if filter_category != "All":
            tasks_query = tasks_query.filter_by(category=filter_category)

        tasks = tasks_query.all()

        # Insert tasks into the Treeview
        for task in tasks:
            self.tree.insert('', 'end', iid=task.task_id,
                             values=(task.title, task.due_date, task.priority, task.category))

    def add_task(self):
        # Function to open the TaskDialog for adding a new task
        TaskDialog(self, None)

    def edit_task(self):
        task = self.get_selected_task()
        if task:
            TaskDialog(self, task)

    def delete_task(self):
        task = self.get_selected_task()
        if task and messagebox.askyesno("Confirm", "Delete this task?"):
            self.master.db.delete(task)
            self.master.db.commit()
            self.refresh_tasks()

    def sort_by(self, col):
        keymap = {'Title': lambda t: t.title,
                  'Due Date': lambda t: datetime.strptime(t.due_date, "%Y-%m-%d"),
                  'Priority': lambda t: t.priority,
                  'Category': lambda t: t.category}

        tasks = sorted(self.master.db.query(Task).all(), key=keymap[col])
        for row in self.tree.get_children():
            self.tree.delete(row)
        for task in tasks:
            self.tree.insert('', 'end', iid=task.task_id,
                             values=(task.title, task.due_date, task.priority, task.category))

    def show_report(self):
        tasks = self.master.db.query(Task).all()
        counts = {}
        for task in tasks:
            counts[task.category] = counts.get(task.category, 0) + 1

        # Pie chart
        fig = Figure(figsize=(4, 4))
        ax = fig.add_subplot(111)
        ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%')
        report_win = tk.Toplevel(self)
        report_win.title("Task Categories Report")
        canvas = FigureCanvasTkAgg(fig, master=report_win)
        canvas.draw()
        canvas.get_tk_widget().pack()

class TaskDialog(tk.Toplevel):
    def __init__(self, master, task=None):
        super().__init__(master)
        self.master = master  # master is TaskListFrame
        self.task = task
        self.session = self.master.master.db

        self.title("Edit Task" if task else "New Task")
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

        ttk.Label(self, text="Priority (1-5):").grid(row=3, column=0, sticky='e')
        self.prio_var = tk.IntVar(value=task.priority if task else 3)
        ttk.Spinbox(self, from_=1, to=5, textvariable=self.prio_var).grid(row=3, column=1)

        ttk.Label(self, text="Category:").grid(row=4, column=0, sticky='e')
        self.cat_var = tk.StringVar(value=task.category if task else "General")
        ttk.Entry(self, textvariable=self.cat_var).grid(row=4, column=1)

        ttk.Button(self, text="Save", command=self._on_save).grid(row=5, columnspan=2, pady=10)

    def _on_save(self):
        try:
            datetime.fromisoformat(self.due_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return

        if not self.task:
            self.task = Task(
                task_id=str(uuid.uuid4()),
                user_id=int(self.master.master.user.user_id),
                title=self.title_var.get().strip(),
                description=self.desc_var.get().strip(),
                due_date=datetime.fromisoformat(self.due_var.get()).date(),
                priority=int(self.prio_var.get()),
                category=self.cat_var.get().strip() or "General"
            )
            self.session.add(self.task)
        else:
            self.task.title = self.title_var.get().strip()
            self.task.description = self.desc_var.get().strip()
            self.task.due_date = datetime.fromisoformat(self.due_var.get()).date()
            self.task.priority = self.prio_var.get()
            self.task.category = self.cat_var.get().strip() or "General"

        self.session.commit()
        self.master.refresh_tasks()
        self.destroy()

