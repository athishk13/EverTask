import tkinter as tk
from database.db import init_db, SessionLocal
from gui.login_frame import LoginFrame

# Main Tkinter application, switches between frames to display
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        init_db()
        self.db = SessionLocal()
        self.user = None
        self.switch_to_login()

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
