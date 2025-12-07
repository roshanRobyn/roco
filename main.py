import customtkinter
import tkinter
import os

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Roco")
        self.geometry("400x500")
        self.textbox = customtkinter.CTkTextbox(master=self,width=400,height=500, corner_radius=0)
        self.textbox.pack(fill="both",expand=True,padx=0,pady=0)


app = App()
app.mainloop()
def key_pressed(event):
            self.textbox.insert(event.char)
app.bind("<Key>",key_pressed)
