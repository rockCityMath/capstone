from Modules.Save import save, saveAs
from Modules.Load import new, load

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtSvg import *
from PySide6.QtWidgets import *

from Models.DraggableContainer import DraggableContainer
from Widgets.Textbox import *

from Modules.EditorSignals import editorSignalsInstance, ChangedWidgetAttribute, CheckSignal
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


    # Checks wether mac is in dark mode, then sets proper window css
    if check_appearance() == False:
        with open('./Styles/styles.qss',"r") as fh:
            editor.setStyleSheet(fh.read())
    else:
        with open('./Styles/stylesDark.qss',"r") as fh:
            editor.setStyleSheet(fh.read())

    build_tabbar(editor)
    # build_menubar(editor)
    # build_toolbar(editor)

    # Main layout of the app
    gridLayout = QGridLayout()
    gridLayout.setSpacing(0)
    gridLayout.setContentsMargins(0, 0, 0, 0)
    gridLayout.setColumnStretch(1, 7)

    centralWidget = QWidget()
    centralWidget.setLayout(gridLayout)

    # Sets up layout of each bar
    topSideLayout = QVBoxLayout()
    topSideContainerWidget = QWidget()
    topSideContainerWidget.setLayout(topSideLayout)
    topSideLayout.setContentsMargins(0, 0, 0, 0)
    topSideLayout.setSpacing(0)

    barsLayout = QVBoxLayout()
    barsLayoutContainerWidget = QWidget()
    barsLayoutContainerWidget.setLayout(barsLayout)
    barsLayout.setContentsMargins(7, 0, 7, 0)
    barsLayout.setSpacing(0)

    # Add the bars to the layout with individual margins
    barsLayout.addWidget(editor.tabbar)
    # barsLayout.addWidget(editor.menubar)
    # barsLayout.addWidget(editor.homeToolbar)
    # barsLayout.addWidget(editor.insertToolbar)
    # barsLayout.addWidget(editor.drawToolbar)

    topSideLayout.addWidget(editor.titlebar, 0)
    topSideLayout.addWidget(barsLayoutContainerWidget, 1)
    # topSideLayout.addWidget(editor.homeToolbar, 2)
    # topSideLayout.addWidget(editor.insertToolbar, 2)
    # topSideLayout.addWidget(editor.drawToolbar, 2)

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

# Constructs the tab bar with different tabs like File, Home, Insert, Draw, and Plugins
# It adds toolbars to these tabs and connects them to their functions
def build_tabbar(editor):
    editor.tabbar = QTabWidget()
    editor.tabbar.setTabsClosable(False)

    editor.fileToolbar = QToolBar()
    editor.homeToolbar = QToolBar()
    editor.insertToolbar = QToolBar()
    editor.drawToolbar = QToolBar()
    editor.pluginToolbar = QToolBar()


    # Toolbars
    # Constructs toolbars for different functionalities like home, insert, and draw
    # It adds actions and buttons to these toolbars and connects them to their functions
    # ---------------------------------------------------------------------------------

    def handleCheck(action):
        action.setChecked(True)
    #editorSignalsInstance.checkMade.connect(editor.checkMade)

    # For adding space to the left the first button added to a toolbar
    spacer1 = QWidget()
    spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer1.setFixedWidth(3)
        
    spacer2 = QWidget()
    spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer2.setFixedWidth(7)
        
    spacer3 = QWidget()
    spacer3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    spacer3.setFixedWidth(3)

    # ---------------------------------------------------------------------------------
    # fileToolbar code

    editor.fileToolbar.setObjectName('fileToolbar')
    editor.fileToolbar.setIconSize(QSize(18,18))
    editor.fileToolbar.setMovable(False)
    editor.fileToolbar.setVisible(False)
    editor.fileToolbar.setFixedHeight(40)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.fileToolbar)

    new_file = build_button(editor.fileToolbar, './Assets/icons/svg_file_open', 'New Notebook', 'New Notebook', False)
    new_file.setShortcut(QKeySequence.StandardKey.New)
    new_file.clicked.connect(lambda: new(editor))

    open_file = build_button(editor.fileToolbar, './Assets/icons/svg_file_open', 'Open Notebook', 'Open Notebook', False)
    open_file.setShortcut(QKeySequence.StandardKey.Open)
    open_file.clicked.connect(lambda: load(editor))

    save_file = build_button(editor.fileToolbar, './Assets/icons/svg_file_save', 'Save Notebook', 'Save Notebook', False)
    save_file.setShortcut(QKeySequence.StandardKey.Save)
    save_file.clicked.connect(lambda: save(editor))

    save_fileAs = build_button(editor.fileToolbar, './Assets/icons/svg_file_save', 'Save Notebook As...', 'Save Notebook As', False)
    save_fileAs.setShortcut(QKeySequence.fromString('Ctrl+Shift+S'))
    save_fileAs.clicked.connect(lambda: saveAs(editor))

    editor.fileToolbar.addWidget(new_file)
    editor.fileToolbar.addWidget(open_file)
    editor.fileToolbar.addWidget(save_file)
    editor.fileToolbar.addWidget(save_fileAs)

    # ---------------------------------------------------------------------------------
    # homeToolbar code

    editor.homeToolbar.setObjectName('homeToolbar')
    editor.homeToolbar.setIconSize(QSize(18, 18))
    editor.homeToolbar.setMovable(False)
    editor.homeToolbar.setFixedHeight(40)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.homeToolbar)

    paste = build_action(editor.homeToolbar, './Assets/icons/svg_paste', "Paste", "Paste", False)
    paste.triggered.connect(editor.frameView.toolbar_paste)

    cut = build_action(editor.homeToolbar, './Assets/icons/svg_cut', "Cut", "Cut", False)
    cut.triggered.connect(lambda: editorSignalsInstance.widgetCut.emit(DraggableContainer))
    
    copy = build_action(editor.homeToolbar, './Assets/icons/svg_copy', "Copy", "Copy", False)
    copy.triggered.connect(lambda: editorSignalsInstance.widgetCopied.emit())

    font_family = QFontComboBox()
    font_family.setObjectName("Font")
    font_family.setFixedWidth(150)
    default_font = font_family.currentFont().family()
    print(f"default font is {default_font}")
    font_family.currentFontChanged.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Font, font_family.currentFont().family()))

    font_size = QComboBox()
    font_size.setObjectName("Font Size")
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

    #refactor = build_action(editor.homeToolbar, './Assets/icons/bold', "Bold", "Bold", True)
    #refactor.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Refactor, None))
    
    delete = build_action(editor.homeToolbar, './Assets/icons/svg_delete', "Delete", "Delete", False)
    delete.triggered.connect(lambda: editorSignalsInstance.widgetRemoved.emit(DraggableContainer))
    
    # Bullets with placeholder for more bullet options
    bullets = build_action(editor.homeToolbar, './Assets/icons/svg_bullets', "Bullets", "Bullets", False)
    bullets.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Bullet, None))

       
    # Adds the undo and redo buttons to the toolbar 
    undo = build_action(editor.homeToolbar, './Assets/icons/svg_undo', "Undo", "Undo", False)
    redo = build_action(editor.homeToolbar, './Assets/icons/svg_redo', "Redo", "Redo", False)
    
    editor.homeToolbar.addWidget(spacer1)
    editor.homeToolbar.addActions([paste, cut, copy])
    
    editor.homeToolbar.addSeparator()
    
    editor.homeToolbar.addWidget(font_family)
    editor.homeToolbar.addWidget(font_size)
    
    editor.homeToolbar.addSeparator()
    
    editor.homeToolbar.addActions([undo, redo, bold, italic, underline, strikethrough, fontColor, textHighlightColor, bgColor, delete, bullets])

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
    
    numbering = build_menubutton(editor, './Assets/icons/svg_bullet_number', "", "Numbering", "width:35px;", numbering_menu)
   
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

    
    # ---------------------------------------------------------------------------------
    # Classic Home Toolbar

    editor.classicToolbar = QToolBar()
    editor.classicToolbar.setObjectName('classicHomeToolbar')
    editor.classicToolbar.setIconSize(QSize(18,18))
    editor.classicToolbar.setFixedHeight(40)
    editor.classicToolbar.setMovable(False)
    editor.classicToolbar.setVisible(False)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.classicToolbar)


    
    # ---------------------------------------------------------------------------------
    # insertToolbar code 

    editor.insertToolbar.setObjectName('insertToolbar')
    editor.insertToolbar.setIconSize(QSize(18,18))
    editor.insertToolbar.setFixedHeight(40)
    editor.insertToolbar.setMovable(False)
    editor.insertToolbar.setVisible(False)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.insertToolbar)

    table = build_button(editor.insertToolbar, './Assets/icons/svg_table', "Table", "Add a Table", False)
    table.clicked.connect(editor.frameView.toolbar_table)
    
    insertSpace = build_button(editor.insertToolbar, './Assets/icons/svg_insert_space', "Insert Space", "Insert Space", False)
    
    screensnip = build_button(editor.insertToolbar, './Assets/icons/svg_screensnip', "Screensnip", "Screensnip", False)
    screensnip.clicked.connect(editor.frameView.toolbar_snipScreen)
    
    pictures = build_button(editor.insertToolbar, './Assets/icons/svg_pictures', "Pictures" , "Pictures", False)
    pictures.clicked.connect(editor.frameView.toolbar_pictures)

    hyperlink = build_button(editor.insertToolbar, './Assets/icons/svg_hyperlink', "Hyperlink", "Hyperlink", False)
    hyperlink.clicked.connect(editor.frameView.toolbar_hyperlink)

    # date and time menu start
    dateTime_menu = QMenu(editor)
    
    date = build_action(dateTime_menu, './Assets/icons/svg_date', "Date", "Date", False)
    date.triggered.connect(editor.frameView.toolbar_date)
    
    time = build_action(dateTime_menu, './Assets/icons/svg_time', "Time", "Time", False)
    time.triggered.connect(editor.frameView.toolbar_time)
    
    dateTime_menu.addActions([date, time])
    
    dateTime = build_menubutton(editor, './Assets/icons/svg_dateTime', "Date && Time", "Date & Time", "width:120px;", dateTime_menu)
    
    editor.insertToolbar.addWidget(spacer2)

    editor.insertToolbar.addWidget(table) 
    
    editor.insertToolbar.addSeparator()
    
    editor.insertToolbar.addWidget(insertSpace)
    
    editor.insertToolbar.addSeparator()
    
    editor.insertToolbar.addWidget(screensnip)
    editor.insertToolbar.addWidget(pictures)
    
    editor.insertToolbar.addSeparator()
    
    editor.insertToolbar.addWidget(hyperlink)
    
    editor.insertToolbar.addSeparator()

    editor.insertToolbar.addWidget(dateTime)
    
    # ---------------------------------------------------------------------------------
    # drawToolbar code

    editor.drawToolbar.setObjectName('drawToolbar')
    editor.drawToolbar.setIconSize(QSize(18, 18))
    editor.drawToolbar.setFixedHeight(40)
    editor.drawToolbar.setMovable(False)
    editor.drawToolbar.setVisible(False)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.drawToolbar)
    
    undo_action = QAction(QIcon('./Assets/icons/undo.png'), '&Undo', editor)
    undo.triggered.connect(editor.triggerUndo)
    
    redo_action = QAction(QIcon('./Assets/icons/redo.png'), '&Redo', editor)
    redo.triggered.connect(editor.triggerRedo)
    # redo.triggered.connect(editor.frameView.triggerRedo)
       
    paperColor= build_action(editor.drawToolbar, './Assets/icons/svg_paper', "Paper Color", "Paper Color", False)
    paperColor.triggered.connect(lambda: editor.frameView.pageColor(QColorDialog.getColor()))
     
    editor.drawToolbar.addWidget(spacer3)
    editor.drawToolbar.addActions([undo, redo])
    
    editor.drawToolbar.addSeparator()

    editor.drawToolbar.addAction(paperColor)

    # ---------------------------------------------------------------------------------
    # pluginToolbar code

    editor.pluginToolbar.setObjectName('pluginToolbar')
    editor.pluginToolbar.setIconSize(QSize(18,18))
    editor.pluginToolbar.setFixedHeight(40)
    editor.pluginToolbar.setMovable(False)
    editor.pluginToolbar.setVisible(False)
    editor.addToolBar(Qt.ToolBarArea.TopToolBarArea, editor.pluginToolbar)

    add_widget = build_button(editor, './Assets/icons/svg_question', 'Add Custom Widget', 'Add Custom Widget', False)

    editor.pluginToolbar.addWidget(add_widget)
    # ---------------------------------------------------------------------------------

    editor.tabbar.addTab(editor.fileToolbar, '&File')
    editor.tabbar.addTab(editor.homeToolbar, '&Home')
    editor.tabbar.addTab(editor.insertToolbar, '&Insert')
    editor.tabbar.addTab(editor.drawToolbar, '&Draw')
    editor.tabbar.addTab(editor.pluginToolbar, '&Plugins')

    # Sets the first shown tab as the home tab
    editor.tabbar.setCurrentIndex(1)

def check_appearance():
    """Checks DARK/LIGHT mode of macos."""
    cmd = 'defaults read -g AppleInterfaceStyle'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    return bool(p.communicate()[0])  

# toggles the visibility of the specified toolbar based on user interaction
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

# opens a color dialog for selecting font color or background color
def openGetColorDialog(purpose):
    color = QColorDialog.getColor()
    if color.isValid():
        if purpose == "font":
            editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontColor, color)
        elif purpose == "background":
            editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.BackgroundColor, color)

# creates a QAction object with the specified parameters
def build_action(parent, icon_path, action_name, tooltip, checkable):
    action = QAction(QIcon(icon_path), action_name, parent)
    action.setObjectName(action_name)
    action.setStatusTip(tooltip)
    action.setCheckable(checkable)
    return action

# creates a QPushButton widget with the specified parameters  
def build_button(parent, icon_path, text, tooltip, checkable):
    button = QPushButton(parent)
    button.setIcon(QIcon(icon_path))
    button.setObjectName(text)
    button.setText(text)
    button.setToolTip(tooltip)
    button.setCheckable(checkable)
    return button
    
# creates a QToolButton widget with an associated menu
def build_menubutton(parent, icon_path, text, tooltip, style, menu):
    button = QToolButton(parent)
    button.setIconSize(QSize(18,18))
    button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    button.setPopupMode(QToolButton.MenuButtonPopup)
    button.setIcon(QIcon(icon_path))
    button.setText(text)
    button.setToolTip(tooltip)
    button.setObjectName(tooltip)
    button.setStyleSheet(style)
    button.setMenu(menu)
    return button
