import time
import threading
import pyperclip
import os
import subprocess
import keyboard  # pip install keyboard

# --- CONFIGURATION ---
LOG_FILE = "clipboard_log.txt"

# --- HELPER: FILE HANDLING ---
def append_to_log(text):
    """
    Opens the text file, appends the new text, and saves it.
    """
    try:
        # 'a' mode means Append (add to end) instead of Overwrite
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n" + "-"*30 + "\n") # Add text + separator
        print(f"[Saved] Text appended to {LOG_FILE}")
        
        # Optional: Force open the file so the user can see it
        # We perform a simple check to see if we should pop it up
        if not is_notepad_open():
             subprocess.Popen(["notepad.exe", LOG_FILE])
             
    except Exception as e:
        print(f"File Error: {e}")

def is_notepad_open():
    """
    Simple check to see if wse have recently opened the file.
    """
    # Just returning False helps ensure it pops up if closed.
    return False 

# --- PART 1: CLIPBOARD MONITOR ---
def monitor_clipboard():
    """
    Runs in the background. Watches for new text on the clipboard.
    """
    last_text = ""
    try:
        last_text = pyperclip.paste() 
    except:
        pass

    while True:
        try:
            current_text = pyperclip.paste()
            # If text has changed and is not empty
            if current_text != last_text and current_text.strip() != "":
                print(f"\n[Clipboard] New text detected: '{current_text[:20]}...'")
                
                # SAVE THE TEXT TO THE FILE AUTOMATICALLY
                append_to_log(current_text)
                
                last_text = current_text
        except Exception as e:
            print(f"Clipboard Error: {e}")
        
        time.sleep(0.5)

# --- PART 2: KEYBOARD LOGIC (With Suppression) ---
def on_f7_triggered():
    """
    Runs when F7 is pressed.
    suppress=True in the listener prevents Chrome/Windows from seeing F7.
    """
    print("F7 Pressed (Suppressed). Performing Copy...")
    
    # We use keyboard.send() to simulate Ctrl+C
    # This is cleaner than pynput's controller when using the keyboard library
    keyboard.send('ctrl+c')

    # The background thread (monitor_clipboard) will catch the change automatically.

# --- MAIN EXECUTION ---

# 1. Create the file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("--- Clipboard History Log ---\n")

# 2. Open it immediately
subprocess.Popen(["notepad.exe", LOG_FILE])

# 3. Start the Clipboard Monitor in the background
clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
clipboard_thread.start()

print(f"App Running. Logging to: {os.path.abspath(LOG_FILE)}")
print("- Select text and press F7 (Key is suppressed from other apps)")
print("- Press F8 to Quit")

# 4. SETUP HOTKEYS
# keyboard.add_hotkey is non-blocking. It runs in the background.
keyboard.add_hotkey('f7', on_f7_triggered, suppress=True)

# 5. BLOCK AND WAIT FOR F8
# This line creates a blocking loop that waits specifically for F8.
# suppress=True ensures F8 doesn't do anything else (like Windows Safe Mode logic).
keyboard.wait('f8', suppress=True)

print("F8 Pressed. Exiting...")