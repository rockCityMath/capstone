from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Models.PageModel import PageModel

class NotebookTitleView(QWidget):
    def __init__(self, notebookTitle: str):
        super(NotebookTitleView, self).__init__()

        self.notebookTitle = notebookTitle # Reference to the title on the notebook model

        # Creating the QTextEdit widget for displaying and editing the title
        self.titleWidget = QTextEdit()
        self.titleWidget.setText(self.notebookTitle)
        self.titleWidget.setFixedHeight(30)
        self.titleWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.titleWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.titleWidget.textChanged.connect(self.titleChanged)

        layout = QVBoxLayout(self)
        layout.addWidget(self.titleWidget)
        layout.setContentsMargins(0, 0, 0, 0)

        print("BUILT TITLEVIEW")

    def toPlainText(self):
        return self.titleWidget.toPlainText()

    def setText(self, text: str):
        self.titleWidget.setText(text)

    def titleChanged(self):
        print("NEW TITLE: " + self.titleWidget.toPlainText())
        self.notebookTitle = self.titleWidget.toPlainText()

