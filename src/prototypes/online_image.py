from tkinter import Tk, Label
from PIL import ImageTk, Image
import requests
from io import BytesIO

root = Tk()
root.title("Cover Image")

link = "https://images.genius.com/d89bfa02744ef691096746045ebd62a3.939x939x1.jpg"

class WebImage:
     def __init__(self,url):
          u = requests.get(url)
          image = Image.open(BytesIO(u.content)).resize((200, 200))
          self.image = ImageTk.PhotoImage(image)
          
     def get(self):
          return self.image

img = WebImage(link).get()
image_label = Label(root, image = img)
image_label.grid(row = 0, column = 0)

root.mainloop()