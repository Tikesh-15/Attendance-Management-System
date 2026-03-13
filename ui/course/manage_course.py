import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_FILE = "database.db"

# ===== 1. DATABASE CONNECTION & INITIALIZATION =====
def get_connection():
    # यह चेक करेगा कि टेबल बनी हैं या नहीं, नहीं तो बना देगा
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # कोर्स टेबल - इसमें teacher और students_count कॉलम्स फिक्स कर दिए हैं
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT UNIQUE,
            course_code TEXT,
            department TEXT,
            duration TEXT,
            description TEXT,
            teacher TEXT DEFAULT 'Not Assigned',
            students_count INTEGER DEFAULT 0
        )
    """)
    
    # स्टाफ टेबल
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first TEXT,
            last TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            designation TEXT,
            dept TEXT
        )
    """)
    
    # सब्जेक्ट टेबल
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subject(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT,
            course TEXT,
            staff_id INTEGER
        )
    """)

    conn.commit()
    return conn

# ===== 2. MANAGE COURSE FRAME =====
class ManageCourse(tk.Frame):
    def __init__(self, parent, controller):
        # UI Setup
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller
        self.search_var = tk.StringVar()

        # --- UI Header ---
        header_frame = tk.Frame(self, bg="#f8fafc")
        header_frame.pack(fill="x", padx=40, pady=(30, 10))
        
        tk.Label(header_frame, text="Course Management", font=("Segoe UI", 22, "bold"), 
                 bg="#f8fafc", fg="#1e293b").pack(anchor="w")
        tk.Label(header_frame, text="Government V.Y.T. PG Autonomous College, Durg", 
                 font=("Segoe UI", 10), bg="#f8fafc", fg="#64748b").pack(anchor="w")

        # --- Toolbar (Search & Add) ---
        toolbar = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#e2e8f0")
        toolbar.pack(fill="x", padx=40, pady=10, ipady=8)

        search_entry = tk.Entry(toolbar, textvariable=self.search_var, font=("Segoe UI", 10), 
                               fg="#1e293b", bd=0, highlightthickness=1, 
                               highlightbackground="#cbd5e1", width=40)
        search_entry.pack(side="left", padx=20, ipady=6)
        
        # Placeholder logic
        search_entry.insert(0, "Search course...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if self.search_var.get() == "" else None)

        tk.Button(toolbar, text="+ Add Course", bg="#0d6efd", fg="white", 
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=5, 
                  cursor="hand2", command=self.open_add_page).pack(side="right", padx=20)

        # --- Scrollable Container Setup ---
        canvas_container = tk.Frame(self, bg="#f8fafc")
        canvas_container.pack(fill="both", expand=True, padx=40, pady=10)

        self.canvas = tk.Canvas(canvas_container, bg="#f8fafc", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        self.card_frame = tk.Frame(self.canvas, bg="#f8fafc")
        
        # Scroll region bind
        self.card_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.card_frame, anchor="nw")
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel functionality
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Data loading
        self.search_var.trace_add("write", lambda *args: self.refresh_cards())
        self.refresh_cards()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        try: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except: pass

    def refresh_cards(self):
        """डेटाबेस से डेटा खींचना और कार्ड्स बनाना"""
        # पुराने कार्ड्स साफ़ करें
        for widget in self.card_frame.winfo_children():
            widget.destroy()

        search_query = self.search_var.get().strip()
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query Order: id(0), name(1), code(2), teacher(3), students(4), duration(5)
        sql = "SELECT id, course_name, course_code, teacher, students_count, duration FROM course"         
        
        if search_query and search_query != "Search course...":
            cursor.execute(f"{sql} WHERE course_name LIKE ? OR course_code LIKE ?", 
                           ('%'+search_query+'%', '%'+search_query+'%'))
        else:
            cursor.execute(sql)
            
        rows = cursor.fetchall()
        conn.close()

        # कार्ड्स को ग्रिड में सजाना (3 columns)
        self.card_frame.columnconfigure((0, 1, 2), weight=1)
        row, col = 0, 0
        for data in rows:
            self.create_course_card(data, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def create_course_card(self, data, r, c):
        # Unpacking must match SQL order
        cid, name, code, teacher, count, duration = data

        card = tk.Frame(self.card_frame, bg="white", highlightthickness=1, 
                        highlightbackground="#e2e8f0", padx=20, pady=20)
        card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")

        # Status Tag
        top_frame = tk.Frame(card, bg="white")
        top_frame.pack(fill="x")
        tk.Label(top_frame, text="📗", font=("Arial", 16), bg="#f0fdf4", fg="#16a34a").pack(side="left")
        tk.Label(top_frame, text="Active", font=("Segoe UI", 8, "bold"), bg="#dcfce7", fg="#166534", padx=10).pack(side="right")

        # Course Info
        tk.Label(card, text=name, font=("Segoe UI", 13, "bold"), bg="white", fg="#1e293b", wraplength=220, justify="left").pack(anchor="w", pady=(15, 0))
        tk.Label(card, text=f"Code: {code}", font=("Segoe UI", 9), bg="white", fg="#64748b").pack(anchor="w")
        
        tk.Label(card, text=f"👨‍🏫 {teacher}", font=("Segoe UI", 9), bg="white", fg="#475569").pack(anchor="w", pady=(10, 0))
        tk.Label(card, text=f"👥 {count} Students", font=("Segoe UI", 9), bg="white", fg="#475569").pack(anchor="w")
        tk.Label(card, text=f"⏳ {duration}", font=("Segoe UI", 9), bg="white", fg="#475569").pack(anchor="w")

        # Buttons
        action_frame = tk.Frame(card, bg="white", pady=10)
        action_frame.pack(fill="x", pady=(15, 0))
        tk.Frame(action_frame, height=1, bg="#f1f5f9").pack(fill="x", side="top", pady=5)

        tk.Button(action_frame, text="📝 Edit", font=("Segoe UI", 9, "bold"), fg="#2563eb", 
                  bg="white", bd=0, cursor="hand2", command=lambda d=data: self.edit_course(d)).pack(side="left", padx=10)

        tk.Button(action_frame, text="🗑 Delete", font=("Segoe UI", 9, "bold"), fg="#dc2626", 
                  bg="white", bd=0, cursor="hand2", command=lambda i=cid: self.delete_course(i)).pack(side="right", padx=10)

    def open_add_page(self):
        try:
            from ui.course.add_course import AddCourse
            self.controller.show_frame(AddCourse)
        except Exception as e:
            messagebox.showerror("Error", f"AddCourse page error: {e}")

    def edit_course(self, data_tuple):
        try:
            # self.controller hamari App class hai main.py wali
            # Direct "AddCourse" string bhej sakte ho ya class
            self.controller.show_frame("AddCourse", edit_data=data_tuple)
        except Exception as e:
            messagebox.showerror("Error", f"Edit error: {e}")

    def delete_course(self, cid):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this course?"):
            conn = get_connection()
            conn.cursor().execute("DELETE FROM course WHERE id=?", (cid,))
            conn.commit()
            conn.close()
            self.refresh_cards()