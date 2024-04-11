from Modules.EditorSignals import editorSignalsInstance

class Clipboard:
    def __init__(self):

        # Initialize variables to store copied widget state and class
        self.copiedWidgetState = None
        self.copiedWidgetClass = None

        editorSignalsInstance.widgetCopied.connect(self.copyWidgetEvent)

    # triggered when a widget is copied
    def copyWidgetEvent(self, draggableContainer):
        widget = draggableContainer.childWidget # Get the child widget from the draggable container
        print("copy widget")
        self.copiedWidgetClass = type(widget)
        self.copiedWidgetState = widget.__getstate__()

    #
    def getWidgetToPaste(self):
        widgetState = self.copiedWidgetState
        widgetClass = self.copiedWidgetClass

        newWidget = widgetClass.__new__(widgetClass) # Get uninitialized instance of widget class
        newWidget.__setstate__(widgetState)          # Initialize the widget instance with its setstate method

        return newWidget # Return the initialized widget instance
