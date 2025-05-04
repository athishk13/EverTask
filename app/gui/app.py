import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database.db import init_db, SessionLocal
from gui.login_frame import LoginFrame

# Main Tkinter application, switches between frames to display
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EverTask")
        init_db()
        self.db = SessionLocal()
        self.user = None
        self.switch_to_login()

        # Menu bar
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        # Add Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Menu", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)

    def show_about(self):
        # Show about information in a pop-up
        messagebox.showinfo("About", "EverTask is a task manager developed by Tiger Yang and Athish Kumar."
                                     "\n ---\nIn Partial Completion for CS122 at San Jose State University.\n---"
                                     "\nVersion 1.0")

    def show_help(self):
        # Show help information in a pop-up
        help_text = (
            "[Add Task]: Click add, then fill in the task form to add\n\n"
            "[Edit Task]: Select a task by left clicking on it, click edit, then fill in the task form to make edits\n\n"
            "[Delete Task]: Select a task by left clicking on it, then click delete\n\n"
            "[Filter]: Select a category from the dropdown menu\n\n"
            "[Report]: Generate a pie chart for remaining tasks by category percentage\n\n"
            "[Sort]: Click on the heading of the category to sort tasks by its content\n\n"
            "[Toggle Complete]: Double click on the check mark or x to toggle completeness\n\n"
            "[Logout]: Close the window to automatically logout"
        )
        messagebox.showinfo("Help", help_text)

    # Switch active view to the login frame
    def switch_to_login(self):
        from gui.login_frame import LoginFrame
        self._switch_frame(LoginFrame)

    # Switch active view to the register frame
    def switch_to_register(self):
        from gui.register_frame import RegisterFrame
        self._switch_frame(RegisterFrame)

    # Switch active view to the tasks frame
    def switch_to_tasks(self):
        from gui.task_list_frame import TaskListFrame
        self._switch_frame(TaskListFrame)

    # Helper function for switching frames
    def _switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if hasattr(self, "_frame"):
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
