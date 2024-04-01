from enum import Enum
from Modules.Enums import TextBoxStyles

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from Models.DraggableContainer import DraggableContainer
from Modules.EditorSignals import editorSignalsInstance,ChangedWidgetAttribute

class MultiselectMode(Enum):
    NONE = 0,
    IS_DRAWING_AREA = 1,
    HAS_SELECTED_OBJECTS = 2,
    IS_DRAGGING_OBJECTS = 3

class Multiselector(QObject):
    def __init__(self, editorFrame):
        super().__init__(editorFrame)
        self.editorFrame = editorFrame

        self.drawingWidget = QWidget(editorFrame)  # Allows the user to see their selected area
        self.mode = MultiselectMode.NONE           # Tracks what state the multiselect is in

        self.drawAreaStartLocalPos = None          # Point where user starts drawing to select multiple objects
        self.drawAreaStartGlobalPos = None
        self.selectedObjects = []                  # All objects in the user's selected area
        self.dragInitEventPos = None               # Position of the event that started the dragging
        self.dragOffset = None                     # Offset of object that is used to drag the others from the first object in the editors list


        # for handling deselect
        self.installEventFilter()
        # Connect signal for widget removal
        editorSignalsInstance.widgetRemoved.connect(self.removeWidgetFromList)
        
        editorSignalsInstance.widgetCut.connect(self.cutWidgetEvent)

    # Slot to remove widget from object list
    @Slot(QWidget)
    def removeWidgetFromList(self, widget):
        if widget in self.selectedObjects:
            self.selectedObjects.remove(widget)
            
    # install event filter to editorframe
    def installEventFilter(self):
        self.editorFrame.installEventFilter(self)

    def eventFilter(self, obj, event):

        multiselector = self

        if isinstance(obj, DraggableContainer):
            # If clicking on an object
            if event.type() == QEvent.MouseButtonPress:
                print("EVENTFILTER TOOK EVENT")
                if multiselector.mode == MultiselectMode.HAS_SELECTED_OBJECTS:
                    multiselector.beginDragIfObjectSelected(obj, event)
                    print("BEGIN MOVING")

            if event.type() == QEvent.MouseMove:
                if multiselector.mode == MultiselectMode.IS_DRAGGING_OBJECTS:
                    multiselector.dragObjects(event)
                    return True # Keep the event from going to the draggablecontainer so it doesnt have that mousemoveevent run on it too

            # If in object-moving mode, and the mouse is released, reset all multiselecting
            if event.type() == QEvent.MouseButtonRelease and isinstance(obj, DraggableContainer):
                if multiselector.mode == MultiselectMode.IS_DRAGGING_OBJECTS:
                    print("FINISH DRAG")
                    multiselector.finishDraggingObjects()

            # After the selection is made, its possible that the user moves in and out of selected textboxes,
            # This will remove their focus border, this mitigates that. Note: Do not let this run when the object is moving, its too expensive bc too many paint events
            if multiselector.mode != MultiselectMode.NONE and multiselector.mode != MultiselectMode.IS_DRAGGING_OBJECTS and event.type() == QEvent.Paint:
                multiselector.focusObjectIfInMultiselect()

            return False
        
        # Handle click outside the selected objects to deselect
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if multiselector.mode == MultiselectMode.HAS_SELECTED_OBJECTS:
                multiselector.deselectIfClickOutsideObjects(event)
                print("DESELECT from multiselect")

        return False

    # check if clicked outside
    def deselectIfClickOutsideObjects(self, event):
        # Check if the click is outside any selected objects
        clickPos = event.globalPos()
        for o in self.selectedObjects:
            o_tl_pos = o.mapToGlobal(QPoint(0, 0))
            o_br_pos = o_tl_pos + QPoint(o.width(), o.height())

            if o_tl_pos.x() <= clickPos.x() <= o_br_pos.x() and o_tl_pos.y() <= clickPos.y() <= o_br_pos.y():
                # Click is inside a selected object, do not deselect'
                print("Click is inside a selected object, do not deselect")
                return

        # Click is outside all selected objects, deselect
        self.finishDraggingObjects()

    def beginDrawingArea(self, event):
        self.mode = MultiselectMode.IS_DRAWING_AREA
        self.drawingWidget.setStyleSheet(TextBoxStyles.INFOCUS.value)
        self.drawingWidget.setGeometry(event.pos().x(), event.pos().y(), 0, 0)
        self.drawingWidget.show()
        self.drawAreaStartLocalPos = event.pos()
        self.drawAreaStartGlobalPos = event.globalPos()

    def continueDrawingArea(self, event):
        start_x = self.drawAreaStartLocalPos.x()
        start_y = self.drawAreaStartLocalPos.y()

        end_x = event.pos().x()
        end_y = event.pos().y()

        width = abs(end_x - start_x)
        height = abs(end_y - start_y)

        # Calculate the x and y for setting the geometry
        x = min(start_x, end_x)
        y = min(start_y, end_y)

        # Adjust the geometry of the drawingWidget
        self.drawingWidget.setGeometry(x, y, width, height)
    def finishDrawingArea(self, event):
        editor = self.editorFrame.editor

        # Get the coordinates of the top-left corner of the selection area
        start_x = min(self.drawAreaStartGlobalPos.x(), event.globalPos().x())
        start_y = min(self.drawAreaStartGlobalPos.y(), event.globalPos().y())

        # Get the coordinates of the bottom-right corner of the selection area
        end_x = max(self.drawAreaStartGlobalPos.x(), event.globalPos().x())
        end_y = max(self.drawAreaStartGlobalPos.y(), event.globalPos().y())

        # Iterate through objects and check if they are inside the selection area
        sectionView = self.editorFrame.editor.sectionView
        currentSectionIndex = sectionView.tabs.currentIndex()
        currentSectionModel = sectionView.sectionModels[currentSectionIndex]
        currentSectionModelWidgets = currentSectionModel.widgets

        for o in currentSectionModelWidgets:
            ob_tl_pos = o.mapToGlobal(QPoint(0, 0))

            if start_x <= ob_tl_pos.x() <= end_x and start_y <= ob_tl_pos.y() <= end_y:
                self.selectedObjects.append(o)

        if len(self.selectedObjects) > 0:
            self.mode = MultiselectMode.HAS_SELECTED_OBJECTS
        else:
            self.finishDraggingObjects()

        print("SELECTION COUNT: ", len(self.selectedObjects))

        # highlight all text for textwidgets
        for o in self.selectedObjects:
            # Checks if child is textwidget
            if (isinstance(o.childWidget, QTextBrowser)):
                print("TEXT WIDGET FOUND. HIGHLIGHTING")
                # Call function in textwidget to highlight all text in their textbox
                o.childWidget.selectAllText()
        # Hide selection area
        self.drawingWidget.hide()

    def beginDragIfObjectSelected(self, object, event):
        if object in self.selectedObjects:
            self.mode = MultiselectMode.IS_DRAGGING_OBJECTS
            self.dragInitEventPos = event.pos()
            self.dragOffset = object.pos() - self.selectedObjects[0].pos()

    def dragObjects(self, event):
        print("DRAGGING OB")

        # Get the position that each object would move to
        objectPositions = []
        for o in reversed(self.selectedObjects): # fuck it, reversed 

            # You have to know this, focus
            # Position of the first (in the reversed array) object's top left corner + the offset of the click inside the selected object - the position of the object to move
            offsetPositionFromInitObject = self.selectedObjects[0].pos() + self.dragInitEventPos - o.pos()
            toMove = event.globalPos() - offsetPositionFromInitObject

            # For some reason it will kind of attempt to move the objects as if the last object in the array was selected by the user
            # So offset that, then add a y offset becase it does something weird with that too

            toMove = toMove - self.dragOffset - QPoint(0, 20)
            toMove = self.editorFrame.mapFromGlobal(toMove)

            # If an object wants to move out of bounds, quit the loop and eat the event
            if toMove.x() < 0: return True
            if toMove.y() < 0: return True
            # if toMove.x() > self.editorFrame.width() - o.width():
            #     print(1)
            #     return True
            # if(toMove.x() < self.editorFrame.width() - o.parentWidget().frame.width()):
            #     print(2)
            #     return True
            # if(toMove.y() < o.parentWidget.height() - o.parentWidget().frame.height()):
            #     print(3)
            #     return True
            # if(toMove.y() > o.parentWidget().frame.height() + 20):
            #     print(4)
            #     return True

            objectPositions.append(toMove)

        # If no objects would move out of bounds, perform the moves
        for i, o in enumerate(reversed(self.selectedObjects)):
            o.move(objectPositions[i])
            # o.newGeometry.emit(o.geometry())

    def finishDraggingObjects(self):
        try:
            for o in self.selectedObjects:
                o.setStyleSheet(TextBoxStyles.OUTFOCUS.value)
        except:
            pass # Generally only fails because the object references are gone so we want to exit anyways

        self.mode = MultiselectMode.NONE

        self.drawAreaStartLocalPos = None
        self.drawAreaStartGlobalPos = None
        self.selectedObjects = []
        self.dragInitEventPos = None
        self.dragOffset = None

    def focusObjectIfInMultiselect(self):

        # Exits multiselecting if the selected object references are no longer accessible
        try:
            for o in self.selectedObjects:
                o.setStyleSheet(TextBoxStyles.INFOCUS.value)
        except:
            self.finishDraggingObjects()
    # Allow removing all selected objects
    def removeWidgetEvent(self):
        for obj in self.selectedObjects:
            editorSignalsInstance.changeMade.emit(obj)
    
    # Allow cutting all selected objects
    def cutWidgetEvent(self):
        for obj in self.selectedObjects:
            editorSignalsInstance.widgetCopied.emit(obj)
            editorSignalsInstance.widgetRemoved.emit(obj)

    # Paste works from clipboard, meaning have to store all objects to clipboard