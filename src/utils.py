import os
import shutil

# Specify the paths for the DOT and image folders
DOT_FOLDER = './res/dot'
IMAGE_FOLDER = './res/img'

# Create directories if they don't exist
os.makedirs(DOT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def get_dot_file_path(filename):
    return os.path.join(DOT_FOLDER, filename)

def get_image_file_path(filename):
    return os.path.join(IMAGE_FOLDER, filename)

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def dump(automaton, filename):
    with open(filename, 'w') as file:
        file.write('digraph G {\n')
        file.write('rankdir=LR;\n')  # Left to right layout
        file.write('node [shape=circle, fontname="Helvetica", fontsize=12];\n')
        for state in automaton.states:
            shape = 'doublecircle' if hasattr(automaton, 'final_states') and state in automaton.final_states else 'circle'
            file.write(f'{state} [shape={shape}];\n')
        for (start_state, symbol), end_states in automaton.transitions.items():
            for end_state in end_states:
                file.write(f'{start_state} -> {end_state} [label="{symbol}"];\n')
        file.write('}\n')
