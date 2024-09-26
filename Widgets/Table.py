from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class TableWidget(QWidget):
    def __init__(self, x, y, w, h, rows, cols):
        super(TableWidget, self).__init__()

        # The actual table widget
        self.table = QTableWidget(rows, cols, self)
        # Hides the horizontal and vertical headers
        # These actually look really cool tho
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)

        # Get the default table border color from the palette
        table_border_color = self.palette().color(QPalette.Window)

        # Add a custom border on the top of the widget
        self.table.setStyleSheet(f"QTableView {{border: 1px solid {table_border_color.name()};}}")
           
        # Make the cells resizable
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setGeometry(x, y, w, h)
        self.table.setGeometry(0, 0, w, h)
        self.resize(w, h)
        self.persistantGeometry = self.geometry()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True) # If extending a qwidget to insert something else, dont receive mouse events

    # Child widget not concerned with pos but is with w, h
    def newGeometryEvent(self, newGeometry: QRect):
        self.table.resize(newGeometry.width(), newGeometry.height())
        self.persistantGeometry = newGeometry
        return

    def addRow(self):
        self.table.insertRow(self.table.rowCount())

    def addCol(self):
        self.table.insertColumn(self.table.columnCount())

    @staticmethod
    def new(clickPos: QPoint):
        dialog = TablePopupWindow()
        if dialog.exec_() == QDialog.Accepted:
            rows_input, cols_input = dialog.get_table_data()
            print(f"rows input is {rows_input} cols_input is {cols_input}")
            table_widget = TableWidget(clickPos.x(), clickPos.y(), 200, 200, int(rows_input), int(cols_input))
            
        return table_widget
    
    def __getstate__(self):
        state = {}

        t = self.table
        rowCnt = t.rowCount()
        colCnt = t.columnCount()
        tableData = [["" if t.item(i, j) == None else t.item(i, j).text() for i in range(rowCnt)] for j in range(colCnt)] # :)

        state['tableData'] = tableData
        state['geometry'] = self.parentWidget().geometry() # Can get whole geometry from parent, or just the pos
        return state

    def __setstate__(self, state):
        self.__init__(state['geometry'].x(),
                      state['geometry'].y(),
                      state['geometry'].width(),
                      state['geometry'].height(),
                      len(state['tableData'][0]),
                      len(state['tableData']))

        rowCnt = len(state['tableData'][0])
        colCnt = len(state['tableData'])

        for i in range(colCnt):
            for j in range(rowCnt):
                self.table.setItem(j, i, QTableWidgetItem(state['tableData'][i][j]))

def show_table_popup(self):
    popup = TablePopupWindow()
    popup.exec_() 
    #def undo_triggered(self):
    # Call the EditorFrameView's triggerUndo method
    #self.EditorFrameView.triggerUndo()

class TablePopupWindow(QDialog):
    def __init__(self):
        super().__init__()

        # to stay on top of application
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        self.setWindowTitle("Table Configuration")
        self.layout = QVBoxLayout()

        self.rows_input = QLineEdit(self)
        self.rows_input.setPlaceholderText("Enter number of rows:")
        self.layout.addWidget(self.rows_input)

        self.cols_input = QLineEdit(self)
        colNum = self.cols_input.setPlaceholderText("Enter number of columns:")
        self.layout.addWidget(self.cols_input)

        create_table_button = QPushButton("Create Table")
        self.layout.addWidget(create_table_button)
        create_table_button.clicked.connect(self.accept)
        #create error message if no data is entered or if number of rows or columns are < 1
        
        cancel_button = QPushButton("Cancel")
        self.layout.addWidget(cancel_button)
        cancel_button.clicked.connect(self.reject)
        

        self.setLayout(self.layout)

        self.setModal(False)
    
    def get_table_data(self):
        rows_input = self.rows_input.text()
        cols_input = self.cols_input.text()
        return rows_input, cols_input

    def create_table(self):
        print("table")

    def mousePressEvent(self, event):
        # Check if the mouse click is outside the dialog
        if event.button() == Qt.LeftButton and not self.rect().contains(event.globalPos()):
            self.close()
