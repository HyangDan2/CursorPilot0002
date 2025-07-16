import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QMenuBar, QMenu, QFileDialog, QDialog, QVBoxLayout, QPushButton, QListWidget, QWidget, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QKeySequence, QImage, QColor, QAction
from PySide6.QtCore import Qt, Signal, QSettings
import os

class PatternManager(QDialog):
    image_selected = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Pattern Manager')
        self.patterns = []
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.add_button = QPushButton('Add Pattern (Image)')
        self.add_button.clicked.connect(self.add_pattern)
        self.layout.addWidget(self.add_button)
        self.setLayout(self.layout)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

    def add_pattern(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters([
            'Images (*.png *.jpg *.jpeg *.bmp *.gif)',
            'All files (*)'
        ])
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.patterns.append(file_path)
            self.list_widget.addItem(os.path.basename(file_path))

    def get_patterns(self):
        return self.patterns

    def on_item_double_clicked(self, item):
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self.patterns):
            self.image_selected.emit(self.patterns[idx])

class PatternDisplay(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
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
        elif pattern_type == 'green':
            self.setStyleSheet('background-color: green;')
            self.setText('')
            self.current_metadata = 'Full Green Pattern'
        elif pattern_type == 'blue':
            self.setStyleSheet('background-color: blue;')
            self.setText('')
            self.current_metadata = 'Full Blue Pattern'
        elif pattern_type == 'white':
            self.setStyleSheet('background-color: white;')
            self.setText('')
            self.current_metadata = 'Full White Pattern'
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
                self.pattern_display.show_pattern('image', self.patterns[0])

    def display_selected_pattern(self, image_path):
        self.pattern_display.show_pattern('image', image_path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Tab:
            self.pattern_display.toggle_metadata()
        elif event.key() == Qt.Key_1:
            self.pattern_display.show_pattern('red')
        elif event.key() == Qt.Key_2:
            self.pattern_display.show_pattern('green')
        elif event.key() == Qt.Key_3:
            self.pattern_display.show_pattern('blue')
        elif event.key() == Qt.Key_4:
            self.pattern_display.show_pattern('white')
        elif event.key() == Qt.Key_Right:
            self.next_pattern()
        elif event.key() == Qt.Key_Left:
            self.prev_pattern()
        else:
            super().keyPressEvent(event)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            self.pattern_display.is_fullscreen = False
            self.pattern_display.resizeEvent(None)
            self.showNormal()
            QApplication.processEvents()
            self.is_fullscreen = False
        else:
            self._normal_geometry = self.geometry()
            self.pattern_display.is_fullscreen = True
            self.pattern_display.resizeEvent(None)
            self.showFullScreen()
            QApplication.processEvents()
            self.is_fullscreen = True

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

    def next_pattern(self):
        if self.patterns:
            self.current_pattern_index = (self.current_pattern_index + 1) % len(self.patterns)
            self.pattern_display.show_pattern('image', self.patterns[self.current_pattern_index])

    def prev_pattern(self):
        if self.patterns:
            self.current_pattern_index = (self.current_pattern_index - 1) % len(self.patterns)
            self.pattern_display.show_pattern('image', self.patterns[self.current_pattern_index])

def main():
    app = QApplication(sys.argv)
    window = HaloPatternGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()