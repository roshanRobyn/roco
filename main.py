import time
import threading
import pyperclip
import os
import subprocess
import keyboard
import psutil
import win32gui
import win32con
import tkinter as tk
import sys
from pynput import mouse
from pynput.mouse import Listener
from pathlib import Path
log_file = os.path.join(Path.home(), "Documents", "RoCopy.txt")

class TextSelectionDetector:
    def __init__(self):
        self.overlay = None
  
        self.is_dragging = False
        self.drag_start = None
        self.drag_end = None

        self.saw_ibeam_during_drag = False
        
        self.mouse_listener = None
        self.root = None 

    def is_text_cursor(self):
  
        try:
        
            flags, hcursor, (x,y) = win32gui.GetCursorInfo()

            system_ibeam = win32gui.LoadCursor(0, win32con.IDC_IBEAM)
            
            if hcursor == system_ibeam:
                return True
                
         
            if hcursor > 50000: 
                 return True
        except Exception:
            pass
        return False

    def monitor_cursor_thread(self):
      
        while self.is_dragging:
            if self.is_text_cursor():
                self.saw_ibeam_during_drag = True
               
                break 
            
            time.sleep(0.016)

    def create_overlay_button(self, x, y):
        def create_button():
            if self.overlay:
                self.overlay.destroy()
                
            self.overlay = tk.Toplevel()
            self.overlay.overrideredirect(True)
            self.overlay.attributes('-topmost', True)
            self.overlay.attributes('-alpha', 0.95)
            self.overlay.config(bg="white")
            self.overlay.attributes('-transparentcolor', "white")

            btn = tk.Button(
                self.overlay,
                text="⚡",
                font=("Segoe UI Emoji", 14),
                width=3,
                command=self.on_button_click,
                bg="#0078D7", # Standard Windows Blue
                fg="white",
                relief="flat",
                cursor="hand2"
            )
            btn.pack()
            
            # Position overlay
            self.overlay.geometry(f"+{x}+{y}")
            self.overlay.deiconify()
            
            # Auto-hide after 3 seconds
            self.overlay.after(3000, self.hide_overlay)
            
        if threading.current_thread() is threading.main_thread():
            create_button()
        else:
            self.overlay_queue = (x, y)
        
    def hide_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            
    def on_button_click(self):
        self.hide_overlay()
        time.sleep(0.5)
        rocopy()
        
    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            if pressed:
                self.is_dragging = True
                self.drag_start = (x, y)
                self.saw_ibeam_during_drag = False

                threading.Thread(target=self.monitor_cursor_thread, daemon=True).start()
                
            else:

                if self.is_dragging:
                    self.is_dragging = False 
                    self.drag_end = (x, y)
                    
                    if self.drag_start and self.drag_end:
                        start_x, start_y = self.drag_start
                        end_x, end_y = self.drag_end
                        
                
                        drag_dist = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
                        
                 
                        if drag_dist > 15 and self.saw_ibeam_during_drag:
                            
                            btn_x = end_x-250
                            btn_y = end_y-175
                            
                            self.overlay_queue = (int(btn_x), int(btn_y))
    def check_overlay_queue(self):
        if hasattr(self, 'overlay_queue'):
            x, y = self.overlay_queue
            self.create_overlay_button(x, y)
            delattr(self, 'overlay_queue')
            
    def start_mouse_listener(self):
        try:
            self.mouse_listener = Listener(on_click=self.on_click)
            self.mouse_listener.start()
            return True
        except Exception as e:
            print(f"❌ Failed to start listener: {e}")
            return False
            
    def stop_mouse_listener(self):
        if self.mouse_listener:
            self.mouse_listener.stop()







def rocopy():
    keyboard.send('ctrl+c')
def append_to_txt(text):
    try:
        with open(log_file,"a",encoding="utf-8") as f:
            f.write(text+"\n")
            f.write("\n\n")
            
        if not is_notepad_open():
            subprocess.Popen(["notepad.exe",log_file])
    except Exception as e:
        print(e)
    
def is_notepad_open():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name']=='notepad.exe':
                return True
        except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess):
            pass
    return False

def monitor_clip():
    last_text=""
    try:
        last_text=pyperclip.paste()
    except:
        pass
    while True:
        try:
            current=pyperclip.paste()
            if current!=last_text and current.strip() !="":
                append_to_txt(current)
                last_text=current
        except Exception as e:
            print(e)
        time.sleep(0.5)

def clear_notepad():
    with open(log_file,'w',encoding="utf-8") as f:
        pass
    hwnd = win32gui.FindWindow('Notepad', None)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        time.sleep(0.05)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
def close_notepad():
    subprocess.run(["taskkill", "/F", "/IM", "notepad.exe"])
    print("Exiting...")
    detector.stop_mouse_listener()
    root.quit()
    sys.exit()
#keyboard.add_hotkey('f6',rocopy,suppress=True)
keyboard.add_hotkey('f8',clear_notepad,suppress=True)
keyboard.add_hotkey('f9',close_notepad,suppress=True)
clipboard_thread=threading.Thread(target=monitor_clip,daemon=True)
clipboard_thread.start()            


print("🎯 Smart Selection Detector Running...")
detector = TextSelectionDetector()

if not detector.start_mouse_listener():
    print("Not Running")

root = tk.Tk()
root.withdraw()
detector.root = root

def check_queue():
    detector.check_overlay_queue()
    root.after(20, check_queue)
    
check_queue()

try:
    root.mainloop()
except KeyboardInterrupt:
    pass
finally:
    detector.stop_mouse_listener()   

