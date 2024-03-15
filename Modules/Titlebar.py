from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtSvg import *
from PySide6.QtWidgets import *

from Models.DraggableContainer import DraggableContainer
from Widgets.Textbox import *

from Modules.BuildUI import *
from Modules.EditorSignals import editorSignalsInstance, ChangedWidgetAttribute
from Modules.Undo import UndoHandler

from Views.EditorFrameView import *

class Build_titlebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        print("Building Titlebar")
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.setFixedHeight(49)
        self.setObjectName("titlebar")
        # self.setStyleSheet("background-color: rgb(119, 25, 170);")
        self.initial_pos = None

        titlebarLayout = QHBoxLayout(self)
        titlebarLayout.setContentsMargins(0, 0, 0, 0)
        titlebarLayout.setSpacing(0)
        
        self.logo = build_titlebutton('./Assets/White-OpenNoteLogo', "logo", None)
        self.logo.setFixedSize(QSize(49, 49))

        self.title = QLabel("OpenNote", self)
        self.title.setStyleSheet("color: white;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setMaximumWidth(parent.width() // 5.5)
        if title := parent.windowTitle():
            self.title.setText(title) 

        self.leftSpacer = QWidget(self)
        self.leftSpacer.setMinimumWidth(parent.width() // 5.5)

        # Search bar
        self.searchbarWidget = QWidget(self)
        self.searchbarLayout = QVBoxLayout()
        self.searchbarWidget.setLayout(self.searchbarLayout)
        self.searchbarWidget.setObjectName("searchbarWidget")
        self.searchbarLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.searchbar = QLineEdit(self)
        self.searchbar.setClearButtonEnabled(True)
        self.searchbar.addAction(QIcon("./Assets/Icons/svg_search"), QLineEdit.LeadingPosition)
        self.searchbar.setMaximumWidth(parent.width() // 2)
        self.searchbar.setPlaceholderText("Search")
        self.searchbar.returnPressed.connect(self.perform_search)
        self.searchbarLayout.addWidget(self.searchbar)

        self.rightSpacer = QWidget(self)
        self.rightSpacer.setMinimumWidth(parent.width() // 6)

        # the names for windowed and fullscreen might be swapped, but it works how it should so 👍
        self.tray = build_titlebutton('./Assets/icons/svg_tray', "tray", self.window().showMinimized)
        # self.windowed = build_titlebutton('./Assets/icons/svg_windowed', "windowed", self.windowed_window) 
        # self.fullscreen = build_titlebutton('./Assets/icons/svg_fullscreen', "fullscreen", self.fullscreen_window)
        self.windowed = build_titlebutton('./Assets/icons/svg_windowed', "windowed", self.window().showNormal) 
        self.fullscreen = build_titlebutton('./Assets/icons/svg_fullscreen', "fullscreen", self.window().showMaximized)
        
        self.close = build_titlebutton('./Assets/icons/svg_close', "close", self.window().close)
        
        titlebarLayout.addWidget(self.logo)

        titlebarLayout.addWidget(self.title)  

        titlebarLayout.addWidget(self.leftSpacer)
        
        titlebarLayout.addWidget(self.searchbarWidget)
        
        titlebarLayout.addWidget(self.rightSpacer)

        titlebarLayout.addWidget(self.tray)
        titlebarLayout.addWidget(self.windowed)
        titlebarLayout.addWidget(self.fullscreen)
        titlebarLayout.addWidget(self.close)

    def window_state_changed(self, state):
        self.windowed.setVisible(state != Qt.WindowState.WindowNoState)
        self.fullscreen.setVisible(state == Qt.WindowState.WindowNoState)
    
    def set_action_names(self, action_names):
        # Populate the completer with search suggestions
        self.search_suggestions = action_names
        completer = QCompleter(self.search_suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.searchbar.setCompleter(completer)

    def perform_search(self):
        search_text = self.searchbar.text().lower()

        # Dictionary mapping search keywords to corresponding actions
        actions = {
            "cut": lambda: None,
            "copy": lambda: None,
            "paste": lambda: None,
            "font": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Font, font_family.currentFont().family()),
            "font size": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontSize, int(font_size.currentText())),
            "bold": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontBold, None),
            "italic": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontItalic, None),
            "underline": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontUnderline, None),
            "font color": lambda: openGetColorDialog(purpose = "font"),
            "text highlight color": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.TextHighlightColor, QColorDialog.getColor()),
            "strikethrough": lambda: lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Strikethrough, None),
            "background color": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.BackgroundColor, QColorDialog.getColor()),
            "delete": lambda: None,
            "bullets": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Bullet, None),
            "numbering": None, # QMenu lambda call???
            "align left": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignLeft, None),
            "align center": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignCenter, None),
            "align right": lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignRight, None),
            "table": None, # editor.frameView.toolbar_table
            "insert space": None, 
            "screensnip": None, # editor.frameView.toolbar_snipScreen
            "pictures": None, # editor.frameView.toolbar_pictures
            "hyperlink": None, # editor.frameView.toolbar_hyperlink
            "date & time": None, # also qmenu
            "undo": lambda: None,
            "redo": lambda: None,
            "paper color": lambda: None #editor.frameView.pageColor(QColorDialog.getColor()),
        }

        # Check if the search_text corresponds to a known action, and execute it if found
        action = actions.get(search_text)
        if action:
            action()
        else:
            # Handle unknown action
            pass
        
def build_titlebutton(icon_path, object_name, on_click):
    button = QToolButton()
    button.setIcon(QIcon(icon_path)) 
    button.setObjectName(object_name)
    button.clicked.connect(on_click)
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    button.setFixedSize(QSize(49, 49))
    button.setStyleSheet("QToolButton { border: none; padding: 0px;}")
    return button
   