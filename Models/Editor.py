from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Modules.BuildUI import *
from Modules.Save import Autosaver
from Modules.Screensnip import SnippingWidget
from Models.NotebookModel import NotebookModel
from Models.SectionModel import SectionModel
from Modules.Undo import UndoHandler

from Views.PageView import PageView
from Views.EditorFrameView import EditorFrameView
from Views.NotebookTitleView import NotebookTitleView
from Views.SectionView import SectionView
from Modules.Titlebar import Build_titlebar


class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.notebook = NotebookModel('Untitled Notebook')    # Current notebook object
        # self.selected = None                                  # Selected object (for font attributes of TextBox)

        # View-Controllers that let the user interact with the underlying models
        self.titlebar = Build_titlebar(self)
        self.notebookTitleView = NotebookTitleView(self.notebook.title)
        self.frameView = EditorFrameView(self)
        self.pageView = PageView(self.notebook.pages)
        self.sectionView = SectionView(self.notebook.pages[0].sections)

        self.autosaver = Autosaver(self) # Waits for change signals and saves the notebook
        self.setFocus()

        self.settings = QSettings("UNT - Team Olive", "OpenNote")

        build_ui(self)
        action_names = self.save_toolbar_actions([self.homeToolbar, self.insertToolbar, self.drawToolbar])
        self.titlebar.set_action_names(action_names)

    def closeEvent(self, event):
        # Save window size and position before exiting

        print("Window closing event triggered")
        
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    def showEvent(self, event):
        # Restores window size and position

        print("Window showing event triggered")

        self.restoreGeometry(self.settings.value("geometry", self.saveGeometry())) 
        self.restoreState(self.settings.value("windowState", self.saveState()))
        super().showEvent(event)
    
    # def focusInEvent(self, event):
    #     self.repaint()
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.titlebar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.moveFlag = False  

    def save_toolbar_actions(self, toolbars):
        action_names = []
        for toolbar in toolbars:
            for action in toolbar.actions():
                if action.objectName():
                    action_names.append(action.objectName())

            for widget in toolbar.findChildren(QPushButton) + toolbar.findChildren(QToolButton) + toolbar.findChildren(QComboBox):
                if widget.objectName() and widget.objectName() != "qt_toolbar_ext_button":
                    action_names.append(widget.objectName())
        
        return action_names