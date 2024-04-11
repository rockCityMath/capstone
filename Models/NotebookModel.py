
# Represents a notebook in the application.
class NotebookModel:
    def __init__(self, title):
        self.path = None # The file path of the notebook if saved
        self.title = title # The title of the notebook

        self.pages = [] # PageModel[] - List to store PageModel instances representing pages in the notebook
