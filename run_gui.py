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

    images = []
    labels = []

    if os.path.exists('res/img/nfa.png'):
        nfa_label = ttk.Label(image_frame, text="NFA:", style="TLabel")
        nfa_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        labels.append(nfa_label)
        nfa_img = Image.open('res/img/nfa.png')
        nfa_img = ImageTk.PhotoImage(nfa_img)
        nfa_img_label = tk.Label(image_frame, image=nfa_img)
        nfa_img_label.image = nfa_img
        nfa_img_label.grid(row=0, column=1, padx=5, pady=5)
        images.append(nfa_img_label)

    if os.path.exists('res/img/dfa.png'):
        dfa_label = ttk.Label(image_frame, text="DFA:", style="TLabel")
        dfa_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        labels.append(dfa_label)
        dfa_img = Image.open('res/img/dfa.png')
        dfa_img = ImageTk.PhotoImage(dfa_img)
        dfa_img_label = tk.Label(image_frame, image=dfa_img)
        dfa_img_label.image = dfa_img
        dfa_img_label.grid(row=1, column=1, padx=5, pady=5)
        images.append(dfa_img_label)

    if os.path.exists('res/img/mindfa.png'):
        mindfa_label = ttk.Label(image_frame, text="Minimized DFA:", style="TLabel")
        mindfa_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        labels.append(mindfa_label)
        mindfa_img = Image.open('res/img/mindfa.png')
        mindfa_img = ImageTk.PhotoImage(mindfa_img)
        mindfa_img_label = tk.Label(image_frame, image=mindfa_img)
        mindfa_img_label.image = mindfa_img
        mindfa_img_label.grid(row=2, column=1, padx=5, pady=5)
        images.append(mindfa_img_label)

    for label, img in zip(labels, images):
        label.grid(row=labels.index(label), column=0, sticky=tk.W, padx=5, pady=5)
        img.grid(row=images.index(img), column=1, padx=5, pady=5)

# Create the main window
root = tk.Tk()
root.title("Automata Generator")

# Style configuration
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc", borderwidth=1, focusthickness=3, focuscolor='none')
style.map("TButton", background=[('active', '#005f87'), ('!active', '#ccc')], relief=[('pressed', 'groove'), ('!pressed', 'flat')])

style.configure("TLabel", font=("Helvetica", 12), padding=5)

# Create the main frame
mainframe = ttk.Frame(root, padding="10 10 20 20")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Add widgets
regex_label = ttk.Label(mainframe, text="Regular Expression:", style="TLabel")
regex_label.grid(row=0, column=0, sticky=tk.W)
regex_entry = ttk.Entry(mainframe, width=30)
regex_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

conversion_label = ttk.Label(mainframe, text="Conversion Type:", style="TLabel")
conversion_label.grid(row=1, column=0, sticky=tk.W)
conversion_var = tk.StringVar(value="minidfa")
conversion_combobox = ttk.Combobox(mainframe, textvariable=conversion_var, values=["minidfa", "dfa", "nfa"])
conversion_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

dot_var = tk.BooleanVar()
dot_checkbutton = ttk.Checkbutton(mainframe, text="Generate DOT files", variable=dot_var, style="TButton")
dot_checkbutton.grid(row=2, column=0, columnspan=2, sticky=tk.W)

png_var = tk.BooleanVar()
png_checkbutton = ttk.Checkbutton(mainframe, text="Generate PNG files", variable=png_var, style="TButton")
png_checkbutton.grid(row=3, column=0, columnspan=2, sticky=tk.W)

generate_button = ttk.Button(mainframe, text="Generate", command=generate_automata, style="TButton")
generate_button.grid(row=4, column=0, columnspan=2, pady=10)

# Create a canvas with scrollbars for displaying images
canvas = tk.Canvas(root, width=1200, height=600)
scroll_y = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
image_frame = ttk.Frame(canvas, padding="10 10 20 20")

image_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=image_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

canvas.grid(row=1, column=0, sticky="nsew")
scroll_y.grid(row=1, column=1, sticky="ns")
scroll_x.grid(row=2, column=0, sticky="ew")

# Configure resizing behavior
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)

# Start the GUI event loop
root.mainloop()
