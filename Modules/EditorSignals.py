from PySide6.QtCore import *
from PySide6.QtGui import *
from enum import Enum

class ChangedWidgetAttribute(Enum):
    # Used for unique signals
    # Add variable to create a unique signal 
    BackgroundColor = 0
    FontColor = 1
    Font = 2
    FontSize = 3
    FontBold = 4
    FontItalic = 5
    FontUnderline = 6
    TextHighlightColor = 7
    Bullet = 8
    Bullet_Num = 9
    LoseFocus = 10

    BulletUR = 11
    BulletUA = 12
    AlignLeft = 13
    AlignCenter = 14
    AlignRight = 15
    PaperColor = 16

    Strikethrough = 17


# Cant be statically typed because importing the classes causes circular imports

class EditorSignals(QObject):

    pageChanged = Signal(object) # Recieves PageModel
    sectionChanged = Signal(object) # Receives SectionModel

    # Recieves DraggableContainer
    widgetAdded = Signal(object)
    widgetRemoved = Signal(object)
    widgetCopied = Signal(object)
    widgetCut = Signal(object)
    
    # Recieves any widget model, and the section model to add the instance of DraggableContainer to
    widgetShouldLoad = Signal(object, object)

    # Receives (ChangedWidgetAttribute, value)
    widgetAttributeChanged = Signal(object, object)

    # Recieves nothing, used by autosaver
    changeMade = Signal()

    # Clear Selection
    loseFocus = Signal()

editorSignalsInstance = EditorSignals()
