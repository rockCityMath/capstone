from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from Modules.EditorSignals import editorSignalsInstance, ChangedWidgetAttribute, CheckSignal

import subprocess

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]


class TextboxWidget(QTextEdit):
    def __init__(self, x, y, w=15, h=30, t=""):
        super().__init__()

        def check_appearance():
            """Checks DARK/LIGHT mode of macos."""
            cmd = 'defaults read -g AppleInterfaceStyle'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
            return bool(p.communicate()[0])   
        
        self.setGeometry(x, y, w, h)  # This sets geometry of DraggableObject
        self.setText(t)

        # self.setStyleSheet("background-color: rgba(0, 0, 0, 0); selection-background-color: #FFFFFF;")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textChanged.connect(self.textChangedEvent)
        editorSignalsInstance.widgetAttributeChanged.connect(self.widgetAttributeChanged)



        if check_appearance() == True:
            self.setStyleSheet("background-color: rgba(31,31,30,255);")
            #self.changeBackgroundColorEvent(31, 31, 30)
            self.setTextColor("white")
            self.changeAllTextColors("white")
        else:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            #self.changeBackgroundColorEvent(0,0,0)
            self.setTextColor("black")
            self.changeAllTextColors("black")

        self.setTextInteractionFlags(Qt.TextEditorInteraction | Qt.TextBrowserInteraction)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            self.handleTabKey()
            return True  # To prevent the default Tab key behavior
        '''if event.type() == QEvent.FocusOut:
            if self.checkEmpty():
                parent = self.parent()
                if parent is not None:
                    parent.deleteLater()'''

        return super(TextboxWidget, self).eventFilter(obj, event)

    # upon clicking somewhere else, remove selection of highlighted text
    def setCursorPosition(self, event):
        print("SET TEXT CURSOR POSITION TO MOUSE POSITION")
        cursor = self.cursorForPosition(event.pos())
        self.setTextCursor(cursor)

    # Initial size is w=15, h=30. once changes to textbox has been detected, change the size
    def textChangedEvent(self):
        width = 150
        height = 50
        if len(self.toPlainText()) < 2:
            self.resize(width, height)
        else:
            # handle cases where text reaches past the textbox
            document = self.document()
            documentSize = document.size().toSize()
            documentHeight = documentSize.height()
            # the document height is the text height. This is to expand the widget size to match document height
            if(height < documentHeight):
                height = documentHeight
                self.resize(width, height)
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        


    

    @staticmethod
    def new(clickPos: QPoint):
        return TextboxWidget(clickPos.x(), clickPos.y())

    def __getstate__(self):
        data = {}

        data["geometry"] = self.parentWidget().geometry()
        data["content"] = self.toHtml()
        data["stylesheet"] = self.styleSheet()
        return data

    def __setstate__(self, data):
        self.__init__(
            data["geometry"].x(),
            data["geometry"].y(),
            data["geometry"].width(),
            data["geometry"].height(),
            data["content"],
        )
        self.setStyleSheet(data["stylesheet"])

    def checkEmpty(self):
        if len(self.toPlainText()) < 1:
            return True
        return False
    
    # Handles events from any toolbar button
    def widgetAttributeChanged(self, changedWidgetAttribute, value):
    # dictionary of toolbar functions
        attribute_functions = {
            # note: for functions with no value passed, lambda _ will allow it to pass with no value

            # font functions
            ChangedWidgetAttribute.FontSize: lambda val: self.changeFontSizeEvent(val),
            ChangedWidgetAttribute.FontBold: lambda _: self.changeFontBoldEvent(),
            ChangedWidgetAttribute.FontItalic: lambda _: self.changeFontItalicEvent(),
            ChangedWidgetAttribute.FontUnderline: lambda _: self.changeFontUnderlineEvent(),
            ChangedWidgetAttribute.Strikethrough: lambda _: self.setStrikeOut(),
            ChangedWidgetAttribute.Font: lambda val: self.changeFontEvent(val),
            ChangedWidgetAttribute.FontColor: lambda val: self.changeFontColorEvent(val),
            ChangedWidgetAttribute.TextHighlightColor: lambda val: self.changeTextHighlightColorEvent(val),

            # background color functions
            ChangedWidgetAttribute.BackgroundColor: lambda val: self.changeBackgroundColorEvent(val),
            ChangedWidgetAttribute.PaperColor: lambda val: self.paperColor(val), # not implemented yet

            # Bullet list functions
            ChangedWidgetAttribute.Bullet: lambda _: self.bullet_list("bulletReg"),
            ChangedWidgetAttribute.Bullet_Num: lambda _: self.bullet_list("bulletNum"),
            ChangedWidgetAttribute.BulletUA: lambda _: self.bullet_list("bulletUpperA"),
            ChangedWidgetAttribute.BulletUR: lambda _: self.bullet_list("bulletUpperR"),

            # Alignment functions
            ChangedWidgetAttribute.AlignLeft: lambda _: self.changeAlignmentEvent("alignLeft"),
            ChangedWidgetAttribute.AlignCenter: lambda _: self.changeAlignmentEvent("alignCenter"),
            ChangedWidgetAttribute.AlignRight: lambda _: self.changeAlignmentEvent("alignRight")
        }
        # if current widget is in focus
        if (self.hasFocus or self.parentWidget().hasFocus) and changedWidgetAttribute in attribute_functions:
        #if self.hasFocus() and changedWidgetAttribute in attribute_functions:
            print(f"{changedWidgetAttribute} {value}")
            # Calls the function in the dictionary
            attribute_functions[changedWidgetAttribute](value)
        else:
            # Handle invalid attribute or other cases
            pass

    def customMenuItems(self):
        def build_action(parent, icon_path, action_name, set_status_tip, set_checkable):
            action = QAction(QIcon(icon_path), action_name, parent)
            action.setStatusTip(set_status_tip)
            action.setCheckable(set_checkable)
            return action

        toolbarTop = QToolBar()
        toolbarTop.setIconSize(QSize(16, 16))
        toolbarTop.setMovable(False)

        toolbarBottom = QToolBar()
        toolbarBottom.setIconSize(QSize(16, 16))
        toolbarBottom.setMovable(False)

        font = QFontComboBox()
        font.setFixedWidth(150) 
        font.currentFontChanged.connect(
            lambda x: self.setCurrentFontCustom(
                font.currentFont() if x else self.currentFont()
            )
        )

        size = QComboBox()
        size.setFixedWidth(50)
        size.addItems([str(fs) for fs in FONT_SIZES])
        size.currentIndexChanged.connect(
            lambda x: self.setFontPointSizeCustom(
                FONT_SIZES[x] if x else self.fontPointSize()
            )
        )
        
        align_left = build_action(toolbarBottom, "./Assets/icons/svg_align_left", "Align Left", "Align Left", False)
        # align_left.triggered.connect(lambda x: self.setAlignment(Qt.AlignLeft))
        align_left.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignLeft, None))


        align_center = build_action(toolbarBottom, "./Assets/icons/svg_align_center", "Align Center", "Align Center", False)
        # align_center.triggered.connect(lambda x: self.setAlignment(Qt.AlignCenter))
        align_center.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignCenter, None))


        align_right = build_action(toolbarBottom, "./Assets/icons/svg_align_right", "Align Right", "Align Right", False)
        align_right.triggered.connect(lambda x: self.setAlignment(Qt.AlignRight))
        align_right.triggered.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.AlignRight, None))


        bold = build_action(
            toolbarBottom, "./Assets/icons/svg_font_bold", "Bold", "Bold", True
        )
        bold.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontBold, None))

        italic = build_action(toolbarBottom, "./Assets/icons/svg_font_italic", "Italic", "Italic", True)
        italic.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontItalic, None))

        underline = build_action(toolbarBottom,"./Assets/icons/svg_font_underline","Underline","Underline",True,)
        underline.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontUnderline, None))

        strikethrough = build_action(toolbarBottom,"./Assets/icons/svg_strikethrough", "Strikethrough", "Strikethrough", True)
        strikethrough.toggled.connect(lambda: editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.Strikethrough, None))


        fontColor = build_action(toolbarBottom,"./Assets/icons/svg_font_color","Font Color","Font Color",False)
        fontColor.triggered.connect(
            lambda: self.setTextColorCustom(QColorDialog.getColor())
        )

        bgColor = build_action(toolbarBottom,"./Assets/icons/svg_font_bucket","Background Color","Background Color",False)
        # bgColor.triggered.connect(lambda: self.setBackgroundColor(QColorDialog.getColor()))
        bgColor.triggered.connect(lambda: self.changeBackgroundColorEvent(QColorDialog.getColor()))
        textHighlightColor = build_action(toolbarBottom,"./Assets/icons/svg_textHighlightColor","Text Highlight Color","Text Highlight Color",False,)
        textHighlightColor.triggered.connect(lambda: self.changeTextHighlightColorEvent(QColorDialog.getColor()))

        bullets = build_action(toolbarBottom, "./Assets/icons/svg_bullets", "Bullets", "Bullets", True)
        bullets.toggled.connect(lambda: self.bullet_list("bulletReg"))

        toolbarTop.addWidget(font)
        toolbarTop.addWidget(size)

        toolbarBottom.addActions(
            [              
                bold,
                italic,
                underline,
                # strikethrough,
                textHighlightColor,
                fontColor, 
                bullets
             ]
        )
        
        # numbering menu has to be added inbetween
        numbering_menu = QMenu(self)
        bullets_num = numbering_menu.addAction(QIcon("./Assets/icons/svg_bullet_number"), "")
        bulletUpperA = numbering_menu.addAction(QIcon("./Assets/icons/svg_bulletUA"), "")
        bulletUpperR = numbering_menu.addAction(QIcon("./Assets/icons/svg_bulletUR"), "")

        bullets_num.triggered.connect(lambda: self.bullet_list("bulletNum"))
        bulletUpperA.triggered.connect(lambda: self.bullet_list("bulletUpperA"))
        bulletUpperR.triggered.connect(lambda: self.bullet_list("bulletUpperR"))


        numbering = QToolButton(self)
        numbering.setIcon(QIcon("./Assets/icons/svg_bullet_number"))
        numbering.setPopupMode(QToolButton.MenuButtonPopup)
        numbering.setMenu(numbering_menu)
        
	# This code would fix an error on the command line but it also makes it not look good soooo
        numbering.setParent(numbering_menu)
        
        toolbarBottom.addWidget(numbering)

        # not required for right-click menu as they arent originally present in OneNote
        '''
        toolbarBottom.addActions(
            [  
                bgColor,
                align_left,
                align_center,
                align_right
            ]
        )
        '''
        qwaTop = QWidgetAction(self)
        qwaTop.setDefaultWidget(toolbarTop)
        qwaBottom = QWidgetAction(self)
        qwaBottom.setDefaultWidget(toolbarBottom)

        return [qwaTop, qwaBottom]

    def setFontItalicCustom(self, italic: bool):
        if not self.applyToAllIfNoSelection(lambda: self.setFontItalic(italic)):
            print("setFontItalicCustom Called")
            self.setFontItalic(italic)

    def setFontWeightCustom(self, weight: int):
        if not self.applyToAllIfNoSelection(lambda: self.setFontWeight(weight)):
            self.setFontWeight(weight)

    def setFontUnderlineCustom(self, underline: bool):
        if not self.applyToAllIfNoSelection(lambda: self.setFontUnderline(underline)):
            self.setFontUnderline(underline)

    def setCurrentFontCustom(self, font: QFont):
        if not self.applyToAllIfNoSelection(lambda: self.setCurrentFontCustom(font)):
            self.setCurrentFont(font)

    def setFontPointSizeCustom(self, size):
        if not self.applyToAllIfNoSelection(lambda: self.setFontPointSize(size)):
            self.setFontPointSize(size)

    def setTextColorCustom(self, color):
        print(color)
        if not self.applyToAllIfNoSelection(lambda: self.setTextColor(color)):
            self.setTextColor(color)

    def setBackgroundColor(self, color: QColor):
        rgb = color.getRgb()
        self.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")

    # If no text is selected, apply to all, else apply to selection
    def applyToAllIfNoSelection(self, func):
        if len(self.textCursor().selectedText()) != 0:
            return False

        # Select all text
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

        # Run function
        func()

        # Unselect all text
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        return True

    def changeFontSizeEvent(self, weight):
        print("changeFontSizeEvent Called")
        self.setFontWeightCustom(weight)

    # for communicating the signal editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontItalic, None)
    # current issue for Event Functions: Only affects highlighted

    def changeFontItalicEvent(self):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        # Checks if currently selected text is italics
        is_italic = current_format.fontItalic()

        # toggles the italics
        current_format.setFontItalic(not is_italic)

        # Apply modified format to selected text
        cursor.setCharFormat(current_format)

        # Update text cursor with modified format
        self.setTextCursor(cursor)

    def changeFontBoldEvent(self):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        # Checks if currently selected text is bold
        is_bold = current_format.fontWeight() == 700

        # toggles the italics
        if is_bold:
            current_format.setFontWeight(500)
        else:
            current_format.setFontWeight(700)
        # Apply modified format to selected text
        cursor.setCharFormat(current_format)

        # Update text cursor with modified format
        self.setTextCursor(cursor)

    def changeFontUnderlineEvent(self):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        # Checks if currently selected text is bold
        is_underlined = current_format.fontUnderline()

        # toggles the underline
        current_format.setFontUnderline(not is_underlined)

        # Apply modified format to selected text
        cursor.setCharFormat(current_format)

        # Update text cursor with modified format
        self.setTextCursor(cursor)

    def bullet_list(self, bulletType):
        cursor = self.textCursor()
        textList = cursor.currentList()

        if textList:
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            removed = 0
            for i in range(textList.count()):
                item = textList.item(i - removed)
                if item.position() <= end and item.position() + item.length() > start:
                    textList.remove(item)
                    blockCursor = QTextCursor(item)
                    blockFormat = blockCursor.blockFormat()
                    blockFormat.setIndent(0)
                    blockCursor.mergeBlockFormat(blockFormat)
                    removed += 1

            cursor = self.textCursor()
            cursor.setBlockFormat(QTextBlockFormat())  # Clear any previous block format

            self.setTextCursor(cursor)
            self.setFocus()

        else:
            listFormat = QTextListFormat()

            if bulletType == "bulletNum":
                style = QTextListFormat.ListDecimal
            if bulletType == "bulletReg":
                style = QTextListFormat.ListDisc
            if bulletType == "bulletLowerA":
                style = QTextListFormat.ListLowerAlpha
            if bulletType == "bulletLowerR":
                style = QTextListFormat.ListLowerRoman
            if bulletType == "bulletUpperA":
                style = QTextListFormat.ListUpperAlpha
            if bulletType == "bulletUpperR":
                style = QTextListFormat.ListUpperRoman

            listFormat.setStyle(style)
            cursor.createList(listFormat)

            self.setTextCursor(cursor)
            self.setFocus()
    def changeAlignmentEvent(self, alignmentType):
        print("Alignment Event Called")
        cursor = self.textCursor()
        blockFormat = cursor.blockFormat()
        
        if alignmentType == "alignLeft":
            blockFormat.setAlignment(Qt.AlignLeft)
        elif alignmentType == "alignCenter":
            blockFormat.setAlignment(Qt.AlignCenter)
        elif alignmentType == "alignRight":
            blockFormat.setAlignment(Qt.AlignRight)
            
        cursor.setBlockFormat(blockFormat)
        self.setTextCursor(cursor)
        self.setFocus()

    def handleTabKey(self):
        cursor = self.textCursor()
        block = cursor.block()
        block_format = block.blockFormat()
        textList = cursor.currentList()

        if textList:
            if cursor.atBlockStart() and block.text().strip() == "":
                current_indent = block_format.indent()

                if current_indent < 11:

                    if current_indent % 3 == 0:
                        block_format.setIndent(current_indent + 1)
                        cursor.setBlockFormat(block_format)
                        cursor.beginEditBlock()
                        list_format = QTextListFormat()
                        currentStyle = textList.format().style()

                        if currentStyle == QTextListFormat.ListDisc:
                            list_format.setStyle(QTextListFormat.ListCircle)
                        if currentStyle == QTextListFormat.ListDecimal:
                            list_format.setStyle(QTextListFormat.ListLowerAlpha)
                        if currentStyle == QTextListFormat.ListLowerAlpha:
                            list_format.setStyle(QTextListFormat.ListLowerRoman)
                        if currentStyle == QTextListFormat.ListLowerRoman:
                            list_format.setStyle(QTextListFormat.ListDecimal)
                        if currentStyle == QTextListFormat.ListUpperAlpha:
                            list_format.setStyle(QTextListFormat.ListLowerAlpha)
                        if currentStyle == QTextListFormat.ListUpperRoman:
                            list_format.setStyle(QTextListFormat.ListLowerAlpha)

                        cursor.createList(list_format)
                        cursor.endEditBlock()

                    if current_indent % 3 == 1:
                        block_format.setIndent(current_indent + 1)
                        cursor.setBlockFormat(block_format)
                        cursor.beginEditBlock()
                        list_format = QTextListFormat()
                        currentStyle = textList.format().style()

                        if currentStyle == QTextListFormat.ListCircle:
                            list_format.setStyle(QTextListFormat.ListSquare)
                        if currentStyle == QTextListFormat.ListLowerAlpha:
                            list_format.setStyle(QTextListFormat.ListLowerRoman)
                        if currentStyle == QTextListFormat.ListLowerRoman:
                            list_format.setStyle(QTextListFormat.ListDecimal)
                        if currentStyle == QTextListFormat.ListDecimal:
                            list_format.setStyle(QTextListFormat.ListLowerAlpha)

                        cursor.createList(list_format)
                        cursor.endEditBlock()

                    if current_indent % 3 == 2:
                        block_format.setIndent(current_indent + 1)
                        cursor.setBlockFormat(block_format)
                        cursor.beginEditBlock()
                        list_format = QTextListFormat()
                        currentStyle = textList.format().style()

                        if currentStyle == QTextListFormat.ListSquare:
                            list_format.setStyle(QTextListFormat.ListDisc)
                        if currentStyle == QTextListFormat.ListLowerRoman:
                            list_format.setStyle(QTextListFormat.ListDecimal)
                        if currentStyle == QTextListFormat.ListDecimal:
                            list_format.setStyle(QTextListFormat.ListLowerAlpha)
                        if currentStyle == QTextListFormat.ListLowerAlpha:
                            list_format.setStyle(QTextListFormat.ListLowerRoman)

                        cursor.createList(list_format)
                        cursor.endEditBlock()

                    cursor.insertText("")
                    cursor.movePosition(QTextCursor.StartOfBlock)
            self.setTextCursor(cursor)

        else:
            cursor.insertText("    ")
            self.setTextCursor(cursor)
            pass

    def insertTextLink(self, link_address, display_text):
        self.setOpenExternalLinks(True)
        link_html = f'<a href="{link_address}">{display_text}</a>'
        cursor = self.textCursor()
        cursor.insertHtml(link_html)
        QDesktopServices.openUrl(link_html)

    def changeFontSizeEvent(self, value):
        # todo: when textbox is in focus, font size on toolbar should match the font size of the text

        cursor = self.textCursor()
        current_format = cursor.charFormat()

        current_format.setFontPointSize(value)
        cursor.setCharFormat(current_format)

        self.setTextCursor(cursor)

    def changeFontEvent(self, font_style):
        cursor = self.textCursor()
        current_format = cursor.charFormat()
        current_format.setFont(font_style)

        cursor.setCharFormat(current_format)

        self.setTextCursor(cursor)

    # Changes font text color
    def changeFontColorEvent(self, new_font_color):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        color = QColor(new_font_color)
        if color.isValid():
            current_format.setForeground(color)

        cursor.setCharFormat(current_format)

        # to not get stuck on highlighted text
        # self.deselectText()
        # self.setTextCursor(cursor)

    # Changes color of whole background

    def changeBackgroundColorEvent(self, color: QColor):
        print("CHANGE BACKGROUND COLOR EVENT")
        
        if color.isValid():
            rgb = color.getRgb()
            self.setStyleSheet(f"QTextEdit {{background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); }}")

        self.deselectText()

    # Changes textbox background color
    def changeTextHighlightColorEvent(self, new_highlight_color):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        color = QColor(new_highlight_color)
        if color.isValid():
            current_format.setBackground(color)

        cursor.setCharFormat(current_format)
        # self.deselectText()

        # self.setTextCursor(cursor)

    # Used to remove text highlighting
    def deselectText(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    # Adds bullet list to text
    def changeBulletEvent(self):
        # put bullet function here
        print("bullet press")

    def changeAllTextColors(self, new_color):
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.Start)

                while not cursor.atEnd():
                    cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    char_format = cursor.charFormat()

                    if char_format.foreground().color() == Qt.black or Qt.white:
                        char_format.setForeground(QColor(new_color))
                        cursor.setCharFormat(char_format)

                cursor.movePosition(QTextCursor.Start)
                self.setTextCursor(cursor)

    def setStrikeOut(self):
        print("strikeout event")
        cursor = self.textCursor()
        format = cursor.charFormat()

        # Toggle strikethrough
        format.setFontStrikeOut(not format.fontStrikeOut())

        # Apply the new format to the selected text
        #cursor.mergeCharFormat(format)
        cursor.setCharFormat(format)

        #cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        #self.setFocus()



    def refactorTest(self):
        cursor = self.textCursor()
        current_format = cursor.charFormat()

        # Checks if currently selected text is bold
        is_bold = current_format.fontWeight() == 700

        # toggles the italics
        if is_bold:
            current_format.setFontWeight(500)
        else:
            current_format.setFontWeight(700)
        # Apply modified format to selected text
        cursor.setCharFormat(current_format)
        cursor.mergeCharFormat(format)
        # Emit signal if no text is bold to toggle bold off
        if not is_bold:
            editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.FontBold, None)
        # Update text cursor with modified format
        self.setTextCursor(cursor)

    def selectAllText(self):
        print("Select All Text function from textwidget called")
        cursor = self.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def removeWidget(self):
        if(self.checkEmpty()):
            print("removing widget")
            editorSignalsInstance.widgetRemoved.emit(self)