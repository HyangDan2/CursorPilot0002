from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMenuBar, QAction, QMessageBox
from PySide6.QtCore import Qt, QTimer
from player.video_player import VideoPlayer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multimedia Player with Mixing")
        self.resize(900, 700)
        self._init_menu()
        self._init_ui()

    def _init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        self.load_video1_action = QAction("Load Video1", self)
        self.load_video1_action.triggered.connect(self.load_video1)
        file_menu.addAction(self.load_video1_action)

        self.load_video2_action = QAction("Load Video2", self)
        self.load_video2_action.triggered.connect(self.load_video2)
        file_menu.addAction(self.load_video2_action)

        self.save_mixed_action = QAction("Save Mixed Video", self)
        self.save_mixed_action.triggered.connect(self.save_mixed_video)
        file_menu.addAction(self.save_mixed_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)

        # FPS label
        self.fps_label = QLabel("FPS: 0")
        layout.addWidget(self.fps_label, alignment=Qt.AlignmentFlag.AlignRight)

        # Control buttons
        controls = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.video_player.play)
        controls.addWidget(self.play_btn)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.video_player.stop)
        controls.addWidget(self.stop_btn)
        self.restart_btn = QPushButton("Restart")
        self.restart_btn.clicked.connect(self.video_player.restart)
        controls.addWidget(self.restart_btn)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.video_player.pause)
        controls.addWidget(self.pause_btn)
        layout.addLayout(controls)

        # Timer for FPS update
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(500)

    def update_fps(self):
        fps = self.video_player.get_fps()
        self.fps_label.setText(f"FPS: {fps:.2f}")

    def load_video1(self):
        file, _ = QFileDialog.getOpenFileName(self, "Load Video 1", "", "Video Files (*.mp4 *.avi *.mov)")
        if file:
            self.video_player.load_video1(file)

    def load_video2(self):
        file, _ = QFileDialog.getOpenFileName(self, "Load Video 2", "", "Video Files (*.mp4 *.avi *.mov)")
        if file:
            self.video_player.load_video2(file)

    def save_mixed_video(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Mixed Video", "", "MP4 Files (*.mp4)")
        if file:
            success = self.video_player.save_mixed_video(file)
            if success:
                QMessageBox.information(self, "Success", "Mixed video saved successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save mixed video.")