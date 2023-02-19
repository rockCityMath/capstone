from models.util import UniqueList
class Section:
	def __init__(self,index,title="Untitled",):
		self.title=title
		self.index=index
		self.items = set()
		self.parent = None
		self.children=UniqueList()

		self.text = "" # temporary, remove when items (drag and drop) is implemented
		self.textedits = [] # all the text boxes (TextBoxDraggable)
		self.images = []

	def setChild(self,page):
		#IMO we should just model this stuff at the UI level. add an indent field that just indents the page name
		#this breaks in any complex case
		if page.parent!=None:
			page.parent.children.remove(page)
		page.parent=self
		self.children.append(page)
  
