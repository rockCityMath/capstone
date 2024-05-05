from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QFileDialog


from Modules.Enums import WidgetType

import random
import cv2

class ImageWidget(QLabel):
    def __init__(self, x, y, w, h, image_matrix):
        super().__init__()
        self.image_matrix = image_matrix
        self.w = w
        self.h = h

        # Image matrix from cv2 -> QImage -> QPixmap on this label
        matrix_height, matrix_width, _ = image_matrix.shape # Calc dimensions from real image matrix, not the current widget geometry
        bytes_per_line = 3 * matrix_width
        q_image = QImage(image_matrix.data, matrix_width, matrix_height, bytes_per_line, QImage.Format_BGR888)
        self.q_pixmap = QPixmap(q_image)
        self.setPixmap(self.q_pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)) # Scale to widget geometry

        self.setGeometry(x, y, w, h) # this should get fixed
        self.persistantGeometry = self.geometry() 

    # Handle resize
    def newGeometryEvent(self, newGeometry):
        new_w = newGeometry.width()
        new_h = newGeometry.height()
        if (self.w != new_w) or (self.h != new_h): # Not exactly sure how object's width and height attribute gets updated but this works
            self.setPixmap(self.q_pixmap.scaled(new_w, new_h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

            pixmap_rect = self.pixmap().rect()
            w = pixmap_rect.width()
            h = pixmap_rect.height()
            # parent.resize(w, h) # Set container to the size of the new scaled pixmap

        self.persistantGeometry = newGeometry

    '''@staticmethod
    def new(clickPos):

        # Get path from user
        path, _ = QFileDialog.getOpenFileName(QWidget(), 'Add Image')
        if path == "": return

        # Get image size
        image_matrix = cv2.imread(path)
        h, w, _ = image_matrix.shape

        # Create image and add to notebook
        h, w, _ = image_matrix.shape
        image = ImageWidget(clickPos.x(), clickPos.y(), w, h, image_matrix) # Note: the editorframe will apply pos based on event

        return image
    '''
    # uses inbuilt qt file dialog 
    def new(clickPos):
        # Create a dummy parent widget for the file dialog
        dummy_parent = QWidget()

        # Get path from user
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Use Qt's built-in dialog instead of the native platform dialog

        # Create file dialog
        file_dialog = QFileDialog(dummy_parent, 'Add Image', '', 'Images (*.png *.xpm *.jpg *.bmp *.jpeg);;All Files (*)', options=options)

        # Set the window flags to keep the dialog on top
        file_dialog.setWindowFlags(file_dialog.windowFlags() | Qt.WindowStaysOnTopHint)

        # Show the file dialog
        if file_dialog.exec():
            # Get the selected file path
            path = file_dialog.selectedFiles()[0]

            # Get image size
            image_matrix = cv2.imread(path)
            h, w, _ = image_matrix.shape

            # Create image and add to notebook
            image = ImageWidget(clickPos.x(), clickPos.y(), w, h, image_matrix)
            return image

        # Return None if the user cancels the dialog
        return None


    @staticmethod # Special staticmethod that screensnip uses
    def newFromMatrix(clickPos, imageMatrix):
        h, w, _ = imageMatrix.shape
        image = ImageWidget(clickPos.x(), clickPos.y(), w, h, imageMatrix)

        return image

    def __getstate__(self):
        state = {}
        state['geometry'] = self.parentWidget().geometry()
        state['image_matrix'] = self.image_matrix
        return state

    def __setstate__(self, state):
        self.__init__(state['geometry'].x(), state['geometry'].y(), state['geometry'].width(), state['geometry'].height(), state['image_matrix'])

    def customMenuItems(self):
        def build_action(parent, icon_path, action_name, set_status_tip, set_checkable):
            action = QAction(QIcon(icon_path), action_name, parent)
            action.setStatusTip(set_status_tip)
            action.setCheckable(set_checkable)
            return action


        toolbarBottom = QToolBar()
        toolbarBottom.setIconSize(QSize(16, 16))
        toolbarBottom.setMovable(False)

        #crop = build_action(toolbarTop, './Assets/icons/svg_crop', "Crop", "Crop", False)
        
        flipHorizontal = build_action(toolbarBottom, './Assets/icons/svg_flip_horizontal', "Horizontal Flip", "Horizontal Flip", False)
        flipHorizontal.triggered.connect(self.flipHorizontal)
        flipVertical = build_action(toolbarBottom, './Assets/icons/svg_flip_vertical', "Vertical Flip", "Vertical Flip", False)
        flipVertical.triggered.connect(self.flipVertical)

        rotateLeftAction = build_action(toolbarBottom, './Assets/icons/svg_rotate_left', "Rotate 90 degrees Left", "Rotate 90 degrees Left", False)
        rotateLeftAction.triggered.connect(self.rotate90Left)
        rotateRightAction = build_action(toolbarBottom, './Assets/icons/svg_rotate_right', "Rotate 90 degrees Right", "Rotate 90 degrees Right", False)
        
        rotateRightAction.triggered.connect(self.rotate90Right)

        shrinkImageAction = build_action(toolbarBottom, 'Assets/icons/svg_shrink', "Shrink", "Shrink", False)
        shrinkImageAction.triggered.connect(self.shrinkImage)
        expandImageAction = build_action(toolbarBottom, 'Assets/icons/svg_expand', "Expand", "Expand", False)
        expandImageAction.triggered.connect(self.expandImage)


        toolbarBottom.addActions([rotateLeftAction, rotateRightAction, flipHorizontal, flipVertical, shrinkImageAction, expandImageAction])

        qwaBottom = QWidgetAction(self)
        qwaBottom.setDefaultWidget(toolbarBottom)

        return [qwaBottom] 
        
    def flipVertical(self):
        # Flip the image matrix vertically using OpenCV
        parent_widget = self.parentWidget()
        if parent_widget:
            newX, newY = parent_widget.x(), parent_widget.y()
            new_width, new_height = parent_widget.height(), parent_widget.width()
            parent_widget.setGeometry(newX, newY, new_width, new_height)

        self.image_matrix = cv2.flip(self.image_matrix, 0)
        self.updatePixmap()


    def flipHorizontal(self):
        # Flip the image matrix horizontally using OpenCV

        parent_widget = self.parentWidget()
        if parent_widget:
            newX, newY = parent_widget.x(), parent_widget.y()
            new_width, new_height = parent_widget.height(), parent_widget.width()
            parent_widget.setGeometry(newX, newY, new_width, new_height)

        self.image_matrix = cv2.flip(self.image_matrix, 1)
        self.updatePixmap()


    def rotate90Left(self):
        # Rotate the image matrix 90 degrees to the left using OpenCV
        self.w, self.h = self.h, self.w

        parent_widget = self.parentWidget()
        if parent_widget:
            newX, newY = parent_widget.x(), parent_widget.y()
            new_width, new_height = parent_widget.height(), parent_widget.width()
            parent_widget.setGeometry(newX, newY, new_width, new_height)
        self.image_matrix = cv2.rotate(self.image_matrix, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.updatePixmap()
    def rotate90Right(self):
        # Rotate the image matrix 90 degrees to the right using OpenCV
        self.w, self.h = self.h, self.w

        # Access parent and update geometry
        parent_widget = self.parentWidget()
        if parent_widget:
            newX, newY = parent_widget.x(), parent_widget.y()
            new_width, new_height = parent_widget.height(), parent_widget.width()
            parent_widget.setGeometry(newX, newY, new_width, new_height)

        self.image_matrix = cv2.rotate(self.image_matrix, cv2.ROTATE_90_CLOCKWISE)
        self.updatePixmap()

    def shrinkImage(self):
        # Decrease image size by 10%
        self.w = int(self.w * 0.9)
        self.h = int(self.h * 0.9)
        parent_widget = self.parentWidget()
        if parent_widget:
            newX, newY = parent_widget.x(), parent_widget.y()
            new_width, new_height = self.w, self.h
            parent_widget.setGeometry(newX, newY, new_width, new_height)
        self.setPixmap(self.q_pixmap.scaled(self.w, self.h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def expandImage(self):
        # Increase image size by 10%
        self.w = int(self.w * 1.1)
        self.h = int(self.h * 1.1)
        parent_widget = self.parentWidget()
        if parent_widget:
            newX, newY = parent_widget.x(), parent_widget.y()
            new_width, new_height = self.w, self.h
            parent_widget.setGeometry(newX, newY, new_width, new_height)
        self.setPixmap(self.q_pixmap.scaled(self.w, self.h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    # Updates display. Note: Keeps Aspect Ratio
    def updateImageSize(self):
        # Update the displayed pixmap with the new size
        self.setPixmap(self.q_pixmap.scaled(self.w, self.h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
  
    def updatePixmap(self):
        # Update the QImage and QPixmap
        matrix_height, matrix_width, _ = self.image_matrix.shape
        bytes_per_line = 3 * matrix_width
        q_image = QImage(self.image_matrix.data, matrix_width, matrix_height, bytes_per_line, QImage.Format_BGR888)
        self.q_pixmap = QPixmap(q_image)

        # Update the displayed pixmap
        self.setPixmap(self.q_pixmap.scaled(self.w, self.h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
