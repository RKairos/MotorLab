"""Ponto de entrada: execute este arquivo no VS Code."""
import sys
from PyQt6.QtWidgets import QApplication
from motorLab.window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("MotorLab")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
