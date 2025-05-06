import sys
import os
# Add path for distribution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

# Suppress SQLAlchemy engine output
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


from app.gui.app import App

if __name__ == "__main__":
    """Main entry point. Start the App and its tkinter mainloop"""
    app = App()
    app.mainloop()
