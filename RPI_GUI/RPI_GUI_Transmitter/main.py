# Entry point for the RPI application
# cd ./dir/to/your/root_project_foldeer
# python main.py

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from windows.rpi_mainwindow import RPIMainWindow
from controllers.rpi_mainwindow_controller import RPIMainController

def main():
    app = QApplication(sys.argv)
    main_win = RPIMainWindow()
    main_ctrl = RPIMainController(main_win)
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# git clone repo
# cd your-rpi-gui-project
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
# python main.py