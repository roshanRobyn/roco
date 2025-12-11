import tkinter as tk
import threading
import time
import win32gui
import win32con
import win32api
from pynput import mouse
from pynput.mouse import Listener
import sys

class TextSelectionDetector:
    def __init__(self):
        self.overlay = None
        self.is_dragging = False
        self.drag_start = None
        self.drag_end = None
        self.mouse_listener = None
        self.root = None # Reference to main root
        
    def get_window_at_point(self, x, y):
        return win32gui.WindowFromPoint((x, y))
        
    def check_edit_control_selection(self, hwnd):
        try:
            class_name = win32gui.GetClassName(hwnd)
            edit_classes = ['edit', 'richedit', 'richedit20a', 'richedit20w', 'richedit50w']
            
            if any(ec in class_name.lower() for ec in edit_classes):
                try:
                    result = win32api.SendMessage(hwnd, win32con.EM_GETSEL, 0, 0)
                    if result != -1 and result != 0:
                        start_pos = result & 0xFFFF
                        end_pos = (result >> 16) & 0xFFFF
                        if start_pos != end_pos:
                            rect = win32gui.GetWindowRect(hwnd)
                            return True, rect
                except:
                    pass
        except:
            pass
        return False, None
        
    def detect_text_selection_heuristic(self, start_x, start_y, end_x, end_y):
        points_to_check = [
            (start_x, start_y),
            (end_x, end_y),
            ((start_x + end_x) // 2, (start_y + end_y) // 2),
        ]
        
        for x, y in points_to_check:
            hwnd = self.get_window_at_point(x, y)
            if hwnd:
                has_selection, rect = self.check_edit_control_selection(hwnd)
                if has_selection:
                    return True, rect
                    
        drag_distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        
        if drag_distance > 20:
            dx = abs(end_x - start_x)
            
            if dx > 10:
                hwnd = self.get_window_at_point((start_x + end_x) // 2, (start_y + end_y) // 2)
                if hwnd:
                    try:
                        class_name = win32gui.GetClassName(hwnd).lower()
                        window_text = win32gui.GetWindowText(hwnd).lower()
                        
                        text_indicators = [
                            'edit', 'richedit', 'static', 'chrome', 'firefox', 'edge',
                            'notepad', 'scintilla', 'text', 'document', 'browser',
                            'word', 'excel', 'powerpoint', 'adobe', 'pdf', 'sublime',
                            'vscode', 'atom', 'intellij', 'pycharm', 'discord', 'slack',
                            'teams', 'outlook', 'thunderbird'
                        ]
                        
                        if (any(indicator in class_name for indicator in text_indicators) or
                            any(indicator in window_text for indicator in text_indicators)):
                            return True, (min(start_x, end_x), min(start_y, end_y), 
                                        max(start_x, end_x), max(start_y, end_y))
                    except:
                        pass
                    
        return False, None
        
    def create_overlay_button(self, x, y):
        def create_button():
            if self.overlay:
                self.overlay.destroy()
                
            self.overlay = tk.Toplevel() # Use Toplevel instead of Tk for overlay
            self.overlay.overrideredirect(True)
            self.overlay.attributes('-topmost', True)
            self.overlay.attributes('-alpha', 0.95)
            
            frame = tk.Frame(self.overlay, bg="#FF6B35", relief="flat", bd=1)
            frame.pack(fill="both", expand=True)
            
            btn = tk.Button(
                frame,
                text="⚡",
                font=("Segoe UI Emoji", 12, "bold"),
                width=2,
                height=1,
                command=self.on_button_click,
                bg="#FF6B35",
                fg="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                activebackground="#FF8C42",
                activeforeground="white"
            )
            btn.pack(padx=2, pady=2)
            
            def on_enter(e):
                btn.config(bg="#FF8C42")
                frame.config(bg="#FF8C42")
                
            def on_leave(e):
                btn.config(bg="#FF6B35")
                frame.config(bg="#FF6B35")
                
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            # Position overlay
            self.overlay.geometry(f"40x32+{x}+{y}")
            self.overlay.deiconify()
            
            # Auto-hide after 5 seconds
            self.overlay.after(5000, self.hide_overlay)
            
        if threading.current_thread() is threading.main_thread():
            create_button()
        else:
            self.overlay_queue = (x, y)
        
    def hide_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            
    def on_button_click(self):
        self.your_f7_function()
        self.hide_overlay()
        
    def your_f7_function(self):
        print("🚀 Action Triggered!")
        # Add your copy/paste logic here
        
    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            if pressed:
                self.is_dragging = True
                self.drag_start = (x, y)
            else:
                if self.is_dragging:
                    self.is_dragging = False
                    self.drag_end = (x, y)
                    
                    if self.drag_start and self.drag_end:
                        start_x, start_y = self.drag_start
                        end_x, end_y = self.drag_end
                        
                        drag_distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
                        if drag_distance > 15:
                            threading.Thread(
                                target=self.delayed_selection_check,
                                args=(start_x, start_y, end_x, end_y),
                                daemon=True
                            ).start()
        
    def delayed_selection_check(self, start_x, start_y, end_x, end_y):
        time.sleep(0.25)
        
        has_selection, selection_rect = self.detect_text_selection_heuristic(
            start_x, start_y, end_x, end_y
        )
        
        if has_selection:
            # --- MODIFIED POSITIONING LOGIC ---
            if selection_rect and len(selection_rect) >= 4:
                # If we have a specific window rect from Win32 API
                # Usually rect is (left, top, right, bottom)
                # We want Top-Right
                right_edge = selection_rect[2]
                top_edge = selection_rect[1]
                
                button_x = int(right_edge)
                button_y = int(top_edge) - 40 # 40px above the top edge
            else:
                # Fallback / Heuristic
                # Max X is the rightmost point of the drag
                # Min Y is the topmost point of the drag
                right_edge = max(start_x, end_x)
                top_edge = min(start_y, end_y)
                
                button_x = right_edge
                button_y = top_edge - 40 # Place it slightly above the start of selection
                
            # Keep button on screen
            # We need a dummy TK instance to check screen dimensions if main isn't accessible
            # But we can just use safe bounds
            button_x = min(button_x, 1920 - 50) # Assuming 1920 width, adjust if needed
            button_y = max(button_y, 0)
            
            self.overlay_queue = (int(button_x), int(button_y))
            
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
            print(f"❌ Failed to start mouse listener: {e}")
            return False
            
    def stop_mouse_listener(self):
        if self.mouse_listener:
            self.mouse_listener.stop()

def main():
    # Install pynput if not available
    try:
        import pynput
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        import pynput
    
    detector = TextSelectionDetector()
    
    if not detector.start_mouse_listener():
        return
        
    print("Running in background... (Close the terminal window to stop)")
    
    # --- UI SETUP ---
    # We create the root window but HIDE it immediately
    root = tk.Tk()
    root.withdraw() # <--- THIS HIDES THE MAIN WINDOW
    
    detector.root = root
    
    # We still need the mainloop to process the button clicks
    def check_queue():
        detector.check_overlay_queue()
        root.after(50, check_queue)
        
    check_queue()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        detector.stop_mouse_listener()

if __name__ == "__main__":
    main()