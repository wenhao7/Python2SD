import tkinter as tk
from tkinter import ttk, DoubleVar
from tkinter.colorchooser import askcolor
import threading
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image, ImageGrab
import base64
import requests
import io

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing App")

        # Variables for drawing
        self.start_x, self.start_y = None, None
        self.current_object = None
        self.color = "black"
        self.linewidth = DoubleVar()
        self.linewidth.set(3)
        self.CANVAS_HEIGHT = 512
        self.CANVAS_WIDTH = 512
        self.root.minsize(self.CANVAS_WIDTH*2,self.CANVAS_HEIGHT+100)  
        
        
        # Create a canvas
        self.canvas = tk.Canvas(root, bg="white", height=self.CANVAS_HEIGHT, width=self.CANVAS_WIDTH)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a toolbar
        self.toolbar = ttk.Frame(root)
        self.toolbar.pack(side=tk.BOTTOM)

        # Create drawing tools buttons
        self.pen_button = ttk.Button(self.toolbar, text="Pen", command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.line_button = ttk.Button(self.toolbar, text="Line", command=self.use_line)
        self.line_button.grid(row=0, column=1)

        self.rectangle_button = ttk.Button(self.toolbar, text="Rectangle", command=self.use_rectangle)
        self.rectangle_button.grid(row=0, column=2)
        
        self.ellipse_button = ttk.Button(self.toolbar, text="Ellipse", command=self.use_ellipse)
        self.ellipse_button.grid(row=0, column=3)

        self.text_button = ttk.Button(self.toolbar, text="Text", command=self.use_text)
        self.text_button.grid(row=0, column=4)
        
        self.color_button = ttk.Button(self.toolbar, text="Color", command=self.color_picker)
        self.color_button.grid(row=0, column=5)
        
        self.clear_button = ttk.Button(self.toolbar, text="Clear", command=self.clear_drawings)
        self.clear_button.grid(row=0, column=6)
        
        self.linewidth_slider = ttk.Scale(self.toolbar, from_=1, to=20, value=3, variable=self.linewidth)
        self.linewidth_slider.grid(row=1, column=0)
        
        self.prompt_button = ttk.Button(self.toolbar, text="Prompt", command=self.prompt_picker)
        self.prompt_button.grid(row=1, column=2)

        # Initialize drawing mode
        self.drawing_mode = "pen"

        # Binding mouse events
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        
        # Stablediffusion variables
        self.url = "http://127.0.0.1:7860"
        self.prompt = "style of anderson wes"
        self.seed = -1
        self.generating = False
        self.cn_model = "control_v11p_sd15_scribble [d4ba51ff]"
        self.image = None
        self.return_image = None
        self.payload = None
        
        # Stablediffusion canvas
        # px = 1/plt.rcParams['figure.dpi']
        # self.fig = plt.figure(figsize=(self.CANVAS_HEIGHT*px, self.CANVAS_WIDTH*px))
        # self.ax = self.fig.add_subplot(111)
        # self.sd = FigureCanvasTkAgg(self.fig, master=root)
        # self.sd.draw()
        # self.sd._tkcanvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # self.background = self.sd.copy_from_bbox(self.ax.bbox)
        self.sd = tk.Canvas(root, height=self.CANVAS_HEIGHT, width=self.CANVAS_WIDTH)
        self.sd.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
    ### Drawing Canvas 
    def use_pen(self):
        self.drawing_mode = "pen"

    def use_line(self):
        self.drawing_mode = "line"

    def use_rectangle(self):
        self.drawing_mode = "rectangle"
    
    def use_ellipse(self):
        self.drawing_mode = "ellipse"

    def use_text(self):
        self.drawing_mode = "text"
    
    def color_picker(self):
        self.color = askcolor(color=self.color)[1]
    
    def clear_drawings(self):
        self.canvas.delete('all')
        self.sd.delete("all")
        
    def prompt_picker(self):
        text = tk.simpledialog.askstring(title="Prompt",
                                         prompt="Please enter your prompt:")
        with open("payload.json", "r") as jsonFile:
            data = json.load(jsonFile)
            
        data["prompt"] = text
        
        with open("payload.json", "w") as jsonFile:
            json.dump(data, jsonFile)


    def start_drawing(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.drawing_mode == "pen":
            self.current_object = self.canvas.create_line(event.x, event.y, event.x, event.y, fill=self.color, width=self.linewidth.get())
        elif self.drawing_mode == "text":
            #text = input("Enter text: ")
            text = tk.simpledialog.askstring(title="Text",
                                             prompt="Please enter text:")
            self.current_object = self.canvas.create_text(event.x, event.y, text=text, font=("Arial", 12))
        else:
            self.start_x, self.start_y = event.x, event.y

    def draw(self, event):
        if self.drawing_mode == "pen":
            x, y = event.x, event.y
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.color, width=self.linewidth.get())
            self.start_x, self.start_y = x, y
        elif self.drawing_mode == "line":
            if self.current_object:
                self.canvas.delete(self.current_object)
            self.current_object = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill=self.color, width=self.linewidth.get())
        elif self.drawing_mode == "rectangle":
            if self.current_object:
                self.canvas.delete(self.current_object)
            self.current_object = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, fill=self.color, width=0)
        elif self.drawing_mode == "ellipse":
            if self.current_object:
                self.canvas.delete(self.current_object)
            self.current_object = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y, fill=self.color, width=0)
        else:
            pass

    def stop_drawing(self, event):
        self.current_object = None
        
        # Try generating an img
        self.generate(self.canvas)

    ### StableDiffusion
    #Draw img2img input
    def getter(self, widget):
        x = self.root.winfo_rootx()+widget.winfo_x()
        y = self.root.winfo_rooty()+widget.winfo_y()
        x1=x+widget.winfo_width()
        y1=y+widget.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save("get.PNG")
    
    def display(self, image_data):
        img_bytes = io.BytesIO(base64.b64decode(image_data))
        img = Image.open(img_bytes)
        img.save('sd1.PNG')
        self.image = ImageTk.PhotoImage(img)
        
        self.sd.create_image(256,256,image=self.image)
        #self.sd.update()
    
    # def send_request(self, payload):
        
    #     response = requests.post(url=f'{self.url}/sdapi/v1/txt2img', json=payload)
    #     r = response.json()
    #     self.return_img = r['images'][0]
        
    def generate(self, widget):
        self.getter(widget)
        if not self.generating:
            self.generating = True
            #img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img = open("get.PNG", 'rb').read()
            b64_string = base64.b64encode(img).decode('utf-8')
            
            with open("payload.json", "r") as f:
                self.payload = json.load(f)
            
            self.payload['alwayson_scripts']["controlnet"]["args"][0]["input_image"] = b64_string
            
            def send_request():
                response = requests.post(url=f'{self.url}/sdapi/v1/txt2img', json=self.payload)
                r = response.json()
                return_img = r['images'][0]
                self.display(return_img)
                self.generating=False
            t = threading.Thread(target=send_request)
            t.start()
            #self.display(self.return_img)
        
    
    
if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
