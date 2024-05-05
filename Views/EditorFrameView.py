from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import importlib
import sys

from Modules.Multiselect import Multiselector, MultiselectMode
from Modules.Clipboard import Clipboard
from Modules.EditorSignals import editorSignalsInstance, ChangedWidgetAttribute
from Modules.Undo import UndoHandler
from Modules.Screensnip import SnippingWidget
from Models.DraggableContainer import DraggableContainer
from Widgets.Textbox import TextboxWidget
from Widgets.Image import ImageWidget
from Widgets.Table import *
from Widgets.Link import LinkDialog

import subprocess



# Handles all widget display (could be called widget view, but so could draggablecontainer)
class EditorFrameView(QWidget):
    SETTINGS_KEY = "BackgroundColor" # Key for saving the background color setting

    # used for storing last mouse click and setting the location of generated images, textboxes, and tables at the last location
    lastClickPos = QPoint()

    def __init__(self, editor):
        super(EditorFrameView, self).__init__()


        def check_appearance():
            """Checks DARK/LIGHT mode of macos."""
            cmd = 'defaults read -g AppleInterfaceStyle'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
            return bool(p.communicate()[0])  

        # Reference to the main editor window
        self.editor = editor # Store reference to the editor (QMainWindow)
        self.editorFrame = QFrame(editor)

        #Default
        self.currentBackgroundColor = self.loadBackgroundColor() or QColor(255, 255, 255)

        is_dark_mode = check_appearance()
        white = QColor("white")

        #background page color
        if is_dark_mode and (self.currentBackgroundColor == white or self.currentBackgroundColor == QColor(255, 255, 255)):
            self.setStyleSheet(f"background-color: rgb(31, 31, 30);")
            print("In dark mode, use dark mode color because the background is white or pciked white")
        elif not is_dark_mode:
            self.setStyleSheet(f"background-color: {self.currentBackgroundColor.name()};")
            print("Set background color based on saved color in light mode")
        else:
            self.setStyleSheet(f"background-color: {self.currentBackgroundColor.name()};")
            self.saveBackgroundColor()
            print("Saving non-white color as the current background color")

        # Layout for the editor frame
        layout = QVBoxLayout(self)
        layout.addWidget(self.editorFrame)
        layout.setContentsMargins(0, 0, 0, 0)

        editorSignalsInstance.sectionChanged.connect(self.sectionChangedEvent)
        editorSignalsInstance.widgetShouldLoad.connect(self.loadWidgetEvent)
        editorSignalsInstance.widgetRemoved.connect(self.removeWidgetEvent)
        editorSignalsInstance.widgetCut.connect(self.cutWidgetEvent)

        # Modularized functionality for the editorFrame and its widgets
        self.clipboard = Clipboard()
        self.undoHandler = UndoHandler()
        self.multiselector = Multiselector(self)

        self.installEventFilter(self.multiselector)

        # Undo setup
        #self.shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        #self.shortcut.setContext(Qt.ApplicationShortcut)
        #self.shortcut.activated.connect(self.triggerUndo)

        print("BUILT FRAMEVIEW") 

    def triggerUndo(self):
        print("triggerUndo Called")
        self.undoHandler.undo
        self.undoHandler.undoWidgetDelete.connect(self.undoWidgetDeleteEvent) 

    def pasteWidget(self, clickPos):
        widgetOnClipboard = self.clipboard.getWidgetToPaste()

        # Create draggable container for pasted widget
        dc = DraggableContainer(widgetOnClipboard, self)
        self.undoHandler.pushCreate(dc)
        editorSignalsInstance.widgetAdded.emit(dc)  # Notify section that widget was added
        editorSignalsInstance.changeMade.emit()
        dc.move(clickPos.x(), clickPos.y())
        dc.show()

    def snipScreen(self, clickPos):
        def onSnippingCompleted(imageMatrix):            # Called after screensnipper gets image
            self.editor.setWindowState(Qt.WindowActive)
            self.editor.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.editor.showMaximized()
            if imageMatrix is None:
                return

            #Create image widget from the captured image
            widgetModel = ImageWidget.newFromMatrix(clickPos, imageMatrix)
            dc = DraggableContainer(widgetModel, self)
            self.undoHandler.pushCreate(dc)
            editorSignalsInstance.widgetAdded.emit(dc)   # Notify the current section and editorFrame that a widget was added
            dc.show()

        # Begin screensnip
        self.editor.setWindowState(Qt.WindowMinimized)
        self.snippingWidget = SnippingWidget()
        self.snippingWidget.onSnippingCompleted = onSnippingCompleted
        self.snippingWidget.start(clickPos)

    def newWidgetOnSection(self, widgetClass, clickPos):
        print("ADDWIDGET: ", widgetClass)
        try:
            widget = widgetClass.new(clickPos)          # All widget classes implement .new() static method
            dc = DraggableContainer(widget, self)
            dc.show()

            self.undoHandler.pushCreate(dc)             # Push to undo stack
            editorSignalsInstance.widgetAdded.emit(dc)  # Notify the current section that a widget was added
            editorSignalsInstance.changeMade.emit()
            dc.mouseDoubleClickEvent(None)              # Enter the child widget after adding

        except Exception as e:
            print("Error adding widget: ", e)

    # When the DC geometry is changed, tell the undoHandler
    def newGeometryOnDCEvent(self, dc):
        self.undoHandler.pushGeometryChange(dc, dc.previousGeometry)
        editorSignalsInstance.changeMade.emit()

    # Special case for adding a widget by undoing a delete, since position is already set
    def undoWidgetDeleteEvent(self, widget):
        print("UNDO DELETE EVENT")
        try:
            dc = DraggableContainer(widget, self)
            dc.show()
            editorSignalsInstance.widgetAdded.emit(dc)  # Notify the current section that a widget was added

        except Exception as e:
            print("Error adding widget: ", e)

    def removeWidgetEvent(self, draggableContainer):
        self.undoHandler.pushDelete(draggableContainer)
        editorSignalsInstance.changeMade.emit()
        draggableContainer.deleteLater()

    def cutWidgetEvent(self, draggableContainer):
        editorSignalsInstance.widgetCopied.emit(draggableContainer)
        editorSignalsInstance.widgetRemoved.emit(draggableContainer)
    
    def copyWidgetEvent(self, draggableContainer):
        editorSignalsInstance.widgetCopied.emit(draggableContainer)

    # Loading a preexisting (saved) widget into the frame inside a DraggableContainer
    # Then add that DC instance reference to the sectionModel's widgets[] for runtime
    def loadWidgetEvent(self, widgetModel, sectionModel):
        dc = DraggableContainer(widgetModel, self)
        sectionModel.widgets.append(dc)
        print("LOADED CONTENT: ", widgetModel)

    def sectionChangedEvent(self, sectionModel):
        print("FRAME: NEW SECTION TITLE: " + sectionModel.title)

        # Hide all old widgets
        for c in self.children():
            if isinstance(c, DraggableContainer):
                print(c)
                c.hide()

        # Show all new widgets
        for widget in sectionModel.widgets:
            print(widget)
            widget.show()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:

            # If releasing mouse after drawing multiselect area
            if self.multiselector.mode == MultiselectMode.IS_DRAWING_AREA:
                self.multiselector.finishDrawingArea(event)

            # Releasing the mouse after clicking to add text
            else:
                print("CREATE DRAGGABLE CONTAINER")
                self.newWidgetOnSection(TextboxWidget, event.pos())

    def mousePressEvent(self, event):
        print("EDITORFRAME MOUSEPRESS")
        editor = self.editor

        EditorFrameView.lastClickPos = event.pos()

        #calls textwidget's clearSelectionSignal
        if event.button() == Qt.LeftButton:
            if self.rect().contains(event.pos()):
                editorSignalsInstance.widgetAttributeChanged.emit(ChangedWidgetAttribute.LoseFocus, None)
            super().mousePressEvent(event)

        # Open context menu on right click
        if event.buttons() == Qt.RightButton:
            frame_menu = QMenu(self)
            # frame_menu.setStyleSheet("font-size: 11pt;")

            paste = QAction("Paste", editor)
            paste.triggered.connect(lambda: self.pasteWidget(event.pos()))
            
            insert_Link = QAction("Insert Link", editor)
            insert_Link.triggered.connect(lambda: self.insertLink(event.pos()))

            add_table = QAction("Add Table", editor)
            add_table.triggered.connect(lambda: self.newWidgetOnSection(TableWidget, event.pos()))
            #add_table.triggered.connect(self.show_table_popup)
            
            # not necessary
            '''
            add_image = QAction("Add Image", self)
            add_image.triggered.connect(lambda: self.newWidgetOnSection(ImageWidget, event.pos()))
            
            take_screensnip = QAction("Snip Screen", editor)
            take_screensnip.triggered.connect(lambda: self.snipScreen(event.pos()))

            add_custom_widget = QAction("Add Custom Widget", editor)
            add_custom_widget.triggered.connect(lambda: self.addCustomWidget(event))
            '''
            
            frame_menu.addAction(paste)
            
            frame_menu.addSeparator()
            
            frame_menu.addAction(insert_Link)
            
            frame_menu.addSeparator()
            
            frame_menu.addAction(add_table)
            
            '''
            frame_menu.addSeparator()
            
            frame_menu.addActions([add_image, take_screensnip, add_custom_widget])
            '''
            
            frame_menu.exec(event.globalPos())

    def insertLink(self, clickPos):
        link_dialog = LinkDialog()
        result = link_dialog.exec_() #Execute the dialog and wait for user input
        if result == QDialog.Accepted:

            link_address, display_text = link_dialog.get_link_data()  # Get the link address and display text from the dialog
            textboxWidget = TextboxWidget.new(clickPos)  # Create a new TextboxWidget at the specified position
            textboxWidget.insertTextLink(link_address, display_text) # Insert the hyperlink into the TextboxWidget

            # Create a DraggableContainer for the TextboxWidget and show it
            dc = DraggableContainer(textboxWidget, self)
            dc.show()

            self.undoHandler.pushCreate(dc)
            editorSignalsInstance.widgetAdded.emit(dc)
            editorSignalsInstance.changeMade.emit()

    def insertDate(self, clickPos):
        current_date = QDateTime.currentDateTime().toString("M/d/yyyy")
        textboxWidget = TextboxWidget.new(clickPos)
        textboxWidget.insertPlainText(current_date) 
        dc = DraggableContainer(textboxWidget, self)
        dc.resize(80,25)
        dc.show()
        self.undoHandler.pushCreate(dc)
        editorSignalsInstance.widgetAdded.emit(dc)
        editorSignalsInstance.changeMade.emit()


    def insertTime(self, clickPos):
        current_time = QDateTime.currentDateTime().toString("h:mm AP")
        textboxWidget = TextboxWidget.new(clickPos)
        textboxWidget.insertPlainText(current_time)
        dc = DraggableContainer(textboxWidget, self)
        dc.resize(80,25)
        dc.show()
        self.undoHandler.pushCreate(dc)
        editorSignalsInstance.widgetAdded.emit(dc)
        editorSignalsInstance.changeMade.emit()

    # will generate images, tables, and textboxes at last mouse press location. If no mouse press location, default to top right of the screen.
    def createAtLastPos(self, widgetClass):
        # no mouse press registered
        if EditorFrameView.lastClickPos == QPoint(0, 0):
            print("lastClickPos is (0, 0)")
            center_x, center_y = self.getCenterOfEditorFrame()
            self.newWidgetOnSection(widgetClass, QPoint(center_x, center_y))
            return
        else:
            self.newWidgetOnSection(widgetClass, EditorFrameView.lastClickPos)
            return

    def getCenterOfEditorFrame(self):
        if self.editorFrame is None:
            # If editor frame is not initialized, return default position
            return 100, 100  # Default position

        editor_frame_geometry = self.editorFrame.geometry()
        center_x = (editor_frame_geometry.width() - 400) // 2
        center_y = (editor_frame_geometry.height() - 400) // 2
        return center_x, center_y
    
    # Used for calling functions in toolbar
    def toolbar_paste(self):
        print("toolbar_paste pressed")
        self.pasteWidget(EditorFrameView.lastClickPos)

    def toolbar_table(self):
        print("toolbar_table pressed")
        
        # bug: table widget if using createAtLastPos will go through the if statement to spawn in the center if qpoint == (0, 0) but fail to be created
        self.createAtLastPos(TableWidget)
        # self.newWidgetOnSection(TableWidget, EditorFrameView.lastClickPos)
    def toolbar_snipScreen(self):
        print("toolbar_snipScreen pressed")
        self.snipScreen(EditorFrameView.lastClickPos)
        
    def toolbar_pictures(self):
        print("toolbar_pictures pressed")
        self.createAtLastPos(ImageWidget)
        
    def toolbar_hyperlink(self):
        print("toolbar_hyperlink pressed")
        self.insertLink(EditorFrameView.lastClickPos)

    def toolbar_date(self):
        print("toolbar_date pressed")
        self.insertDate(EditorFrameView.lastClickPos)

    def toolbar_time(self):
        print("toolbar_time pressed")
        self.insertTime(EditorFrameView.lastClickPos)

    def addCustomWidget(self, e):
        def getCustomWidgets():
            customWidgets = {} # dict where entries are {name: class}

            # Check for files ending in .py, import them, and add their attribtues to the dict
            # Should add checks that the plugin implements required methods
            pluginDirectory = os.path.join(os.path.dirname(os.getcwd()), "PluginWidgets")

            for filename in os.listdir(pluginDirectory):
                if filename[-3:]!=".py": continue
                className = filename[:-3]

                module = importlib.__import__(f"{className}")

                c = getattr(module,className)
                customWidgets[className]=c

            return customWidgets.items()

        pluginMenu = QMenu(self)

        for customWidget in getCustomWidgets():
            item_action = QAction(customWidget[0], self)
            def tmp(c, pos):
                return lambda: self.newWidgetOnSection(c, pos)
            item_action.triggered.connect(tmp(customWidget[1], e.pos()))
            pluginMenu.addAction(item_action)

        pluginMenu.exec(e.globalPos())

    def mouseMoveEvent(self, e): # This event is only called after clicking down on the frame and dragging
        # Set up multi-select on first move of mouse drag
        if self.multiselector.mode != MultiselectMode.IS_DRAWING_AREA:
                self.multiselector.beginDrawingArea(e)

        # Resize multi-select widget on mouse every proceeding mouse movement (dragging)
        else:
            self.multiselector.continueDrawingArea(e)

    def slot_action1(self, item):
        print("Action 1 triggered")

    #  Handles changes to the background color of the editor frame.
    def pageColor(self, color: QColor):
        print("CHANGE BACKGROUND COLOR EVENT")
        if color.isValid():
            self.currentBackgroundColor = color
            self.editorFrame.setStyleSheet(f"background-color: {color.name()};")
            self.saveBackgroundColor()

    #Loads the previously saved background color from settings
    def loadBackgroundColor(self):
        settings = QSettings()
        color = settings.value(self.SETTINGS_KEY, type=QColor)
        return color

    #  Saves the current background color to settings
    def saveBackgroundColor(self):
        settings = QSettings()
        settings.setValue(self.SETTINGS_KEY, self.currentBackgroundColor)

    # Retrieves the current background color of the editor frame
    def getCurrentBackgroundColor(self):
        return self.currentBackgroundColor



