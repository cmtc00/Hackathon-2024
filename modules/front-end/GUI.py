import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QMessageBox
from face_reconize2 import run_face_recognition
import subprocess


class LoadingScreen(QWidget):
    loading_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading")
        self.setFixedSize(800, 480)

        layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("Untitled-2_copy.png")
        self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        layout.addWidget(self.image_label)

        self.text_label = QLabel("Sania", self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("color: green; font-size: 30px; font-weight: bold;")
        layout.addWidget(self.text_label)

        self.progress = 0
        self.progress_bar = QProgressBar(self)
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
                background-color: #44B52C;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)

        self.setLayout(layout)

    def update_progress(self):
        self.progress += 3
        self.progress_bar.setValue(self.progress)
        if self.progress > 100:
            self.timer.stop()
            self.loading_complete.emit()

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        try:
            for frame in run_face_recognition():
                if frame is not None:
                    self.change_pixmap_signal.emit(frame)
        except Exception as e:
            print(f"Error in CameraThread: {e}")

class DataThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        try:
            for frame in run_create_data():
                if frame is not None:
                    self.change_pixmap_signal.emit(frame)
        except Exception as e:
            print(f"Error in CameraThread: {e}")


class MenuScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 480)
        self.setStyleSheet("background-color: #2C3E50;")

        welcome_label = QLabel("Welcome Back")
        welcome_label.setFont(QFont("Arial", 20))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            color: #44B52C; 
            font-weight: bold; 
            background-color: transparent;
            border-radius: 10px;
            padding: 10px;
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(welcome_label)
        self.login_button = QPushButton("Login", self)
        self.register_button = QPushButton("Register", self)
        self.camera_button = QPushButton("Camera", self)

        button_style = """
            QPushButton {
                background-color: #44B52C;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #30801F; /* Darker shade on hover */
            }
            QPushButton:pressed {
                background-color: #0E6655; /* Even darker shade when pressed */
            }
        """
        self.login_button.setStyleSheet(button_style)
        self.register_button.setStyleSheet(button_style)
        self.camera_button.setStyleSheet(button_style)

        self.login_button.setFixedSize(200, 60)
        self.register_button.setFixedSize(200, 60)
        self.camera_button.setFixedSize(200, 60)

        layout.addStretch()
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.camera_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)


class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        try:
            for frame in run_face_recognition():
                if frame is not None:
                    self.change_pixmap_signal.emit(frame)
        except Exception as e:
            print(f"Error in CameraThread: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")
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

        self.loading_screen = LoadingScreen()
        self.loading_screen.loading_complete.connect(self.show_menu_screen)
        self.setCentralWidget(self.loading_screen)

    def show_menu_screen(self):
        self.menu_screen = MenuScreen()
        self.setCentralWidget(self.menu_screen)

        self.menu_screen.register_button.clicked.connect(self.show_register_screen)
        self.menu_screen.login_button.clicked.connect(self.show_login_screen)
        self.menu_screen.camera_button.clicked.connect(self.show_camera_feed)

    def show_login_screen(self):
        self.show_camera_feed()

    def show_register_screen(self):
        dialog = RegisterDialog(self)
        if dialog.exec_():  # If the dialog is accepted
            self.execute_create_data(dialog.name, dialog.code)

    def show_camera_feed(self):
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(640, 480)
        layout = QVBoxLayout()
        layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.camera_thread = CameraThread()
        self.camera_thread.change_pixmap_signal.connect(self.update_image)
        self.camera_thread.start()

    def update_image(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def execute_create_data(self, name, code):
        processing_label = QLabel("Processing registration...")
        processing_label.setAlignment(Qt.AlignCenter)
        processing_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        self.setCentralWidget(processing_label)

        try:
            subprocess.run(["python", "create_data.py", name, code], check=True)
            QMessageBox.information(self, "Success", "Registration completed successfully!")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {e}")
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "create_data.py not found.")
        finally:
            self.show_menu_screen()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #2C3E50; color: white;")

        layout = QVBoxLayout()
        self.name_label = QLabel("Enter your name:")
        layout.addWidget(self.name_label)
        self.name_label.setFont(QFont("Arial", 12))
        self.name_label.setStyleSheet("""
            color: #FFFFFF; 
            font-weight: bold; 
            background-color: transparent;
            border-radius: 10px;
            padding: 10px;
        """)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name here")  # Placeholder text
        self.name_input.setMaxLength(10)  # Limit to 10 characters
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #44B52C;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #FFFFFF;
                background-color: #34495E;
            }
            QLineEdit:focus {
                border: 2px solid #1ABC9C;
            }
        """)
        layout.addWidget(self.name_input)


        self.code_label = QLabel("Enter your code:")
        layout.addWidget(self.code_label)
        self.code_label.setFont(QFont("Arial", 12))
        self.code_label.setStyleSheet("""
            color: #FFFFFF; 
            font-weight: bold; 
            background-color: transparent;
            border-radius: 10px;
            padding: 10px;
        """)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter your code here")  # Placeholder text
        self.code_input.setMaxLength(10)  # Limit to 10 characters
        self.code_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #44B52C;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #FFFFFF;
                background-color: #34495E;
            }
            QLineEdit:focus {
                border: 2px solid #1ABC9C;
            }
        """)
        layout.addWidget(self.code_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedSize(120, 40)  # Set button size
        self.submit_button.setCursor(Qt.PointingHandCursor)  # Change the cursor to a hand pointer
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #44B52C;  /* Background color */
                color: white;              /* Text color */
                border-radius: 10px;       /* Rounded corners */
                padding: 8px;              /* Padding around the text */
                font-size: 16px;           /* Font size */
                font-weight: bold;         /* Bold font */
            }
            QPushButton:hover {
                background-color: #30801F; /* Darker shade on hover */
            }
            QPushButton:pressed {
                background-color: #0E6655; /* Even darker shade when pressed */
            }
        """)
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)  # Center the button

        self.setLayout(layout)

    def on_submit(self):
        self.name = self.name_input.text().strip()
        self.code = self.code_input.text().strip()

        if not self.name or not self.code:
            QMessageBox.warning(self, "Input Error", "Please fill in both fields.")
            return

        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
