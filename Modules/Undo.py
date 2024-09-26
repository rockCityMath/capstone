from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from Modules.EditorSignals import editorSignalsInstance
import os


#current version of undo does not work. When using ctrl+z in textboxes, it uses the QTextEdit default settings for ctrl+z(undo) and ctrl+y(redo) to make it appear as if undo does work
class UndoActionCreate:
    def __init__(self, draggableContainer):
        self.draggableContainer = draggableContainer

class UndoActionDelete:
    def __init__(self, widgetClass, widgetState):
        self.widgetClass = widgetClass
        self.widgetState = widgetState

class UndoActionGeometryChange:
    def __init__(self, draggableContainer, oldGeometry):
        self.draggableContainer = draggableContainer
        self.oldGeometry = oldGeometry

class UndoHandler(QObject):
    undoWidgetDelete = Signal(object)

    def __init__(self):
        super().__init__()
        self.undoStack = []

    # When an undo-able action is pushed, assign to the undo stack with appropriate undo class and data
    def pushCreate(self, draggableContainer):
        self.undoStack.append(UndoActionCreate(draggableContainer))
        print("PUSHED CREATE")

    def pushDelete(self, draggableContainer):
        widget = draggableContainer.childWidget
        widgetClass = type(widget)
        widgetState = widget.__getstate__()
        self.undoStack.append(UndoActionDelete(widgetClass, widgetState))
        print("PUSHED DELETE")

    def pushGeometryChange(self, draggableContainer, oldGeometry):
        self.undoStack.append(UndoActionGeometryChange(draggableContainer, oldGeometry))
        print("PUSHED GEOMETRY CHANGE")

    # When undoing an action, pop the undo stack and perform the appropriate undo
    def undo(self):
        print("UNDO CALLED")
        if len(self.undoStack) == 0:
            print("NOTHING TO UNDO")
            return

        undoAction = self.undoStack.pop()
        if isinstance(undoAction, UndoActionCreate):
            try:
                print(undoAction.draggableContainer, file=open(os.devnull, "w")) # This makes it fail and move to the except block if the draggableContainer is gone, i think..

                editorSignalsInstance.widgetRemoved.emit(undoAction.draggableContainer)
                if len(self.undoStack) != 0: self.undoStack.pop() # A delete event will be added to the undo stack from the above emit, we want to disreguard that
                print("UNDONE CREATE")
            except:
                print("CANNOT WIDGET CREATE AFTER AN UNDO ON ITS DELETION")

        elif isinstance(undoAction, UndoActionDelete):
            widgetState = undoAction.widgetState
            widgetClass = undoAction.widgetClass

            newWidget = widgetClass.__new__(widgetClass) # Get uninitialized instance of widget class
            newWidget.__setstate__(widgetState)          # Initialize the widget instance with its setstate method

            self.undoWidgetDelete.emit(newWidget)
            print("UNDONE DELETE")

        elif isinstance(undoAction, UndoActionGeometryChange):
            try:
                undoAction.draggableContainer.setGeometry(undoAction.oldGeometry)
                print("UNDONE GEOMETRY CHANGE")
            except:
                print("CANNOT UNDO GEOMETRY CHANGE ON WIDGET THAT HAS BEEN PREVIOUSLY DELETED")

