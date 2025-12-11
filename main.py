import time
import threading
import pyperclip
import os
import subprocess
import keyboard
import psutil
import win32gui
import win32con
from pathlib import Path
log_file = os.path.join(Path.home(), "Documents", "RoCopy.txt")

def rocopy():
    keyboard.send('ctrl+c')
def append_to_txt(text):
    try:
        with open(log_file,"a",encoding="utf-8") as f:
            f.write(text+"\n")
        if not is_notepad_open():
            with open(log_file,"w",encoding="utf-8") as f:
                pass
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
keyboard.add_hotkey('f7',rocopy,suppress=True)
clipboard_thread=threading.Thread(target=monitor_clip,daemon=True)
clipboard_thread.start()            
keyboard.wait('f8',suppress=True)