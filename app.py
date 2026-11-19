import tkinter as tk
from gui.main_window import ImageDuplicateDetectorDemo

print("Step 1: app.py is running")

if __name__ == "__main__":

    app_root = tk.Tk()
    print("Step 2: Tkinter window created")

    app = ImageDuplicateDetectorDemo(app_root)
    print("Step 3: GUI class created")

    app_root.mainloop()