import sys
import os
import pandas as pd
from diffusers import DiffusionPipeline
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QPushButton, QLineEdit, QMessageBox)
from PyQt5.QtGui import QPixmap
from PIL import Image

class ImageRatingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.image_data = []  # List to store prompts and image paths
        self.current_index = 0  # To track the current image displayed
        
        self.initUI()
        self.load_images()

    def initUI(self):
        self.setWindowTitle('Image Rating Application')

        # Layout setup
        layout = QVBoxLayout()

        # Prompt display label
        self.prompt_label = QLabel(self)
        layout.addWidget(self.prompt_label)

        # Image display label
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # Quality input field
        self.quality_input = QLineEdit(self)
        self.quality_input.setPlaceholderText('Enter image quality (1-10)')
        layout.addWidget(self.quality_input)

        # Buttons for saving quality and navigating images
        save_button = QPushButton('Save Quality', self)
        save_button.clicked.connect(self.save_quality)
        layout.addWidget(save_button)

        next_button = QPushButton('Next Image', self)
        next_button.clicked.connect(self.next_image)
        layout.addWidget(next_button)

        self.setLayout(layout)

    def load_images(self):
        # Load images and prompts from CSV file
        df = pd.read_csv('generated_images.csv')
        self.image_data = df.to_dict(orient='records')
        
    def display_image(self):
        if self.image_data and self.current_index < len(self.image_data):
            current_entry = self.image_data[self.current_index]
            prompt = current_entry['Prompt']
            image_path = current_entry['Image Path']
            
            # Display prompt and image
            self.prompt_label.setText(prompt)
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(400, 400, aspectRatioMode=True))

    def save_quality(self):
        quality = self.quality_input.text()
        
        if not quality:
            QMessageBox.warning(self, "Input Error", "Please enter a quality rating before saving.")
            return
        
        try:
            quality_value = int(quality)
            if quality_value < 1 or quality_value > 10:
                raise ValueError("Quality must be between 1 and 10.")
            
            current_entry = self.image_data[self.current_index]
            prompt_path = current_entry['Image Path']
            data = {'Prompt': current_entry['Prompt'], 'Image Path': prompt_path, 'Quality': quality}
            
            # Append to CSV file or create it if it doesn't exist
            df = pd.DataFrame([data])
            df.to_csv('image_ratings.csv', mode='a', header=not pd.io.common.file_exists('image_ratings.csv'), index=False)

            QMessageBox.information(self, "Success", "Quality rating saved successfully.")

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def next_image(self):
        if not self.quality_input.text():
            QMessageBox.warning(self, "Input Error", "Please enter a quality rating before proceeding to the next image.")
            return
        
        quality_value = int(self.quality_input.text())
        
        if quality_value < 1 or quality_value > 10:
            QMessageBox.warning(self, "Input Error", "Quality must be between 1 and 10.")
            return
        
        if self.image_data:
            self.current_index += 1
            if self.current_index >= len(self.image_data):
                self.prompt_label.setText("No more images.")
                self.image_label.clear()
                return
            
            # Clear the input field for the next image
            self.quality_input.clear()
            
            # Display the next image
            self.display_image()

def generate_images(prompts):
    # Load the diffusion model
    pipe = DiffusionPipeline.from_pretrained("stabilityai/sdxl-turbo")
    pipe.to("cpu")

    output_dir = 'generated_images'
    os.makedirs(output_dir, exist_ok=True)

    image_data = []

    for i, prompt in enumerate(prompts):
        image = pipe(prompt).images[0]
        
        # Define the image path
        image_path = os.path.join(output_dir, f'image_{i + 1}.png')
        
        # Save the image
        image.save(image_path)
        
        # Append prompt and image path to the list
        image_data.append({'Prompt': prompt, 'Image Path': image_path})

    # Create a DataFrame and save it to CSV
    df = pd.DataFrame(image_data)
    df.to_csv('generated_images.csv', index=False)

if __name__ == '__main__':
    prompts = [
        "A gothic cathedral illuminated by moonlight.",
        "A crystal-clear river running through a tropical jungle.",
        "A futuristic city with glowing skyscrapers surrounded by greenery.",
    ]

    generate_images(prompts)  # Generate images before starting the app

    app = QApplication(sys.argv)
    ex = ImageRatingApp()
    
    ex.resize(500, 500)
    ex.show()
    
    # Display the first image initially
    ex.display_image()
    
    sys.exit(app.exec_())