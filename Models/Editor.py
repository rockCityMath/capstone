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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) 
        # self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint) # This changes the window back to a state that allows resizing
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

        self.settings = QSettings("UNT - Team Olive", "OpenNote") #pre-saved settings needed for window state restoration

        build_ui(self)
        
        action_names = self.save_toolbar_actions([self.fileToolbar, self.homeToolbar, self.insertToolbar, self.drawToolbar, self.pluginToolbar])
        self.titlebar.set_action_names(action_names)

    def closeEvent(self, event):

        print("Window closing event triggered")
        
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    # Handles the window showing event, it restores the window's geometry and state
    def showEvent(self, event):

        print("Window showing event triggered")

        self.restoreGeometry(self.settings.value("geometry", self.saveGeometry())) 
        self.restoreState(self.settings.value("windowState", self.saveState()))
        super().showEvent(event)
    
    # def focusInEvent(self, event):
    #     self.repaint()
    # Handles changes in window state, particularly the window state change event
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.titlebar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()
        
    def triggerUndo(self):
        print("Item added to Stack")
        # Get the currently focused widget
        focused_widget = self.focusWidget()
        print(f"Focused widget: {focused_widget}")

        if focused_widget and isinstance(focused_widget, (QTextEdit, QLineEdit)):
            print("Undo Action Completed")

        
            backspace_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier)
            backspace_release_event = QKeyEvent(QEvent.KeyRelease, Qt.Key_Backspace, Qt.NoModifier)

            # Post the key press event to the focused widget
            QApplication.postEvent(focused_widget, backspace_event)
            QApplication.postEvent(focused_widget, backspace_release_event)
            
    # mousePress, mouseMove, and mouseRelease handle mouse move events inside the window
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.setWindowState(Qt.WindowNoState)
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.moveFlag = False  

    # Collects action names from the toolbars
    def save_toolbar_actions(self, toolbars):
        action_names = []
        for toolbar in toolbars: #loops through all toolbars 
            for action in toolbar.actions():
                if action.objectName():
                    action_names.append(action.objectName())  # Add the object name of the action to the list

             # Loop through child widgets of the toolbar (buttons, tool buttons, combo boxes)
            for widget in toolbar.findChildren(QPushButton) + toolbar.findChildren(QToolButton) + toolbar.findChildren(QComboBox):
                if widget.objectName() and widget.objectName() != "qt_toolbar_ext_button":
                    action_names.append(widget.objectName()) # Add the object name of the widget to the list
        
        return action_names  # Return the list of action names collected from the toolbars
