import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QProgressBar

class LoadingScreen(QWidget):
    loading_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading")
        self.setFixedSize(800, 480)
        self.progress = 0
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(300, 420, 200, 20)  # Adjusted position and size
        self.progress_bar.setValue(self.progress)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid black;
                border-radius: 5px;
                text-align: center;
                background-color: #A9A9A9;  /* Slightly dark grey */
            }
            QProgressBar::chunk {
                background-color: #7e909c;
                width: 20px;
            }
        """)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)
        self.show()

    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        if self.progress > 100:
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
        self.setStyleSheet("""
            QLabel {
                border: 3px solid gray;
                border-radius: 5px;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap():
            painter = QPainter(self)
            painter.setPen(QColor(255, 0, 0))
            
            # Calculate the top-left corner of the rectangle to center it
            label_width = self.width()
            label_height = self.height()
            x = (label_width - self.rect_width) // 2
            y = (label_height - self.rect_height) // 2
            
            painter.drawRect(x, y, self.rect_width, self.rect_height)
            painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Feed")
        self.setFixedSize(800, 480)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, 
                    x2: 1, y2: 1, 
                    stop: 0 #85C1E9, stop: 1 #2E86C1
                );
            }
            QPushButton {
                background-color: #7e909c;
                color: white;
                border: 2px solid black;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.loading_screen = LoadingScreen()
        self.loading_screen.loading_complete.connect(self.show_camera_feed)
        self.setCentralWidget(self.loading_screen)
        self.image_label = None

    def show_camera_feed(self):
        self.image_label = CameraLabel(self)
        self.image_label.setFixedSize(360, 360)
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setFixedSize(100, 40)
        
        # Center the image label and button
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.capture_button, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.thread = CameraThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
        self.image_label.update()  # Trigger paintEvent

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(360, 360, Qt.IgnoreAspectRatio)  # Ignore aspect ratio to fit the box
        return QPixmap.fromImage(p)

    def capture_image(self):
        frame = self.image_label.pixmap().toImage()
        frame.save("captured_image.jpg", "JPG")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())