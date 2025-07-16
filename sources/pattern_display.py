from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QImage, QColor, Qt
import os

class PatternDisplay(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet('background-color: black;')
        self.current_pixmap = None
        self.current_metadata = ''
        self.show_metadata = False
        self.is_fullscreen = False
        self._normal_geometry = None

    def show_pattern(self, pattern_type, image_path=None, fullscreen=None):
        if fullscreen is not None:
            self.is_fullscreen = fullscreen
        if pattern_type == 'red':
            self.setStyleSheet('background-color: red;')
            self.setText('')
            self.current_metadata = 'Full Red Pattern'
            self.current_pixmap = None
        elif pattern_type == 'green':
            self.setStyleSheet('background-color: green;')
            self.setText('')
            self.current_metadata = 'Full Green Pattern'
            self.current_pixmap = None
        elif pattern_type == 'blue':
            self.setStyleSheet('background-color: blue;')
            self.setText('')
            self.current_metadata = 'Full Blue Pattern'
            self.current_pixmap = None
        elif pattern_type == 'white':
            self.setStyleSheet('background-color: white;')
            self.setText('')
            self.current_metadata = 'Full White Pattern'
            self.current_pixmap = None
        elif pattern_type == 'image' and image_path:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.setText('Failed to load image')
                self.current_metadata = 'Invalid image file.'
                self.current_pixmap = None
            else:
                self.current_pixmap = pixmap
                if self.is_fullscreen:
                    self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.current_metadata = image_path
            self.setStyleSheet('background-color: black;')
        else:
            self.setStyleSheet('background-color: black;')
            self.setText('')
            self.current_metadata = ''
            self.current_pixmap = None
        self.update_metadata()

    def resizeEvent(self, event):
        if self.current_pixmap:
            if self.is_fullscreen:
                self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.clear()
        super().resizeEvent(event)
        self.update_metadata()

    def update_metadata(self):
        if self.show_metadata and self.current_metadata:
            self.setToolTip(self.current_metadata)
        else:
            self.setToolTip('')

    def toggle_metadata(self):
        self.show_metadata = not self.show_metadata
        self.update_metadata()

    def increase_pixels(self):
        # TODO: 현재 이미지의 모든 픽셀 값을 +1 (최대 0xFF)
        pass

    def decrease_pixels(self):
        # TODO: 현재 이미지의 모든 픽셀 값을 -1 (최소 0x00)
        pass 