from PyQt5.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel("GUI berhasil!")
label.show()
sys.exit(app.exec_())