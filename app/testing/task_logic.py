# task_logic.py
from datetime import datetime

from app.models.task import Task


def load_tasks(db):
    """Load all Task objects from the database."""
    return db.query(Task).all()

def get_categories(tasks):
    """Return sorted list of unique categories from tasks."""
    return sorted({t.category for t in tasks})

def filter_tasks(tasks, filter_value):
    """Filter tasks by category. 'All' returns all tasks."""
    if filter_value == "All":
        return list(tasks)
    return [t for t in tasks if t.category == filter_value]

def sort_by_logic(sorted_column, sort_reverse, col):
    """Compute new sort state (column, reverse) when header clicked."""
    if sorted_column == col:
        return col, not sort_reverse
    return col, False

def sort_tasks_logic(tasks, sorted_column, sort_reverse):
    """Sort tasks according to column and order."""
    if not sorted_column:
        return list(tasks)
    keymap = {
        '✓/x':      lambda t: t.complete,
        'Title':    lambda t: t.title,
        'Due Date': lambda t: datetime.strptime(t.due_date, "%Y-%m-%d")
                                 if isinstance(t.due_date, str) else t.due_date,
        'Description': lambda t: (t.description[:42] + '...')
                                if len(t.description) > 45 else t.description,
        'Priority': lambda t: t.priority,
        'Category': lambda t: t.category
    }
    return sorted(tasks, key=keymap[sorted_column], reverse=sort_reverse)

def toggle_complete_logic(task_id, tasks, db):
    """Toggle the complete flag on the Task with given id."""
    task = next((t for t in tasks if t.task_id == task_id), None)
    if task:
        task.complete = not task.complete
        db.commit()
    return task

def delete_task_logic(task_id, tasks, db):
    """Delete the given Task from DB and return the new list."""
    task = next((t for t in tasks if t.task_id == task_id), None)
    if task:
        db.delete(task)
        db.commit()
        remaining = [t for t in tasks if t.task_id != task_id]
        return remaining, task
    return tasks, None

def report_counts_logic(tasks):
    """Return a dict of category→count, grouping completed under 'Complete'."""
    counts = {}
    for t in tasks:
        key = "Complete" if t.complete else t.category
        counts[key] = counts.get(key, 0) + 1
    return counts
