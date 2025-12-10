import time
import threading
import pyperclip
import os
import subprocess
import keyboard

log_file="RoCopy.txt"

def rocopy():
    keyboard.send('ctrl+c')

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
                print(f"text was copied  {current}")
                last_text=current
        except Exception as e:
            print(e)
        time.sleep(0.5)

clipboard_thread=threading.Thread(target=monitor_clip,daemon=True)
clipboard_thread.start()            
keyboard.wait('f8',suppress=True)