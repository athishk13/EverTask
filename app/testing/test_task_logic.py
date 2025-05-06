import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.task import Task
from app.database.db import Base
from app.models.user import User
import app.testing.task_logic as L

class TestTaskLogic(unittest.TestCase):
    def setUp(self):
        # In-memory SQLite
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.db = Session()

        # Create and add a user
        user = User(user_id=1, username="testuser", password_hash="hashed")
        self.db.add(user)
        self.db.commit()

        # Seed sample tasks linked to the user
        t1 = Task(
            task_id="1",
            user_id=1,
            title="A",
            description="foo",
            due_date=date(2025, 5, 10),
            priority=2,
            category="Work",
            complete=False
        )
        t2 = Task(
            task_id="2",
            user_id=1,
            title="B",
            description="bar",
            due_date=date(2025, 5, 9),
            priority=3,
            category="Home",
            complete=True
        )
        t3 = Task(
            task_id="3",
            user_id=1,
            title="C",
            description="baz",
            due_date=date(2025, 5, 8),
            priority=1,
            category="Work",
            complete=False
        )
        self.db.add_all([t1, t2, t3])
        self.db.commit()
        self.sample = [t1, t2, t3]

    def test_load_and_get_categories(self):
        loaded = L.load_tasks(self.db)
        self.assertEqual(len(loaded), 3)
        cats = L.get_categories(loaded)
        self.assertEqual(cats, ["Home", "Work"])

    def test_filter_tasks(self):
        all_tasks = list(self.sample)
        self.assertEqual(len(L.filter_tasks(all_tasks, "All")), 3)
        work_tasks = L.filter_tasks(all_tasks, "Work")
        self.assertEqual(len(work_tasks), 2)
        home_tasks = L.filter_tasks(all_tasks, "Home")
        self.assertEqual(len(home_tasks), 1)

    def test_sort_tasks_logic(self):
        tasks = list(self.sample)
        # sort by Due Date ascending
        sorted_by_date = L.sort_tasks_logic(tasks, "Due Date", False)
        dates = [t.due_date for t in sorted_by_date]
        self.assertEqual(dates, sorted(dates))
        # sort by Priority descending
        sorted_by_prio = L.sort_tasks_logic(tasks, "Priority", True)
        prios = [t.priority for t in sorted_by_prio]
        self.assertEqual(prios, sorted(prios, reverse=True))

    def test_sort_by_logic(self):
        # toggling behavior
        col, rev = L.sort_by_logic(None, False, "Title")
        self.assertEqual((col, rev), ("Title", False))
        # same column flips reverse
        col2, rev2 = L.sort_by_logic("Title", False, "Title")
        self.assertEqual((col2, rev2), ("Title", True))

    def test_toggle_complete_logic(self):
        tasks = L.load_tasks(self.db)
        t = L.toggle_complete_logic("1", tasks, self.db)
        self.assertTrue(t.complete)
        # toggle back
        t_back = L.toggle_complete_logic("1", tasks, self.db)
        self.assertFalse(t_back.complete)

    def test_delete_task_logic_and_report(self):
        tasks = L.load_tasks(self.db)
        remaining, deleted = L.delete_task_logic("2", tasks, self.db)
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted.task_id, "2")
        self.assertEqual(len(remaining), 2)
        counts = L.report_counts_logic(remaining)
        # both remaining are category "Work" and incomplete
        self.assertEqual(counts, {"Work": 2})

if __name__ == "__main__":
    unittest.main()
