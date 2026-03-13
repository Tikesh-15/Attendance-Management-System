import tkinter as tk

from ui.sidebar import Sidebar
from ui.navbar import Navbar
from ui.home import HomePage


class Dashboard(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f2f5")

        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")
        # ===== NAVBAR =====
        self.navbar = Navbar(self, self.toggle_sidebar)
        self.navbar.pack(side="top", fill="x")

        # ===== WRAPPER =====
        self.wrapper = tk.Frame(self, bg="#f0f2f5")
        self.wrapper.pack(fill="both", expand=True)

        # ===== SIDEBAR =====
        self.sidebar = Sidebar(
            self.wrapper,
            self.controller,
            None
        )
        self.sidebar.pack(side="left", fill="y")

        # ===== MAIN AREA =====
        self.main_area = tk.Frame(self.wrapper, bg="#f0f2f5")
        self.main_area.pack(side="right", fill="both", expand=True)

        # ===== PAGE CONTAINER =====
        self.page_container = tk.Frame(self.main_area, bg="#f0f2f5")
        self.page_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Sidebar को सही content frame देना
        self.sidebar.content_frame = self.page_container

        # ===== DEFAULT PAGE =====
        self.sidebar.show_page(HomePage)

    # ===== SIDEBAR TOGGLE =====
    def toggle_sidebar(self):

        # अगर sidebar दिख रहा है → hide
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()

        # अगर hidden है → show
        else:
            self.sidebar.pack(side="left", fill="y")