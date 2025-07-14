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
        """Start or resume video playback."""
        if not self._playing:
            self._playing = True
            self._paused = False
            self._timer.start(0)
        elif self._paused:
            self._paused = False
            self._timer.start(0)

    def stop(self):
        """Stop video playback and reset to the beginning."""
        self._playing = False
        self._paused = False
        self._timer.stop()
        self._reset_videos()
        self.label.setText("Video Area")

    def restart(self):
        """Restart video playback from the beginning."""
        self._restart_flag = True
        self.stop()
        self.play()

    def pause(self):
        """Pause video playback."""
        self._paused = True
        self._timer.stop()

    def load_video1(self, path):
        """Load the first video file."""
        if self._video1:
            self._video1.release()
        self._video1 = cv2.VideoCapture(path)
        self._video1_path = path
        self._check_mix_mode()
        self._reset_videos()

    def load_video2(self, path):
        """Load the second video file."""
        if self._video2:
            self._video2.release()
        self._video2 = cv2.VideoCapture(path)
        self._video2_path = path
        self._check_mix_mode()
        self._reset_videos()

    def save_mixed_video(self, path):
        """Save the interleaved mixed video to the specified file path."""
        if not (self._video1_path and self._video2_path):
            return False
        cap1 = cv2.VideoCapture(self._video1_path)
        cap2 = cv2.VideoCapture(self._video2_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap1.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # If video2 has different size, resize frames
        width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width2 != width or height2 != height:
            resize2 = True
        else:
            resize2 = False
        out = cv2.VideoWriter(path, fourcc, fps, (width, height))
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        current = 1
        while ret1 or ret2:
            if current == 1 and ret1:
                out.write(frame1)
                ret1, frame1 = cap1.read()
                current = 2
            elif current == 2 and ret2:
                if resize2 and frame2 is not None:
                    frame2 = cv2.resize(frame2, (width, height))
                out.write(frame2)
                ret2, frame2 = cap2.read()
                current = 1
            elif ret1:
                out.write(frame1)
                ret1, frame1 = cap1.read()
            elif ret2:
                if resize2 and frame2 is not None:
                    frame2 = cv2.resize(frame2, (width, height))
                out.write(frame2)
                ret2, frame2 = cap2.read()
        cap1.release()
        cap2.release()
        out.release()
        return True

    def get_fps(self):
        """Return the current calculated FPS."""
        return self._fps

    def set_loop(self, loop: bool):
        """Enable or disable looping playback."""
        self._loop = loop

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