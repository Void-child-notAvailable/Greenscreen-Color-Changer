import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import sys
import json


def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])


def replace_green(img, hex_color):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    new_bgr = np.uint8([[hex_to_bgr(hex_color)]])
    new_hsv = cv2.cvtColor(new_bgr, cv2.COLOR_BGR2HSV)[0][0]
    hsv[:, :, 0][mask > 0] = new_hsv[0]
    hsv[:, :, 1][mask > 0] = new_hsv[1]
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

class GreenScreenReplacer:
    def __init__(self, root):
        self.root = root
        self.root.title("Green Screen Replacer")
        self.image_path = None
        self.output_image = None
        self.selected_hex = "#ffffff"
        self.root.configure(bg="#6E6161")

        tk.Button(root, text="Select Image", command=self.load_image,
                bg="black", fg="white", activebackground="#222222",
                activeforeground="white").pack(pady=5)


        self.pick_btn = tk.Button(root, text="Pick Color (Wheel)", command=self.pick_color,
                bg="black", fg="white", activebackground="#222222",
                activeforeground="white")
        self.hex_entry = tk.Entry(root, width=10,
                            bg="#111111", fg="white",
                            insertbackground="white")
        self.hex_entry.insert(0, self.selected_hex)
        self.hex_entry
        self.save_btn = tk.Button(root, text="Save Result", command=self.save_image,bg="black", fg="white", activebackground="#222222",
                activeforeground="white")
        self.preview_label = tk.Label(root, bg="#6E6161")
        self.preview_label.pack(pady=10)

    def load_image(self):
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            img = Image.open(self.image_path)
            img.thumbnail((550, 550))
            self.preview = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview)
            self.pick_btn.pack(pady=5)
            self.hex_entry.pack(pady=5)
            self.save_btn.pack(pady=5)

    def pick_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.selected_hex = color
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, color)
        self.process_image()

    def hex_to_bgr(self, hex_color):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (rgb[2], rgb[1], rgb[0])

    def process_image(self):
        if not self.image_path:
            messagebox.showerror("Error", "Select an image first")
            return

        hex_color = self.hex_entry.get()

        try:
            img = cv2.imread(self.image_path)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            #green mask
            lower_green = np.array([35, 50, 50])
            upper_green = np.array([85, 255, 255])

            mask = cv2.inRange(hsv, lower_green, upper_green)
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            new_bgr = np.uint8([[self.hex_to_bgr(hex_color)]])
            new_hsv = cv2.cvtColor(new_bgr, cv2.COLOR_BGR2HSV)[0][0]

            #hue / saturation
            hsv[:, :, 0][mask > 0] = new_hsv[0]
            hsv[:, :, 1][mask > 0] = new_hsv[1]
            self.output_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            preview_img = cv2.cvtColor(self.output_image, cv2.COLOR_BGR2RGB)
            preview_img = Image.fromarray(preview_img)
            preview_img.thumbnail((550, 550))
            self.preview = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=self.preview)

        except:
            messagebox.showerror("Error", "Invalid hex color")

    def save_image(self):
        if self.output_image is None:
            messagebox.showerror("Error", "Process image first")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png")
        if save_path:
            cv2.imwrite(save_path, self.output_image)
            messagebox.showinfo("Saved", "Image saved successfully")


if __name__ == "__main__":
    if (len(sys.argv)==3):
        ppath=sys.argv[1]
        jjson=sys.argv[2]
        img=cv2.imread(ppath) 
        with open(jjson,"r") as f:
            colors = json.load(f)
        for entry in colors:
            name = entry["name"]
            result = replace_green(img, entry["hex"])
            filename = name.replace(" ", "_") + ".png"
            cv2.imwrite(filename, result)
            print(f"Saved {filename}")
    else:
        root = tk.Tk()
        root.geometry("800x700")
        app = GreenScreenReplacer(root)
        root.mainloop()