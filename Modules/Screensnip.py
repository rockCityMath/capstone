import numpy as np
import cv2
from PIL import ImageGrab
from sys import platform

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# General widget from https://github.com/harupy/snipping-tool <3
class SnippingWidget(QWidget):
    is_snipping = False

    def __init__(self):
        super(SnippingWidget, self).__init__()

        if platform == "linux":
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
        self.setWindowFlags(Qt.WindowStaysOnTopHint) 
        self.parent = None
        self.screen = QApplication.instance().primaryScreen()
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.begin = self.end = QPoint()
        self.onSnippingCompleted = None
        self.event_pos = None

    def start(self, event_pos):
        print("SnippingWidget.start")
        SnippingWidget.is_snipping = True

        if platform != "linux":
            self.setWindowOpacity(0.3)

        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.event_pos = event_pos
        self.show()
        print("SnippingWidget.start done")

    def paintEvent(self, event):
        if SnippingWidget.is_snipping:
            #brush_color = (128, 128, 255, 100)
            brush_color = (0, 0, 0, 0)
            lw = 3
            opacity = 0.3

            if platform != "linux":
                self.setWindowOpacity(opacity)
    
            qp = QPainter(self)
            qp.setPen(QPen(QColor('black'), lw))
            qp.setBrush(QColor(*brush_color))
            rect = QRectF(self.begin, self.end)
            qp.drawRect(rect)
        else:
            self.begin = QPoint()
            self.end = QPoint()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.is_snipping = False
        QApplication.restoreOverrideCursor()
        rect = self.geometry()
        x1 = min(self.begin.x(), self.end.x()) + rect.left()
        y1 = min(self.begin.y(), self.end.y()) + rect.top()
        x2 = max(self.begin.x(), self.end.x()) + rect.left()
        y2 = max(self.begin.y(), self.end.y()) + rect.top()

        self.repaint()
        QApplication.processEvents()

        try:
            if platform == "darwin":
                #img = ImageGrab.grab(bbox=( (x1 ) * 2, (y1 + 55 ) * 2, (x2 ) * 2, (y2 + 55) * 2)) [may be needed for different mac version - testing in progress]
                img = ImageGrab.grab(bbox=(x1, y1 + 55, x2, y2 + 55)) # For mac version 14.1.2
            else:
                img = ImageGrab.grab(bbox=(x1 + 2, y1 + 2, x2 - 1, y2 - 1))

        except Exception as e:
            print(f"Error grabbing screenshot: {e}")
            img = None


        try:
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except:
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()
