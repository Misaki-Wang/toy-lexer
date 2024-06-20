import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from src import regex, nfa_to_dfa, dfa_minimizer
from src.utils import get_dot_file_path, get_image_file_path, clear_directory, dump
import os

def generate_automata():
    regex_input = regex_entry.get()
    conversion_type = conversion_var.get()
    generate_dot = dot_var.get()
    generate_png = png_var.get()
    
    if not regex_input:
        messagebox.showerror("Input Error", "Please enter a regular expression.")
        return
    
    clear_directory('res/dot')
    clear_directory('res/img')

    nfa = regex.parse(regex_input)
    
    if conversion_type in ['minidfa', 'dfa', 'nfa']:
        if generate_dot:
            nfa_dot_path = get_dot_file_path('nfa.dot')
            dump(nfa, nfa_dot_path)
        
        if conversion_type in ['minidfa', 'dfa']:
            dfa = nfa_to_dfa.convert(nfa)
            if generate_dot:
                dfa_dot_path = get_dot_file_path('dfa.dot')
                dump(dfa, dfa_dot_path)
            
            if conversion_type == 'minidfa':
                mindfa = dfa_minimizer.minimize(dfa)
                if generate_dot:
                    mindfa_dot_path = get_dot_file_path('mindfa.dot')
                    dump(mindfa, mindfa_dot_path)
        
        if generate_png:
            for dot_file in os.listdir('res/dot'):
                if dot_file.endswith('.dot'):
                    dot_path = get_dot_file_path(dot_file)
                    png_path = get_image_file_path(dot_file.replace('.dot', '.png'))
                    os.system(f'dot -Tpng {dot_path} -o {png_path}')
                    
            display_images()

    messagebox.showinfo("Success", "Automata generated successfully!")

def display_images():
    for widget in image_frame.winfo_children():
        widget.destroy()

    if os.path.exists('res/img/nfa.png'):
        nfa_label = ttk.Label(image_frame, text="NFA:")
        nfa_label.grid(row=0, column=0, sticky=tk.W)
        nfa_img = Image.open('res/img/nfa.png')
        nfa_img = ImageTk.PhotoImage(nfa_img)
        nfa_img_label = tk.Label(image_frame, image=nfa_img)
        nfa_img_label.image = nfa_img
        nfa_img_label.grid(row=0, column=1, pady=5)

    if os.path.exists('res/img/dfa.png'):
        dfa_label = ttk.Label(image_frame, text="DFA:")
        dfa_label.grid(row=1, column=0, sticky=tk.W)
        dfa_img = Image.open('res/img/dfa.png')
        dfa_img = ImageTk.PhotoImage(dfa_img)
        dfa_img_label = tk.Label(image_frame, image=dfa_img)
        dfa_img_label.image = dfa_img
        dfa_img_label.grid(row=1, column=1, pady=5)

    if os.path.exists('res/img/mindfa.png'):
        mindfa_label = ttk.Label(image_frame, text="Minimized DFA:")
        mindfa_label.grid(row=2, column=0, sticky=tk.W)
        mindfa_img = Image.open('res/img/mindfa.png')
        mindfa_img = ImageTk.PhotoImage(mindfa_img)
        mindfa_img_label = tk.Label(image_frame, image=mindfa_img)
        mindfa_img_label.image = mindfa_img
        mindfa_img_label.grid(row=2, column=1, pady=5)

# Create the main window
root = tk.Tk()
root.title("Automata Generator")

# Create the main frame
mainframe = ttk.Frame(root, padding="10 10 20 20")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Add widgets
regex_label = ttk.Label(mainframe, text="Regular Expression:")
regex_label.grid(row=0, column=0, sticky=tk.W)
regex_entry = ttk.Entry(mainframe, width=30)
regex_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

conversion_label = ttk.Label(mainframe, text="Conversion Type:")
conversion_label.grid(row=1, column=0, sticky=tk.W)
conversion_var = tk.StringVar(value="minidfa")
conversion_combobox = ttk.Combobox(mainframe, textvariable=conversion_var, values=["minidfa", "dfa", "nfa"])
conversion_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

dot_var = tk.BooleanVar()
dot_checkbutton = ttk.Checkbutton(mainframe, text="Generate DOT files", variable=dot_var)
dot_checkbutton.grid(row=2, column=0, columnspan=2, sticky=tk.W)

png_var = tk.BooleanVar()
png_checkbutton = ttk.Checkbutton(mainframe, text="Generate PNG files", variable=png_var)
png_checkbutton.grid(row=3, column=0, columnspan=2, sticky=tk.W)

generate_button = ttk.Button(mainframe, text="Generate", command=generate_automata)
generate_button.grid(row=4, column=0, columnspan=2)

# Frame for displaying images
image_frame = ttk.Frame(root, padding="10 10 20 20")
image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configure resizing behavior
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)

# Start the GUI event loop
root.mainloop()
