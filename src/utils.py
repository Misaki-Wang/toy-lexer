import os

# Specify the paths for the DOT and image folders
DOT_FOLDER = '../res/dot'
IMAGE_FOLDER = '../res/img'

# Create directories if they don't exist
os.makedirs(DOT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def get_dot_file_path(filename):
    return os.path.join(DOT_FOLDER, filename)

def get_image_file_path(filename):
    return os.path.join(IMAGE_FOLDER, filename)
