from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QFileDialog
from PySide6.QtCore import Signal
import os
import shutil

IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Image')

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
        self.load_image_folder()

    def load_image_folder(self):
        self.patterns.clear()
        self.list_widget.clear()
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
        for fname in os.listdir(IMAGE_DIR):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                fpath = os.path.join(IMAGE_DIR, fname)
                self.patterns.append(fpath)
                self.list_widget.addItem(fname)

    def add_pattern(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters([
            'Images (*.png *.jpg *.jpeg *.bmp *.gif)',
            'All files (*)'
        ])
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            # Image 폴더에 복사
            if not os.path.exists(IMAGE_DIR):
                os.makedirs(IMAGE_DIR)
            dest_path = os.path.join(IMAGE_DIR, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            self.load_image_folder()

    def on_item_double_clicked(self, item):
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self.patterns):
            self.image_selected.emit(self.patterns[idx])

    def get_patterns(self):
        return self.patterns 