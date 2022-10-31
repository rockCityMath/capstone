
from classes.Notebook import Notebook
from classes.Page import Page
from classes.DragItem import DragItem

def main():
	nb = Notebook()
	for i in range(3):
		nb.pages.append(Page('I have a title'))
	
	for i in range(3):
		page = nb.pages[i]
		for i2 in range(i+1):
			page.items.add(DragItem((i2*50,0)))

	nb.title="somenameimadeuplol"
	nb.pages[2].setChild(nb.pages[1])

	nb.location="/Users/suleiman/Desktop/lefile.on"
	nb.save()
	print(nb.pages)

if __name__=="__main__":
	main()
