from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Models.SectionModel import SectionModel
from Modules.Undo import UndoHandler

from typing import List
from functools import partial

from Modules.EditorSignals import editorSignalsInstance

# Page view and controller
class SectionView(QWidget):
    def __init__(self, sectionModels: List[SectionModel]):
        super(SectionView, self).__init__()

        self.sectionModels: List[SectionModel] # Reference to the current section models (draggableContainer in runtime)

        # The tabbed section widget
        self.tabs = QTabBar(self)

        # Layout that holds this view
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.setExpanding(False)

        self.tabs.customContextMenuRequested.connect(self.openMenu)
        self.tabs.currentChanged.connect(self.changeSection)
        editorSignalsInstance.pageChanged.connect(self.pageChangedEvent)
        editorSignalsInstance.widgetAdded.connect(self.widgetAddedEvent)
        editorSignalsInstance.widgetRemoved.connect(self.widgetRemovedEvent)
        self.isLoading = False

        self.tabs.tabSizeHint = self.tabSizeHint
        self.tabs.minimumTabSizeHint = self.minimumTabSizeHint

        self.loadSections(sectionModels)
        print("BUILT SECTIONVIEW")

    def tabSizeHint(self, index):
        return QSize(300, 35)

    def minimumTabSizeHint(self, index):
        return QSize(300, 35)

    def widgetRemovedEvent(self, draggableContainer):
        try:
            currentSectionIndex = self.tabs.currentIndex()
            currentSectionModel = self.sectionModels[currentSectionIndex]
            currentSectionModel.widgets.remove(draggableContainer)
        except:
            print("CANNOT REMOVE WIDGET FROM SECTIONVIEW")

    def widgetAddedEvent(self, draggableContainer):
        print("SECTIONVIEW KNOWS WIDGET ADDED")

        # Add the new widget to the current section's list of widgets
        currentSectionIndex = self.tabs.currentIndex()
        currentSectionModel = self.sectionModels[currentSectionIndex]
        currentSectionModelWidgets = currentSectionModel.widgets
        currentSectionModelWidgets.append(draggableContainer)

    # When the page is changed, load that pages sections
    def pageChangedEvent(self, pageModel):
        print("SECTION KNOWS PAGE CHANGE")
        self.loadSections(pageModel.sections)

    def loadSections(self, sectionModels: List[SectionModel]):
        print("LOADING SECTIONS")
        self.isLoading = True   # Because when tabs are removed (i think) it triggers a currentChanged event

        # Remove any old tabs
        for i in range(self.tabs.count()):
            self.tabs.removeTab(0)

        # If no sections are found, add one (not superr ideal)
        if len(sectionModels) < 1:
            print("NO SECTIONS FOUND, GIVING A NEW ONE")
            newSectionModel = SectionModel("New Section")
            sectionModels.append(newSectionModel)   # Add a new section to the local list of SectionModels

        # Load the sections into the tabview
        for s in sectionModels:
            addedTabIndex = self.tabs.addTab(s.title)
            self.tabs.setTabData(addedTabIndex, s)

        self.isLoading = False
        self.sectionModels = sectionModels  # Update the view's stored reference to the section models

        self.tabs.setCurrentIndex(0)        # Update the current index in the UI
        self.changeSection(0)               # After loading new sections, select the first one

    def openMenu(self, position: QPoint):
        clickedSectionIndex = self.tabs.tabAt(position)
        sectionModel = self.tabs.tabData(clickedSectionIndex)

        menu = QMenu()
        renameSectionAction = menu.addAction(self.tr("Rename Section"))
        renameSectionAction.setIcon(QIcon('./Assets/icons/svg_rename'))
        renameSectionAction.triggered.connect(partial(self.renameSection, sectionModel, clickedSectionIndex))

        deleteSectionAction = menu.addAction(self.tr("Delete Section"))
        deleteSectionAction.setIcon(QIcon('./Assets/icons/svg_delete'))
        deleteSectionAction.triggered.connect(partial(self.deleteSection, sectionModel, clickedSectionIndex))

        addSectionAction = menu.addAction(self.tr("Add Section"))
        addSectionAction.setIcon(QIcon('./Assets/icons/svg_add_page'))
        addSectionAction.triggered.connect(partial(self.addSection, sectionModel, clickedSectionIndex))

        menu.exec(self.tabs.mapToGlobal(position))

    def addSection(self, sectionModel: SectionModel, clickedSectionIndex: int):
        print("ADD SECTION")

        addedSectionIndex = self.tabs.addTab("New Section")                  # Add section to UI
        rightOfClickedSectionIndex = clickedSectionIndex + 1
        self.tabs.moveTab(addedSectionIndex, rightOfClickedSectionIndex)     # Move to right of right clicked section

        newSectionModel = SectionModel("New Section")                        # Create new SectionModel
        self.tabs.setTabData(rightOfClickedSectionIndex, newSectionModel)    # Set new SectionModel as section data

        self.sectionModels.insert(clickedSectionIndex + 1, newSectionModel)  # Insert new SectionModel into list of section models

    def deleteSection(self, sectionModel: SectionModel, clickedSectionIndex: int):
        print("DELETE SECTION")
        self.tabs.removeTab(clickedSectionIndex)                            # Remove section from UI
        self.sectionModels.pop(clickedSectionIndex)                         # Remove section from list of section models

    def renameSection(self, sectionModel: SectionModel, clickedSectionIndex: int):
        print("RENAME SECTION")
        newName, accept = QInputDialog.getText(self, 'Change Section Title', 'Enter new title of section: ')
        if accept:
            self.tabs.setTabText(clickedSectionIndex, newName)        # Rename section in UI
            self.sectionModels[clickedSectionIndex].title = newName   # Rename section in SectionModel

    def changeSection(self, sectionIndex: int):
        if self.isLoading:  # Dont change sections while loading in new tabs (it will keep emitting the sectionChanged signal)
            return

        print("CHANGED SECTION")
        sectionModel = self.tabs.tabData(sectionIndex)
        editorSignalsInstance.sectionChanged.emit(sectionModel)       # Notify editorframe that section has changed

