import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import time

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel("Video Area")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self._fps = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)
        self._playing = False
        self._paused = False
        self._loop = False
        self._video1 = None
        self._video2 = None
        self._video1_path = None
        self._video2_path = None
        self._mix_mode = False
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._frame_times = []
        self._current_video = 1
        self._restart_flag = False

    def play(self):
        if not self._playing:
            self._playing = True
            self._paused = False
            self._timer.start(0)
        elif self._paused:
            self._paused = False
            self._timer.start(0)

    def stop(self):
        self._playing = False
        self._paused = False
        self._timer.stop()
        self._reset_videos()
        self.label.setText("Video Area")

    def restart(self):
        self._restart_flag = True
        self.stop()
        self.play()

    def pause(self):
        self._paused = True
        self._timer.stop()

    def load_video1(self, path):
        if self._video1:
            self._video1.release()
        self._video1 = cv2.VideoCapture(path)
        self._video1_path = path
        self._check_mix_mode()
        self._reset_videos()

    def load_video2(self, path):
        if self._video2:
            self._video2.release()
        self._video2 = cv2.VideoCapture(path)
        self._video2_path = path
        self._check_mix_mode()
        self._reset_videos()

    def save_mixed_video(self, path):
        # Stub: Implement actual saving logic if needed
        return False

    def get_fps(self):
        return self._fps

    def _reset_videos(self):
        if self._video1_path:
            if self._video1:
                self._video1.release()
            self._video1 = cv2.VideoCapture(self._video1_path)
        if self._video2_path:
            if self._video2:
                self._video2.release()
            self._video2 = cv2.VideoCapture(self._video2_path)
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._frame_times = []
        self._current_video = 1

    def _check_mix_mode(self):
        self._mix_mode = self._video1_path is not None and self._video2_path is not None

    def _next_frame(self):
        if not self._playing or self._paused:
            return
        frame = None
        ret1, frame1 = (self._video1.read() if self._video1 else (False, None))
        ret2, frame2 = (self._video2.read() if self._video2 else (False, None))
        if self._mix_mode:
            # Interleave: alternate frames from video1 and video2
            if self._current_video == 1 and ret1:
                frame = frame1
                self._current_video = 2
            elif self._current_video == 2 and ret2:
                frame = frame2
                self._current_video = 1
            elif ret1:
                frame = frame1
            elif ret2:
                frame = frame2
            else:
                self._handle_video_end()
                return
        else:
            if ret1:
                frame = frame1
            elif ret2:
                frame = frame2
            else:
                self._handle_video_end()
                return
        if frame is not None:
            self._show_frame(frame)
            self._update_fps()
        else:
            self._handle_video_end()

    def _show_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _update_fps(self):
        now = time.time()
        self._frame_count += 1
        self._frame_times.append(now)
        # Keep only the last 30 frames for FPS calculation
        if len(self._frame_times) > 30:
            self._frame_times.pop(0)
        if len(self._frame_times) > 1:
            self._fps = (len(self._frame_times) - 1) / (self._frame_times[-1] - self._frame_times[0])
        else:
            self._fps = 0.0

    def _handle_video_end(self):
        if self._loop:
            self._reset_videos()
        else:
            self.stop()