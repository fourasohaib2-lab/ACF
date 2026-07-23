from PySide6.QtWidgets import QApplication, QWidget

app = QApplication([])

window = QWidget()
window.setWindowTitle("Test Qt")
window.resize(500, 300)

window.show()

print("Visible :", window.isVisible())

app.exec()
