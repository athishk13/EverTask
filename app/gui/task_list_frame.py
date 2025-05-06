import tkinter as tk
import uuid
import threading
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from app.models.task import Task

class TaskListFrame(tk.Frame):
    """Main tasks frame. Inherits from tk.Frame"""
    def __init__(self, master):
        # Links to master window
        super().__init__(master)

        # Lists of tasks to prevent repeated database queries
        self.all_tasks = []
        self.sorted_column = None
        self.sort_reverse = False

        # Display welcome message
        tk.Label(self, text=f"Welcome, {master.user.username}").pack()

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text="Add Task", command=self.add_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Edit Task", command=self.edit_task).pack(side='left')
        ttk.Button(toolbar, text="Delete Task", command=self.delete_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Report", command=self.show_report).pack(side='right', padx=5)

        # Filter by category
        ttk.Label(toolbar, text="Filter:").pack(side='left', padx=(200, 5))
        self.filter_var = tk.StringVar(value="All")
        self.filter_menu = ttk.OptionMenu(toolbar, self.filter_var, "All")
        self.filter_menu.configure(width=10)
        self.filter_menu.pack(side='left')

        # Treeview
        cols = ('✓/x', 'Title', 'Due Date', 'Description', 'Priority', 'Category')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')

        # Tree Columns
        self.tree.column('✓/x', width=50, anchor="c")
        self.tree.column('Title', width=150)
        self.tree.column('Due Date', width=150)
        self.tree.column('Description', width=300)
        self.tree.column('Priority', width=70, anchor="c")
        self.tree.column('Category', width=150)

        # Tree column headings (sort when clicked)
        self.tree.heading('✓/x', text='✓/x', command=lambda: self.sort_by('✓/x'))
        self.tree.heading('Title', text='Title', command=lambda: self.sort_by('Title'))
        self.tree.heading('Due Date', text='Due Date', command=lambda: self.sort_by('Due Date'))
        self.tree.heading('Description', text='Description', command=lambda: self.sort_by('Description'))
        self.tree.heading('Priority', text='Priority', command=lambda: self.sort_by('Priority'))
        self.tree.heading('Category', text='Category', command=lambda: self.sort_by('Category'))

        # Draw the tree
        self.tree.pack(fill='both', expand=True, pady=10)

        # Bind double click action to mark tasks as completed
        self.tree.bind("<Double-1>", self.toggle_complete)

        # Refresh the display
        self.refresh_tasks()

    def toggle_complete(self, event):
        """Toggles complete status. Bound to double-click action. Input: event action."""
        # Check location of double-click
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        # IF location is the first column, toggle the complete status
        if item and column == '#1':
            task = next((t for t in self.all_tasks if t.task_id == item), None)
            if task:
                task.complete = not task.complete
                self.master.db.commit()
                self.refresh_tasks()

    def refresh_tasks(self):
        """Refresh the list of tasks, threaded to prevent mainloop blocking."""
        # Define function to be threaded
        def load_and_display_tasks():
            # Query tasks
            self.all_tasks = self.master.db.query(Task).all()
            # Update filter
            self.update_filter_menu()
            # Refresh display
            self.display_tasks()

        # Start the database operation in a new thread, auto close thread
        threading.Thread(target=load_and_display_tasks, daemon=True).start()

    def update_filter_menu(self):
        """Update the filter menu, Fills dropdown with all unique categories."""
        categories = sorted({task.category for task in self.all_tasks})
        menu = self.filter_menu['menu']
        menu.delete(0, 'end')
        menu.add_command(label="All", command=lambda: self.set_filter("All"))
        for cat in categories:
            menu.add_command(label=cat, command=lambda c=cat: self.set_filter(c))

    def set_filter(self, value):
        """Set the filter, changes the current filter category to display correctly. Input: filter category."""
        self.filter_var.set(value)
        self.display_tasks()

    def display_tasks(self):
        """Refresh the tree view display with tasks"""
        # Remove all tasks from the tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add all the tasks back in
        tasks = self.all_tasks
        if self.filter_var.get() != "All":
            tasks = [t for t in tasks if t.category == self.filter_var.get()]

        # Sort the selected column based on content
        if self.sorted_column:
            keymap = {
                '✓/x': lambda t: t.complete,
                'Title': lambda t: t.title,
                'Due Date': lambda t: datetime.strptime(t.due_date, "%Y-%m-%d") if isinstance(t.due_date, str) else t.due_date,
                'Description': lambda t: (t.description[:42] + '...') if len(t.description) > 45 else t.description,
                'Priority': lambda t: t.priority,
                'Category': lambda t: t.category
            }
            tasks.sort(key=keymap[self.sorted_column], reverse=self.sort_reverse)

        # Insert values for each task
        for task in tasks:
            # Custom output for completed column given boolean state
            complete_text = "✓" if task.complete else "x"
            # Otherwise fill with content
            self.tree.insert('', 'end', iid=task.task_id,
                             values=(complete_text, task.title, task.due_date, task.description, task.priority, task.category))

    def add_task(self):
        """Open window to add Task."""
        TaskDialog(self, None)

    def edit_task(self):
        """Open window to edit currently selected Task"""
        task = self.get_selected_task()
        if task:
            TaskDialog(self, task)

    def delete_task(self):
        """Delete the currently selected task, threaded to prevent blocking"""
        task = self.get_selected_task()
        # Open confirmation popup window
        if task and messagebox.askyesno("Confirm", "Delete this task?"):
            # Define delete function to thread
            def delete_task_in_thread():
                # Delete task in the background
                self.master.db.delete(task)
                self.master.db.commit()
                self.refresh_tasks()
            # Thread the delete operation
            threading.Thread(target=delete_task_in_thread, daemon=True).start()

    def get_selected_task(self):
        """Helper function to get the selected task from treeview selection."""
        sel = self.tree.selection()
        # If no selection, display a warning popup window
        if not sel:
            messagebox.showwarning("Warning", "No task selected.")
            return None
        # Obtain the task_id
        task_id = sel[0]
        # Return the corresponding task to the unique task_id
        return next((t for t in self.all_tasks if t.task_id == task_id), None)

    def sort_by(self, col):
        """Helper function that determines the next state of the sort function. Input: column to sort"""
        # Toggle the sorted by status according to the column
        if self.sorted_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sorted_column = col
            self.sort_reverse = False

        # Refresh the display
        self.display_tasks()

    def show_report(self):
        """Display the category distribution pie chart"""
        counts = {}
        for task in self.all_tasks:
            category = "Complete" if task.complete else task.category
            counts[category] = counts.get(category, 0) + 1

        fig = Figure(figsize=(4, 4))
        ax = fig.add_subplot(111)
        ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%')
        report_win = tk.Toplevel(self)
        report_win.title("Task Categories Report")
        canvas = FigureCanvasTkAgg(fig, master=report_win)
        canvas.draw()
        canvas.get_tk_widget().pack()

class TaskDialog(tk.Toplevel):
    """TaskDialog class. Popup window for adding and editing tasks. Inherits from tk.TopLevel."""
    def __init__(self, master, task=None):
        """Init for TaskDialog class. Input: Task list Frame, selected task (optional)."""
        # Link to tasks frame
        super().__init__(master)
        self.master = master
        self.task = task
        self.session = self.master.master.db

        # Status is set based on if a task is selected or not
        self.title("Edit Task" if task else "New Task")
        self.resizable(False, False)
        # Title entry field
        ttk.Label(self, text="Title:").grid(row=0, column=0, sticky='e')
        self.title_var = tk.StringVar(value=task.title if task else "")
        ttk.Entry(self, textvariable=self.title_var).grid(row=0, column=1)
        # Description entry field
        ttk.Label(self, text="Description:").grid(row=1, column=0, sticky='e')
        self.desc_var = tk.StringVar(value=task.description if task else "")
        ttk.Entry(self, textvariable=self.desc_var).grid(row=1, column=1)
        # Due date entry field
        ttk.Label(self, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, sticky='e')
        self.due_var = tk.StringVar(value=task.due_date if task else datetime.now().date().isoformat())
        ttk.Entry(self, textvariable=self.due_var).grid(row=2, column=1)
        # Priority entry field
        ttk.Label(self, text="Priority (1-5):").grid(row=3, column=0, sticky='e')
        self.prio_var = tk.IntVar(value=task.priority if task else 3)
        ttk.Entry(self, textvariable=self.prio_var).grid(row=3, column=1)
        # Category entry field
        ttk.Label(self, text="Category:").grid(row=4, column=0, sticky='e')
        self.cat_var = tk.StringVar(value=task.category if task else "General")
        ttk.Entry(self, textvariable=self.cat_var).grid(row=4, column=1)
        # Completed checkbutton field
        ttk.Label(self, text="Completed:").grid(row=5, column=0, sticky='e')
        self.comp_var = tk.BooleanVar(value=task.complete if task else False)
        ttk.Checkbutton(self, variable=self.comp_var).grid(row=5, column=1, sticky='w', padx=(2, 0))
        # Save button
        ttk.Button(self, text="Save", command=self._on_save).grid(row=6, columnspan=2, pady=10)

    def _on_save(self):
        """Validate the date in the entry form"""
        try:
            due_date = datetime.fromisoformat(self.due_var.get()).date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        def save_task_in_thread():
            """Helper function. Save function to run in thread"""
            try:
                if not self.task:
                    self.task = Task(
                        task_id=str(uuid.uuid4()),
                        user_id=int(self.master.master.user.user_id),
                        title=self.title_var.get().strip(),
                        description=self.desc_var.get().strip(),
                        due_date=due_date,
                        priority=int(self.prio_var.get()),
                        category=self.cat_var.get().strip() or "General",
                        complete=self.comp_var.get()
                    )
                    self.session.add(self.task)
                else:
                    self.task.title = self.title_var.get().strip()
                    self.task.description = self.desc_var.get().strip()
                    self.task.due_date = due_date
                    self.task.priority = int(self.prio_var.get())
                    self.task.category = self.cat_var.get().strip() or "General"
                    self.task.complete = self.comp_var.get()

                self.session.commit()
                self.master.after(0, self.master.refresh_tasks)
                self.master.after(0, self.destroy)

            except Exception as e:
                self.session.rollback()
                self.master.after(0, lambda: messagebox.showerror("Error", f"Could not save task:"))

        threading.Thread(target=save_task_in_thread, daemon=True).start()

