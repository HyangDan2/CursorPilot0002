from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QColor, Qt
import os
import numpy as np

class PatternDisplay(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet('background-color: black;')
        self.current_pixmap = None
        self.current_metadata = ''
        self.show_metadata = False
        self.is_fullscreen = False
        self._normal_geometry = None
        self.mouse_pos = None
        self.setMouseTracking(True)
        self.image_brightness_level = 100  # 0~100, 100이 100%
        self.image_brightness_max = 100
        self.image_brightness_min = 0
        self.original_image = None  # 원본 QImage
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

    def show_pattern(self, pattern_type, image_path=None, fullscreen=None, level=255):
        if fullscreen is not None:
            self.is_fullscreen = fullscreen
        width = self.width() if self.width() > 0 else 640
        height = self.height() if self.height() > 0 else 480
        if pattern_type == 'red':
            img = QImage(width, height, QImage.Format.Format_RGB32)
            img.fill(QColor(level, 0, 0))
            self.current_pixmap = QPixmap.fromImage(img)
            self.setPixmap(self.current_pixmap)
            self.current_metadata = f'Full Red Pattern (Level: {level})'
        elif pattern_type == 'green':
            img = QImage(width, height, QImage.Format.Format_RGB32)
            img.fill(QColor(0, level, 0))
            self.current_pixmap = QPixmap.fromImage(img)
            self.setPixmap(self.current_pixmap)
            self.current_metadata = f'Full Green Pattern (Level: {level})'
        elif pattern_type == 'blue':
            img = QImage(width, height, QImage.Format.Format_RGB32)
            img.fill(QColor(0, 0, level))
            self.current_pixmap = QPixmap.fromImage(img)
            self.setPixmap(self.current_pixmap)
            self.current_metadata = f'Full Blue Pattern (Level: {level})'
        elif pattern_type == 'white':
            img = QImage(width, height, QImage.Format.Format_RGB32)
            img.fill(QColor(level, level, level))
            self.current_pixmap = QPixmap.fromImage(img)
            self.setPixmap(self.current_pixmap)
            self.current_metadata = f'Full White Pattern (Level: {level})'
        elif pattern_type == 'black':
            img = QImage(width, height, QImage.Format.Format_RGB32)
            img.fill(QColor(0, 0, 0))
            self.current_pixmap = QPixmap.fromImage(img)
            self.setPixmap(self.current_pixmap)
            self.current_metadata = 'Full Black Pattern'
        elif pattern_type == 'image' and image_path:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.setText('Failed to load image')
                self.current_metadata = 'Invalid image file.'
                self.current_pixmap = None
                self.original_image = None
                self.image_brightness_level = 100
            else:
                self.current_pixmap = pixmap
                self.original_image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGB32)
                self.image_brightness_level = 100
                self.adjust_image_graylevel(0) # 이미지 로드 시 밝기 조정
                self.current_metadata = f"{image_path} (Brightness: {self.image_brightness_level}%)"
        else:
            self.setText('')
            self.current_metadata = ''
            self.current_pixmap = None
            self.original_image = None
            self.image_brightness_level = 100
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

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        if self.show_metadata:
            self.update()
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.show_metadata:
            from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
            painter = QPainter(self)
            # 오버레이 배경
            overlay_rect = self._overlay_rect()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(QColor(255,255,255,230)))
            painter.setPen(QPen(QColor(0,0,0), 2))
            painter.drawRect(overlay_rect)
            # 텍스트(메타데이터 + RGB)
            painter.setPen(QPen(QColor(0,0,0)))
            painter.setFont(QFont('Arial', 10))
            lines = [self.current_metadata]
            rgb_str = self._get_mouse_rgb_str()
            if rgb_str:
                lines.append(rgb_str)
            for i, line in enumerate(lines):
                painter.drawText(overlay_rect.adjusted(8, 8 + i*18, 0, 0), line)

    def _overlay_rect(self):
        # 오버레이 크기 동적 계산
        width = 220
        height = 40 if not self._get_mouse_rgb_str() else 60
        return self.rect().adjusted(8, 8, -self.width()+width+8, -self.height()+height+8)

    def _get_mouse_rgb_str(self):
        if self.current_pixmap and self.mouse_pos:
            img = self.current_pixmap.toImage()
            x, y = self.mouse_pos.x(), self.mouse_pos.y()
            if 0 <= x < img.width() and 0 <= y < img.height():
                c = img.pixelColor(x, y)
                return f"RGB: ({c.red()}, {c.green()}, {c.blue()})"
        return None

    def adjust_image_graylevel(self, delta):
        if not self.original_image:
            return
        new_level = self.image_brightness_level + delta
        # 보정: 1~9에서 +10이면 10, 91~99에서 +10이면 100, 91~99에서 -10이면 90, 1~9에서 -10이면 0
        if delta == 10:
            if 1 <= self.image_brightness_level < 10:
                new_level = 10
            elif 91 <= self.image_brightness_level < 100:
                new_level = 100
        elif delta == -10:
            if 91 <= self.image_brightness_level < 100:
                new_level = 90
            elif 1 <= self.image_brightness_level < 10:
                new_level = 0
        if new_level < self.image_brightness_min or new_level > self.image_brightness_max:
            return
        self.image_brightness_level = new_level
        factor = self.image_brightness_level / self.image_brightness_max
        arr = np.frombuffer(memoryview(self.original_image.bits()), dtype=np.uint8).reshape((self.original_image.height(), self.original_image.width(), 4)).astype(np.float32)
        arr[:, :, 0:3] = np.clip(arr[:, :, 0:3] * factor, 0, 255)
        arr = arr.astype(np.uint8)
        img2 = QImage(arr.data, self.original_image.width(), self.original_image.height(), QImage.Format.Format_RGB32)
        self.current_pixmap = QPixmap.fromImage(img2.copy())
        self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.current_metadata = f"{self.current_metadata.split(' (Brightness:')[0]} (Brightness: {self.image_brightness_level}%)"
        self.update() 