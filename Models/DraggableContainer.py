from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import *
from Modules.Enums import *
from Modules.EditorSignals import editorSignalsInstance, ChangedWidgetAttribute
from enum import Enum

# Draggable object modes
class Mode(Enum):
    NONE = 0,
    MOVE = 1,
    RESIZETL = 2,
    RESIZET = 3,
    RESIZETR = 4,
    RESIZER = 5,
    RESIZEBR = 6,
    RESIZEB = 7,
    RESIZEBL = 8,
    RESIZEL = 9

# Object that wraps a child widget and makes it draggable/resizable (read: manages geometry)
# Based off https://wiki.qt.io/Widget-moveable-and-resizeable <3
class DraggableContainer(QWidget):
    menu = None
    mode = Mode.NONE
    position = None
    outFocus = Signal(bool) # Signal emitted when the container loses focus
    newGeometry = Signal(QRect) # Signal emitted when the container's geometry changes

    #  Initializes a DraggableContainer object
    def __init__(self, childWidget, editorFrame):
        super().__init__(parent=editorFrame)

        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()
        self.old_x = 0
        self.old_y = 0
        self.vLayout = QVBoxLayout(self)
        self.setChildWidget(childWidget)
        self.m_showMenu = False
        self.m_isEditing = True
        self.installEventFilter(editorFrame.multiselector)
        self.setGeometry(childWidget.geometry())
        self.old_state = {}
        self.isSelected = False

        self.previousGeometry = self.geometry() # for undo

        self.childWidgetActive = False
        self.menu = self.buildDragContainerMenu()

        if hasattr(self.childWidget, "newGeometryEvent"): self.newGeometry.connect(childWidget.newGeometryEvent)
        
        editorSignalsInstance.widgetAttributeChanged.connect(self.deselect_and_delete)
        editorSignalsInstance.widgetAttributeChanged.connect(self.widgetAttributeChanged)

        
                
    def setChildWidget(self, childWidget):
        if childWidget:
            self.childWidget = childWidget
            self.childWidget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.childWidget.setParent(self)
            self.childWidget.releaseMouse()
            self.childWidget.installEventFilter(self)
            self.vLayout.addWidget(childWidget)
            self.vLayout.setContentsMargins(0,0,0,0)

    def eventFilter(self, obj, e):

        # If child widget resized itself, resize this drag container, not ideal bc child resizes on hover
        if isinstance(e, QResizeEvent):
            self.resize(self.childWidget.size())
        return False

    # Displays the container menu at a given position
    def popupShow(self, pt: QPoint):
        global_ = self.mapToGlobal(pt)
        self.m_showMenu = True
        self.menu.exec(global_)
        self.m_showMenu = False
        
    def mousePressEvent(self, e: QMouseEvent):
        self.position = QPoint(e.globalX() - self.geometry().x(), e.globalY() - self.geometry().y())

        print("Draggable Container MOUSE PRESS")

        # Undo related
        # self.old_x = e.globalX()
        # self.old_y = e.globalY()
        # self.old_state = {'type':'object','action':'move','name':self.name,'x':self.old_x,'y':self.old_y}

        self.previousGeometry = self.geometry()

        if not self.m_isEditing:
            print("NOT EDIT")
            return
        if not e.buttons() and Qt.LeftButton:
            print("Draggable Container GOT MOUSE PRESS")
            self.setCursorShape(e.pos())


            return True
        if e.button() == Qt.RightButton:
            self.popupShow(e.pos())
            e.accept()

        self.childWidget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.childWidget.setFocus()
        # checks if the child is a textbox
        if (isinstance(self.childWidget, QTextEdit)):
            # sets cursor position to where mouse is upon clicking
            self.childWidget.setCursorPosition(e)
            # check settings at cursor and match the visual of the toolbar toggle with the current cursor setting


        #brings text cursor to cursor position but causes exception
        '''if isinstance(self.childWidget, TextboxWidget):
            self.childWidget.setCursorPosition(e)
        else:
            # Handle the case where self.childWidget is not a TextBox
            pass'''
       


    # On double click, focus on child and make mouse events pass through this container to child
    def mouseDoubleClickEvent(self, e: QMouseEvent):
        print("MOUSEDOUBLECLICKEVENT FROM DRAGGABLE CONTAINER")
        self.childWidget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.childWidget.setFocus()
        return

    def mouseReleaseEvent(self, e: QMouseEvent):
        # self.parentWidget().undo_stack.append(self.old_state)
        # self.parentWidget().autosaver.onChangeMade()

        self.parentWidget().newGeometryOnDCEvent(self)
        return True # Dont let the release go to the editor frame

    def leaveEvent(self, e: QMouseEvent):
        #if(self.childWidget.hasFocus() == False):
        self.childWidget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("border: none;")
        # If mouse leaves draggable container, set focus to the editor
        #if self.childWidget.hasFocus():
        #    self.setFocus()'''

    # this is to lose the border of the draggable container if the container is no longer in focus
    '''def focusOutEvent(self, event: QMouseEvent):
        print("FOCUS OUT EVENT CALLED FROM DRAGGABLE CONTAINER")
        self.childWidget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("border: none;")
        super().focusOutEvent(event)'''

    # Builds and returns the context menu for the container
    def buildDragContainerMenu(self):

        # Get custom menu actions from child widget
        customMenuItems = []
        widgetCustomMenu = getattr(self.childWidget, "customMenuItems", None)
        if callable(widgetCustomMenu):
            customMenuItems = self.childWidget.customMenuItems()

        menu = QMenu()

        # Add any widget type menu actions from child
        for item in customMenuItems:
            if type(item) == QWidgetAction:
                menu.addAction(item)

        # Add standard menu actions
        cut = QAction("Cu&t", self)
        cut.triggered.connect(lambda: editorSignalsInstance.widgetCut.emit(self))

        copy = QAction("&Copy", self)
        copy.triggered.connect(lambda: editorSignalsInstance.widgetCopied.emit(self))
        
        paste = QAction("&Paste", self)
        paste.triggered.connect(lambda: self.pasteWidget(self.pos()))
        
        delete = QAction("&Delete", self)
        delete.triggered.connect(lambda: editorSignalsInstance.widgetRemoved.emit(self))
        
        menu.addActions([cut, copy, paste, delete])
        
        menu.addSeparator()

        link = QAction("&Link", self)
        # link.triggered.connect(lambda: self.insertLink(event.pos()))
        
        menu.addAction(link)
        
        menu.addSeparator()
        
        orderMenu = QMenu("&Order", self)
        
        bringForwards = QAction("Bring &Forwards", self)
        bringForwards.triggered.connect(self.childWidget.raise_())
        
        orderMenu.addAction(bringForwards)
        
        # not ready for deployment
        # menu.addMenu(orderMenu)
            
        # text boxes
        if isinstance(self.childWidget, QTextEdit):
            table = QAction("&Table", self)
            # table.triggered.connect(lambda: self.newWidgetOnSection(TableWidget, event.pos()))
        
            menu.addAction(table) 
        
            menu.addSeparator()
            
        # images
        elif isinstance(self.childWidget, QLabel):
            # Create submenus for rotate and resize
            rotateMenu = QMenu("R&otate", self)
            rotateMenu.setStyleSheet("font-size: 11pt;")
            
            resizeMenu = QMenu("&Resize", self)
            resizeMenu.setStyleSheet("font-size: 11pt;")

            # Create actions for rotate submenu
            rotateRightAction = QAction("Rotate &Right 90°", self)
            rotateRightAction.triggered.connect(self.childWidget.rotate90Right)
            rotateRightAction.setIcon(QIcon('./Assets/icons/svg_rotate_right'))
            
            rotateLeftAction = QAction("Rotate &Left 90°", self)
            rotateLeftAction.triggered.connect(self.childWidget.rotate90Left)
            rotateLeftAction.setIcon(QIcon('./Assets/icons/svg_rotate_left'))
            
            flipHorizontal = QAction("Flip &Horizontal", self)
            flipHorizontal.triggered.connect(self.childWidget.flipHorizontal)
            flipHorizontal.setIcon(QIcon('./Assets/icons/svg_flip_horizontal'))
            
            flipVertical = QAction("Flip &Vertical", self)
            flipVertical.triggered.connect(self.childWidget.flipVertical)
            flipVertical.setIcon(QIcon('./Assets/icons/svg_flip_vertical'))

            # Add actions to rotate submenu
            rotateMenu.addActions([rotateLeftAction, rotateRightAction, flipHorizontal, flipVertical])

            # Create actions for resize submenu
            shrinkImageAction = QAction("&Shrink Image", self)
            shrinkImageAction.triggered.connect(self.childWidget.shrinkImage)
            shrinkImageAction.setIcon(QIcon('./Assets/icons/svg_shrink'))
            
            expandImageAction = QAction("&Expand Image", self)
            expandImageAction.triggered.connect(self.childWidget.expandImage)
            expandImageAction.setIcon(QIcon('./Assets/icons/svg_expand'))

            # Add actions to resize submenu
            resizeMenu.addActions([shrinkImageAction, expandImageAction])

            # Add submenus to the main menu
            menu.addMenu(rotateMenu)
            menu.addMenu(resizeMenu)

        # tables    
        elif isinstance(self.childWidget, QWidget):
            tableMenu = QMenu("&Table", self)
            tableMenu.setStyleSheet("font-size: 11pt;")
            
            addRow = QAction("Add Row", self)
            addRow.triggered.connect(self.childWidget.addRow)
            
            addCol = QAction("Add Column", self)
            addCol.triggered.connect(self.childWidget.addCol)  
            
            tableMenu.addActions([addRow, addCol]) 
            menu.addMenu(tableMenu)

        # Add any non-widget type menu actions from child
        for item in customMenuItems:
            if type(item) != QWidgetAction:
                menu.addAction(item)

        return menu  # returns the QMenu: The constructed context menu

    # Determine which cursor to show and which mode to be in when user is interacting with the box
    def setCursorShape(self, e_pos: QPoint):
        diff = 10 # Amount of padding from the edge where resize cursors will show

        # Left - Bottom
        if (((e_pos.y() > self.y() + self.height() - diff) and # Bottom
            (e_pos.x() < self.x() + diff)) or # Left
        # Right-Bottom
        ((e_pos.y() > self.y() + self.height() - diff) and # Bottom
        (e_pos.x() > self.x() + self.width() - diff)) or # Right
        # Left-Top
        ((e_pos.y() < self.y() + diff) and # Top
        (e_pos.x() < self.x() + diff)) or # Left
        # Right-Top
        (e_pos.y() < self.y() + diff) and # Top
        (e_pos.x() > self.x() + self.width() - diff)): # Right
            # Left - Bottom
            if ((e_pos.y() > self.y() + self.height() - diff) and # Bottom
            (e_pos.x() < self.x()
                + diff)): # Left
                self.mode = Mode.RESIZEBL
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
                # Right - Bottom
            if ((e_pos.y() > self.y() + self.height() - diff) and # Bottom
            (e_pos.x() > self.x() + self.width() - diff)): # Right
                self.mode = Mode.RESIZEBR
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            # Left - Top
            if ((e_pos.y() < self.y() + diff) and # Top
            (e_pos.x() < self.x() + diff)): # Left
                self.mode = Mode.RESIZETL
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            # Right - Top
            if ((e_pos.y() < self.y() + diff) and # Top
            (e_pos.x() > self.x() + self.width() - diff)): # Right
                self.mode = Mode.RESIZETR
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
        # check cursor horizontal position
        elif ((e_pos.x() < self.x() + diff) or # Left
            (e_pos.x() > self.x() + self.width() - diff)): # Right
            if e_pos.x() < self.x() + diff: # Left
                self.setCursor(QCursor(Qt.SizeHorCursor))
                self.mode = Mode.RESIZEL
            else: # Right
                self.setCursor(QCursor(Qt.SizeHorCursor))
                self.mode = Mode.RESIZER
        # check cursor vertical position
        elif ((e_pos.y() > self.y() + self.height() - diff) or # Bottom
            (e_pos.y() < self.y() + diff)): # Top
            if e_pos.y() < self.y() + diff: # Top
                self.setCursor(QCursor(Qt.SizeVerCursor))
                self.mode = Mode.RESIZET
            else: # Bottom
                self.setCursor(QCursor(Qt.SizeVerCursor))
                self.mode = Mode.RESIZEB
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.mode = Mode.MOVE

    # Determine how to handle the mouse being moved inside the box
    def mouseMoveEvent(self, e: QMouseEvent):
        self.setStyleSheet("border: 1px dashed rgba(0, 0, 0, 0.5)")
        # QWidget.mouseMoveEvent(self, e) need??

        if not self.m_isEditing:
            return
        if not e.buttons() and Qt.LeftButton:
            p = QPoint(e.x() + self.geometry().x(), e.y() + self.geometry().y())
            self.setCursorShape(p)
            return

        if (self.mode == Mode.MOVE or self.mode == Mode.NONE) and e.buttons() and Qt.LeftButton:
            toMove = e.globalPos() - self.position

            if toMove.x() < 0:return
            if toMove.y() < 0:return
            if toMove.x() > self.parentWidget().width() - self.width(): return

            self.move(toMove)
            self.newGeometry.emit(self.geometry())
            self.parentWidget().repaint()

        # debt: To make images resize better, ImageWidget should probaly implement this and setCursorShape
        # So that it can make the cursor move with the corners of pixmap and not corners of this container
        if (self.mode != Mode.MOVE) and e.buttons() and Qt.LeftButton:
            child_widget = self.childWidget
            if self.mode == Mode.RESIZETL: # Left - Top
                newwidth = e.globalX() - self.position.x() - self.geometry().x()
                newheight = e.globalY() - self.position.y() - self.geometry().y()
                toMove = e.globalPos() - self.position
                self.resize(self.geometry().width() - newwidth, self.geometry().height() - newheight)
                self.move(toMove.x(), toMove.y())
            elif self.mode == Mode.RESIZETR: # Right - Top
                newheight = e.globalY() - self.position.y() - self.geometry().y()
                toMove = e.globalPos() - self.position
                self.resize(e.x(), self.geometry().height() - newheight)
                self.move(self.x(), toMove.y())
                '''if hasattr(self.childWidget, "newGeometryEvent"): 
                    self.newGeometry.connect(self.childWidget.newGeometryEvent)'''
            elif self.mode== Mode.RESIZEBL: # Left - Bottom
                newwidth = e.globalX() - self.position.x() - self.geometry().x()
                toMove = e.globalPos() - self.position
                self.resize(self.geometry().width() - newwidth, e.y())
                self.move(toMove.x(), self.y())
            elif self.mode == Mode.RESIZEB: # Bottom
               self.resize(self.width(), e.y())
            elif self.mode == Mode.RESIZEL: # Left
                newwidth = e.globalX() - self.position.x() - self.geometry().x()
                toMove = e.globalPos() - self.position
                self.resize(self.geometry().width() - newwidth, self.height())
                self.move(toMove.x(), self.y())
            elif self.mode == Mode.RESIZET:# Top
               newheight = e.globalY() - self.position.y() - self.geometry().y()
               toMove = e.globalPos() - self.position
               self.resize(self.width(), self.geometry().height() - newheight)
               self.move(self.x(), toMove.y())
            elif self.mode == Mode.RESIZER: # Right
                self.resize(e.x(), self.height())
            elif self.mode == Mode.RESIZEBR:# Right - Bottom
                #if child is a image, resize differently
                if isinstance(child_widget, QLabel):
                    # change this
                    self.resize(e.x(), e.y())
                else:
                    self.resize(e.x(), e.y())
            self.parentWidget().repaint()
        self.newGeometry.emit(self.geometry())
    
    # Used for deselecting text and removing container if empty
    def deselect_and_delete(self, changedWidgetAttribute):
        #print(f"changedWidgetAttribute is {changedWidgetAttribute} and value is {value}")
        child_widget = self.childWidget
        
        # If clicking on no object, deselect text
        if hasattr(child_widget, "deselectText") and (changedWidgetAttribute == ChangedWidgetAttribute.LoseFocus):
            child_widget.deselectText()
            # remove the widget if empty
            if hasattr(self.childWidget, "checkEmpty") and isinstance(child_widget, QTextEdit):
                if self.childWidget.checkEmpty():
                    print("Removing empty container")
                    editorSignalsInstance.widgetRemoved.emit(self)

    def widgetAttributeChanged(self, changedWidgetAttribute, value):
        child_widget = self.childWidget
        if self.hasFocus() or child_widget.hasFocus():
            if hasattr(child_widget, "changeBulletEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.Bullet):
                print("Change Bullet Event Called")
                child_widget.bullet_list("bulletReg")
            elif hasattr(child_widget, "changeBulletEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.Bullet_Num):
                print("Change Bullet Event Called")
                child_widget.bullet_list("bulletNum")
            elif hasattr(child_widget, "changeBulletEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.BulletUA):
                print("Change Bullet Event Called")
                child_widget.bullet_list("bulletUpperA")
            elif hasattr(child_widget, "changeBulletEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.BulletUR):
                print("Change Bullet Event Called")
                child_widget.bullet_list("bulletUpperR")
            elif hasattr(child_widget, "changeAlignmentEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.AlignLeft):
                print("Change Alignment Event Called")
                child_widget.changeAlignmentEvent("alignLeft")
            elif hasattr(child_widget, "changeAlignmentEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.AlignCenter):
                print("Change Alignment Event Called")
                child_widget.changeAlignmentEvent("alignCenter")
            elif hasattr(child_widget, "changeAlignmentEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.AlignRight):
                print("Change Alignment Event Called")
                child_widget.changeAlignmentEvent("alignRight")
                
            elif hasattr(child_widget, "changeBackgroundColorEvent") and (changedWidgetAttribute == ChangedWidgetAttribute.BackgroundColor):
                print("Chang Background Color Event Called")
                child_widget.changeBackgroundColorEvent(value)
            elif hasattr(child_widget, "paperColor") and (changedWidgetAttribute == ChangedWidgetAttribute.PaperColor):
                print("Change Page Color Event Called")
                child_widget.paperColor(value)



    def connectTableSignals(self, tableWidget):
        tableWidget.rowAdded.connect(self.resizeTable)
    def resizeTable(self):
        self.resize(self.childWidget.size())
        self.newGeometry.emit(self.geometry())
        self.parentWidget().repaint()

    def keyPressEvent(self, event: QKeyEvent) -> None: 
        if event.key() == Qt.Key_Shift:
            print("SHIFT PRESSED")
            self.shift_pressed = True
        else:
            super().keyPressEvent(event)
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Shift:
            print("SHIFT RELEASED")
            self.shift_pressed = False
        else:
            super().keyReleaseEvent(event)

    # Pastes a widget at the specified position
    def pasteWidget(self, clickPos):
        widgetOnClipboard = self.clipboard.getWidgetToPaste()

        dc = DraggableContainer(widgetOnClipboard, self) # Create a new DraggableContainer with the widget to paste
        self.undoHandler.pushCreate(dc)
        editorSignalsInstance.widgetAdded.emit(dc)  # Notify section that widget was added
        editorSignalsInstance.changeMade.emit()

        # Move the container to the specified position and show it
        dc.move(clickPos.x(), clickPos.y())
        dc.show()

