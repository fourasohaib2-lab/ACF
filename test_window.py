import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QLabel

app = QApplication(sys.argv)

w = QMainWindow()
w.setWindowTitle("TEST")
w.resize(800, 500)

label = QLabel("Bonjour ACF")
label.setStyleSheet("font-size:30px")
w.setCentralWidget(label)

w.show()

print("Visible :", w.isVisible())
print("Hidden :", w.isHidden())

sys.exit(app.exec())
