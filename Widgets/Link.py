from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
class LinkDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Link")
        layout = QVBoxLayout()

        # to stay on top of application
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        self.link_label = QLabel("Link Address:")
        self.link_textbox = QLineEdit()
        self.display_label = QLabel("Display Text:")
        self.display_textbox = QLineEdit()

        layout.addWidget(self.link_label)
        layout.addWidget(self.link_textbox)
        layout.addWidget(self.display_label)
        layout.addWidget(self.display_textbox)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

        self.setModal(False)

    def get_link_data(self):
        link_address = self.link_textbox.text()
        display_text = self.display_textbox.text()
        return link_address, display_text

