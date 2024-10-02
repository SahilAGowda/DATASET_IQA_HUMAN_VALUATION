import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QPushButton, QLineEdit, QFileDialog)
from PyQt5.QtGui import QPixmap

class ImageQualityApp(QWidget):
    def __init__(self):
        super().__init__()
        self.image_paths = []  # List to store image paths
        self.current_index = 0  # To track the current image displayed
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Quality Rating')

        # Layout setup
        layout = QVBoxLayout()

        # Image display label
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # Quality input field
        self.quality_input = QLineEdit(self)
        self.quality_input.setPlaceholderText('Enter image quality (1-10)')
        layout.addWidget(self.quality_input)

        # Buttons for loading images and saving quality
        load_button = QPushButton('Load Image', self)
        load_button.clicked.connect(self.load_image)
        layout.addWidget(load_button)

        save_button = QPushButton('Save Quality', self)
        save_button.clicked.connect(self.save_quality)
        layout.addWidget(save_button)

        next_button = QPushButton('Next Image', self)
        next_button.clicked.connect(self.next_image)
        layout.addWidget(next_button)

        self.setLayout(layout)

    def load_image(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", 
                                                 "Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)", options=options)
        if files:
            self.image_paths = files
            self.current_index = 0
            self.display_image()

    def display_image(self):
        if self.image_paths:
            pixmap = QPixmap(self.image_paths[self.current_index])
            self.image_label.setPixmap(pixmap.scaled(400, 400, aspectRatioMode=True))

    def save_quality(self):
        quality = self.quality_input.text()
        if quality and self.image_paths:
            image_path = self.image_paths[self.current_index]
            data = {'Image Path': [image_path], 'Quality': [quality]}
            df = pd.DataFrame(data)

            # Append to CSV file or create it if it doesn't exist
            df.to_csv('image_quality_ratings.csv', mode='a', header=not pd.io.common.file_exists('image_quality_ratings.csv'), index=False)

    def next_image(self):
        if self.image_paths:
            self.current_index += 1
            if self.current_index >= len(self.image_paths):
                self.current_index = 0  # Loop back to the first image
            self.display_image()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageQualityApp()
    ex.resize(500, 500)
    ex.show()
    sys.exit(app.exec_())