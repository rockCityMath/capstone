import pickle
import os

from Modules.Save import Autosaver
import pyautogui
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from Models.NotebookModel import NotebookModel

# Creates a new notebook
def new(editor):
    print("RAN NEW")
    destroy(editor)
    p_name = pyautogui.prompt("Enter Notebook Name")
    editor.notebook = NotebookModel(p_name)
    editor.notebookTitleView.setText(editor.notebook.title)
    editor.selected = None
    editor.autosaver = Autosaver(editor)
    build(editor) # should we build here, or should above be in build?

# Loads models.notebook.Notebook class from file
def load(editor):
    print("LOADING")

    # Open file dialog for selecting notebook file
    path, accept = QFileDialog.getOpenFileName(
        editor,
        'Open Notebook',
        '',
        'OpenNote (*.on *.ontemp)'
    )
    if accept:
        file = open(path, 'rb')
        destroy(editor)
        editor.notebook = pickle.load(file)
        # for page in editor.notebook.pages:
        #   for section in page.sections:
        #     for o in section.objects:
        #         o.restoreWidget(editor)
        #         o.hide() # NEW: Need this?
        print("LOADED")
    else:
        return
    build(editor)

# Try to find and open the most recent OpenNote related file
def load_most_recent_notebook(editor):

    print("LOAD RECENT RAN")
    # Search for most recent notebook file
    files = []
    saves_directory = os.path.join(os.getcwd(), 'Saves')
    for file in os.listdir(saves_directory):
       file_path = os.path.join(saves_directory, file)
       if os.path.isfile(file_path):
          files.append(file_path)
          print(file_path)

    directory_files = reversed(sorted(files, key = os.path.getmtime))
    for f in directory_files:
        if (f.endswith(".on") or f.endswith(".ontemp")):
            print("FOUND: " + str(f))
            try:
                # Open and load the notebook
                # prob need load from file function, dup functionality
                file = open(os.path.join(os.getcwd() + "\\Saves", f), 'rb')
                destroy(editor)
                editor.notebook = pickle.load(file)
                build(editor)
                # for page in editor.notebook.pages:
                #   for section in page.sections:
                #     for o in section.objects:
                #         o.restoreWidget(editor)
                #         o.hide() # NEW: Need this?
                #         build(editor)
                return
            except:
                continue

def build(editor):
    print("BUILDING FROM LOAD")

    # Display Notebook title
    editor.setWindowTitle(editor.notebook.title + " - OpenNote")
    editor.notebookTitleView.setText(editor.notebook.title)

    # Initialize the autosaver
    editor.autosaver = Autosaver(editor)
    # editor.object = []
    editor.selected = None

    # editor.object = []
    # editor.selected = None

    print("PREP TO LOAD VIEWS")

    editor.pageView.loadPages(editor.notebook.pages)

    print("LOADPAGES")
    editor.sectionView.loadSections(editor.notebook.pages[0].sections)

    print("RELOADED VIEWS ")

    if len(editor.notebook.pages) > 0:   # If pages exist

        print("PAGES EXIST")
        # Show all Pages in Notebook
        # editor.pageView.loadPages(editor.notebook.pages)
        # for p in range(len(editor.notebook.page)):
        #     params = editor.notebook.page[p]
        #     build_page(editor, params.title)    # Build functions add widgets to editor
        # editor.pages.itemAt(0).widget().setStyleSheet("background-color: #c2c2c2")
        # editor.pageIndex = 0

        # if len(editor.notebook.page[0].section) > 0:    #If sections exist

        #     # Show all Sections in page 1
        #     for s in range(len(editor.notebook.page[0].section)):
        #         params = editor.notebook.page[0].section[s]
        #         build_section(editor, params.title)
        #     editor.sections.itemAt(0).widget().setStyleSheet("background-color: #c2c2c2")
        #     editor.sectionIndex = 0

        #     if len(editor.notebook.page[0].section[0].object) > 0:  # If objects exist
        #         # Show objects in page1, section1
        #         for o in range(len(editor.notebook.page[0].section[0].object)):
        #             params = editor.notebook.page[0].section[0].object[o]
        #             build_object(editor, params)

    # # Select page1, section1
    # editor.pageIndex = 0
    # editor.sectionIndex = 0

# Destroy all Widgets in the Current Notebook
def destroy(editor):
    print("RAN DESTROY")
    # if(len(editor.notebook.page)) > 0:
    #     # Destroy all Pages
    #     for p in range (len(editor.notebook.page)):
    #         editor.pages.itemAt(p).widget().deleteLater()

    #     if(len(editor.notebook.page[editor.page].section)) > 0:
    #         # Destroy all Sections
    #         for s in range(len(editor.notebook.page[editor.page].section)):
    #             editor.sections.itemAt(s).widget().deleteLater()

    #         if(len(editor.notebook.page[editor.page].section[editor.section].object)) > 0:
    #             # Destory all Objects
    #             for o in range(len(editor.notebook.page[editor.page].section[editor.section].object)):
    #                 editor.object[o].childWidget.deleteLater()
    #                 editor.object[o].deleteLater()
