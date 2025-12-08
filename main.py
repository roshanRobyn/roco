import customtkinter as ctk
import tkinter
from tkinter import filedialog
import os
class MyTabView(ctk.CTkTabview):
    def __init__(self,master, **kwargs):
        super().__init__(master,**kwargs)
        self.tab_count=0
        self.configure(command=self.check_tab_event)
        self.add_new_tab()
        
    def check_tab_event(self):
        if self.get()=="+":
            self.add_new_tab()
            
    def add_new_tab(self):
        self.tab_count+=1
        new_tab_name=f"Document{self.tab_count}"
        try:
            self.delete("+")
        except ValueError:
            pass
        self.add(new_tab_name)
        textbox=ctk.CTkTextbox(self.tab(new_tab_name))
        textbox.pack(fill="both",expand=True)
        self.add("+")
        self.set(new_tab_name)


        
        
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Roco")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        self.geometry("400x500")
        self.tabV=MyTabView(master=self)
        self.tabV.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

app = App()
app.mainloop()
def key_pressed(event):
            self.textbox.insert(event.char)
app.bind("<Key>",key_pressed)
