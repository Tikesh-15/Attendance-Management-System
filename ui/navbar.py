import tkinter as tk

class Navbar(tk.Frame):

    def __init__(self, parent, toggle_command):
        super().__init__(parent, bg="white", height=50)

        # height fix rahe
        self.pack_propagate(False)

        # ===== LEFT SECTION =====
        left_frame = tk.Frame(self, bg="white")
        left_frame.pack(side="left", padx=10)

        # Menu Button
        self.menu_btn = tk.Button(
            left_frame,
            text="☰",
            font=("Arial", 16, "bold"),
            bg="white",
            bd=0,
            cursor="hand2",
            command=toggle_command
        )
        self.menu_btn.pack(side="left", padx=5)

        # Title
        self.title_label = tk.Label(
            left_frame,
            text="Student Management System",
            bg="white",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(side="left", padx=10)

        # ===== RIGHT SECTION =====
        right_frame = tk.Frame(self, bg="white")
        right_frame.pack(side="right", padx=15)

        self.user_label = tk.Label(
            right_frame,
            text="Admin",
            bg="white",
            font=("Arial", 12),
            fg="#555"
        )
        self.user_label.pack()