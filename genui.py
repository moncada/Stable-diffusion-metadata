#!/usr/bin/python3
import os
import platform
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, Scrollbar
from PIL import Image, ImageTk
import threading
from concurrent.futures import ThreadPoolExecutor
from tkinter.constants import *
from tkinter import ttk



class FirsttryApp():
    def __init__(self, master=None):
        # build ui

        self.tag_sort = None
        self.tag_summary = set()
        self.current_image_file = None
        self.tk_image = None
        self.current_index = 0
        self.size_image_list = None
        self.image_files = []
        self.default_dir = None
        self.folder_path = None

        self.toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        screen_width = self.toplevel1.winfo_screenwidth()
        screen_height = self.toplevel1.winfo_screenheight()
        width = int(screen_width * 0.9)
        height = int(screen_height * 0.9)

        self.toplevel1.geometry(f"{width}x{height}")
        self.toplevel1.maxsize(screen_width, screen_height)
        self.toplevel1.title("ML image manipulation")

        self.notebook = ttk.Notebook(self.toplevel1)
        self.notebook.configure(height=height, width=width)
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Write tags")

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Tag summary")

        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Excluded tags")
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="Replace tag")
        # Create the StringVar to hold the selected option



        self.panedwindow1 = tk.PanedWindow(self.tab1, orient="horizontal")
        self.panedwindow1.pack(fill='both', expand=True)

        self.image = tk.Canvas(self.panedwindow1)
        self.image.configure(
            background="#000000",
            insertbackground="#000000",
            insertborderwidth=5,
            highlightthickness=0,
            highlightbackground="black")

        self.image.place(anchor="nw", height=height, width=width*0.5)

        self.TextFile = tk.Text(self.panedwindow1)
        self.TextFile.configure()
        self.TextFile.place(
            anchor="nw",
            bordermode="inside",
            height=height*0.95,
            relx=0.48,
            rely=0.05,
            width=width*0.55,
            x=0,
            y=0)
        self.TextFile.bind("<FocusOut>", self.save_text)
        self.TextFile.bind("<Leave>", self.save_text)
        self.tag_field = tk.Text(self.tab2)
        # self.tag_field.place(anchor="center", bordermode="inside",width=1800,height=1000,relx=0.3,rely=0.3,x=0,y=0)
        self.scrollbar = Scrollbar(self.tag_field, command=self.tag_field.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.tag_field.config(yscrollcommand=self.scrollbar.set)
        self.tag_field.pack(side=LEFT, fill=BOTH, expand=True)
        self.Picture_number = tk.Label(self.tab1)
        self.Picture_number.configure(text=f'Picture number:{self.current_index}')
        self.Picture_number.place(relx=0.55, rely=0.02)
        self.tag_instruct = ttk.Label(self.tab3)
        self.tag_instruct.configure(
            text="Tags needs to be seperated by , .These tags are removed from all text files in current working directory")
        self.tag_instruct.pack()
        self.exclude_text = tk.Text(self.tab3)
        self.exclude_text.pack()

        self.pict_input = tk.Entry(self.tab1)
        self.pict_input.place(anchor="nw", relx=0.7, rely=0.02, width=50, x=0, y=0)

        self.label2 = tk.Label(self.tab1)
        size_image_list = tk.IntVar(value=self.size_image_list)
        self.label2.place(anchor="nw", relx=0.73, rely=0.02, x=0, y=0)
        self.summary = ttk.Button(self.tab2)
        self.summary.configure(text='Update summary', command=self.read_files_display_variables)
        # self.summary.place(anchor="nw", relx=0.79, rely=0.02, x=0, y=0)
        self.summary.pack()
        self.tag_nr_label = ttk.Label(self.tab2)
        self.tag_nr_label.configure(text="Total tags: 0")
        self.tag_nr_label.pack()

        self.jump = ttk.Button(self.tab1)
        self.jump.configure(text='Jump', command=self.jump_to_picture)
        self.jump.place(anchor="nw", relx=0.79, rely=0.02, x=0, y=0)
        self.load_tag_button = ttk.Button(self.tab3)
        self.load_tag_button.configure(text="Load from file", command=self.load_excluded_tags)
        self.load_tag_button.pack()
        self.save_tag_button = ttk.Button(self.tab3)
        self.save_tag_button.configure(text="Save to file", command=self.save_exluded_tags)
        self.save_tag_button.pack()
        self.purge_tags = ttk.Button(self.tab3)
        self.purge_tags.configure(text="Remove from tag pool", command=self.purge_tags_exec)
        self.purge_tags.pack()
        # pack the notebook widget and main window
        self.notebook.pack(fill='both', expand=True)
        self.mainwindow = self.toplevel1
        self.notebook.bind("<<NotebookTabChanged>>", self.specific_tab_activated)
        self.mainwindow.bind("<Prior>", self.decrease_index_one)
        self.mainwindow.bind("<Next>", self.increase_index_one)
        self.tab4row1 = ttk.Frame(self.tab4)
        self.tab4row1.pack(side="top",fill="x")
        self.tab4labelinput = ttk.Label(self.tab4row1, text="Tag to change",width=20)
        self.tab4labelinput.pack(side="left")
        self.tab4labeloutput = ttk.Label(self.tab4row1, text="Tag to change to",width=20)
        self.tab4labeloutput.pack(side="left")
        self.tab4row2 = ttk.Frame(self.tab4)
        self.tab4row2.pack(side="top",fill="x")
        self.taginputtext = tk.Text(self.tab4row2, height=1, width=19)
        self.taginputtext.bind("<KeyRelease>", self.update_text_color_confirm)
        self.taginputtext.pack(side="left")
        self.tagouttext = tk.Text(self.tab4row2, height=1, width=20)
        self.tagouttext.bind("<KeyRelease>", self.update_text_color_exists)
        self.tagouttext.pack(side="left")
        self.tab4button = ttk.Button(self.tab4row2, text="Replace", command=self.replace_tag)
        self.tab4button.pack(side="left")

    def run(self):

        self.select_folder()
        self.update_image()
        self.mainwindow.mainloop()

    def update_image(self):
        if not self.image_files:
            return
        img_file = self.image_files[self.current_index]

        if img_file == self.current_image_file:
            # no need to update the canvas
            pass
        else:
            # update the canvas with the new image
            image = Image.open(os.path.join(self.folder_path, img_file))
            canvas_width = self.image.winfo_width()
            canvas_height = self.image.winfo_height()
            image_width, image_height = image.size
            width_ratio = canvas_width / image_width
            height_ratio = canvas_height / image_height

            # choose the smaller ratio to maintain aspect ratio
            scale_ratio = min(width_ratio, height_ratio)

            # scale the image and display on the canvas
            new_width = int(image_width * scale_ratio)
            new_height = int(image_height * scale_ratio)
            resized_image = image.resize((new_width, new_height))
            tk_image = ImageTk.PhotoImage(resized_image)
            self.tk_image = ImageTk.PhotoImage(resized_image)
            self.image.create_image(0, 0, image=self.tk_image, anchor="nw")
            self.current_image_file = img_file
            self.Picture_number.config(text=f'Picture number:{self.current_index}')
            self.update_text_file()
        self.mainwindow.after(20, self.update_image)
        # self.mainwindow.after(20, self.update_text_file)

    def jump_to_picture(self):
        self.current_index = int(self.pict_input.get())
        self.save_text()

    def select_folder(self):
        system = platform.system()
        if system == 'Windows':
            self.default_dir = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        elif system == 'Linux':
            self.default_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        elif system == 'Darwin':
            self.default_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            self.default_dir = os.getcwd()

        self.folder_path = filedialog.askdirectory(initialdir=self.default_dir)
        self.image_files = [f for f in os.listdir(self.folder_path) if
                            f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]
        self.image_files.sort()

    def update_text_file(self):
        img_file = self.image_files[self.current_index]
        text_file_name = os.path.splitext(img_file)[0] + ".txt"
        text_file_path = os.path.join(self.folder_path, text_file_name)
        if os.path.exists(text_file_path):
            with open(text_file_path, 'r') as f:
                text = f.read()
            self.TextFile.delete("1.0", "end")
            self.TextFile.insert("end", text)
        else:
            with open(text_file_path, 'w') as f:
                f.write("")

    def save_text(self, event=None):
        if self.current_image_file is None:
            return
        text_file_path = os.path.join(self.folder_path, os.path.splitext(self.current_image_file)[0] + ".txt")
        current_text = self.TextFile.get("1.0", "end-1c")
        try:
            with open(text_file_path, "w") as f:
                f.write(current_text)
        except IOError as e:
            print(f"Failed to save text: {e}")

    def increase_index_one(self, event=None):
        self.save_text()
        self.current_index = (self.current_index + 1) % len(self.image_files)
        if self.current_index < 0:
            self.current_index = len(self.image_files) - 1

    def decrease_index_one(self, event=None):
        self.save_text()
        self.current_index = (self.current_index - 1) % len(self.image_files)
        if self.current_index < 0:
            self.current_index = len(self.image_files) - 1

    def read_files_display_variables(self):
        folder = self.folder_path

        self.tag_summary = set()  # Reset the tag_summary set

        if not folder:
            pass
        else:
            for filename in os.listdir(folder):
                if filename.endswith('.txt'):
                    # Open the text file and read its contents
                    with open(os.path.join(folder, filename), 'r') as file:
                        text = file.read()

                    # Split the text into variables using the comma as the delimiter
                    text_variables = set(text.split(','))

                    # Strip whitespace from variables and add to self.tag_summary set
                    text_variables_stripped = {item.strip() for item in text_variables}
                    self.tag_summary.update(text_variables_stripped)
                    self.tag_sort = sorted(self.tag_summary)
                    total_tag_pool = len(self.tag_sort)
                    self.tag_nr_label.configure(text=f"Total tags: {total_tag_pool}")

            summary = "\n".join(self.tag_sort)
            self.tag_field.delete("1.0", "end")
            self.tag_field.insert("end", summary)

    def save_exluded_tags(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        current_text = self.exclude_text.get("1.0", "end-1c")
        if file_path:
            with open(file_path, 'w') as file:
                file.write(current_text)

    def load_excluded_tags(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.exclude_text.delete("1.0", "end")
                self.exclude_text.insert("end", content)

    def purge_tags_exec(self):

        text_tags = []
        text_tags = self.exclude_text.get("1.0", "end-1c").split(",")
        text_tags = [tag.strip() for tag in text_tags if tag.strip()]

        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(self.folder_path, file_name)
                with open(file_path, "r") as f:
                    file_tags = f.read().split(",")
                new_tag_list = []
                for tag in file_tags:
                    if tag.strip() not in [t.strip() for t in text_tags]:
                        new_tag_list.append(tag.strip())
                with open(file_path, "w") as f:
                    text = ", ".join(new_tag_list)

                    # Check for trailing comma and remove it if present
                    if text.endswith(','):
                        text = text[:-1]

                    f.write(text)
        self.update_text_file()
    # Define a function to run when the specific tab is activated
    def specific_tab_activated(self,event):
        # Get the index of the active tab
        active_index = event.widget.index("current")

        selected_option = tk.StringVar()
        # Check if the active tab is the specific tab
        if active_index == 1:  # Replace 1 with the index of your specific tab
            # Code to run when the specific tab is activated
            self.read_files_display_variables()

    def replace_tag(self):
        text_input = self.taginputtext.get("1.0", "end-1c")
        text_output = self.tagouttext.get("1.0", "end-1c")
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(self.folder_path, file_name)
                with open(file_path, "r") as f:
                    file_tags = f.read().split(",")
                new_tag_list = []
                for tag in file_tags:
                    if tag.strip() == text_input.strip():
                        new_tag_list.append(text_output.strip())
                    else:
                        new_tag_list.append(tag.strip())
                with open(file_path, "w") as f:
                    text = ", ".join(new_tag_list)

                    # Check for trailing comma and remove it if present
                    if text.endswith(","):
                        text = text[:-1]

                    f.write(text)
        self.update_text_file()

    def update_text_color_confirm(self, event):
        # Get the text in the text box
        text = self.taginputtext.get("1.0", "end-1c")

        # Loop through the match list and check for matches
        for match in self.tag_summary:
            if match == text:
                self.taginputtext.config(foreground="green")
                break
        else:
            self.taginputtext.config(foreground="red")
    def update_text_color_exists(self, event):
        # Get the text in the text box
        text = self.tagouttext.get("1.0", "end-1c")

        # Loop through the match list and check for matches
        for match in self.tag_summary:
            if match == text:
                self.tagouttext.config(foreground="blue")
                break
        else:
            self.tagouttext.config(foreground="green")

if __name__ == "__main__":
    app = FirsttryApp()
    app.run()
