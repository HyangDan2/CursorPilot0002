from PySide6.QtWidgets import QMainWindow, QApplication, QMenuBar, QMenu, QFileDialog
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSettings
from sources.pattern_manager import PatternManager
from sources.pattern_display import PatternDisplay
import os

class HaloPatternGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Halo Evaluation Pattern Generator')
        self.pattern_manager = PatternManager(self)
        self.pattern_manager.image_selected.connect(self.display_selected_pattern)
        self.pattern_display = PatternDisplay(self)
        self.setCentralWidget(self.pattern_display)
        self.patterns = []
        self.current_pattern_index = -1
        self.settings = QSettings('CursorPilot', 'HaloPatternGenerator')
        self.is_fullscreen = False
        self._normal_geometry = None
        self.pattern_display.show_pattern('black')  # 초기 Black Pattern 표시
        self.rgbw_level = 255  # RGBW 패턴의 레벨(0~255)
        self.current_rgbw = None  # 'red', 'green', 'blue', 'white' 중 하나
        self.restore_state()
        self.init_menu()
        self.show()

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        pattern_manager_action = QAction('Pattern Manager', self)
        pattern_manager_action.triggered.connect(self.open_pattern_manager)
        file_menu.addAction(pattern_manager_action)
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_pattern_manager(self):
        if self.pattern_manager.exec():
            self.patterns = self.pattern_manager.get_patterns()
            if self.patterns:
                self.current_pattern_index = 0
                self.pattern_display.show_pattern('image', self.patterns[0], fullscreen=self.is_fullscreen)

    def display_selected_pattern(self, image_path):
        self.pattern_display.show_pattern('image', image_path, fullscreen=self.is_fullscreen)
        self.settings.setValue('last_image', image_path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Up:
            if self.current_rgbw in ['red', 'green', 'blue', 'white'] and self.rgbw_level < 255:
                self.rgbw_level += 1
                self.pattern_display.show_pattern(self.current_rgbw, level=self.rgbw_level)
        elif event.key() == Qt.Key.Key_Down:
            if self.current_rgbw in ['red', 'green', 'blue', 'white'] and self.rgbw_level > 0:
                self.rgbw_level -= 1
                self.pattern_display.show_pattern(self.current_rgbw, level=self.rgbw_level)
        elif (event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal) and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            if self.current_rgbw in ['red', 'green', 'blue', 'white']:
                self.rgbw_level = min(self.rgbw_level + 32, 255)
                self.pattern_display.show_pattern(self.current_rgbw, level=self.rgbw_level)
        elif (event.key() == Qt.Key.Key_Minus or event.key() == Qt.Key.Key_Underscore) and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            if self.current_rgbw in ['red', 'green', 'blue', 'white']:
                self.rgbw_level = max(self.rgbw_level - 32, 0)
                self.pattern_display.show_pattern(self.current_rgbw, level=self.rgbw_level)
        elif event.key() == Qt.Key.Key_Tab:
            self.pattern_display.toggle_metadata()
        elif event.key() == Qt.Key.Key_1:
            self.current_rgbw = 'red'
            self.rgbw_level = 255
            self.pattern_display.show_pattern('red', level=self.rgbw_level)
        elif event.key() == Qt.Key.Key_2:
            self.current_rgbw = 'green'
            self.rgbw_level = 255
            self.pattern_display.show_pattern('green', level=self.rgbw_level)
        elif event.key() == Qt.Key.Key_3:
            self.current_rgbw = 'blue'
            self.rgbw_level = 255
            self.pattern_display.show_pattern('blue', level=self.rgbw_level)
        elif event.key() == Qt.Key.Key_4:
            self.current_rgbw = 'white'
            self.rgbw_level = 255
            self.pattern_display.show_pattern('white', level=self.rgbw_level)
        elif event.key() == Qt.Key.Key_Right:
            self.next_pattern()
        elif event.key() == Qt.Key.Key_Left:
            self.prev_pattern()
        elif event.key() == Qt.Key.Key_I and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # 현재 이미지가 없으면 마지막 이미지를 QSettings에서 불러와 표시
            if self.patterns and self.current_pattern_index >= 0:
                image_path = self.patterns[self.current_pattern_index]
                self.pattern_display.show_pattern('image', image_path, fullscreen=self.is_fullscreen)
                self.settings.setValue('last_image', image_path)
            else:
                last_image = self.settings.value('last_image', None)
                if last_image:
                    last_image = str(last_image)
                    if os.path.exists(last_image):
                        self.pattern_display.show_pattern('image', last_image, fullscreen=self.is_fullscreen)
        else:
            super().keyPressEvent(event)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            QApplication.processEvents()
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            self.pattern_display.is_fullscreen = False
            self.pattern_display.resizeEvent(None)
            self.is_fullscreen = False
            if self.menuBar():
                self.menuBar().show()
        else:
            self._normal_geometry = self.geometry()
            self.showFullScreen()
            QApplication.processEvents()
            self.pattern_display.is_fullscreen = True
            self.pattern_display.resizeEvent(None)
            self.is_fullscreen = True
            if self.menuBar():
                self.menuBar().hide()

    def next_pattern(self):
        if self.patterns:
            self.current_pattern_index = (self.current_pattern_index + 1) % len(self.patterns)
            self.pattern_display.show_pattern('image', self.patterns[self.current_pattern_index], fullscreen=self.is_fullscreen)

    def prev_pattern(self):
        if self.patterns:
            self.current_pattern_index = (self.current_pattern_index - 1) % len(self.patterns)
            self.pattern_display.show_pattern('image', self.patterns[self.current_pattern_index], fullscreen=self.is_fullscreen)

    def restore_state(self):
        geometry = self.settings.value('geometry')
        fullscreen = self.settings.value('fullscreen', False, type=bool)
        last_image = self.settings.value('last_image')
        if geometry:
            self.setGeometry(geometry)
        if fullscreen:
            self.toggle_fullscreen()
        if last_image:
            self.pattern_display.show_pattern('image', last_image, fullscreen=self.is_fullscreen)

    def closeEvent(self, event):
        self.settings.setValue('geometry', self.geometry())
        self.settings.setValue('fullscreen', self.is_fullscreen)
        if self.pattern_display.current_pixmap:
            self.settings.setValue('last_image', self.pattern_display.current_metadata)
        else:
            self.settings.remove('last_image')
        super().closeEvent(event) 