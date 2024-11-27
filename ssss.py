import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QProgressBar

class LoadingScreen(QWidget):
    loading_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading")
        self.setFixedSize(800, 480)
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    x1: 0, y1: 0, 
                    x2: 1, y2: 1, 
                    stop: 0 #34495E, stop: 1 #2C3E50
                );
            }
        """)

        # Progress Bar
        self.progress = 0
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(300, 400, 200, 30)
        self.progress_bar.setValue(self.progress)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495E;
                border-radius: 10px;
                text-align: center;
                color: white;
                background-color: #2C3E50;
            }
            QProgressBar::chunk {
                background-color: #1ABC9C;
                border-radius: 10px;
            }
        """)

        # Loading Label
        self.loading_label = QLabel("Loading, please wait...", self)
        self.loading_label.setFont(QFont("Arial", 14))
        self.loading_label.setStyleSheet("color: white;")
        self.loading_label.setGeometry(310, 350, 300, 30)
        self.loading_label.setAlignment(Qt.AlignCenter)

        # Timer for Progress Bar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)
        self.show()

    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        if self.progress >= 100:
            self.timer.stop()
            self.loading_complete.emit()

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                self.change_pixmap_signal.emit(frame)

class CameraLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rect_width = 240
        self.rect_height = 240
        self.setStyleSheet("QLabel { border: 3px solid #1ABC9C; border-radius: 10px; }")

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap():
            painter = QPainter(self)
            painter.setPen(QColor(255, 255, 255))
            
            # Calculate rectangle position for centering
            x = (self.width() - self.rect_width) // 2
            y = (self.height() - self.rect_height) // 2
            
            painter.drawRect(x, y, self.rect_width, self.rect_height)
            painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Feed")
        self.setFixedSize(800, 480)
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(
                    x1: 0, y1: 0, 
                    x2: 1, y2: 1, 
                    stop: 0 #34495E, stop: 1 #2C3E50
                );
            }
        """)

        # Loading Screen
        self.loading_screen = LoadingScreen()
        self.loading_screen.loading_complete.connect(self.show_camera_feed)
        self.setCentralWidget(self.loading_screen)

    def show_camera_feed(self):
        self.image_label = CameraLabel(self)
        self.image_label.setFixedSize(360, 360)
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.setFont(QFont("Arial", 12))
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #1ABC9C;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
        """)
        self.capture_button.setFixedSize(120, 50)
        self.capture_button.clicked.connect(self.capture_image)

        # Layout
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.capture_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)

        # Fade-In Animation for Transition
        self.central_widget_animation(container)

        # Start Camera Thread
        self.thread = CameraThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def central_widget_animation(self, new_widget):
        animation = QPropertyAnimation(new_widget, b"windowOpacity")
        animation.setDuration(1000)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        self.setCentralWidget(new_widget)

    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(360, 360, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def capture_image(self):
        frame = self.image_label.pixmap().toImage()
        frame.save("captured_image.jpg", "JPG")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
