from Widgets.Textbox import TextboxWidget
from Models.DraggableContainer import DraggableContainer
from Modules.EditorSignals import editorSignalsInstance
from typing import List

class SectionModel:
    def __init__(self, title: str):
        self.title = title
        self.widgets: List[DraggableContainer] = [] # List of draggable containers in the section, each container holds an instance of a widget (ex. TextboxWidget)

    # When saving, convert the list of DraggableContainers to a list of their child widget's models
    def __getstate__(self):
        widgetModels = []
        for w in self.widgets:
            widgetModels.append(w.childWidget)
        return { 'title': self.title, 'widgetModels': widgetModels}

    # When loading, add all widget models to the editorframe (which will wrap them in draggablecontainers)
    def __setstate__(self, state):
        self.title = state['title']
        self.widgets = []  # This will be populated by the editorFrame as it recieves widgetShouldLoad signals
        widgetModels = state['widgetModels']

        for wm in widgetModels:
            editorSignalsInstance.widgetShouldLoad.emit(wm, self)  # Tell the editorframe to load the widget model into this section
