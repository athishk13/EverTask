# Evertask by Tiger Yang and Athish Kumar

A simple yet efficient task management system built using Python, Tkinter, and SQLAlchemy. This app allows users to manage their tasks, keep track of progress, and organize their day-to-day activities.

## Features

- **User Authentication**: Secure login system for multiple users.
- **Task Management**: Add, edit, delete, and mark tasks as completed.
- **Database Integration**: Tasks are stored in a SQL database, ensuring persistence across sessions.
- **Task Filtering**: Filter tasks based on their status (e.g., active, completed).
- **User-Specific Tasks**: Tasks are shown based on the logged-in user, so each user has a personalized task list.

## Dependencies
- bcrypt
- matplotlib
- numpy
- python-dateutil
- python-dotenv
- SQLAlchemy
- pyinstaller

## Installation

To set up the Task Management System on your local machine, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/athishk13/EverTask.git
cd EverTask
```

### 2. Install the required dependencies

```bash
pip install -r requirements.txt
```

### 3. Compile the distributable

```bash
pyinstaller --onefile --windowed app/main.py
```

### 4. Launch Evertask

```bash
open dist/main
```

## FIle Structure Overview
```text
EverTask/
├── app/                        # Application source code
│ ├── database/                 # Database code
│ │ ├── init.py
│ │ └── db.py
│ ├── gui/                      # Tkinter Frames
│ │ ├── init.py
│ │ ├── app.py
│ │ ├── login_frame.py
│ │ ├── register_frame.py
│ │ └── task_list_frame.py
│ ├── models/                   # SQLAlchemy tables
│ │ ├── init.py
│ │ ├── task.py
│ │ └── user.py
│ ├── testing/                  # Unit tests
│ ├── utils/                    # Utility functions
│ │ ├── init.py
│ │ └── auth.py
│ ├── init.py
│ └── main.py                   # Application entry point
├── task_manager.db             # SQLite database file
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

## Known Bugs
- Pyinstaller executables open a console window even when run using --windowed, --noconsole, or console=False in .spec file




