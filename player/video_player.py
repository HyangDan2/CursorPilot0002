"""
VideoPlayer Widget for PySide6 Multimedia Player

This module provides a comprehensive video player widget that supports:
- Single video playback
- Interleaved mixing of two videos (frame-by-frame alternation)
- Real-time FPS calculation and display
- Video saving with automatic resizing
- Memory-efficient frame processing
- Playback controls (play, pause, stop, restart)
- Loop functionality

Author: Multimedia Player Team
Date: 2024
"""

import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
import time
import os
from typing import Optional, Tuple

class VideoPlayer(QWidget):
    """
    A PySide6 widget for video playback with mixing capabilities.
    
    This widget handles video loading, playback, and interleaved mixing
    of two videos. It uses OpenCV for video processing and PySide6 for
    GUI display. The widget is designed to be memory-efficient by
    processing only the current frame at a time.
    
    Attributes:
        _fps (float): Current calculated frames per second
        _playing (bool): Whether video is currently playing
        _paused (bool): Whether video is paused
        _loop (bool): Whether to loop the video
        _mix_mode (bool): Whether two videos are loaded for mixing
        _current_video (int): Current video source (1 or 2) for mixing
        _frame_count (int): Total frames processed
        _frame_times (list): List of frame timestamps for FPS calculation
    """
    
    # Signals for external communication
    video_loaded = Signal(str, str)  # video_path, video_name
    playback_started = Signal()
    playback_stopped = Signal()
    playback_paused = Signal()
    fps_updated = Signal(float)
    
    def __init__(self):
        """Initialize the VideoPlayer widget with default settings."""
        super().__init__()
        self._init_ui()
        self._init_variables()
        self._init_timer()
        
    def _init_ui(self):
        """Initialize the user interface components."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Video display area
        self.label = QLabel("Video Area - Load a video to start")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px dashed #555555;
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.label)
        
        # Progress bar for video playback
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def _init_variables(self):
        """Initialize internal variables and state."""
        self._fps = 0.0
        self._playing = False
        self._paused = False
        self._loop = False
        self._video1: Optional[cv2.VideoCapture] = None
        self._video2: Optional[cv2.VideoCapture] = None
        self._video1_path: Optional[str] = None
        self._video2_path: Optional[str] = None
        self._mix_mode = False
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._frame_times = []
        self._current_video = 1
        self._restart_flag = False
        
        # Video properties
        self._total_frames = 0
        self._current_frame = 0
        self._video_fps = 30.0
        self._video_duration = 0.0
        
    def _init_timer(self):
        """Initialize the QTimer for frame updates."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)
        
    def play(self) -> None:
        """
        Start or resume video playback.
        
        This method starts the video playback timer. If the video is already
        playing, it resumes from the paused state. The timer runs as fast as
        possible (0ms interval) to achieve smooth playback.
        """
        if not self._playing:
            self._playing = True
            self._paused = False
            self._timer.start(0)  # Run as fast as possible
            self.playback_started.emit()
        elif self._paused:
            self._paused = False
            self._timer.start(0)
            self.playback_started.emit()

    def stop(self) -> None:
        """
        Stop video playback and reset to the beginning.
        
        This method stops the video playback, resets the video to the beginning,
        and clears the display area. It also resets all internal counters and
        state variables.
        """
        self._playing = False
        self._paused = False
        self._timer.stop()
        self._reset_videos()
        self.label.setText("Video Area - Load a video to start")
        self.progress_bar.setVisible(False)
        self.playback_stopped.emit()

    def restart(self) -> None:
        """
        Restart video playback from the beginning.
        
        This method stops the current playback and immediately starts it again
        from the beginning of the video.
        """
        self._restart_flag = True
        self.stop()
        self.play()

    def pause(self) -> None:
        """
        Pause video playback.
        
        This method pauses the video playback by stopping the timer. The video
        can be resumed by calling play() again.
        """
        self._paused = True
        self._timer.stop()
        self.playback_paused.emit()

    def load_video1(self, path: str) -> bool:
        """
        Load the first video file.
        
        Args:
            path (str): Path to the video file
            
        Returns:
            bool: True if video loaded successfully, False otherwise
            
        This method loads the first video file using OpenCV. It releases any
        previously loaded video and updates the internal state accordingly.
        """
        try:
            if not os.path.exists(path):
                return False
                
            if self._video1:
                self._video1.release()
                
            self._video1 = cv2.VideoCapture(path)
            if not self._video1.isOpened():
                return False
                
            self._video1_path = path
            self._update_video_properties()
            self._check_mix_mode()
            self._reset_videos()
            
            video_name = os.path.basename(path)
            self.video_loaded.emit(path, video_name)
            return True
            
        except Exception as e:
            print(f"Error loading video1: {e}")
            return False

    def load_video2(self, path: str) -> bool:
        """
        Load the second video file.
        
        Args:
            path (str): Path to the video file
            
        Returns:
            bool: True if video loaded successfully, False otherwise
            
        This method loads the second video file using OpenCV. It releases any
        previously loaded video and updates the internal state accordingly.
        """
        try:
            if not os.path.exists(path):
                return False
                
            if self._video2:
                self._video2.release()
                
            self._video2 = cv2.VideoCapture(path)
            if not self._video2.isOpened():
                return False
                
            self._video2_path = path
            self._update_video_properties()
            self._check_mix_mode()
            self._reset_videos()
            
            video_name = os.path.basename(path)
            self.video_loaded.emit(path, video_name)
            return True
            
        except Exception as e:
            print(f"Error loading video2: {e}")
            return False

    def save_mixed_video(self, path: str) -> bool:
        """
        Save the interleaved mixed video to the specified file path.
        
        Args:
            path (str): Output file path for the mixed video
            
        Returns:
            bool: True if video saved successfully, False otherwise
            
        This method creates a new video file by interleaving frames from
        two loaded videos. It handles different video sizes by automatically
        resizing frames to match the first video's dimensions.
        """
        if not (self._video1_path and self._video2_path):
            return False
            
        try:
            cap1 = cv2.VideoCapture(self._video1_path)
            cap2 = cv2.VideoCapture(self._video2_path)
            
            if not cap1.isOpened() or not cap2.isOpened():
                return False
                
            # Get video properties from first video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = cap1.get(cv2.CAP_PROP_FPS) or 30
            width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Check if second video needs resizing
            width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
            height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
            resize2 = (width2 != width or height2 != height)
            
            # Create video writer
            out = cv2.VideoWriter(path, fourcc, fps, (width, height))
            if not out.isOpened():
                return False
                
            # Read first frames
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            current = 1
            frame_count = 0
            
            # Interleave frames
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
                    
                frame_count += 1
                
            # Clean up
            cap1.release()
            cap2.release()
            out.release()
            
            return True
            
        except Exception as e:
            print(f"Error saving mixed video: {e}")
            return False

    def get_fps(self) -> float:
        """
        Return the current calculated FPS.
        
        Returns:
            float: Current frames per second
        """
        return self._fps

    def set_loop(self, loop: bool) -> None:
        """
        Enable or disable looping playback.
        
        Args:
            loop (bool): True to enable looping, False to disable
        """
        self._loop = loop

    def _reset_videos(self) -> None:
        """
        Reset video captures to the beginning.
        
        This method reopens the video files and resets all internal counters
        and state variables to prepare for playback from the beginning.
        """
        if self._video1_path:
            if self._video1:
                self._video1.release()
            self._video1 = cv2.VideoCapture(self._video1_path)
            
        if self._video2_path:
            if self._video2:
                self._video2.release()
            self._video2 = cv2.VideoCapture(self._video2_path)
            
        self._frame_count = 0
        self._current_frame = 0
        self._last_fps_time = time.time()
        self._frame_times = []
        self._current_video = 1
        
        # Update progress bar
        if self._total_frames > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(self._total_frames)
            self.progress_bar.setValue(0)

    def _check_mix_mode(self) -> None:
        """
        Check if both videos are loaded and enable mix mode.
        
        This method determines whether both videos are loaded and enables
        the interleaved mixing mode accordingly.
        """
        self._mix_mode = (self._video1_path is not None and 
                         self._video2_path is not None)

    def _update_video_properties(self) -> None:
        """
        Update video properties like total frames, FPS, and duration.
        
        This method reads video properties from the loaded videos and
        updates internal variables for progress tracking and timing.
        """
        if self._video1 and self._video1.isOpened():
            self._total_frames = int(self._video1.get(cv2.CAP_PROP_FRAME_COUNT))
            self._video_fps = self._video1.get(cv2.CAP_PROP_FPS) or 30
            self._video_duration = self._total_frames / self._video_fps

    def _next_frame(self) -> None:
        """
        Process the next frame for display.
        
        This method reads frames from the video sources, handles interleaved
        mixing, and displays the current frame. It also updates FPS calculation
        and progress tracking.
        """
        if not self._playing or self._paused:
            return
            
        frame = None
        ret1, frame1 = (self._video1.read() if self._video1 else (False, None))
        ret2, frame2 = (self._video2.read() if self._video2 else (False, None))
        
        # Interleaved mixing logic
        if self._mix_mode:
            # Alternate between video1 and video2 frames
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
            # Single video playback
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
            self._update_progress()
        else:
            self._handle_video_end()

    def _show_frame(self, frame: np.ndarray) -> None:
        """
        Display the frame in the GUI.
        
        Args:
            frame (np.ndarray): OpenCV frame to display
            
        This method converts the OpenCV BGR frame to RGB, creates a QImage,
        converts it to QPixmap, and displays it in the QLabel with proper
        scaling to maintain aspect ratio.
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # Create QImage from numpy array
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, 
                         QImage.Format.Format_RGB888)
            
            # Convert to QPixmap and scale
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(
                self.label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"Error displaying frame: {e}")

    def _update_fps(self) -> None:
        """
        Update FPS calculation based on recent frame times.
        
        This method calculates the current FPS based on the timing of
        recent frames. It maintains a rolling window of the last 30
        frame times for accurate FPS calculation.
        """
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
            
        self.fps_updated.emit(self._fps)

    def _update_progress(self) -> None:
        """
        Update the progress bar with current playback position.
        """
        if self._total_frames > 0:
            self._current_frame += 1
            self.progress_bar.setValue(self._current_frame)

    def _handle_video_end(self) -> None:
        """
        Handle video end - either loop or stop playback.
        
        This method is called when a video reaches its end. If looping
        is enabled, it resets the video to the beginning. Otherwise,
        it stops playback.
        """
        if self._loop:
            self._reset_videos()
        else:
            self.stop()