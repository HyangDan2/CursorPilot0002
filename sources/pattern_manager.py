from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QFileDialog
from PySide6.QtCore import Signal
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

    def on_item_double_clicked(self, item):
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self.patterns):
            self.image_selected.emit(self.patterns[idx])

    def get_patterns(self):
        return self.patterns 