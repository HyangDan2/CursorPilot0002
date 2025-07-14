from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel("Video Area")
        layout.addWidget(self.label)
        self._fps = 0.0

    def play(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass

    def pause(self):
        pass

    def load_video1(self, path):
        pass

    def load_video2(self, path):
        pass

    def save_mixed_video(self, path):
        return False

    def get_fps(self):
        return self._fps