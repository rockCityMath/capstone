from Modules.Save import save, saveAs
from Modules.Load import new, load

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Models.DraggableContainer import DraggableContainer
from Widgets.Textbox import *

from Modules.EditorSignals import editorSignalsInstance, ChangedWidgetAttribute
from Modules.Undo import UndoHandler
from Widgets.Table import *

from Views.EditorFrameView import *

import subprocess

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]

def build_ui(editor):
    print("Building UI")
    editor.setWindowTitle("OpenNote")
    editor.setWindowIcon(QIcon('./Assets/OpenNoteLogo.png'))
    editor.resize(800, 450)
    editor.setAcceptDrops(True)

    if check_appearance() == False:
        with open('./Styles/styles.qss',"r") as fh:
            editor.setStyleSheet(fh.read())
    else:
        with open('./Styles/stylesDark.qss',"r") as fh:
            editor.setStyleSheet(fh.read())

    editor.titlebar = build_titlebar(editor)
    build_menubar(editor)
    build_toolbar(editor)

    # Main layout of the app
    gridLayout = QGridLayout()
    gridLayout.setSpacing(3)
    gridLayout.setContentsMargins(6, 6, 0, 0)
    gridLayout.setColumnStretch(1, 7)

    centralWidget = QWidget()
    centralWidget.setLayout(gridLayout)

    # Sets up layout of each bar
    topSideLayout = QVBoxLayout()
    topSideContainerWidget = QWidget()
    topSideContainerWidget.setLayout(topSideLayout)
    topSideLayout.setContentsMargins(0, 0, 0, 0)
    topSideLayout.setSpacing(0)

    topSideLayout.addWidget(editor.titlebar, 0)
    topSideLayout.addWidget(editor.menubar, 1)
    topSideLayout.addWidget(editor.homeToolbar, 2)
    topSideLayout.addWidget(editor.insertToolbar, 2)
    topSideLayout.addWidget(editor.drawToolbar, 2)

    # Sets up left side notebook view
    leftSideLayout = QVBoxLayout()
    leftSideContainerWidget = QWidget()
    leftSideContainerWidget.setLayout(leftSideLayout)
    leftSideLayout.setContentsMargins(0, 0, 0, 0)
    leftSideLayout.setSpacing(0)

    leftSideLayout.addWidget(editor.notebookTitleView, 0)
    leftSideLayout.addWidget(editor.pageView, 1)

    # Sets up right side section view
    rightSideLayout = QVBoxLayout()
    rightSideContainerWidget = QWidget()
    rightSideContainerWidget.setLayout(rightSideLayout)
    rightSideLayout.setContentsMargins(0, 0, 0, 0)
    rightSideLayout.setSpacing(0)

    rightSideLayout.addWidget(editor.sectionView, 0)
    rightSideLayout.addWidget(editor.frameView, 1)

    gridLayout.addWidget(topSideContainerWidget, 0, 0, 1, 2, alignment = Qt.AlignmentFlag.AlignTop)
    gridLayout.addWidget(leftSideContainerWidget, 1, 0, 1, 1)
    gridLayout.addWidget(rightSideContainerWidget, 1, 1, 1, 2)

    editor.setCentralWidget(centralWidget)

    #Saves window size 
    #editor.restoreGeometry(editor.settings.value("geometry", editor.saveGeometry()))
    #editor.restoreState(editor.settings.value("windowState", editor.saveState()))


class build_titlebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.setStyleSheet(
            """
                background-color: rgb(119, 25, 170);
                height: 50px;
            """
        )
        self.initial_pos = None

        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)

        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setStyleSheet(
            """
               color: white;
            """
        )
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)   

        # Min button
        self.min_button = QToolButton(self)
        min_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarMinButton
        )
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        self.max_button = QToolButton(self)
        max_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarMaxButton
        )
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = QToolButton(self)
        close_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarCloseButton
        )
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)
        
        # Normal button
        self.normal_button = QToolButton(self)
        normal_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarNormalButton
        )
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)
        
        # Add buttons             
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(28, 28))
            button.setStyleSheet(
                """QToolButton { color: white;
                }
                """
            )
            title_bar_layout.addWidget(button)

    def window_state_changed(self, state):
        if state == Qt.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

def build_menubar(editor):
    editor.menubar = editor.menuBar()
    
    file = editor.menubar.addMenu('&File')
    home = editor.menubar.addMenu('&Home')
    insert = editor.menubar.addMenu('&Insert')
    draw = editor.menubar.addMenu('&Draw')
    plugins = editor.menubar.addMenu('&Plugins')

    new_file = build_action(editor, './Assets/icons/svg_file_open', 'New Notebook', 'New Notebook', False)
    new_file.setShortcut(QKeySequence.StandardKey.New)
    new_file.triggered.connect(lambda: new(editor))

    open_file = build_action(editor, './Assets/icons/svg_file_open', 'Open Notebook', 'Open Notebook', False)
    open_file.setShortcut(QKeySequence.StandardKey.Open)
    open_file.triggered.connect(lambda: load(editor))

    save_file = build_action(editor, './Assets/icons/svg_file_save', 'Save Notebook', 'Save Notebook', False)
    save_file.setShortcut(QKeySequence.StandardKey.Save)
    save_file.triggered.connect(lambda: save(editor))

    save_fileAs = build_action(editor, './Assets/icons/svg_file_save', 'Save Notebook As...', 'Save Notebook As', False)
    save_fileAs.setShortcut(QKeySequence.fromString('Ctrl+Shift+S'))
    save_fileAs.triggered.connect(lambda: saveAs(editor))

    toggle_home_toolbar = build_action(editor, '', 'Toggle Home Toolbar', 'Toggle Home Toolbar', False)
    toggle_home_toolbar.triggered.connect(lambda: set_toolbar_visibility(editor, 'homeToolbar'))

    toggle_insert_toolbar = build_action(editor, '', 'Toggle Insert Toolbar', 'Toggle Insert Toolbar', False)
    toggle_insert_toolbar.triggered.connect(lambda: set_toolbar_visibility(editor, 'insertToolbar'))
    
    toggle_draw_toolbar = build_action(editor, '', 'Toggle Draw Toolbar', 'Toggle Draw Toolbar', False)
    toggle_draw_toolbar.triggered.connect(lambda: set_toolbar_visibility(editor, 'drawToolbar'))

    add_widget = build_action(editor, './Assets/icons/svg_question', 'Add Custom Widget', 'Add Custom Widget', False)

    file.addActions([new_file, open_file, save_file, save_fileAs])
    home.addAction(toggle_home_toolbar)
    insert.addAction(toggle_insert_toolbar)
    draw.addAction(toggle_draw_toolbar)
    plugins.addAction(add_widget)    

def build_toolbar(editor):
    # homeToolbar code
    editor.homeToolbar = QToolBar()
    editor.homeToolbar.setObjectName('homeToolbar')
    editor.homeToolbar.setIconSize(QSize(18, 18))
    editor.homeToolbar.setMovable(False)
    editor.homeToolbar.setStyleSheet('height: 40px; spacing: 10px;')
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.homeToolbar)

    #separates toolbar with a line break
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    cut = build_action(editor.homeToolbar, './Assets/icons/svg_cut', "cut", "cut", False)
    cut.triggered.connect(editor.frameView.cutWidgetEvent)
    
    copy = build_action(editor.homeToolbar, './Assets/icons/svg_copy', "copy", "copy", False)
    copy.triggered.connect(editor.frameView.copyWidgetEvent)


    font_family = QFontComboBox()
    font_family.setFixedWidth(150)
    default_font = font_family.currentFont().family()
    print(f"default font is {default_font}")
    font_family.currentFontChanged.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Font, font_family.currentFont().family()))

    font_size = QComboBox()
    font_size.setFixedWidth(50)
    font_size.addItems([str(fs) for fs in FONT_SIZES])
    # default text size is 11
    default_font_size_index = 4
    font_size.setCurrentIndex(default_font_size_index)
    font_size.currentIndexChanged.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontSize, int(font_size.currentText())))

    #current issues: 
    # - Alternates between working and not working
    # - Textboxes do not remember settings like if font is toggled or current font size

    bgColor = build_action(editor.homeToolbar, './Assets/icons/svg_font_bucket', "Background Color", "Background Color", False)
    #bgColor.triggered.connect(lambda: openGetColorDialog(purpose = "background"))
    #current bug, alternates between activating and not working when using
    bgColor.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.BackgroundColor, QColorDialog.getColor()))

    textHighlightColor = build_action(editor.homeToolbar, './Assets/icons/svg_textHighlightColor', "Text Highlight Color", "Text Highlight Color", True)

    textHighlightColor.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.TextHighlightColor, QColorDialog.getColor()))

    #defines font color icon appearance and settings
    fontColor = build_action(editor.homeToolbar, './Assets/icons/svg_font_color', "Font Color", "Font Color", False)
    fontColor.triggered.connect(lambda: openGetColorDialog(purpose = "font"))

    bold = build_action(editor.homeToolbar, './Assets/icons/bold', "Bold", "Bold", True)
    bold.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontBold, None))

    italic = build_action(editor.homeToolbar, './Assets/icons/italic.svg', "Italic", "Italic", True)
    italic.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontItalic, None))

    underline = build_action(editor.homeToolbar, './Assets/icons/underline.svg', "Underline", "Underline", True)
    underline.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontUnderline, None))

    strikethrough = build_action(editor.homeToolbar, './Assets/icons/svg_strikethrough.svg', "Strikethrough", "Strikethrough", True)
    strikethrough.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Strikethrough, None))
    
    # Bullets with placeholder for more bullet options
    bullet = build_action(editor.homeToolbar, './Assets/icons/svg_bullets', "Bullets", "Bullets", False)
    bullet.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Bullet, None))

    paperColor= build_action(editor.homeToolbar, './Assets/icons/svg_paper', "Paper Color", "Paper Color", False)
    paperColor.triggered.connect(lambda: editor.frameView.pageColor(QColorDialog.getColor()))
    
    editor.homeToolbar.addActions([cut, copy])
    
    editor.homeToolbar.addSeparator()
    
    editor.homeToolbar.addWidget(font_family)
    editor.homeToolbar.addWidget(font_size)
    
    editor.homeToolbar.addSeparator()
    
    editor.homeToolbar.addActions([bold, italic, underline, strikethrough, fontColor, textHighlightColor, bgColor, paperColor, bullet])


    # numbering menu start
    numbering_menu = QMenu(editor)
    
    bullet_num = build_action(numbering_menu, './Assets/icons/svg_bullet_number', "", "", False)
    bullet_num.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Bullet_Num, None))
    
    bullet_num = build_action(numbering_menu, './Assets/icons/svg_bullet_number', "", "", False)
    bullet_num.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Bullet_Num, None))
    bulletUpperA = build_action(numbering_menu, './Assets/icons/svg_bulletUA', "", "", False)
    bulletUpperA.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.BulletUA, None))
    bulletUpperR = build_action(numbering_menu, './Assets/icons/svg_bulletUR', "", "", False)
    bulletUpperR.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.BulletUR, None))

    numbering_menu.addActions([bullet_num, bulletUpperA, bulletUpperR])

    # cant directly add numbering menu to homeToolbar so this is required 
    numbering = QToolButton(editor)
    numbering.setIcon(QIcon('./Assets/icons/svg_bullet_number'))
    numbering.setIconSize(QSize(18,18))
    numbering.setPopupMode(QToolButton.InstantPopup)
    numbering.setMenu(numbering_menu)
    
    editor.homeToolbar.addWidget(numbering)
    
    # QActionGroup used to display that only one can be toggled at a time
    align_group = QActionGroup(editor.homeToolbar)
    
    align_left = build_action(align_group,"./Assets/icons/svg_align_left","Align Left","Align Left", True)
    align_left.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignLeft, None))
    align_center = build_action(align_group,"./Assets/icons/svg_align_center","Align Center","Align Center", True)
    align_center.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignCenter, None))
    align_right = build_action(align_group, "./Assets/icons/svg_align_right", "Align Right", "Align Right", True)
    align_right.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignRight, None))
    
    align_group.addAction(align_left)
    align_group.addAction(align_center)
    align_group.addAction(align_right)
    editor.homeToolbar.addActions(align_group.actions())

    editor.homeToolbar.addSeparator()
    
    
    # insertToolbar code 
    editor.insertToolbar = QToolBar()
    editor.insertToolbar.setObjectName('insertToolbar')
    editor.insertToolbar.setIconSize(QSize(18,18))
    editor.insertToolbar.setStyleSheet('height: 40px; spacing: 10px;')
    editor.insertToolbar.setMovable(False)
    editor.insertToolbar.setVisible(False)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.insertToolbar)
    
    table = build_button(editor.insertToolbar, './Assets/icons/svg_table', " Table ", "Add a Table", False)
    table.clicked.connect(editor.frameView.toolbar_table)
    
    insertSpace = build_button(editor.insertToolbar, './Assets/icons/svg_insert_space', "Insert Space", "Insert Space", False)
    
    screensnip = build_button(editor.insertToolbar, './Assets/icons/svg_screensnip', " Screensnip ", "Screensnip", False)
    screensnip.clicked.connect(editor.frameView.toolbar_snipScreen)
    
    pictures = build_button(editor.insertToolbar, './Assets/icons/svg_pictures', " Pictures ", "Pictures", False)
    pictures.clicked.connect(editor.frameView.toolbar_pictures)

    hyperlink = build_button(editor.insertToolbar, './Assets/icons/svg_hyperlink', " Hyperlink ", "Hyperlink", False)
    hyperlink.clicked.connect(editor.frameView.toolbar_hyperlink)
    
    editor.insertToolbar.addWidget(table) 
    
    editor.insertToolbar.addSeparator()
    
    editor.insertToolbar.addWidget(insertSpace)
    
    editor.insertToolbar.addSeparator()
    
    editor.insertToolbar.addWidget(screensnip)
    editor.insertToolbar.addWidget(pictures)
    
    editor.insertToolbar.addSeparator()
    
    editor.insertToolbar.addWidget(hyperlink)
    editor.insertToolbar.addSeparator()
    
    # drawToolbar code
    editor.drawToolbar = QToolBar()
    editor.drawToolbar.setObjectName('drawToolbar')
    editor.drawToolbar.setIconSize(QSize(18, 18))
    editor.drawToolbar.setStyleSheet('height: 40px; spacing: 10px;')
    editor.drawToolbar.setMovable(False)
    editor.drawToolbar.setVisible(False)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.drawToolbar)
    
    undo = build_action(editor.drawToolbar, './Assets/icons/svg_undo', "undo", "undo", False)
    undo.triggered.connect(editor.frameView.triggerUndo)

    redo = build_action(editor.drawToolbar, './Assets/icons/svg_redo', "redo", "redo", False)
    # redo.triggered.connect(editor.frameView.triggerRedo)
    
    editor.drawToolbar.addActions([undo, redo])
    
    editor.drawToolbar.addSeparator()

def check_appearance():
    """Checks DARK/LIGHT mode of macos."""
    cmd = 'defaults read -g AppleInterfaceStyle'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    return bool(p.communicate()[0])  

def set_toolbar_visibility(editor, triggered_toolbar):
    # Find all toolbars in the editor
    toolbars = editor.findChildren(QToolBar)

    # Iterate over each toolbar
    for toolbar in toolbars:
        if toolbar.objectName() == triggered_toolbar:
            # Toggle the visibility of the triggered toolbar
            print(toolbar.objectName(),"visibility change")
            toolbar.setVisible(not toolbar.isVisible())
        else:
            # Hide all other toolbars
            toolbar.setVisible(False)

def openGetColorDialog(purpose):
    color = QColorDialog.getColor()
    if color.isValid():
        if purpose == "font":
            editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontColor, color)
        elif purpose == "background":
            editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.BackgroundColor, color)

def build_action(parent, icon_path, action_name, set_status_tip, set_checkable):
    action = QAction(QIcon(icon_path), action_name, parent)
    action.setStatusTip(set_status_tip)
    action.setCheckable(set_checkable)
    return action
    
def build_button(parent, icon_path, text, tooltip, checkable):
    button = QPushButton(parent)
    button.setIcon(QIcon(icon_path))
    button.setText(text)
    button.setToolTip(tooltip)
    button.setCheckable(checkable)
    return button
