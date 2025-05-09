import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
ASSET_DIR = BASE_DIR / "assets"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def get_icon_path():
    if sys.platform.startswith("win"):
        if (ASSET_DIR / "icon.ico").exists():
            return ASSET_DIR / "icon.ico"
        elif (ASSET_DIR / "icon.png").exists():
            return ASSET_DIR / "icon.png"

    else:
        if (ASSET_DIR / "icon.png").exists():
            return ASSET_DIR / "icon.png"
        elif (ASSET_DIR / "icon.ico").exists():
            return ASSET_DIR / "icon.ico"

    return None

from windows.mainwindow import MainWindow
from controllers.mainwindow_controller import MainWindowController

def main():
    app = QApplication(sys.argv)
    
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(str(icon_path)))

    main_window = MainWindow()
    main_controller = MainWindowController(main_window)

    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
