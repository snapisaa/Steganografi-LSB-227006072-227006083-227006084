import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# LSB Embedding Class
class LSBEmbedding:
    def __init__(self, cover_image_path, secret_message, output_path):
        self.cover_image_path = cover_image_path
        self.secret_message = secret_message
        self.output_path = output_path

    def embed_message(self):
        try:
            # Load cover image
            cover_image = Image.open(self.cover_image_path)
            width, height = cover_image.size

            # Convert secret message to binary
            secret_binary = ''.join(format(ord(char), '08b') for char in self.secret_message)
            message_length = len(secret_binary)
            length_binary = format(message_length, '032b')  # Store length as 32-bit binary
            secret_binary = length_binary + secret_binary

            # Embed message into image
            if len(secret_binary) > width * height:
                raise ValueError("Secret message is too large for the cover image.")

            data_index = 0
            for y in range(height):
                for x in range(width):
                    pixel = list(cover_image.getpixel((x, y)))
                    for i in range(3):  # RGB channels
                        if data_index < len(secret_binary):
                            pixel[i] = pixel[i] & 0xFE | int(secret_binary[data_index])
                            data_index += 1
                    cover_image.putpixel((x, y), tuple(pixel))

            # Save stego image
            cover_image.save(self.output_path)
            messagebox.showinfo("Success", "Secret message embedded successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# LSB Extraction Class
class LSBExtraction:
    def __init__(self, stego_image_path):
        self.stego_image_path = stego_image_path
        self.extracted_message = ""

    def extract_message(self):
        try:
            # Load stego image
            stego_image = Image.open(self.stego_image_path)
            width, height = stego_image.size

            # Extract message from image
            extracted_binary = ""
            for y in range(height):
                for x in range(width):
                    pixel = stego_image.getpixel((x, y))
                    for i in range(3):  # RGB channels
                        extracted_binary += str(pixel[i] & 1)

            # Extract the length of the message
            length_binary = extracted_binary[:32]
            message_length = int(length_binary, 2)
            message_binary = extracted_binary[32:32 + message_length]

            # Convert binary to string
            self.extracted_message = "".join(chr(int(message_binary[i:i+8], 2)) for i in range(0, len(message_binary), 8))

            messagebox.showinfo("Extracted Message", f"The extracted message is: {self.extracted_message}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# GUI Class for Encoding and Decoding
class LSBSteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSB Steganography")

        # Create frames
        self.encode_frame = tk.LabelFrame(root, text="Encode", padx=10, pady=10, bg="#add8e6")
        self.encode_frame.grid(row=0, column=0, padx=10, pady=10)

        self.decode_frame = tk.LabelFrame(root, text="Decode", padx=10, pady=10, bg="#add8e6")
        self.decode_frame.grid(row=0, column=1, padx=10, pady=10)

        # Encoding widgets
        tk.Label(self.encode_frame, text="Cover Image:", bg="#add8e6").grid(row=0, column=0, sticky="w")
        self.cover_image_entry = tk.Entry(self.encode_frame, width=40)
        self.cover_image_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        tk.Button(self.encode_frame, text="Browse", command=self.browse_cover_image).grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self.encode_frame, text="Secret Message:", bg="#add8e6").grid(row=1, column=0, sticky="w")
        self.secret_message_entry = tk.Entry(self.encode_frame, width=40)
        self.secret_message_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        self.embed_button = tk.Button(self.encode_frame, text="Embed Message", command=self.embed_message, bg="#4682b4", fg="white")
        self.embed_button.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        # Decoding widgets
        tk.Label(self.decode_frame, text="Stego Image:", bg="#add8e6").grid(row=0, column=0, sticky="w")
        self.stego_image_entry = tk.Entry(self.decode_frame, width=40)
        self.stego_image_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        tk.Button(self.decode_frame, text="Browse", command=self.browse_stego_image).grid(row=0, column=3, padx=5, pady=5)

        self.extract_button = tk.Button(self.decode_frame, text="Extract Message", command=self.extract_message, bg="#4682b4", fg="white")
        self.extract_button.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Label to display extracted message
        self.extracted_message_label = tk.Label(self.decode_frame, text="Extracted Message:", padx=5, pady=5, bg="#add8e6")
        self.extracted_message_label.grid(row=2, column=0, columnspan=4)

        # Label to display cover image
        self.cover_image_label = tk.Label(self.encode_frame, padx=10, pady=10, bg="white")
        self.cover_image_label.grid(row=3, column=0, columnspan=4)

        # Label to display stego image for decoding
        self.stego_image_label = tk.Label(self.decode_frame, padx=10, pady=10, bg="white")
        self.stego_image_label.grid(row=3, column=0, columnspan=4)

        # Button to clear all
        self.clear_button = tk.Button(root, text="Clear", command=self.clear_all, bg="#4682b4", fg="white")
        self.clear_button.grid(row=1, column=0, columnspan=2, pady=10)

    def browse_cover_image(self):
        cover_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if cover_image_path:
            self.cover_image_entry.delete(0, tk.END)
            self.cover_image_entry.insert(0, cover_image_path)
            self.show_cover_image(cover_image_path)

    def browse_stego_image(self):
        stego_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if stego_image_path:
            self.stego_image_entry.delete(0, tk.END)
            self.stego_image_entry.insert(0, stego_image_path)
            self.show_stego_image(stego_image_path)

    def embed_message(self):
        cover_image_path = self.cover_image_entry.get()
        secret_message = self.secret_message_entry.get()
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if cover_image_path and secret_message and output_path:
            embedding = LSBEmbedding(cover_image_path, secret_message, output_path)
            embedding.embed_message()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def extract_message(self):
        stego_image_path = self.stego_image_entry.get()
        if stego_image_path:
            extraction = LSBExtraction(stego_image_path)
            extraction.extract_message()
            # Display extracted message
            self.extracted_message_label.config(text=f"Extracted Message: {extraction.extracted_message}")
        else:
            messagebox.showerror("Error", "Please select a stego image.")

    def show_cover_image(self, cover_image_path):
        cover_image = Image.open(cover_image_path)
        cover_image.thumbnail((200, 200))  # Resize image to fit within 200x200 pixels
        cover_image = ImageTk.PhotoImage(cover_image)
        self.cover_image_label.config(image=cover_image)
        self.cover_image_label.image = cover_image  # Keep a reference to prevent garbage collection

    def show_stego_image(self, stego_image_path):
        stego_image = Image.open(stego_image_path)
        stego_image.thumbnail((200, 200))  # Resize image to fit within 200x200 pixels
        stego_image = ImageTk.PhotoImage(stego_image)
        self.stego_image_label.config(image=stego_image)
        self.stego_image_label.image = stego_image  # Keep a reference to prevent garbage collection

    def clear_all(self):
        # Clear all entry fields, labels, and images
        self.cover_image_entry.delete(0, tk.END)
        self.secret_message_entry.delete(0, tk.END)
        self.stego_image_entry.delete(0, tk.END)
        self.extracted_message_label.config(text="Extracted Message:")
        self.cover_image_label.config(image=None)
        self.stego_image_label.config(image=None)

if __name__ == "__main__":
    root = tk.Tk()
    app = LSBSteganographyApp(root)
    root.configure(bg="#add8e6")  # Change main background color to light blue
    root.mainloop()
