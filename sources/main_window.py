from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox, QApplication
from PySide6.QtCore import Qt, QSettings, QRect
from PySide6.QtGui import QKeySequence
from sources.pattern_display import PatternDisplay
from sources.pattern_manager import PatternManager
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Halo Pattern Display')
        self.settings = QSettings('CursorPilot', 'HaloPattern')
        self.pattern_display = PatternDisplay(self)
        self.pattern_manager = PatternManager(self)
        self.last_image_path = None
        self.is_fullscreen = False
        self.normal_geometry = None
        self.init_ui()
        self.restore_settings()
        self.show_black_pattern()

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.pattern_display)
        self.setCentralWidget(central)
        # PatternManager는 별도 창으로 띄우거나 필요시 연동
        self.pattern_manager.image_selected.connect(self.on_image_selected)

    def restore_settings(self):
        geom = self.settings.value('geometry')
        if geom:
            self.setGeometry(QRect(*map(int, geom)))
        self.is_fullscreen = self.settings.value('fullscreen', False, type=bool)
        if self.is_fullscreen:
            self.enter_fullscreen()
        self.last_image_path = self.settings.value('last_image', None, type=str)

    def save_settings(self):
        self.settings.setValue('geometry', [self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()])
        self.settings.setValue('fullscreen', self.is_fullscreen)
        self.settings.setValue('last_image', self.last_image_path)

    def show_black_pattern(self):
        self.pattern_display.show_pattern('black')

    def on_image_selected(self, image_path):
        self.last_image_path = image_path
        self.show_image(image_path)

    def show_image(self, image_path):
        self.pattern_display.show_pattern('image', image_path=image_path)
        self.adjust_window_to_image(image_path)

    def adjust_window_to_image(self, image_path):
        from PySide6.QtGui import QImage
        img = QImage(image_path)
        if not img.isNull():
            self.resize(img.width(), img.height())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.exit_fullscreen()
            else:
                self.enter_fullscreen()
        # ↑, ↓ 키 관련 코드는 제거
        elif event.key() == Qt.Key.Key_Tab:
            self.pattern_display.toggle_metadata()
        elif event.matches(QKeySequence('Ctrl+I')):
            self.toggle_last_image()
        else:
            super().keyPressEvent(event)

    def enter_fullscreen(self):
        if not self.isFullScreen():
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True

    def exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            QApplication.processEvents()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False

    def toggle_last_image(self):
        if self.pattern_display.current_metadata == self.last_image_path and self.last_image_path:
            self.show_black_pattern()
        elif self.last_image_path:
            self.show_image(self.last_image_path)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event) 