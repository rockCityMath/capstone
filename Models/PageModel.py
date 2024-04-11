import uuid

# Represents a page within a notebook

class PageModel:
    def __init__(self, title: str, parentUuid: int = 0):
        self.title = title
        self.sections = []  # SectionModel[] -  List to store SectionModel instances representing sections in the page

        # These are used to represent the tree structure, the model is not actually concerned with parent and children
        # The tree structure lets us build a view that we can interact with as if there were really nested pages
        self.__uuid = uuid.uuid4()
        self.__parentUuid = parentUuid

    @staticmethod
    def newRootPage():
        rootPage = PageModel("Notebook")
        rootPage.__uuid = 0
        return rootPage # A new root page

    def isRoot(self):
        return self.__uuid == 0

    def getUUID(self):
        return self.__uuid

    def getParentUUID(self):
        return self.__parentUuid
